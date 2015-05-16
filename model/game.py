# coding:utf-8

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
    def reload_data(cls):
        """ 重新加载题目 """
        cls.init()

    @classmethod
    def save_to_json(cls, fn):
        info = {
            'score_board': cls.score_board,
            'solved': cls.solved,
            'solved_all': cls.solved_all,
        }
        open(fn, 'w').write(json.dumps(info))

    @classmethod
    def load_from_json(cls, fn):
        txt = open(fn, 'r').read()
        info = json.loads(txt)
        cls.score_board = info['score_board']
        cls.solved = info['solved']
        cls.solved_all = info['solved_all']

    @classmethod
    def solve(cls, user, game_id, key):
        """
        尝试回答问题。答对加分，答错或重答不管。
        :param user: 用户对象
        :param game_id: 题目id
        :param key: 答案
        :return: True 回答成功，False回答失败
        """
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
        """ 获取用户已经解决的问题列表 """
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
