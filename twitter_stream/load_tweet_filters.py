import json
from datastore_client import DatastoreClient

filename = 'tweet_filters.json'
with open('tweet_filters.json') as f:
    tweet_filters = json.load(f)

datastore_client = DatastoreClient()
datastore_key = 'tweet_filter'
for tf in tweet_filters:
    print('Loading {} tweet filter: {}'.format(tf['id'], tf['data']))
    datastore_client.update(key=datastore_key, data=tf['data'], id=tf['id'])
