import json
import tweepy

class TwitterClient(object):
    def __init__(self, creds_file=None,
        wait_on_rate_limit=True,
        wait_on_rate_limit_notify=True):
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
            self.api = tweepy.API(self.auth,
                wait_on_rate_limit=wait_on_rate_limit,
                wait_on_rate_limit_notify=wait_on_rate_limit_notify)
        except Exception as e:
            print('ERROR! Authentication Failed... Exception:\n{}'.format(e))

    def query_tweets(self, tweet_filter, count=10):
        try:
            # transform filter list to query string
            query = self.transform_filter_to_query(tweet_filter)
            for tweets in tweepy.Cursor(self.api.search, q=query).items(count):
                yield tweets

        except tweepy.TweepError as e:
            print('ERROR! {}'.format(e))

    def stream_tweets(self, listener, tweet_filter=[]):
        stream = tweepy.Stream(self.auth, listener)
        if tweet_filter:
            stream.filter(track=tweet_filter)
        else:
            stream.sample()

    def transform_filter_to_query(self, tweet_filter):
        output = ' OR '.join(tweet_filter)
        return output
