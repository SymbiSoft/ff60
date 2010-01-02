#-*-coding:utf-8-*-

"""

Partially based on MOO example from http://habrahabr.ru/blogs/PyS60/73951/

"""

import friendfeed
import sys

oauth_consumer_key = u'039f2ee0fea942be9ca9ccdd3455a98c'
oauth_consumer_secret = u'6cdfe18c375644d4a5619aa5b42c81d85cb4116dd4a84a948f274059ff096ea0'

print u'Getting for', sys.argv[1:]
user, passwd = sys.argv[1:]
consumer_token = dict(key=oauth_consumer_key, secret=oauth_consumer_secret)
access_token = friendfeed.fetch_installed_app_access_token(consumer_token, user, passwd)
ff = friendfeed.FriendFeed(consumer_token, access_token)
data = ff.fetch_feed("home")
items = []
for e in data['entries']:
    items.append((e['from']['name'], e['body'][:25] + u'...'))
print items

