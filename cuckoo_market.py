import argparse
import json
from twitter_client import TwitterClient
from twitter_stream_listeners import StdOutListener

twitter_filter = 'Google'

def query(args):
    twitter_client = TwitterClient(creds_file=args.twitter_creds)
    tweets = twitter_client.query_tweets(query=twitter_filter, count = 10)
    for tweet in tweets:
        print(tweet.text)
    print('Returned Tweets: {}'.format(len(tweets)))

def stream(args):
    twitter_client = TwitterClient(creds_file=args.twitter_creds)
    twitter_client.stream_tweets(StdOutListener, filter=[twitter_filter])

def main():
    print('Starting the main script')
    parser = argparse.ArgumentParser(description='Cuckoo Market')
    subparsers = parser.add_subparsers(help='sub-command help')
    query_parser = subparsers.add_parser('query', help='query help')
    stream_parser = subparsers.add_parser('stream', help='stream help')
    query_parser.add_argument('--twitter_creds',
            required=True,
            help='File containing twitter credentials.')
    stream_parser.add_argument('--twitter_creds',
            required=True,
            help='File containing twitter credentials.')
    query_parser.set_defaults(func=query)
    stream_parser.set_defaults(func=stream)
    args = parser.parse_args()
    args.func(args)

    print('Finished!')

if __name__ == '__main__':
    main()
