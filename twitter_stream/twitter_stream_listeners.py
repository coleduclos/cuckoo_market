import base64
import datetime
import json
from google.cloud import pubsub
from tweepy import StreamListener

class PubSubListener(StreamListener):
    def __init__(self, pubsub_topic,
        batch_size=50,
        num_retries=3,
        total_tweets=1000):
        super()
        self.batch_size = batch_size
        self.count = 0
        self.num_retries = num_retries
        self.pubsub_topic = pubsub_topic
        self.total_tweets = total_tweets
        self.tweets = []
        self.pubsub_client = pubsub.PublisherClient()

    def on_data(self, data):
        self.tweets.append(data)
        if len(self.tweets) >= self.batch_size:
            self.write_to_pubsub(self.tweets)
            self.tweets = []
        self.count += 1
        if self.count >= self.total_tweets:
            if len(self.tweets) > 0:
                self.write_to_pubsub(self.tweets)
            return False
        if (self.count % 1000) == 0:
            print('count is: {} at {}'.format(self.count, datetime.datetime.now()))
        return True

    def flush_buffer(self):
        if len(self.tweets) > 0:
            self.write_to_pubsub(self.tweets)
            self.tweets = []
            return True
        else:
            return False

    def on_error(self, status):
        print('ERROR: {}'.format(status))

    def write_to_pubsub(self, data_list):
        messages = []
        for data in data_list:
            messages.append({'data': data})
        body = base64.urlsafe_b64encode(json.dumps({'messages': messages}).encode('utf-8'))
        response = self.pubsub_client.publish(self.pubsub_topic, body)
        return response

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
