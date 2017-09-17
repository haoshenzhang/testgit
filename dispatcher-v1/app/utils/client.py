# !/usr/bin/python
# -*- coding: utf-8 -*-
"""
    sxw 2016-11-4

    An OAuth 2.0 client.
    Tools for interacting with OAuth 2.0 protected catalog.
    ref: https://github.com/google/oauth2client/blob/master/oauth2client/client.py
"""

import collections
import copy
import datetime
import functools

import httplib2
from six.moves import http_client
from six.moves import urllib
from flask import current_app, g, json

from app.utils import helpers as _helpers
from app.utils import transport
from app.utils.helpers import update_query_params

HAS_OPENSSL = False
HAS_CRYPTO = False

# # Expiry is stored in RFC3339 UTC format
# EXPIRY_FORMAT = '%Y-%m-%dT%H:%M:%SZ'
# Expiry is stored in UTC8 format
EXPIRY_FORMAT = '%Y-%m-%d %H:%M:%SZ'

# The access token along with the seconds in which it expires.
AccessTokenInfo = collections.namedtuple(
    'AccessTokenInfo', ['access_token', 'expires_in'])

# Expose utcnow() at module level to allow for
# easier testing (by replacing with a stub).
_UTC8 = datetime.datetime.now

# NOTE: These names were previously defined in this module but have been
#       moved into `app.utils.transport`,
clean_headers = transport.clean_headers
MemoryCache = transport.MemoryCache
REFRESH_STATUS_CODES = transport.REFRESH_STATUS_CODES

# 备注：和code.py中的保持一致
REQUEST_SUCCEED = 10000  # 成功
REQUEST_ERROR = 10001  # 失败，有错误消息


class Error(Exception):
    """Base error for this module."""


class HttpRequestError(Error):
    u"""请求参数异常."""


class FlowExchangeError(Error):
    """Error trying to exchange an authorization grant for an access token."""


class AccessTokenRefreshError(Error):
    """Error trying to refresh an expired access token."""


class HttpAccessTokenRefreshError(AccessTokenRefreshError):
    """Error (with HTTP status) trying to refresh an expired access token."""

    def __init__(self, *args, **kwargs):
        super(HttpAccessTokenRefreshError, self).__init__(*args)
        self.status = kwargs.get('message')


class TokenRevokeError(Error):
    """Error trying to revoke a token."""


class UnknownClientSecretsFlowError(Error):
    """The client secrets file called for an unknown type of OAuth 2.0 flow."""


class AccessTokenCredentialsError(Error):
    """Having only the access_token means no refresh is possible."""


class VerifyJwtTokenError(Error):
    """Could not retrieve certificates for validation."""


class NonAsciiHeaderError(Error):
    """Header names and values must be ASCII strings."""


class ApplicationDefaultCredentialsError(Error):
    """Error retrieving the Application Default Credentials."""


class CryptoUnavailableError(Error, NotImplementedError):
    """Raised when a crypto library is required, but none is available."""


def _parse_expiry(expiry):
    if expiry and isinstance(expiry, datetime.datetime):
        return expiry.strftime(EXPIRY_FORMAT)
    else:
        return None


class Credentials(object):
    """Base class for all Credentials objects.

    Subclasses must define an authorize() method that applies the credentials
    to an HTTP transport.

    Subclasses must also specify a classmethod named 'from_json' that takes a
    JSON string as input and returns an instantiated Credentials object.
    """

    NON_SERIALIZED_MEMBERS = frozenset(['store'])

    def authorize(self, http):
        """Take an httplib2.Http instance (or equivalent) and authorizes it.

        Authorizes it for the set of credentials, usually by replacing
        http.request() with a method that adds in the appropriate headers and
        then delegates to the original Http.request() method.

        Args:
            http: httplib2.Http, an http object to be used to make the refresh
                  request.
        """
        raise NotImplementedError

    def refresh(self, http):
        """Forces a refresh of the access_token.

        Args:
            http: httplib2.Http, an http object to be used to make the refresh
                  request.
        """
        raise NotImplementedError

    def revoke(self, http):
        """Revokes a refresh_token and makes the credentials void.

        Args:
            http: httplib2.Http, an http object to be used to make the revoke
                  request.
        """
        raise NotImplementedError

    def apply(self, headers):
        """Add the authorization to the headers.

        Args:
            headers: dict, the headers to add the Authorization header to.
        """
        raise NotImplementedError

    def _to_json(self, strip, to_serialize=None):
        """Utility function that creates JSON repr. of a Credentials object.

        Args:
            strip: array, An array of names of members to exclude from the
                   JSON.
            to_serialize: dict, (Optional) The properties for this object
                          that will be serialized. This allows callers to
                          modify before serializing.

        Returns:
            string, a JSON representation of this instance, suitable to pass to
            from_json().
        """
        curr_type = self.__class__
        if to_serialize is None:
            to_serialize = copy.copy(self.__dict__)
        else:
            # Assumes it is a str->str dictionary, so we don't deep copy.
            to_serialize = copy.copy(to_serialize)
        for member in strip:
            if member in to_serialize:
                del to_serialize[member]
        to_serialize['token_expiry'] = _parse_expiry(
            to_serialize.get('token_expiry'))
        # Add in information we will need later to reconstitute this instance.
        to_serialize['_class'] = curr_type.__name__
        to_serialize['_module'] = curr_type.__module__
        for key, val in to_serialize.items():
            if isinstance(val, bytes):
                to_serialize[key] = val.decode('utf-8')
            if isinstance(val, set):
                to_serialize[key] = list(val)
        return json.dumps(to_serialize)

    def to_json(self):
        """Creating a JSON representation of an instance of Credentials.

        Returns:
            string, a JSON representation of this instance, suitable to pass to
            from_json().
        """
        return self._to_json(self.NON_SERIALIZED_MEMBERS)

    @classmethod
    def new_from_json(cls, json_data):
        """Utility class method to instantiate a Credentials subclass from JSON.

        Expects the JSON string to have been produced by to_json().

        Args:
            json_data: string or bytes, JSON from to_json().

        Returns:
            An instance of the subclass of Credentials that was serialized with
            to_json().
        """
        json_data_as_unicode = _helpers._from_bytes(json_data)
        data = json.loads(json_data_as_unicode)
        # Find and call the right classmethod from_json() to restore
        # the object.
        module_name = data['_module']
        module_obj = __import__(module_name,
                                fromlist=module_name.split('.')[:-1])
        kls = getattr(module_obj, data['_class'])
        return kls.from_json(json_data_as_unicode)

    @classmethod
    def from_json(cls, unused_data):
        """Instantiate a Credentials object from a JSON description of it.

        The JSON should have been produced by calling .to_json() on the object.

        Args:
            unused_data: dict, A deserialized JSON object.

        Returns:
            An instance of a Credentials subclass.
        """
        return Credentials()


class Storage(object):
    """Base class for all Storage objects.

    Store and retrieve a single credential. This class supports locking
    such that multiple processes and threads can operate on a single
    store.
    """

    def __init__(self, lock=None):
        """Create a Storage instance.

        Args:
            lock: An optional threading.Lock-like object. Must implement at
                  least acquire() and release(). Does not need to be
                  re-entrant.
        """
        self._lock = lock

    def acquire_lock(self):
        """Acquires any lock necessary to access this Storage.

        This lock is not reentrant.
        """
        if self._lock is not None:
            self._lock.acquire()

    def release_lock(self):
        """Release the Storage lock.

        Trying to release a lock that isn't held will result in a
        RuntimeError in the case of a threading.Lock or multiprocessing.Lock.
        """
        if self._lock is not None:
            self._lock.release()

    def locked_get(self):
        """Retrieve credential.

        The Storage lock must be held when this is called.

        Returns:
            oauth2client.client.Credentials
        """
        raise NotImplementedError

    def locked_put(self, credentials):
        """Write a credential.

        The Storage lock must be held when this is called.

        Args:
            credentials: Credentials, the credentials to store.
        """
        raise NotImplementedError

    def locked_delete(self):
        """Delete a credential.

        The Storage lock must be held when this is called.
        """
        raise NotImplementedError

    def get(self):
        """Retrieve credential.

        The Storage lock must *not* be held when this is called.

        Returns:
            oauth2client.client.Credentials
        """
        self.acquire_lock()
        try:
            return self.locked_get()
        finally:
            self.release_lock()

    def put(self, credentials):
        """Write a credential.

        The Storage lock must be held when this is called.

        Args:
            credentials: Credentials, the credentials to store.
        """
        self.acquire_lock()
        try:
            self.locked_put(credentials)
        finally:
            self.release_lock()

    def delete(self):
        """Delete credential.

        Frees any catalog associated with storing the credential.
        The Storage lock must *not* be held when this is called.

        Returns:
            None
        """
        self.acquire_lock()
        try:
            return self.locked_delete()
        finally:
            self.release_lock()


class OAuth2Credentials(Credentials):
    """Credentials object for OAuth 2.0.

    Credentials can be applied to an httplib2.Http object using the authorize()
    method, which then adds the OAuth 2.0 access token to each request.

    OAuth2Credentials objects may be safely pickled and unpickled.
    """

    @_helpers.positional(8)
    def __init__(self, access_token, client_id, client_secret, refresh_token,
                 token_expiry, token_uri, user_agent, revoke_uri=None,
                 id_token=None, token_response=None, scopes=None,
                 token_info_uri=None):
        """Create an instance of OAuth2Credentials.

        This constructor is not usually called by the user, instead
        OAuth2Credentials objects are instantiated by the OAuth2WebServerFlow.

        Args:
            access_token: string, access token.
            client_id: string, client identifier.
            client_secret: string, client secret.
            refresh_token: string, refresh token.
            token_expiry: datetime, when the access_token expires.
            token_uri: string, URI of token endpoint.
            user_agent: string, The HTTP User-Agent to provide for this
                        application.
            revoke_uri: string, URI for revoke endpoint. Defaults to None; a
                        token can't be revoked if this is None.
            id_token: object, The identity of the resource owner.
            token_response: dict, the decoded response to the token request.
                            None if a token hasn't been requested yet. Stored
                            because some providers (e.g. wordpress.com) include
                            extra fields that clients may want.
            scopes: list, authorized scopes for these credentials.
          token_info_uri: string, the URI for the token info endpoint. Defaults
                          to None; scopes can not be refreshed if this is None.

        Notes:
            store: callable, A callable that when passed a Credential
                   will store the credential back to where it came from.
                   This is needed to store the latest access_token if it
                   has expired and been refreshed.
        """
        self.access_token = access_token
        self.client_id = client_id
        self.client_secret = client_secret
        self.refresh_token = refresh_token
        self.store = None
        self.token_expiry = token_expiry
        self.token_uri = token_uri
        self.user_agent = user_agent
        self.revoke_uri = revoke_uri
        self.id_token = id_token
        self.token_response = token_response
        self.scopes = set(_helpers.string_to_scopes(scopes or []))
        self.token_info_uri = token_info_uri

        # True if the credentials have been revoked or expired and can't be
        # refreshed.
        self.invalid = False

    def authorize(self, http):
        """Authorize an httplib2.Http instance with these credentials.

        The modified http.request method will add authentication headers to
        each request and will refresh access_tokens when a 401 is received on a
        request. In addition the http.request method has a credentials
        property, http.request.credentials, which is the Credentials object
        that authorized it.

        Args:
            http: An instance of ``httplib2.Http`` or something that acts
                  like it.

        Returns:
            A modified instance of http that was passed in.

        Example::

            h = httplib2.Http()
            h = credentials.authorize(h)

        You can't create a new OAuth subclass of httplib2.Authentication
        because it never gets passed the absolute URI, which is needed for
        signing. So instead we have to overload 'request' with a closure
        that adds in the Authorization header and then calls the original
        version of 'request()'.
        """
        transport.wrap_http_for_auth(self, http)
        return http

    def refresh(self, http):
        """Forces a refresh of the access_token.

        Args:
            http: httplib2.Http, an http object to be used to make the refresh
                  request.
        """
        self._refresh(http)

    def revoke(self, http):
        """Revokes a refresh_token and makes the credentials void.

        Args:
            http: httplib2.Http, an http object to be used to make the revoke
                  request.
        """
        self._revoke(http)

    def apply(self, headers):
        """Add the authorization to the headers.

        Args:
            headers: dict, the headers to add the Authorization header to.
        """
        headers['Authorization'] = 'Bearer ' + self.access_token

    def has_scopes(self, scopes):
        """Verify that the credentials are authorized for the given scopes.

        Returns True if the credentials authorized scopes contain all of the
        scopes given.

        Args:
            scopes: list or string, the scopes to check.

        Notes:
            There are cases where the credentials are unaware of which scopes
            are authorized. Notably, credentials obtained and stored before
            this code was added will not have scopes, AccessTokenCredentials do
            not have scopes. In both cases, you can use refresh_scopes() to
            obtain the canonical set of scopes.
        """
        scopes = _helpers.string_to_scopes(scopes)
        return set(scopes).issubset(self.scopes)

    def retrieve_scopes(self, http):
        """Retrieves the canonical list of scopes for this access token.

        Gets the scopes from the OAuth2 provider.

        Args:
            http: httplib2.Http, an http object to be used to make the refresh
                  request.

        Returns:
            A set of strings containing the canonical list of scopes.
        """
        self._retrieve_scopes(http)
        return self.scopes

    @classmethod
    def from_json(cls, json_data):
        """Instantiate a Credentials object from a JSON description of it.

        The JSON should have been produced by calling .to_json() on the object.

        Args:
            json_data: string or bytes, JSON to deserialize.

        Returns:
            An instance of a Credentials subclass.
        """
        data = json.loads(_helpers._from_bytes(json_data))
        if (data.get('token_expiry') and
                not isinstance(data['token_expiry'], datetime.datetime)):
            try:
                data['token_expiry'] = datetime.datetime.strptime(
                    data['token_expiry'], EXPIRY_FORMAT)
            except ValueError:
                data['token_expiry'] = None
        retval = cls(
            data['access_token'],
            data['client_id'],
            data['client_secret'],
            data['refresh_token'],
            data['token_expiry'],
            data['token_uri'],
            data['user_agent'],
            revoke_uri=data.get('revoke_uri', None),
            id_token=data.get('id_token', None),
            token_response=data.get('token_response', None),
            scopes=data.get('scopes', None),
            token_info_uri=data.get('token_info_uri', None))
        retval.invalid = data['invalid']
        return retval

    @property
    def access_token_expired(self):
        """True if the credential is expired or invalid.

        If the token_expiry isn't set, we assume the token doesn't expire.
        """
        if self.invalid:
            return True

        if not self.token_expiry:
            return False

        now = _UTC8()
        if now >= self.token_expiry:
            current_app.logger.info('access_token is expired. Now: %s, token_expiry: %s',
                                    now, self.token_expiry)
            return True
        return False

    def get_access_token(self, http=None):
        """Return the access token and its expiration information.

        If the token does not exist, get one.
        If the token expired, refresh it.
        """
        if not self.access_token or self.access_token_expired:
            if not http:
                http = transport.get_http_object()
            self.refresh(http)
        return AccessTokenInfo(access_token=self.access_token,
                               expires_in=self._expires_in())

    def set_store(self, store):
        """Set the Storage for the credential.

        Args:
            store: Storage, an implementation of Storage object.
                   This is needed to store the latest access_token if it
                   has expired and been refreshed. This implementation uses
                   locking to check for updates before updating the
                   access_token.
        """
        self.store = store

    def _expires_in(self):
        """Return the number of seconds until this token expires.

        If token_expiry is in the past, this method will return 0, meaning the
        token has already expired.

        If token_expiry is None, this method will return None. Note that
        returning 0 in such a case would not be fair: the token may still be
        valid; we just don't know anything about it.
        """
        if self.token_expiry:
            now = _UTC8()
            if self.token_expiry > now:
                time_delta = self.token_expiry - now
                # TODO(orestica): return time_delta.total_seconds()
                # once dropping support for Python 2.6
                return time_delta.days * 86400 + time_delta.seconds
            else:
                return 0

    def _updateFromCredential(self, other):
        """Update this Credential from another instance."""
        self.__dict__.update(other.__getstate__())

    def __getstate__(self):
        """Trim the state down to something that can be pickled."""
        d = copy.copy(self.__dict__)
        del d['store']
        return d

    def __setstate__(self, state):
        """Reconstitute the state of the object from being pickled."""
        self.__dict__.update(state)
        self.store = None

    def _generate_refresh_request_body(self):
        """Generate the body that will be used in the refresh request."""
        body = urllib.parse.urlencode({
            'grant_type': 'refresh_token',
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'refresh_token': self.refresh_token,
        })
        return body

    def _generate_refresh_request_headers(self):
        """Generate the headers that will be used in the refresh request."""
        headers = {
            'content-type': 'application/x-www-form-urlencoded',
        }

        if self.user_agent is not None:
            headers['user-agent'] = self.user_agent

        return headers

    def _refresh(self, http):
        """Refreshes the access_token.

        This method first checks by reading the Storage object if available.
        If a refresh is still needed, it holds the Storage lock until the
        refresh is completed.

        Args:
            http: an object to be used to make HTTP requests.

        Raises:
            HttpAccessTokenRefreshError: When the refresh fails.
        """
        if not self.store:
            self._do_refresh_request(http)
        else:
            self.store.acquire_lock()
            try:
                new_cred = self.store.locked_get()

                if (new_cred and not new_cred.invalid and
                            new_cred.access_token != self.access_token and
                        not new_cred.access_token_expired):
                    current_app.logger.info('Updated access_token read from Storage')
                    self._updateFromCredential(new_cred)
                else:
                    self._do_refresh_request(http)
            finally:
                self.store.release_lock()

    def _do_refresh_request(self, http):
        """Refresh the access_token using the refresh_token.

        Args:
            http: an object to be used to make HTTP requests.

        Raises:
            HttpAccessTokenRefreshError: When the refresh fails.
        """
        body = self._generate_refresh_request_body()
        headers = self._generate_refresh_request_headers()

        current_app.logger.info('Refreshing access_token')
        resp, content = transport.request(
            http, self.token_uri, method='POST',
            body=body, headers=headers)
        content = _helpers._from_bytes(content)
        if resp.status == http_client.OK:
            d = json.loads(content)
            self.token_response = d
            self.access_token = d['access_token']
            self.refresh_token = d.get('refresh_token', self.refresh_token)
            if 'expires_in' in d:
                delta = datetime.timedelta(seconds=int(d['expires_in']))
                self.token_expiry = delta + _UTC8()
            else:
                self.token_expiry = None
            if 'id_token' in d:
                self.id_token = _extract_id_token(d['id_token'])
            else:
                self.id_token = None
            # On temporary refresh errors, the user does not actually have to
            # re-authorize, so we unflag here.
            self.invalid = False
            if self.store:
                self.store.locked_put(self)
        else:
            # An {'error':...} response body means the token is expired or
            # revoked, so we flag the credentials as such.
            current_app.logger.info('Failed to retrieve access token: %s', content)
            error_msg = 'Invalid response {0}.'.format(resp.status)
            try:
                d = json.loads(content)
                if 'error' in d:
                    error_msg = d['error']
                    if 'error_description' in d:
                        error_msg += ': ' + d['error_description']
                    self.invalid = True
                    if self.store is not None:
                        self.store.locked_put(self)
            except (TypeError, ValueError):
                pass
            raise HttpAccessTokenRefreshError(error_msg, status=resp.status)

    def _revoke(self, http):
        """Revokes this credential and deletes the stored copy (if it exists).

        Args:
            http: an object to be used to make HTTP requests.
        """
        self._do_revoke(http, self.refresh_token or self.access_token)

    def _do_revoke(self, http, token):
        """Revokes this credential and deletes the stored copy (if it exists).

        Args:
            http: an object to be used to make HTTP requests.
            token: A string used as the token to be revoked. Can be either an
                   access_token or refresh_token.

        Raises:
            TokenRevokeError: If the revoke request does not return with a
                              200 OK.
        """
        current_app.logger.info('Revoking token')
        query_params = {'token': token}
        token_revoke_uri = _helpers.update_query_params(
            self.revoke_uri, query_params)
        resp, content = transport.request(http, token_revoke_uri)
        if resp.status == http_client.METHOD_NOT_ALLOWED:
            body = urllib.parse.urlencode(query_params)
            resp, content = transport.request(http, token_revoke_uri,
                                              method='POST', body=body)
        if resp.status == http_client.OK:
            self.invalid = True
        else:
            error_msg = 'Invalid response {0}.'.format(resp.status)
            try:
                d = json.loads(_helpers._from_bytes(content))
                if 'error' in d:
                    error_msg = d['error']
            except (TypeError, ValueError):
                pass
            raise TokenRevokeError(error_msg)

        if self.store:
            self.store.delete()

    def _retrieve_scopes(self, http):
        """Retrieves the list of authorized scopes from the OAuth2 provider.

        Args:
            http: an object to be used to make HTTP requests.
        """
        self._do_retrieve_scopes(http, self.access_token)

    def _do_retrieve_scopes(self, http, token):
        """Retrieves the list of authorized scopes from the OAuth2 provider.

        Args:
            http: an object to be used to make HTTP requests.
            token: A string used as the token to identify the credentials to
                   the provider.

        Raises:
            Error: When refresh fails, indicating the the access token is
                   invalid.
        """
        current_app.logger.info('Refreshing scopes')
        query_params = {'access_token': token, 'fields': 'scope'}
        token_info_uri = _helpers.update_query_params(
            self.token_info_uri, query_params)
        resp, content = transport.request(http, token_info_uri)
        content = _helpers._from_bytes(content)
        if resp.status == http_client.OK:
            d = json.loads(content)
            self.scopes = set(_helpers.string_to_scopes(d.get('scope', '')))
        else:
            error_msg = 'Invalid response {0}.'.format(resp.status)
            try:
                d = json.loads(content)
                if 'error_description' in d:
                    error_msg = d['error_description']
            except (TypeError, ValueError):
                pass
            raise Error(error_msg)


class AccessTokenCredentials(OAuth2Credentials):
    """Credentials object for OAuth 2.0.

    Credentials can be applied to an httplib2.Http object using the
    authorize() method, which then signs each request from that object
    with the OAuth 2.0 access token. This set of credentials is for the
    use case where you have acquired an OAuth 2.0 access_token from
    another place such as a JavaScript client or another web
    application, and wish to use it from Python. Because only the
    access_token is present it can not be refreshed and will in time
    expire.

    AccessTokenCredentials objects may be safely pickled and unpickled.

    Usage::

        credentials = AccessTokenCredentials('<an access token>',
            'my-user-agent/1.0')
        http = httplib2.Http()
        http = credentials.authorize(http)

    Raises:
        AccessTokenCredentialsExpired: raised when the access_token expires or
                                       is revoked.
    """

    def __init__(self, access_token, user_agent, revoke_uri=None):
        """Create an instance of OAuth2Credentials

        This is one of the few types if Credentials that you should contrust,
        Credentials objects are usually instantiated by a Flow.

        Args:
            access_token: string, access token.
            user_agent: string, The HTTP User-Agent to provide for this
                        application.
            revoke_uri: string, URI for revoke endpoint. Defaults to None; a
                        token can't be revoked if this is None.
        """
        super(AccessTokenCredentials, self).__init__(
            access_token,
            None,
            None,
            None,
            None,
            None,
            user_agent,
            revoke_uri=revoke_uri)

    @classmethod
    def from_json(cls, json_data):
        data = json.loads(_helpers._from_bytes(json_data))
        retval = AccessTokenCredentials(
            data['access_token'],
            data['user_agent'])
        return retval

    def _refresh(self, http):
        """Refreshes the access token.

        Args:
            http: unused HTTP object.

        Raises:
            AccessTokenCredentialsError: always
        """
        raise AccessTokenCredentialsError(
            'The access_token is expired or invalid and can\'t be refreshed.')

    def _revoke(self, http):
        """Revokes the access_token and deletes the store if available.

        Args:
            http: an object to be used to make HTTP requests.
        """
        self._do_revoke(http, self.access_token)


class MyOAuthCredentials(Credentials):
    """
    sxw 2016-11-4

    Credentials can be applied to an httplib2.Http object using the authorize()
    method, which then adds the OAuth 2.0 access token to each request.
    实现目前系统的OAuth认证流程
    """

    @_helpers.positional(8)
    def __init__(self, access_token, client_name, client_id, client_secret, token_expiry, user_agent, token_uri=None,
                 revoke_uri=None,
                 id_token=None, token_response=None, scopes=None, token_info_uri=None):
        """Create an instance of OAuth2Credentials.

        This constructor is not usually called by the user, instead
        OAuth2Credentials objects are instantiated by the OAuth2WebServerFlow.
        Args:
            access_token: string, access token.
            token_expiry: datetime, when the access_token expires.
            token_uri: string, URI of token endpoint.
            user_agent: string, The HTTP User-Agent to provide for this
                        application.
            revoke_uri: string, URI for revoke endpoint. Defaults to None; a
                        token can't be revoked if this is None.
            id_token: object, The identity of the resource owner.
            token_response: dict, the decoded response to the token request.
                            None if a token hasn't been requested yet. Stored
                            because some providers (e.g. wordpress.com) include
                            extra fields that clients may want.
            scopes: list, authorized scopes for these credentials.
          token_info_uri: string, the URI for the token info endpoint. Defaults
                          to None; scopes can not be refreshed if this is None.

        Notes:
            store: callable, A callable that when passed a Credential
                   will store the credential back to where it came from.
                   This is needed to store the latest access_token if it
                   has expired and been refreshed.
        """
        self.access_token = access_token
        self.client_name = client_name
        self.client_id = client_id
        self.client_secret = client_secret
        self.store = None
        self.token_expiry = token_expiry
        self.token_uri = token_uri
        self.user_agent = user_agent
        self.revoke_uri = revoke_uri
        self.id_token = id_token
        self.token_response = token_response
        self.scopes = set(_helpers.string_to_scopes(scopes or []))
        self.token_info_uri = token_info_uri

        # True if the credentials have been revoked or expired and can't be
        # refreshed.
        self.invalid = False

    def revoke(self, http):
        """Revokes a refresh_token and makes the credentials void.

        Args:
            http: httplib2.Http, an http object to be used to make the revoke
                  request.
        """
        self._revoke(http)

    def _revoke(self, http):
        """Revokes this credential and deletes the stored copy (if it exists).

        Args:
            http: an object to be used to make HTTP requests.
        """
        self._do_revoke(http, self.access_token)

    def _do_revoke(self, http, token):
        """Revokes this credential and deletes the stored copy (if it exists).

        Args:
            http: an object to be used to make HTTP requests.
            token: A string used as the token to be revoked. Can be either an
                   access_token or refresh_token.

        Raises:
            TokenRevokeError: If the revoke request does not return with a
                              200 OK.
        """
        current_app.logger.info('Revoking access token')
        query_params = {'token': token}
        token_revoke_uri = _helpers.update_query_params(
            self.revoke_uri, query_params)
        resp, content = transport.request(http, token_revoke_uri)
        if resp.status == http_client.METHOD_NOT_ALLOWED:
            body = urllib.parse.urlencode(query_params)
            resp, content = transport.request(http, token_revoke_uri,
                                              method='POST', body=body)
        if resp.status == http_client.OK:
            self.invalid = True
        else:
            error_msg = 'Invalid response {0}.'.format(resp.status)
            try:
                d = json.loads(_helpers._from_bytes(content))
                if 'error' in d:
                    error_msg = d['error']
            except (TypeError, ValueError):
                pass
            raise TokenRevokeError(error_msg)

        if self.store:
            self.store.delete()

    def authorize(self, http, app_token=None):
        """Authorize an httplib2.Http instance with these credentials.

        The modified http.request method will add authentication headers to
        each request and will refresh access_tokens when a 401 is received on a
        request. In addition the http.request method has a credentials
        property, http.request.credentials, which is the Credentials object
        that authorized it.

        Args:
            http: An instance of ``httplib2.Http`` or something that acts
                  like it.

        Returns:
            A modified instance of http that was passed in.

        Example::

            h = httplib2.Http()
            h = credentials.authorize(h)

        You can't create a new OAuth subclass of httplib2.Authentication
        because it never gets passed the absolute URI, which is needed for
        signing. So instead we have to overload 'request' with a closure
        that adds in the Authorization header and then calls the original
        version of 'request()'.
        :param http: 连接句柄，方便封装参数
        :param app_token: app_token认证信息
        """

        if app_token:
            transport.wrap_http_for_auth(self, http, app_token)
        else:
            transport.wrap_http_for_auth(self, http)
        return http

    def _generate_refresh_request_body(self):
        """Generate the body that will be used in the refresh request."""
        body = urllib.parse.urlencode({
            'grant_type': 'refresh_token',
            'client_name': self.client_name,
            'client_id': self.client_id,
            'client_secret': self.client_secret,
        })
        return body

    def _generate_refresh_request_headers(self):
        """Generate the headers that will be used in the refresh request."""
        # headers = {
        #     'content-type': 'application/json',
        # }
        headers = {}

        if self.user_agent is not None:
            headers['user-agent'] = self.user_agent

        return headers

    def refresh(self, http):
        """Forces a refresh of the access_token.

        Args:
            http: httplib2.Http, an http object to be used to make the refresh
                  request.
        """
        self._refresh(http)

    def _refresh(self, http):
        """Refreshes the access_token.

        This method first checks by reading the Storage object if available.
        If a refresh is still needed, it holds the Storage lock until the
        refresh is completed.

        Args:
            http: an object to be used to make HTTP requests.

        Raises:
            HttpAccessTokenRefreshError: When the refresh fails.
        """
        if not self.store:
            self._do_refresh_request(http)
        else:
            self.store.acquire_lock()
            try:
                new_cred = self.store.locked_get()

                if (new_cred and not new_cred.invalid and
                            new_cred.access_token != self.access_token and
                        not new_cred.access_token_expired):
                    current_app.logger.info('Updated access_token read from Storage')
                    self._updateFromCredential(new_cred)
                else:
                    self._do_refresh_request(http)
            finally:
                self.store.release_lock()

    def _do_refresh_request(self, http):
        """Refresh the access_token.

        Args:
            http: an object to be used to make HTTP requests.

        Raises:
            HttpAccessTokenRefreshError: When the refresh fails.
        """
        uri = update_query_params(self.token_uri, {
            'grant_type': 'refresh_token',
            'client_name': self.client_name,
            'client_id': self.client_id,
            'client_secret': self.client_secret,
        })
        headers = self._generate_refresh_request_headers()

        current_app.logger.info('Refreshing access_token')
        resp, content = transport.request(
            http, uri, method='GET', headers=headers)
        content = _helpers._from_bytes(content)
        if resp.status == http_client.OK:
            d = json.loads(content)
            if d['status'] == REQUEST_SUCCEED or d['status'] == str(REQUEST_SUCCEED):
                self.token_response = d
                self.access_token = d['access_token']
                current_app.config['access_token'] = self.access_token
                if 'expires_in' in d:
                    delta = datetime.timedelta(seconds=int(d['expires_in']))
                    self.token_expiry = delta + _UTC8()
                else:
                    self.token_expiry = None
                if 'id_token' in d:
                    self.id_token = _extract_id_token(d['id_token'])
                else:
                    self.id_token = None
                # On temporary refresh errors, the user does not actually have to
                # re-authorize, so we unflag here.
                self.invalid = False
                if self.store:
                    self.store.locked_put(self)
            # 若认证错误，则打印日志错误信息，显示日志错误
            elif d['status'] == REQUEST_ERROR or d['status'] == str(REQUEST_ERROR):
                self.invalid = True
                if self.store is not None:
                    self.store.locked_put(self)
                raise AccessTokenCredentialsError(d["message"] if "message" in d else "")
            # 不标准的OAuth实现，解析自定义返回参数错误
            else:
                # An {'error':...} response body means the token is expired or
                # revoked, so we flag the credentials as such.
                current_app.logger.info(u"获取Access token失败：%s", content)
                error_msg = u"失败的返回 {0}。".format(d['status'])
                try:
                    if 'message' in d:
                        error_msg = d['message']
                        self.invalid = True
                        if self.store is not None:
                            self.store.locked_put(self)
                except (TypeError, ValueError):
                    pass
                raise HttpAccessTokenRefreshError(error_msg, status=d['status'])

        else:
            # An {'error':...} response body means the token is expired or
            # revoked, so we flag the credentials as such.
            current_app.logger.info('Failed to retrieve access token: %s', content)
            error_msg = 'Invalid response {0}.'.format(resp.status)
            try:
                d = json.loads(content)
                if 'error' in d:
                    error_msg = d['error']
                    if 'error_description' in d:
                        error_msg += ': ' + d['error_description']
                    self.invalid = True
                    if self.store is not None:
                        self.store.locked_put(self)
            except (TypeError, ValueError):
                pass
            raise HttpAccessTokenRefreshError(error_msg, status=resp.status)

    def apply(self, headers):
        """Add the authorization to the headers.

        Args:
            headers: dict, the headers to add the Authorization header to.
        """
        headers['content-type'] = 'application/json'
        headers['access_token'] = self.access_token
        headers['client_name'] = self.client_name
        # headers['Authorization'] = 'Bearer ' + self.access_token

    def has_scopes(self, scopes):
        """Verify that the credentials are authorized for the given scopes.

        Returns True if the credentials authorized scopes contain all of the
        scopes given.

        Args:
            scopes: list or string, the scopes to check.

        Notes:
            There are cases where the credentials are unaware of which scopes
            are authorized. Notably, credentials obtained and stored before
            this code was added will not have scopes, AccessTokenCredentials do
            not have scopes. In both cases, you can use refresh_scopes() to
            obtain the canonical set of scopes.
        """
        scopes = _helpers.string_to_scopes(scopes)
        return set(scopes).issubset(self.scopes)

    def retrieve_scopes(self, http):
        """Retrieves the canonical list of scopes for this access token.

        Gets the scopes from the OAuth2 provider.

        Args:
            http: httplib2.Http, an http object to be used to make the refresh
                  request.

        Returns:
            A set of strings containing the canonical list of scopes.
        """
        self._retrieve_scopes(http)
        return self.scopes

    def _retrieve_scopes(self, http):
        """Retrieves the list of authorized scopes from the OAuth2 provider.

        Args:
            http: an object to be used to make HTTP requests.
        """
        self._do_retrieve_scopes(http, self.access_token)

    def _do_retrieve_scopes(self, http, token):
        """Retrieves the list of authorized scopes from the OAuth2 provider.

        Args:
            http: an object to be used to make HTTP requests.
            token: A string used as the token to identify the credentials to
                   the provider.

        Raises:
            Error: When refresh fails, indicating the the access token is
                   invalid.
        """
        current_app.logger.info('Refreshing scopes')
        query_params = {'access_token': token, 'fields': 'scope'}
        token_info_uri = _helpers.update_query_params(
            self.token_info_uri, query_params)
        resp, content = transport.request(http, token_info_uri)
        content = _helpers._from_bytes(content)
        if resp.status == http_client.OK:
            d = json.loads(content)
            self.scopes = set(_helpers.string_to_scopes(d.get('scope', '')))
        else:
            error_msg = 'Invalid response {0}.'.format(resp.status)
            try:
                d = json.loads(content)
                if 'error_description' in d:
                    error_msg = d['error_description']
            except (TypeError, ValueError):
                pass
            raise Error(error_msg)

    @property
    def access_token_expired(self):
        """True if the credential is expired or invalid.

        If the token_expiry isn't set, we assume the token doesn't expire.
        """
        if self.invalid:
            return True

        if not self.token_expiry:
            return False

        now = _UTC8()
        if now >= self.token_expiry:
            current_app.logger.info('access_token is expired. Now: %s, token_expiry: %s',
                                    now, self.token_expiry)
            return True
        return False

    def get_access_token(self, http=None):
        """Return the access token and its expiration information.

        If the token does not exist, get one.
        If the token expired, refresh it.
        """
        if not self.access_token or self.access_token_expired:
            if not http:
                http = transport.get_http_object()
            self.refresh(http)
        return AccessTokenInfo(access_token=self.access_token,
                               expires_in=self._expires_in())

    def _expires_in(self):
        """Return the number of seconds until this token expires.

        If token_expiry is in the past, this method will return 0, meaning the
        token has already expired.

        If token_expiry is None, this method will return None. Note that
        returning 0 in such a case would not be fair: the token may still be
        valid; we just don't know anything about it.
        """
        if self.token_expiry:
            now = _UTC8()
            if self.token_expiry > now:
                time_delta = self.token_expiry - now
                # TODO(orestica): return time_delta.total_seconds()
                # once dropping support for Python 2.6
                return time_delta.days * 86400 + time_delta.seconds
            else:
                return 0

    def set_store(self, store):
        """Set the Storage for the credential.

        Args:
            store: Storage, an implementation of Storage object.
                   This is needed to store the latest access_token if it
                   has expired and been refreshed. This implementation uses
                   locking to check for updates before updating the
                   access_token.
        """
        self.store = store

    def _updateFromCredential(self, other):
        """Update this Credential from another instance."""
        self.__dict__.update(other.__getstate__())

    def __getstate__(self):
        """Trim the state down to something that can be pickled."""
        d = copy.copy(self.__dict__)
        del d['store']
        return d

    def __setstate__(self, state):
        """Reconstitute the state of the object from being pickled."""
        self.__dict__.update(state)
        self.store = None


def _extract_id_token(id_token):
    """Extract the JSON payload from a JWT.

    Does the extraction w/o checking the signature.

    Args:
        id_token: string or bytestring, OAuth 2.0 id_token.

    Returns:
        object, The deserialized JSON payload.
    """
    if type(id_token) == bytes:
        segments = id_token.split(b'.')
    else:
        segments = id_token.split(u'.')

    if len(segments) != 3:
        raise VerifyJwtTokenError(
            'Wrong number of segments in token: {0}'.format(id_token))

    return json.loads(
        _helpers._from_bytes(_helpers._urlsafe_b64decode(segments[1])))


def wrapper_request_except(func):
    """
        songxiaowei 2017-3-3

        装饰器方法捕获并处理异常
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if current_app.config['DEBUG']:
            log_list = []
            if len(args):
                log_list.append(u"url={}".format(*args))
            log_list.extend([u"{}={}".format(key, value) for key, value in kwargs.items()])
            current_app.logger.debug(u"开始请求，请求参数为：" + u"，".join(log_list))
        try:
            resp, content = func(*args, **kwargs)
        except (TypeError, ValueError, HttpAccessTokenRefreshError, AccessTokenCredentialsError, Exception) as e:
            import socket
            if isinstance(e, (TypeError, ValueError, AccessTokenCredentialsError)):
                current_app.logger.error(u"请检查认证参数配置！ 异常信息为：{}".format(e))
                raise e
            elif isinstance(e, HttpAccessTokenRefreshError):
                current_app.logger.error(u"请求access token异常，请联系相关负责人！异常信息为：{}".format(e))
            elif isinstance(e, socket.error):
                current_app.logger.error(u"连接异常，请检查相关网络情况！异常信息为：{}".format(e))
                current_app.logger.error(
                    u"如果异常信息为10061，则认证服务器地址可能有误，请修改app.configs.default.py和app.configs.api_uri.user中相关认证信息！")
            else:
                # 日志记录异常信息
                current_app.logger.error(u"请求异常，请检查，异常为：{}".format(e))
                raise HttpRequestError(e)
            return False, None, None
        else:
            if resp.status == http_client.OK:
                content = _helpers._to_bytes(content)
                d = json.loads(content)
                # 查看请求是否成功，如果成功，则返回data内容
                if d['status'] == REQUEST_SUCCEED or d['status'] == str(REQUEST_SUCCEED):
                    return True, d['data'] if 'data' in d else '', d
                elif d['status'] == 404 or d['status'] == '404':
                    current_app.logger.error(u"请求连接错误，请检查uri参数！")
                error_msg = d['message'] if 'message' in d else d
            else:
                error_msg = content
            return False, error_msg, resp.status

    return wrapper


@wrapper_request_except
def new_request(uri, method='GET', body=None, headers=None, redirections=httplib2.DEFAULT_MAX_REDIRECTS,
                connection_type=None):
    """
    sxw 2016-11-7

    封装公共请求异常处理
    """
    return g.http.request(uri, method=method, body=body, headers=headers, redirections=redirections,
                          connection_type=connection_type)


@wrapper_request_except
def task_request(uri, method='GET', body=None, headers=None, redirections=httplib2.DEFAULT_MAX_REDIRECTS,
                 connection_type=None, app_token=None):
    """
    sxw 2017-3-3

    异步任务中封装公共请求异常处理
    """
    h = httplib2.Http()
    http = current_app.oauth.authorize(h, app_token)
    return http.request(uri, method=method, body=body, headers=headers, redirections=redirections,
                        connection_type=connection_type)
