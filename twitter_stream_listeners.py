import datetime
from tweepy import StreamListener

class StdOutListener(StreamListener):
    """
    A listener simply prints to standard out
    """
    def __init__(self, total_tweets=1000):
        super()
        self.count = 0
        self.total_tweets = total_tweets

    def on_data(self, data):
        print(data)
        self.count += 1
        if self.count > self.total_tweets:
            return False
        if (self.count % 1000) == 0:
            print('count is: {} at {}'.format(self.count, datetime.datetime.now()))
        return True

    def on_error(self, status):
        print('ERROR: {}'.format(status))
