# coding:utf-8
import json

import time
from lib.jsdict import JsDict
from view import route, url_for, View, AdminView
from model.game import Games, game_init


@route('/admin', name='admin')
class Admin(AdminView):
    def get(self):
        lst = Games.last_save_time
        if lst == 0:
            lst = u'从未'
        else:
            x = time.localtime(lst)
            lst = time.strftime('%Y-%m-%d %H:%M:%S',x)
        self.render('admin/admin.html', nav='admin', last_save_time=lst, is_end=Games.is_end)


@route('/admin/backup', name='admin_backup')
class Admin(AdminView):
    def get(self):
        Games.save_to_json('save.json')
        self.messages.success("进度已保存")
        self.redirect(url_for('admin'))


@route('/admin/restore', name='admin_restore')
class Admin(AdminView):
    def get(self):
        try:
            Games.load_from_json('save.json')
            self.messages.success("已读取记录中的进度")
        except:
            self.messages.error("没有找到备份文件")
        self.redirect(url_for('admin'))


@route('/admin/reload', name='admin_reload')
class Admin(AdminView):
    def get(self):
        Games.reload_data()
        self.redirect(url_for('admin'))


@route('/admin/halt', name='admin_halt')
class Admin(AdminView):
    def get(self):
        Games.is_end = True
        self.messages.success('中止答题！')
        self.redirect(url_for('admin'))

@route('/admin/boot', name='admin_boot')
class Admin(AdminView):
    def get(self):
        Games.is_end = False
        self.messages.success('答题重新开放！')
        self.redirect(url_for('admin'))


@route('/admin/reset', name='admin_reset')
class Admin(AdminView):
    def get(self):
        Games.reset()
        self.messages.success('重置完成！')
        self.redirect(url_for('admin'))


@route('/admin/questions', name='admin_questions')
class Questions(AdminView):
    def get(self):
        self.render('admin/questions.html', lst=Games.get_lst())


class QuestionCheck(AdminView):
    def value_valid(self, qid):
        id = self.get_argument('id', '').strip()
        title = self.get_argument('title', '').strip()
        author = self.get_argument('author', '').strip()
        score = self.get_argument('score', '').strip()
        depend = self.get_argument('depend', '[]').strip()
        depend_g = self.get_argument('depend-g', '[]').strip()
        txt = self.get_argument('txt', '').strip()
        key = self.get_argument('key', '').strip()

        # id
        if id == '':
            self.messages.error(u'编号为必填')
        else:
            if not id.isdigit():
                self.messages.error(u'编号必须为数字')
            elif (qid is None or int(id) != int(qid)) and int(id) in Games.data:
                self.messages.error(u'该编号已经存在')

        # 标题
        if title == '':
            self.messages.error(u'标题不能为空')

        # 分数
        if score == '':
            self.messages.error(u'分数为必填')
        else:
            if not id.isdigit():
                self.messages.error(u'分数必须为数字')

        # 前置检查
        def depend_check(prefix, txt):
            try:
                info = json.loads(txt)
                if type(info) != list:
                    self.messages.error(u'%s类型不为list' % prefix)
                else:
                    for i in info:
                        if type(i) != int:
                            self.messages.error(u'%s子项类型必须为整型' % prefix)
                            break
                        else:
                            if not int(i) in Games.data:
                                self.messages.error(u'%s中的编号%s不存在' % (prefix, i))
                                break
                if not self.messages.has_error():
                    return info
            except:
                self.messages.error(u'%s不是标准的json格式' % prefix)

        # 用户前置题
        _ = depend_check(u'用户前置题', depend)
        depend = _ if _ is not None else depend

        # 全局前置题
        _ = depend_check(u'全局前置题', depend_g)
        depend_g = _ if _ is not None else depend

        # 最后总结
        if self.messages.has_error():
            return {
                'id': id,
                'title': title,
                'author': author,
                'score': score,
                'depend': depend,
                'depend-g': depend_g,
                'txt': txt,
                'key': key,
            }
        else:
            return {
                'id': int(id),
                'title': title,
                'author': author,
                'score': int(score),
                'depend': depend,
                'depend-g': depend_g,
                'txt': txt,
                'key': key,
            }


@route('/admin/question/edit/(\d+)', name='admin_question_edit')
class QuestionEdit(QuestionCheck):

    def get(self, qid):
        q = Games.data.get(int(qid))
        if not q:
            self.write_error(404)
        else:
            self.render('admin/question_edit.html', question=JsDict(q), title=u'编辑：%s' % q['title'])

    def post(self, qid):
        ret = self.value_valid(qid)

        if self.messages.has_error():
            q = Games.data.get(int(qid))
            self.render('admin/question_edit.html', question=JsDict(ret), title=u'编辑：%s' % q['title'])
        else:
            ret['id'] = int(qid)
            Games.game_edit(ret)
            self.messages.success(u'编辑成功')
            self.redirect(url_for('admin_questions'))


@route('/admin/question/add', name='admin_question_add')
class QuestionAdd(QuestionCheck):
    def get(self):
        self.render('admin/question_edit.html', question=JsDict({}), title=u'添加题目', is_new_question=True)

    def post(self):
        ret = self.value_valid(None)

        if self.messages.has_error():
            self.render('admin/question_edit.html', question=JsDict(ret), title=u'添加题目', is_new_question=True)
        else:
            Games.game_add(ret)
            self.messages.success(u'添加题目成功')
            self.redirect(url_for('admin_questions'))


@route('/admin/question/rm/(\d+)', name='admin_question_rm')
class QuestionRemove(AdminView):
    def get(self, qid):
        Games.game_rm(int(qid))
        self.messages.success(u'题目%s已经删除！' % qid)
        self.redirect(url_for('admin'))
