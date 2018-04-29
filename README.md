# Cuckoo Market
## Twitter Stream
### Stream
```
python3 twitter_stream_main.py stream \
    --stock $STOCK \
    --twitter_creds $TWITTER_CREDS_FILE \
    --total_tweets 10 \
    --pubsub_topic projects/$PROJECT_ID/topics/$PUBSUB_TOPIC
```
### Query
```
python3 twitter_stream_main.py query \
    --stock $STOCK \
    --twitter_creds $TWITTER_CREDS_FILE \
    --total_tweets 10 \
    --pubsub_topic projects/$PROJECT_ID/topics/$PUBSUB_TOPIC
```
## Dataflow
### BigQuery
```
python twitter_sentiment_bq.py \
    --project $PROJECT_ID \
    --subscription projects/$PROJECT_ID/subscriptions/$PUBSUB_SUBSCRIPTION_BQ \
    --dataset $BIGQUERY_DATASET
```
### Google Cloud Storage
```
python twitter_sentiment_gcs.py \
    --project $PROJECT_ID \
    --subscription projects/$PROJECT_ID/subscriptions/$PUBSUB_SUBSCRIPTION_GCS \
    --output $GCS_PREFIX
```
## Kubernetes Setup
```
kubectl create secret generic twitter --from-file=$TWITTER_CREDS_FILE
```
