# coding:utf-8

from view import route, url_for, View
from model.game import Games
from lib.jsdict import JsDict
from tornado.web import authenticated

@route('/game', name='game')
class Game(View):
    def get(self):
        self.render(
            nav='game',
            lst=Games.get_lst(),
            score=Games.get_score(self.current_user()),
            solved=Games.get_user_solved(self.current_user()),
            score_board=Games.get_score_board(),
        )


@route('/game_get/(\d+)', name='game_get')
class GameGet(View):
    def get(self, game_id):
        if not self.current_user():
            self.messages.error('请先登录！')
            return self.redirect(url_for('signin'))

        g = Games.data[int(game_id)]
        if g:
            ret = g.copy()
            del ret['key']
            self.render(game=JsDict(ret))

    def post(self, game_id):
        if not self.current_user():
            self.messages.error('请先登录！')
            return self.redirect(url_for('signin'))

        if Games.is_reach_deadline():
            self.messages.error("答题时间已经结束！")
            return self.redirect(url_for('game'))

        k = self.get_argument('key')
        if Games.solve(self.current_user(), game_id, k):
            self.messages.success("回答正确！")
            self.redirect(url_for('game'))
        else:
            self.messages.error("回答错误或已经回答过！")
            self.render(game=Games.get_without_key(game_id))


@route('/about', name='about')
class About(View):
    def get(self):
        self.render(nav='about')

'''
@route('/j/game_get/(\d+)', name='j_game_get')
class GameGet(View):
    def get(self, game_id):
        g = Games.data[int(game_id)]
        if g:
            ret = g.copy()
            del ret['key']
            self.finish(ret)

    def post(self, game_id):
        k = self.get_argument('key')
        g = Games.data[int(game_id)]
        if g and g.key == k:
            self.finish({'code':0})
        else:
            self.finish({'code':1})
'''
