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
#### DirectRunner
```
python twitter_sentiment_bq.py \
    --project $PROJECT_ID \
    --subscription projects/$PROJECT_ID/subscriptions/$PUBSUB_SUBSCRIPTION_BQ \
    --dataset $BIGQUERY_DATASET
```
#### DataflowRunner
```
python twitter_sentiment_bq.py \
    --project $PROJECT_ID \
    --subscription projects/$PROJECT_ID/subscriptions/$PUBSUB_SUBSCRIPTION_BQ \
    --dataset $BIGQUERY_DATASET \
    --runner DataflowRunner \
    --requirements_file requirements.txt \
    --staging_location $DATAFLOW_GCS_STAGING \
    --temp_location $DATAFLOW_GCS_TEMP
```
### Google Cloud Storage
#### DirectRunner
```
python twitter_sentiment_gcs.py \
    --project $PROJECT_ID \
    --subscription projects/$PROJECT_ID/subscriptions/$PUBSUB_SUBSCRIPTION_GCS \
    --output $GCS_PREFIX
```
#### DataflowRunner
```
python twitter_sentiment_gcs.py \
    --project $PROJECT_ID \
    --subscription projects/$PROJECT_ID/subscriptions/$PUBSUB_SUBSCRIPTION_GCS \
    --output $GCS_PREFIX \
    --runner DataflowRunner \
    --staging_location $DATAFLOW_GCS_STAGING \
    --temp_location $DATAFLOW_GCS_TEMP
```
## Kubernetes Setup
```
kubectl create secret generic twitter --from-file=$TWITTER_CREDS_FILE
```
