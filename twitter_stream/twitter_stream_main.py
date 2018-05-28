import argparse
import json
import sys
from datastore_client import DatastoreClient
from twitter_client import TwitterClient
from twitter_stream_listeners import PubSubListener
from twitter_stream_listeners import StdOutListener

def get_tweet_filter(id, kind='tweet_filter'):
    datastore_client = DatastoreClient()
    response = datastore_client.get_from_id(kind, id)
    if response:
        return response.get('filter', [])
    else:
        print('ERROR: Could not find tweet filter from Datastore for {}. Exitting...'.format(id))
        sys.exit(1)

def query(args, listener):
    twitter_client = TwitterClient(creds_file=args.twitter_creds)
    tweet_filter = get_tweet_filter(args.stock.lower())
    print('Querying Tweets related to {}... \nUsing filter: {}'.format(args.stock, tweet_filter))
    tweets = twitter_client.query_tweets(tweet_filter=tweet_filter,
        count=args.total_tweets)
    count = 0
    for tweet in tweets:
        count += 1
        listener.on_data(json.dumps(tweet._json))
    # Flush any remaining tweets in the buffer
    listener.flush_buffer()
    print('Returned Tweets: {}'.format(count))

def stream(args, listener):
    twitter_client = TwitterClient(creds_file=args.twitter_creds)
    tweet_filter = get_tweet_filter(args.stock.lower())
    print('Streaming Tweets related to {}... \nUsing filter: {}'.format(args.stock, tweet_filter))
    twitter_client.stream_tweets(listener,
        tweet_filter=tweet_filter)

def main():
    print('Starting the main script')
    parser = argparse.ArgumentParser(description='Twitter Stream')
    subparsers = parser.add_subparsers(help='sub-command help')
    query_parser = subparsers.add_parser('query', help='query help')
    stream_parser = subparsers.add_parser('stream', help='stream help')
    query_parser.add_argument('--stock',
            required=True,
            help='Stock used to filter tweets.')
    query_parser.add_argument('--twitter_creds',
            required=True,
            help='File containing twitter credentials.')
    query_parser.add_argument('--total_tweets',
            default=1000,
            type=int,
            help='Total number of tweets to query.')
    query_parser.add_argument('--pubsub_topic',
            help='The Pub/Sub topic to send queried Tweets to.')
    stream_parser.add_argument('--stock',
            required=True,
            help='Stock used to filter tweets.')
    stream_parser.add_argument('--pubsub_topic',
            help='The Pub/Sub topic to stream Tweets to.')
    stream_parser.add_argument('--twitter_creds',
            required=True,
            help='File containing twitter credentials.')
    stream_parser.add_argument('--total_tweets',
            type=int,
            help='Total number of tweets to stream.')
    query_parser.set_defaults(func=query)
    stream_parser.set_defaults(func=stream)
    args = parser.parse_args()

    # Set the listener based on pubsub_topic
    if args.pubsub_topic:
        print('Sending Tweets to {}...'.format(args.pubsub_topic))
        listener = PubSubListener(args.pubsub_topic,
            label=args.stock,
            total_tweets=args.total_tweets)
    else:
        print('Sending Tweets to Standard Out...')
        listener = StdOutListener(total_tweets=args.total_tweets)

    args.func(args, listener)
    print('Finished!')

if __name__ == '__main__':
    main()
