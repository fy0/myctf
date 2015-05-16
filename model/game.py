﻿# coding:utf-8

import os
import re
import json
from lib.jsdict import JsDict
from collections import OrderedDict


class Games(object):
    data = JsDict()
    score_board = JsDict()  # k user_name v score
    solved = {}  # k user_name v list of game_id
    solved_all = {}  # k game_id v user_name

    @classmethod
    def solve(cls, user, game_id, key):
        g = cls.get_game(game_id)
        if g:
            if g.key != key:
                return False
            if not user.username in cls.solved:
                cls.solved[user.username] = []
            if game_id in cls.solved[user.username]:
                return False
            if not user.username in cls.score_board:
                cls.score_board[user.username] = 0
            cls.score_board[user.username] += g.score
            cls.solved[user.username].append(game_id)
            return True

    @classmethod
    def get_user_solved(cls, user):
        ''' 获取用户已经解决的问题列表'''
        if user and user.username in cls.solved:
            return map(int, cls.solved[user.username])
        return []

    @classmethod
    def get_score(cls, user):
        if user:
            if user.username in cls.score_board:
                return cls.score_board[user.username]
        return 0
        
    @classmethod
    def get_score_board(cls):
        return OrderedDict(sorted(cls.score_board.items(), key=lambda x: x[1], reverse=True))

    @classmethod
    def get_lst(cls):
        ret = []
        for i in cls.data.keys():
            ret.append([cls.data[i].id, cls.data[i].title, cls.data[i].score])
        return ret

    @classmethod
    def init(cls):
        for i in os.listdir('ctf'):
            if i.endswith('.txt'):
                raw_txt = open("ctf/"+i).read()
                txt = raw_txt
                for t in re.findall(r'"(.*?)(?<!\\)"', raw_txt, re.DOTALL):
                    txt = txt.replace(t, t.replace('\r', r'\r').replace('\n', r'\n'))

                data = JsDict(json.loads(txt))
                data.txt = data.txt.strip()
                cls.data[data.id] = data

    @classmethod
    def get_game(cls, game_id):
        return cls.data[int(game_id)]

    @classmethod
    def get_without_key(cls, game_id):
        ret = cls.data[int(game_id)].copy()
        del ret['key']
        return  JsDict(ret)

Games.init()
