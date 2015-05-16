# coding:utf-8

from view import route, url_for, View
from model.game import Games
from lib.jsdict import JsDict

@route('/admin3123', name='admin')
class Admin(View):
    def get(self):
        self.render()

@route('/admin/backup', name='admin_backup')
class Admin(View):
    def get(self):
        Games.save_to_json('save.json')
        self.redirect(url_for('admin'))

@route('/admin/restore', name='admin_restore')
class Admin(View):
    def get(self):
        try:
            Games.load_from_json('save.json')
        except:
            self.messages.error("没有找到备份文件")
        self.redirect(url_for('admin'))

@route('/admin/reload', name='admin_reload')
class Admin(View):
    def get(self):
        Games.reload_data()
        self.redirect(url_for('admin'))
