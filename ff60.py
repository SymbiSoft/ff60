#-*-coding:utf-8-*-

"""

Partially based on MOO example from http://habrahabr.ru/blogs/PyS60/73951/

"""

import appuifw

appuifw.app.directional_pad = False
appuifw.app.body = appuifw.Text(u'Please update your feed')
appuifw.app.title = u'ff60'
appuifw.app.screen = 'normal'

import sys
import e32
import e32dbm

import friendfeed
import re

SIS_VERSION = "0.2"

oauth_consumer_key = u'039f2ee0fea942be9ca9ccdd3455a98c'
oauth_consumer_secret = u'6cdfe18c375644d4a5619aa5b42c81d85cb4116dd4a84a948f274059ff096ea0'
ff_num_per_page = 25

class Main:
    def __init__(self):
        # отключаем экранную клавиатуру
        self.db = e32dbm.open(u'c:\\ff60.db', 'c')
        self.data = None
        self.lb = None
        self.links_list = appuifw.Listbox([u'Links list'], self.open_link)
        self.page = 0
        self.ff = None
        self.feed_list = []
        self.locale = self.db and  self.db.get('locale', 'en') or 'en'
        self.waiter = appuifw.Text(u'Please wait...')
        appuifw.app.menu = [
            (u'Update feed', self.view_feed),
            (u'Change password', self.ask_passwd),
            (u'Change locale', self.change_locale),
        ]

    def change_locale(self):
        languages = {
            u'English': 'en', 
            u'Русский': 'ru',
        }
        keys = languages.keys()
        idx = appuifw.selection_list(keys)
        self.locale = languages[keys[idx]]
        self.db['locale'] = self.locale
        self.ff = None

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
            self.feed_list = self.ff.fetch_feed_list(locale=self.locale)
            self.feed_info = self.ff.fetch_feed_info('me', locale=self.locale)
        self.data = self.ff.fetch_feed("home", num=ff_num_per_page, start=ff_num_per_page*self.page, maxcomments=0, maxlikes=0, raw=1, locale=self.locale)

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

        appuifw.app.title = u'ff60 - view feed'
        appuifw.app.body = self.lb
        app_menu = [
            (u'New post', self.new_post),
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

    def new_post(self):
        post_text = appuifw.Text(u'')
        appuifw.app.title = u'ff60 - new post'
        appuifw.app.body = post_text
        appuifw.app.menu = [
            (u'Send', self.send_post),
        ]
        appuifw.app.exit_key_handler = self.view_feed

    def send_post(self):
        feed_dict = {'me': u'My feed'}
        feed_dict.update(dict(map(lambda s: (s['id'], s['name']), filter(lambda s: s['type'] == u'group', self.feed_info['subscriptions']))))
        post_to_ids = appuifw.multi_selection_list(feed_dict.values(), 'checkbox', 1)
        post_to = map(lambda id: feed_dict.keys()[id], post_to_ids)
        body = appuifw.app.body.get()
        if body and post_to:
            appuifw.note('Posting %s to %s ...' % (body, u', '.join(post_to)))
            self.ff.post_entry(body, to=u','.join(post_to))
            appuifw.note('ok! now updating your feed...')
            self.view_feed(update=True)
        else:
            self.view_feed(update=False)

    def show_post(self):
        entry = self.data['entries'][self.lb.current()]
        post_text = appuifw.Text(entry['rawBody'])
        post_text.color = 0x000066

        # self.links = [entry['url']]
        self.links = []
        self.links += re.findall(u'[^>](https?://[^"<>\s]+)', entry['body'] + u' ' + entry['rawBody'], re.I)
        self.links += [t['link'] for t in entry.get('thumbnails', [])]
        self.links = list(set(self.links))

        appuifw.app.title = u'ff60 - view post'
        post_text.add(u'\n\nLinks:\n' + u'\n'.join(self.links))
        appuifw.app.body = post_text
        appuifw.app.menu = [
            (u'Browse post', self.open_url),
            (u'Browse links', self.show_links),
            (u'View feed', self.view_feed),
        ]
        appuifw.app.exit_key_handler = self.view_feed

    def show_links(self):
        entry = self.data['entries'][self.lb.current()]
        self.links_list.set_list(self.links)
        appuifw.app.body = self.links_list
        appuifw.app.menu = [
            (u'Open', self.open_link),
        ]
        appuifw.app.exit_key_handler = self.show_post

    def open_url(self):
        browserApp ='BrowserNG.exe'
        url = self.data['entries'][self.lb.current()]['url']
        e32.start_exe(browserApp, ' "4 %s"' % url, 1)

    def open_link(self):
        browserApp ='BrowserNG.exe'
        url = self.links[self.links_list.current()]
        e32.start_exe(browserApp, ' "4 %s"' % url, 1)

# создаем объект lock, который нужен, чтоб ваше приложение не закрылось сразу после открытия
lock = e32.Ao_lock()
# при нажатии правую софт клавишу, освобождаем lock, приложение закроется.
appuifw.app.exit_key_handler = lock.signal
main_obj = Main()
lock.wait()
