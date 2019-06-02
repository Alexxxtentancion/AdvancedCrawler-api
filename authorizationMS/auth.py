import datetime

import jwt

from asyncorm.main import User, Token
from authorizationMS.utils import sharable_secret, encode_password


class AuthMs:

    @staticmethod
    async def create_token(email, user, expire_date):

        token = jwt.encode({
            'email': email,
        }, sharable_secret)
        tok = token.decode('utf-8')
        try:
            token = await Token.objects.get(user_id=user.id)
            token_obj = Token(id=token.id, token=tok, user_id=user.id, expire_date=expire_date)
            await token_obj.save()
        except Exception:
            await Token.objects.create(token=tok, user_id=user.id, expire_date=expire_date)
        return tok

    async def validate(self, token):
        try:
            try:
                token_data = await Token.objects.get(token=token)
                if datetime.datetime.strptime(token_data.expire_date, '%Y-%m-%d %H:%M:%S') < datetime.datetime.now():
                    return {"status": "error", "reason": "expired token"}
            except:
                return {"status": "error", "reason": "wrong token"}
            user = await User.objects.get(id=token_data.user_id)
            data = {"id": user.id, "email": user.email, "password": user.password,
                    "name": user.name, "created_date": user.created_date, "last_login_date": user.last_login_date}
            return {"status": "success", "data": data}
        except Exception as e:
            return {"status": "error", "reason": str(e)}

    async def signup(self, data):
        if len(await User.objects.filter(email=data.get('email'))) == 0:
            try:
                expire_date = (datetime.datetime.now() + datetime.timedelta(hours=1)).strftime("%Y-%m-%d %H:%M:%S")
                await User.objects.create(email=data.get('email'),
                                          password=encode_password(data.get('password')),
                                          name=data.get('name'),
                                          created_date=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                          last_login_date=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                user = await User.objects.get(email=data.get('email'))
                token = await self.create_token(data.get('email'), user,
                                                expire_date)
                return {"status": "success", "data": {"token": token, "expire_date": expire_date}}
            except Exception:
                return {"status": "error", "reason": "wrong data"}
        else:
            return {"status": "error", "reason": "user with this username exists"}

    async def login(self, data):
        try:
            expire_date = (datetime.datetime.now() + datetime.timedelta(hours=1)).strftime("%Y-%m-%d %H:%M:%S")
            user = await User.objects.get(email=data.get('email'), password=encode_password(data.get('password')))
            if user:
                token = await self.create_token(data.get('email'), user, expire_date)
                await User(id=user.id, email=user.email, password=user.password, name=user.name,
                           created_date=user.created_date,
                           last_login_date=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")).save()
                return {"status": "ok", "data": {"token": token, "expire": expire_date}}
        except Exception as e:
            return {"status": "error", "reason": "no user with this email and password"}
