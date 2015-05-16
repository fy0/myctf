# coding:utf-8

import os
import re
import json
import time
from lib.jsdict import JsDict
from collections import OrderedDict


class Games(object):
    data = JsDict()
    score_board = JsDict()  # k user_name v score
    solved = {}  # k user_name v list of game_id
    solved_all = {}  # k game_id v user_name
    extra = {}  # 附加分值
    deadline = 9431781807  # 时间戳，关闭提交的时间期限
    last_submit = JsDict()  # 最后提交

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
            'extra': cls.extra,
            'last_submit': cls.last_submit,
        }
        open(fn, 'w').write(json.dumps(info))

    @classmethod
    def load_from_json(cls, fn):
        txt = open(fn, 'r').read()
        info = json.loads(txt)
        if 'score_board' in info:
            cls.score_board = info['score_board']
        if 'solved' in info:
            cls.solved = info['solved']
        if 'solved_all' in info:
            cls.solved_all = info['solved_all']
        if 'extra' in info:
            for k, v in info['extra'].items():
                # json 的 key 不能为数字，所以。。
                k = int(k)
                cls.extra[k] = v
        if 'last_submit' in info:
            cls.last_submit = info['last_submit']
        if 'deadline' in info:
            cls.deadline = info['deadline']

    @classmethod
    def solve(cls, user, game_id, key):
        """
        尝试回答问题。答对加分，答错或重答不管。
        :param user: 用户对象
        :param game_id: 题目id
        :param key: 答案
        :return: True 回答成功，False回答失败
        """
        game_id = int(game_id)
        g = cls.get_game(game_id)
        if g:
            # 答案错误直接返回
            if g.key != key:
                return False

            # 初始化回答列表
            if not user.username in cls.solved:
                cls.solved[user.username] = []

            # 已经回答过直接返回
            if game_id in cls.solved[user.username]:
                return False

            # 加分
            if not user.username in cls.score_board:
                cls.score_board[user.username] = 0
            cls.score_board[user.username] += g.score

            # 奖励分数
            if game_id in cls.extra and cls.extra[game_id] > 0:
                cls.score_board[user.username] += cls.extra[game_id]
                cls.extra[game_id] -= 1

            # 加入回答列表
            cls.solved[user.username].append(game_id)

            # 标记最后提交
            cls.last_submit[user.username] = time.time()

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
                data.id = int(data.id)
                if not data.id in cls.extra:
                    cls.extra[data.id] = data.extra if 'extra' in data else 5
                cls.data[data.id] = data

    @classmethod
    def get_game(cls, game_id):
        return cls.data[int(game_id)]

    @classmethod
    def get_without_key(cls, game_id):
        ret = cls.data[int(game_id)].copy()
        del ret['key']
        return JsDict(ret)

# 初始化
Games.init()

# 读取数据
if os.path.exists('save.json'):
    Games.load_from_json('save.json')
