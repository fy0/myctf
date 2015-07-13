# coding:utf-8

from lib.jsdict import JsDict
from view import route, url_for, View
from model.game import Games


@route('/game', name='game')
class Game(View):
    def get(self):
        depend_check = lambda x: Games.depend_check(self.current_user(), int(x))
        self.render(
            nav='game',
            lst=Games.get_brief_lst(),
            score=Games.get_score(self.current_user()),
            solved=Games.get_user_solved(self.current_user()),
            score_board=Games.get_score_board(),
            depend_check=depend_check,
        )


@route('/game_get/(\d+)', name='game_get')
class GameGet(View):
    def get(self, game_id):
        if not self.current_user():
            self.messages.error('请先登录！')
            return self.redirect(url_for('signin'))

        g = Games.data[int(game_id)]
        if g and Games.depend_check(self.current_user(), int(game_id)):
            ret = g.copy()
            del ret['key']
            self.render(game=JsDict(ret))
        else:
            self.write_error(404)

    def post(self, game_id):
        if not self.current_user():
            self.messages.error('请先登录！')
            return self.redirect(url_for('signin'))

        if Games.is_end:
            self.messages.error("答题时间已经结束！")
            return self.redirect(url_for('game'))

        if not Games.depend_check(self.current_user(), int(game_id)):
            self.messages.error("题目尚未解锁！")
            return self.redirect(url_for('game'))

        k = self.get_argument('key')
        if Games.solve(self.current_user(), int(game_id), k):
            self.messages.success("回答正确！")
            self.redirect(url_for('game'))
        else:
            self.messages.error("回答错误或已经回答过！")
            self.render(game=Games.get_without_key(game_id))
