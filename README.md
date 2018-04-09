# Cuckoo Market
## Twitter Stream
```
python3 twitter_stream_main.py stream \
    --twitter_creds $TWITTER_CREDS_FILE \
    --total_tweets 10 \
    --pubsub_topic projects/$PROJECT_ID/topics/$PUBSUB_TOPIC
```
## Dataflow
```
python twitter_sentiment_bq.py \
    --project $PROJECT_ID \
    --subscription projects/$PROJECT_ID/subscriptions/$PUBSUB_SUBSCRIPTION \
    --dataset $BIGQUERY_DATASET
```
