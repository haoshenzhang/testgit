# -*- coding: utf-8 -*-
"""
    app.utils.tokens
    sxw 2016-7-8
    token相关函数
"""
from flask import current_app
from app.extensions import redis_store
from itsdangerous import (TimedJSONWebSignatureSerializer, SignatureExpired,
                          BadSignature)


def make_token(user, operation='normal', token_expire=None, redis_expire=None, redis_update_enable=True):
    """Generates a JSON Web Signature (JWS).

    See `RFC 7515 <https://tools.ietf.org/html/rfc7515>` if you want to know
    more about JWS.

    :param user: The user object for whom the token should be generated.
    :param operation: The function of the token. For example, you might want
                      to generate two different tokens. One for a
                      passwd reset link, which you hypothetically want
                      to name 'reset' and the second one, for the generation
                      of a token for a E-Mail confirmation link, which you
                      name 'email'. 此外再增加交互token生成，默认为操作会话token
    :param token_expire: The time, in seconds, after which the token should be
                   invalid. Defaults to 1800（30分钟)，请在配置文件中设置，TOKEN_EXPIRE.
    :param redis_expire: The time, in seconds, after which the redis value should be
                   invalid. Defaults to token_expire，must low token_expire.
    :param redis_update_enable: Whether this update redis stored in time.
    """
    token = None
    redis_key = str(user.id) + operation

    # 为何不加在默认值部，因为current_app没法在编译阶段调用
    token_expire = token_expire if token_expire else current_app.config['TOKEN_EXPIRE']
    # 续命7秒，针对产生token需要时间和redis-5的时间
    token_expire += 7
    # 假如redis可用，则优先从redis中获取，否则直接生成
    if current_app.config['REDIS_ENABLED']:
        token = redis_store.get(redis_key)
        # 如果redis_expire不为空且小于token_expire-5，则采用redis_expire值
        # 否则采用token-5
        redis_expire = redis_expire if redis_expire and redis_expire < token_expire - 5 else token_expire - 5

    if not token:
        s = TimedJSONWebSignatureSerializer(
            current_app.config['SECRET_KEY'], token_expire
        )
        # secure code#passwd#id
        data = {"id": user.id, "op": operation, "passwd": user.passwd}
        token = s.dumps(data)

        # 若redis可用，则存储将token存储到redis中
        if current_app.config['REDIS_ENABLED']:
            redis_store.set(redis_key, token, redis_expire)
    else:
        # 存在token，更新redis中当前键值缓存时间为redis_expire
        if redis_update_enable and current_app.config['REDIS_ENABLED'] and redis_expire:
            redis_store.expire(redis_key, redis_expire)
    return token


def get_token_status(token, operation='normal', return_data=False):
    """Returns the expired status, invalid status, the user and optionally
    the content of the JSON Web Signature token.

    :param token: A valid JSON Web Signature token.
    :param operation: The function of the token.
    :param return_data: If set to ``True``, it will also return the content
                        of the token.
    """
    s = TimedJSONWebSignatureSerializer(current_app.config['SECRET_KEY'])
    user, data = None, None
    expired, invalid = False, False

    try:
        data = s.loads(token)
    except SignatureExpired:
        expired = True
    except (BadSignature, TypeError, ValueError):
        invalid = True

    if data is not None:
        # check if the operation matches the one from the token
        if operation == data.get("op", None):
            from app.user.member.models import CmdbUser
            user = CmdbUser.query.filter_by(id=data.get('id')).first()
            # 如果redis可用，则再进行redis中token校验
            token = True
            if current_app.config['REDIS_ENABLED']:
                redis_key = str(user.id) + operation
                token = redis_store.get(redis_key)
            if token and user and user.passwd != data.get("passwd", None):
                invalid = True
                user = None
        else:
            invalid = True

    if return_data:
        return expired, invalid, user, data

    return expired, invalid, user
