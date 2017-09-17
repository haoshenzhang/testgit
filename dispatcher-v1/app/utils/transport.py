# -*- coding: utf-8 -*-
"""
    sxw 2016-11-4

    api请求
    ref: https://github.com/google/oauth2client/blob/master/oauth2client/transport.py
"""
import json

import httplib2
import six
from flask import g, current_app
from six.moves import http_client

from app.utils import helpers as _helpers

# Properties present in file-like streams / buffers.
_STREAM_PROPERTIES = ('read', 'seek', 'tell')

# Google Data client libraries may need to set this to [401, 403].
REFRESH_STATUS_CODES = (http_client.UNAUTHORIZED,)


class MemoryCache(object):
    """httplib2 Cache implementation which only caches locally."""

    def __init__(self):
        self.cache = {}

    def get(self, key):
        return self.cache.get(key)

    def set(self, key, value):
        self.cache[key] = value

    def delete(self, key):
        self.cache.pop(key, None)


def get_cached_http():
    """Return an HTTP object which caches results returned.

    This is intended to be used in methods like
    oauth2client.client.verify_id_token(), which calls to the same URI
    to retrieve certs.

    Returns:
        httplib2.Http, an HTTP object with a MemoryCache
    """
    return _CACHED_HTTP


def get_http_object(*args, **kwargs):
    """Return a new HTTP object.

    Args:
        :param args: tuple, The positional arguments to be passed when contructing a new HTTP object.
        :param kwargs: dict, The keyword arguments to be passed when contructing a new HTTP object.

    Returns:
        httplib2.Http, an HTTP object.
    """
    return httplib2.Http(*args, **kwargs)


def _initialize_headers(headers):
    """Creates a copy of the headers.

    Args:
        headers: dict, request headers to copy.

    Returns:
        dict, the copied headers or a new dictionary if the headers
        were None.
    """
    return {} if headers is None else dict(headers)


def _apply_user_agent(headers, user_agent):
    """Adds a user-agent to the headers.

    Args:
        headers: dict, request headers to add / modify user
                 agent within.
        user_agent: str, the user agent to add.

    Returns:
        dict, the original headers passed in, but modified if the
        user agent is not None.
    """
    if user_agent is not None:
        if 'user-agent' in headers:
            headers['user-agent'] = (user_agent + ' ' + headers['user-agent'])
        else:
            headers['user-agent'] = user_agent

    return headers


def clean_headers(headers):
    """Forces header keys and values to be strings, i.e not unicode.

    The httplib module just concats the header keys and values in a way that
    may make the message header a unicode string, which, if it then tries to
    contatenate to a binary request body may result in a unicode decode error.

    Args:
        headers: dict, A dictionary of headers.

    Returns:
        The same dictionary but with all the keys converted to strings.
    """
    clean = {}
    try:
        for k, v in six.iteritems(headers):
            if not isinstance(k, six.binary_type):
                k = str(k)
            if not isinstance(v, six.binary_type):
                v = str(v)
            clean[_helpers._to_bytes(k)] = _helpers._to_bytes(v)
    except UnicodeEncodeError:
        from app.utils.client import NonAsciiHeaderError
        raise NonAsciiHeaderError(k, ': ', v)
    return clean


def wrap_http_for_auth(credentials, http, app_token=None):
    u"""Prepares an HTTP object's request method for auth.

    Wraps HTTP requests with logic to catch auth failures (typically
    identified via a 401 status code). In the event of failure, tries
    to refresh the token used and then retry the original request.

    Args:
        credentials: Credentials, the credentials used to identify the authenticated user.
        http: httplib2.Http, an http object to be used to make auth requests.
        app_token: 传递前端传过来的app_token.
    """
    orig_request_method = http.request

    # The closure that will replace 'httplib2.Http.request'.
    def new_request(uri, method='GET', body=None, headers=None,
                    redirections=httplib2.DEFAULT_MAX_REDIRECTS,
                    connection_type=None):
        # 若应用g.access_token存在且credentials.access_token不存在，则给credentials赋值
        if "access_token" in current_app.config and current_app.config["access_token"] and not credentials.access_token:
            credentials.access_token = current_app.config["access_token"]

        if not credentials.access_token:
            current_app.logger.info('Attempting refresh to obtain '
                                    'initial access_token')
            credentials._refresh(orig_request_method)

        # 将app_token赋值到headers中
        if app_token:
            headers = headers or {}
            headers['app_token'] = app_token
        # Clone and modify the request headers to add the appropriate
        # Authorization header.
        headers = _initialize_headers(headers)
        credentials.apply(headers)
        _apply_user_agent(headers, credentials.user_agent)

        # 如果传递的body是字典类型，进行序列化输出
        if isinstance(body, dict):
            body = json.dumps(body)

        # 如果method: 'GET'，则移除Content-Type: application/json
        if method.upper() == 'GET' and headers.get('content-type', None) == 'application/json':
            headers.pop('content-type')

        body_stream_position = None
        # Check if the body is a file-like stream.
        if all(getattr(body, stream_prop, None) for stream_prop in
               _STREAM_PROPERTIES):
            body_stream_position = body.tell()

        resp, content = request(orig_request_method, uri, method, body,
                                clean_headers(headers),
                                redirections, connection_type)

        # A stored token may expire between the time it is retrieved and
        # the time the request is made, so we may need to try twice.
        max_refresh_attempts = 2
        for refresh_attempt in range(max_refresh_attempts):
            if resp.status not in REFRESH_STATUS_CODES:
                break
            current_app.logger.info('Refreshing due to a %s (attempt %s/%s)',
                                    resp.status, refresh_attempt + 1,
                                    max_refresh_attempts)
            credentials._refresh(orig_request_method)
            credentials.apply(headers)
            if body_stream_position is not None:
                body.seek(body_stream_position)

            resp, content = request(orig_request_method, uri, method, body,
                                    clean_headers(headers),
                                    redirections, connection_type)

        return resp, content

    # Replace the request method with our own closure.
    http.request = new_request

    # Set credentials as a property of the request method.
    http.request.credentials = credentials


def wrap_http_for_jwt_access(credentials, http):
    """Prepares an HTTP object's request method for JWT access.

    Wraps HTTP requests with logic to catch auth failures (typically
    identified via a 401 status code). In the event of failure, tries
    to refresh the token used and then retry the original request.

    Args:
        credentials: _JWTAccessCredentials, the credentials used to identify
                     a service account that uses JWT access tokens.
        http: httplib2.Http, an http object to be used to make
              auth requests.
    """
    orig_request_method = http.request
    wrap_http_for_auth(credentials, http)
    # The new value of ``http.request`` set by ``wrap_http_for_auth``.
    authenticated_request_method = http.request

    # The closure that will replace 'httplib2.Http.request'.
    def new_request(uri, method='GET', body=None, headers=None,
                    redirections=httplib2.DEFAULT_MAX_REDIRECTS,
                    connection_type=None):
        if 'aud' in credentials._kwargs:
            # Preemptively refresh token, this is not done for OAuth2
            if (credentials.access_token is None or
                    credentials.access_token_expired):
                credentials.refresh(None)
            return request(authenticated_request_method, uri,
                           method, body, headers, redirections,
                           connection_type)
        else:
            # If we don't have an 'aud' (audience) claim,
            # create a 1-time token with the uri root as the audience
            headers = _initialize_headers(headers)
            _apply_user_agent(headers, credentials.user_agent)
            uri_root = uri.split('?', 1)[0]
            token, unused_expiry = credentials._create_token({'aud': uri_root})

            headers['Authorization'] = 'Bearer ' + token
            return request(orig_request_method, uri, method, body,
                           clean_headers(headers),
                           redirections, connection_type)

    # Replace the request method with our own closure.
    http.request = new_request

    # Set credentials as a property of the request method.
    http.request.credentials = credentials


def request(http, uri, method='GET', body=None, headers=None,
            redirections=httplib2.DEFAULT_MAX_REDIRECTS,
            connection_type=None):
    """Make an HTTP request with an HTTP object and arguments.

    Args:
        http: httplib2.Http, an http object to be used to make requests.
        uri: string, The URI to be requested.
        method: string, The HTTP method to use for the request. Defaults to 'GET'.

        body: string, The payload / body in HTTP request. By default there is no payload.
        headers: dict, Key-value pairs of request headers. By default there are no headers.
        redirections: int, The number of allowed 203 redirects for the request. Defaults to 5.
        connection_type: httplib.HTTPConnection, a subclass to be used for establishing connection.
        If not set, the type will be determined from the ``uri``.

    Returns:
        tuple, a pair of a httplib2.Response with the status code and other
        headers and the bytes of the content returned.
    """
    # NOTE: Allowing http or http.request is temporary (See Issue 601).
    http_callable = getattr(http, 'request', http)
    return http_callable(uri, method=method, body=body, headers=headers,
                         redirections=redirections,
                         connection_type=connection_type)


_CACHED_HTTP = httplib2.Http(MemoryCache())
