import friendfeed

consumer_token = dict(
    key="<consumer key>", 
    secret="<consumer secret>")

access_token = friendfeed.fetch_installed_app_access_token(
    consumer_token, "<username>", "<password>")

ff = friendfeed.FriendFeed(consumer_token, access_token)

print ff.fetch_feed("home")
