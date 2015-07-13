# coding:utf-8

from peewee import *
from model import BaseModel
from random import Random
from hashlib import md5


def random_str(random_length=16):
    str = ''
    chars = 'AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz0123456789'
    length = len(chars) - 1
    random = Random()
    for i in range(random_length):
        str+=chars[random.randint(0, length)]
    return str


class USER_LEVEL:
    BAN = 0
    NORMAL = 10
    ADMIN = 100


class User(BaseModel):
    username = TextField()
    password = TextField()
    level = IntegerField()
    salt = TextField()

    @classmethod
    def new(cls, username, password):
        salt = random_str()
        password_md5 = md5(password.encode('utf-8')).hexdigest()
        password_final = md5((password_md5 + salt).encode('utf-8')).hexdigest()
        level = USER_LEVEL.ADMIN if cls.count() == 0 else USER_LEVEL.NORMAL  # 首个用户赋予admin权限
        return cls.create(username=username, password=password_final, salt=salt, level=level)

    def is_admin(self):
        return self.level == USER_LEVEL.ADMIN

    @classmethod
    def auth(cls, username, password):
        try:
            u = cls.get(cls.username==username)
        except DoesNotExist:
            return False
        password_md5 = md5(password.encode('utf-8')).hexdigest()
        password_final = md5((password_md5 + u.salt).encode('utf-8')).hexdigest()
        if u.password == password_final:
            return u

    @classmethod
    def exist(cls, username):
        return cls.select().where(cls.username==username).exists()

    @classmethod
    def get_by_key(cls, key):
        try:
            return cls.get(cls.salt == key)
        except DoesNotExist:
            return None
