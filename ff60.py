#-*-coding:utf-8-*-

"""

Partially based on MOO example from http://habrahabr.ru/blogs/PyS60/73951/

"""

import appuifw

appuifw.app.directional_pad = False
appuifw.app.body = appuifw.Text(u'Please update your feed')

import sys
import e32
import e32dbm

import friendfeed

SYMBIAN_UID = 0xeed4e242
SIS_VERSION = "0.1"

oauth_consumer_key = u'039f2ee0fea942be9ca9ccdd3455a98c'
oauth_consumer_secret = u'6cdfe18c375644d4a5619aa5b42c81d85cb4116dd4a84a948f274059ff096ea0'
ff_num_per_page = 25

class Main:
    def __init__(self):
        # отключаем экранную клавиатуру
        self.db = e32dbm.open(u'c:\\ff60.db', 'c')
        self.data = None
        self.lb = None
        self.page = 0
        self.ff = None
        self.waiter = appuifw.Text(u'Please wait...')
        appuifw.app.menu = [
            (u'Update feed', self.view_feed),
            (u'Change password', self.ask_passwd),
        ]

    def ask_passwd(self):
        user, passwd = appuifw.multi_query(u'username', u'password')
        self.db['user'], self.db['passwd'] = user, passwd
        self.ff = None

    def update_feed(self):
        appuifw.app.body = self.waiter
        if not self.ff:
            if not self.db.has_key('user') or not self.db.has_key('passwd'):
                self.ask_passwd()
            user, passwd = self.db['user'], self.db['passwd']
            consumer_token = dict(key=oauth_consumer_key, secret=oauth_consumer_secret)
            access_token = friendfeed.fetch_installed_app_access_token(consumer_token, user, passwd)
            self.ff = friendfeed.FriendFeed(consumer_token, access_token)
        self.data = self.ff.fetch_feed("home", num=ff_num_per_page, start=ff_num_per_page*self.page, maxcomments=0, maxlikes=0, raw=1)

    def view_feed(self, update=False):
        if update or not self.data:
            self.update_feed()
        if update or not self.lb:
            items = []
            for e in self.data['entries']:
                items.append((e['from']['name'], e['rawBody'][:64] + u'...'))
            if not self.lb:
                self.lb = appuifw.Listbox(items, self.show_post)
            else:
                self.lb.set_list(items)

        appuifw.app.body = self.lb
        app_menu = [
            (u'Next page', self.next_page),
        ]
        if self.page > 0:
            app_menu = app_menu + [(u'Previous page', self.prev_page), ]
        appuifw.app.menu = app_menu
        appuifw.app.exit_key_handler = lock.signal

    def prev_page(self):
        if self.page > 0:
            self.page -= 1
        self.view_feed(update=True)

    def next_page(self):
        self.page += 1
        self.view_feed(update=True)

    def show_post(self):
        appuifw.app.body = appuifw.Text(self.data['entries'][self.lb.current()]['rawBody'])
        appuifw.app.menu = [
            (u'Open in browser', self.open_url),
            (u'View feed', self.view_feed),
        ]
        appuifw.app.exit_key_handler = self.view_feed

    def open_url(self):
        browserApp ='BrowserNG.exe'
        url = self.data['entries'][self.lb.current()]['url']
        e32.start_exe(browserApp, ' "4 %s"' % url, 1)

# создаем объект lock, который нужен, чтоб ваше приложение не закрылось сразу после открытия
lock = e32.Ao_lock()
# при нажатии правую софт клавишу, освобождаем lock, приложение закроется.
appuifw.app.exit_key_handler = lock.signal
main_obj = Main()
lock.wait()