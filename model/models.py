# coding:utf-8

from model import db
from model.user import User
import model.game

db.connect()
try:
    db.create_tables([User])
except:
    pass
