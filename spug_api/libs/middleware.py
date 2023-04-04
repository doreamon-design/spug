# Copyright: (c) OpenSpug Organization. https://github.com/openspug/spug
# Copyright: (c) <spug.dev@gmail.com>
# Released under the AGPL-3.0 License.
from django.utils.deprecation import MiddlewareMixin
from django.conf import settings
from .utils import json_response, get_request_real_ip
from apps.account.models import User
from apps.setting.utils import AppSetting
import traceback
import time
import uuid

import jwt

class HandleExceptionMiddleware(MiddlewareMixin):
    """
    处理试图函数异常
    """

    def process_exception(self, request, exception):
        traceback.print_exc()
        return json_response(error='Exception: %s' % exception)


class AuthenticationMiddleware(MiddlewareMixin):
    """
    登录验证
    """

    def process_request(self, request):
        if request.path in settings.AUTHENTICATION_EXCLUDES:
            return None
        if any(x.match(request.path) for x in settings.AUTHENTICATION_EXCLUDES if hasattr(x, 'match')):
            return None
        access_token = request.headers.get('x-token') or request.GET.get('x-token')
        if access_token and len(access_token) == 32:
            x_real_ip = get_request_real_ip(request.headers)
            user = User.objects.filter(access_token=access_token).first()
            if user and user.token_expired >= time.time() and user.is_active:
                if x_real_ip == user.last_ip or AppSetting.get_default('bind_ip') is False:
                    request.user = user
                    user.token_expired = time.time() + settings.TOKEN_TTL
                    user.save()
                    return None
        
        x_connect_token = request.headers.get('x-connect-token')
        if x_connect_token:
            # jwt parse token
            try:
                payload = jwt.decode(x_connect_token, settings.SECRET_KEY, algorithms=['HS256'], options={
                    'verify_iat': False,
                })
                print('jwt payload: ', payload)
                username = payload['user_email']
                nickname = payload['user_nickname']
                user_avatar = payload['user_avatar']

                user = User.objects.filter(username=username).first()
                if not user:
                    print('username not found: %s' % username)
                    form = {
                        'username': username,
                        'nickname': nickname or username,
                        'password_hash': User.make_password(uuid.uuid4().hex),
                        'access_token': uuid.uuid4().hex,
                    }
                    User.objects.create(**form)
                    user = User.objects.filter(username=username).first()

                is_user_changed = False    
                if nickname and nickname != user.nickname:
                    user.nickname = nickname
                    is_user_changed = True

                print('[x-connect-token][sign] nickname: %s, is_admin(%s == %s): %s' % (user.nickname, username, settings.ADMIN_USERNAME, settings.ADMIN_USERNAME == username))
                
                # if role and role.upper() == 'SUPER_ADMIN':
                #     user.is_supper = True
                #     user.is_active = True
                #     is_user_changed = True
                # elif role and (role.upper() == 'FORBIDDEN' or role.upper() == 'BAN'):
                #     user.is_supper = False
                #     user.is_active = False
                #     is_user_changed = True

                if settings.ADMIN_USERNAME and settings.ADMIN_USERNAME == username:
                    user.is_supper = True
                    user.is_active = True
                    is_user_changed = True

                token_is_valid = user.access_token and len(user.access_token) == 32 and user.token_expired and user.token_expired >= time.time()
                print('[x-connect-token][sign] is_token_valid(%s): %s' % (user.access_token, token_is_valid))
                if not token_is_valid:
                    user.access_token = uuid.uuid4().hex
                    user.token_expired = time.time() + 8 * 60 * 60
                    is_user_changed = True

                if is_user_changed == True:
                    user.save()

                print('[x-connect-token] jwt user(%s), is_super: %s, is_active: %s' % (user.nickname, user.is_supper, user.is_active))
                request.user = user
                return None
            except Exception as e:
                print('[x-connect-token] token (%s) is invalid: %s' % (x_connect_token, e))

                response = json_response(error='invalid x-connect-token(%s): %s' % (x_connect_token, e))
                response.status_code = 401
                return response

        response = json_response(error="验证失败，请重新登录")
        response.status_code = 401
        return response
