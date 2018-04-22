import json
import tweepy

class TwitterClient(object):
    def __init__(self, creds_file=None):
        if creds_file:
            creds_obj = json.load(open(creds_file))
            access_token = creds_obj['access_token']
            access_token_secret = creds_obj['access_token_secret']
            consumer_key = creds_obj['consumer_key']
            consumer_secret = creds_obj['consumer_secret']
        else:
            access_token = os.environ['TWITTER_ACCESS_TOKEN']
            access_token_secret = os.environ['TWITTER_ACCESS_TOKEN_SECRET']
            consumer_key = os.environ['TWITTER_CONSUMER_KEY']
            consumer_secret = os.environ['TWITTER_CONSUMER_SECRET']
        try:
            # create OAuthHandler object
            self.auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
            # set access token and secret
            self.auth.set_access_token(access_token, access_token_secret)
            # create tweepy API object to fetch tweets
            self.api = tweepy.API(self.auth)
        except:
            print('ERROR! Authentication Failed...')

    def query_tweets(self, filter, count=10):
        try:
            # transform filter list to query string
            query = self.transform_filter_to_query(filter)
            for tweets in tweepy.Cursor(self.api.search, q=query).items(count):
                yield tweets

        except tweepy.TweepError as e:
            print('ERROR! {}'.format(e))

    def stream_tweets(self, listener, filter=[]):
        stream = tweepy.Stream(self.auth, listener)
        if filter:
            stream.filter(track=filter)
        else:
            stream.sample()

    def transform_filter_to_query(self, filter):
        output = ' OR '.join(filter)
        return output
