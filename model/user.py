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


class User(BaseModel):
    username = TextField()
    password = TextField()
    salt = TextField()

    @classmethod
    def new(cls, username, password):
        salt = random_str()
        password_md5 = md5(password).hexdigest()
        password_final = md5(password_md5 + salt).hexdigest()
        return cls.create(username=username, password=password_final, salt=salt)

    @classmethod
    def auth(cls, username, password):
        try:
            u = cls.get(cls.username==username)
        except DoesNotExist:
            return False
        password_md5 = md5(password).hexdigest()
        password_final = md5(password_md5 + u.salt).hexdigest()
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
