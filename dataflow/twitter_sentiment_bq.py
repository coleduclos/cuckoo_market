import argparse
import logging
import sys

import apache_beam as beam
from apache_beam.io.gcp.internal.clients import bigquery
from apache_beam.metrics.metric import Metrics
from apache_beam.options.pipeline_options import GoogleCloudOptions
from apache_beam.options.pipeline_options import PipelineOptions
from apache_beam.options.pipeline_options import StandardOptions

twitter_sentiment_schema = [
    {
        'name' : 'id',
        'type' : 'INTEGER',
        'mode' : 'REQUIRED'
    },
    {
        'name' : 'created_at',
        'type' : 'DATETIME',
        'mode' : 'REQUIRED'
    },
    {
        'name' : 'text',
        'type' : 'STRING',
        'mode' : 'NULLABLE'
    },
    {
        'name' : 'sentiment_score',
        'type' : 'FLOAT',
        'mode' : 'REQUIRED'
    },
    {
        'name' : 'sentiment_magnitude',
        'type' : 'FLOAT',
        'mode' : 'REQUIRED'
    },
    {
        'name' : 'favorite_count',
        'type' : 'INTEGER',
        'mode' : 'NULLABLE'
    },
    {
        'name' : 'retweet_count',
        'type' : 'INTEGER',
        'mode' : 'NULLABLE'
    },
    {
        'name' : 'lang',
        'type' : 'STRING',
        'mode' : 'REQUIRED'
    },
    {
        'name' : 'label',
        'type' : 'STRING',
        'mode' : 'REQUIRED'
    },
    {
        'name' : 'user',
        'type' : 'RECORD',
        'mode' : 'REQUIRED',
        'fields': [
            {
                'name': 'id',
                'type': 'INTEGER',
                'mode': 'REQUIRED'
            },
            {
                'name': 'followers_count',
                'type': 'INTEGER',
                'mode': 'REQUIRED'
            },
            {
                'name': 'friends_count',
                'type': 'INTEGER',
                'mode': 'REQUIRED'
            }
        ]
    }
]

twitter_raw_schema = [
    {
        'name' : 'label',
        'type' : 'STRING',
        'mode' : 'REQUIRED'
    },
    {
        'name' : 'data',
        'type' : 'STRING',
        'mode' : 'REQUIRED'
    }
]

class ExtractRawTweetsFn(beam.DoFn):
    def __init__(self):
        super(ExtractRawTweetsFn, self).__init__()
        self.num_extract_errors = Metrics.counter(self.__class__, 'num_extract_errors')

    def process(self, elem):
        import base64
        import json
        try:
            elem_decoded = base64.urlsafe_b64decode(str(elem)).decode('utf-8')
            tweets = json.loads(elem_decoded)
            yield tweets.get('messages', [])

        except Exception as e:
            # Log and count parse errors
            self.num_extract_errors.inc()
            logging.error('Exception: {}'.format(e))
            logging.error('Extract error on "%s"', elem)

class ParseTweetsFn(beam.DoFn):
    def __init__(self):
        super(ParseTweetsFn, self).__init__()
        self.num_parse_errors = Metrics.counter(self.__class__, 'num_parse_errors')

    def process(self, elem):
        import json
        try:
            output = []
            for tweet in elem:
                message = json.loads(tweet['data'])
                message['label'] = tweet['label']
                output.append(message)
            logging.debug('Parsed {} tweets: {}'.format(len(output), output))
            yield output

        except Exception as e:
            # Log and count parse errors
            self.num_parse_errors.inc()
            logging.error('Exception: {}'.format(e))
            logging.error('Parse error on "%s"', elem)

class FilterTweetsFn(beam.DoFn):
    def __init__(self, languages_supported=['en']):
        super(FilterTweetsFn, self).__init__()
        self.languages_supported = languages_supported
    def process(self, elem):
        output = [ tweet for tweet in elem if tweet.get('lang', None) in self.languages_supported ]
        yield output

class CleanTweetsFn(beam.DoFn):
    def __init__(self):
        super(CleanTweetsFn, self).__init__()
        self.num_clean_errors = Metrics.counter(self.__class__, 'num_clean_errors')

    def process(self, elem):
        import re
        try:
            for tweet in elem:
                tweet['text'] = ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", tweet['text']).split())
            yield elem

        except Exception as e:
            # Log and count clean errors
            self.num_clean_errors.inc()
            logging.error('Exception: {}'.format(e))
            logging.error('Clean error on "%s"', elem)

class AnalyzeSentimentFn(beam.DoFn):
    def __init__(self):
        super(AnalyzeSentimentFn, self).__init__()
        self.num_sentiment_errors = Metrics.counter(self.__class__, 'num_sentiment_errors')

    def process(self, elem):
        from google.cloud import language
        from google.api_core import retry
        language_client = language.LanguageServiceClient()
        api_retry = retry.Retry(deadline=60)
        try:
            for tweet in elem:
                tweet_document = language.types.Document(
                    content=tweet['text'],
                    type=language.enums.Document.Type.PLAIN_TEXT)
                tweet_annotations = language_client.analyze_sentiment(document=tweet_document, retry=api_retry)
                tweet['sentiment_score'] = tweet_annotations.document_sentiment.score
                tweet['sentiment_magnitude'] = tweet_annotations.document_sentiment.magnitude
                print('TWEET: {} \nSCORE: {} | MAGNITUDE: {}'.format(tweet['text'], tweet['sentiment_score'], tweet['sentiment_magnitude']))
            yield elem

        except Exception as e:
            # Log and count sentiment errors
            self.num_sentiment_errors.inc()
            logging.error('Exception: {}'.format(e))
            logging.error('Sentiment error on "%s"', elem)

class ConvertBigQueryRowFn(beam.DoFn):
    def __init__(self, schema):
        super(ConvertBigQueryRowFn, self).__init__()
        self.schema = schema

    def process(self, elem):
        for tweet in elem:
            yield self.convert(self.schema, tweet)

    def convert(self, schema, tweet):
        from datetime import datetime
        output = {}
        for field in schema:
            column = field['name']
            if field['type'] == 'DATETIME':
                # Convert YYYY-MM-DDTHH:MM:SS
                output[column] = datetime.strptime(tweet[column], '%a %b %d %X +0000 %Y').strftime('%Y-%m-%dT%X')
            elif field['type'] == 'RECORD':
                output[column] = self.convert(field['fields'], tweet[column])
            else:
                output[column] = tweet[column]
        return output

class WriteToBigQuery(beam.PTransform):
    """Generate, format, and write BigQuery table row information."""
    def __init__(self, table_name, dataset, schema):
        """Initializes the transform.
        Args:
          table_name: Name of the BigQuery table to use.
          dataset: Name of the dataset to use.
          schema: Dictionary in the format {'column_name': 'bigquery_type'}
        """
        super(WriteToBigQuery, self).__init__()
        self.table_name = table_name
        self.dataset = dataset
        self.schema = schema

    def get_bq_table_schema(self):
        table_schema = bigquery.TableSchema()
        for field in self.schema:
            field_schema = self.get_bq_field_schema(field)
            table_schema.fields.append(field_schema)
        return table_schema

    def get_bq_field_schema(self, field):
        field_schema = bigquery.TableFieldSchema()
        field_schema.name = field['name']
        field_schema.type = field['type']
        field_schema.mode = field['mode']
        if field['type'] == 'RECORD':
            for nested_field in field['fields']:
                nested_field_schema = self.get_bq_field_schema(nested_field)
                field_schema.fields.append(nested_field_schema)
        return field_schema

    def expand(self, pcoll):
        project = pcoll.pipeline.options.view_as(GoogleCloudOptions).project
        return (
            pcoll
            | 'ConvertBigQueryRowFn' >> beam.ParDo(ConvertBigQueryRowFn(self.schema))
            | beam.io.WriteToBigQuery(
                self.table_name, self.dataset, project, self.get_bq_table_schema()))

def run(argv=None):
    """Main entry point; defines and runs the hourly_team_score pipeline."""
    parser = argparse.ArgumentParser()
    parser.add_argument('--subscription',
        type=str,
        required=True,
        help='Pub/Sub subscription to use when reading from topic.')
    parser.add_argument('--dataset',
        type=str,
        required=True,
        help='BigQuery Dataset to write tables to. '
        'Must already exist.')
    parser.add_argument('--table_name',
        type=str,
        default='tweet_sentiment',
        help='The BigQuery table name. Should not already exist.')

    args, pipeline_args = parser.parse_known_args(argv)
    options = PipelineOptions(pipeline_args)
    google_languages_supported = ['de', 'en', 'es', 'fr', 'it', 'ja', 'ko', 'pt', 'zh', 'zh-Hant']
    raw_table_name = '{}_raw'.format(args.table_name)

    # We also require the --project option to access --dataset
    if options.view_as(GoogleCloudOptions).project is None:
        parser.print_usage()
        print(sys.argv[0] + ': error: argument --project is required')
        sys.exit(1)

    # Enforce that this pipeline is always run in streaming mode
    options.view_as(StandardOptions).streaming = True

    with beam.Pipeline(options=options) as pipeline:
        # Read events from Pub/Sub and extract raw tweets
        tweets_raw = (
            pipeline
            | 'ReadPubSub' >> beam.io.gcp.pubsub.ReadStringsFromPubSub(subscription=args.subscription)
            | 'ExtractRawTweetsFn' >> beam.ParDo(ExtractRawTweetsFn()))
        # Write raw tweets to BigQuery
        tweets_raw_to_bq = (
            tweets_raw
            | 'WriteRawTweetsToBigQuery' >> WriteToBigQuery(raw_table_name,
                args.dataset, twitter_raw_schema))
        # Calculate sentiment of each tweet and write to BigQuery
        tweets_sentiment = (
            tweets_raw
            | 'ParseTweetsFn' >> beam.ParDo(ParseTweetsFn())
            | 'FilterTweetsFn' >> beam.ParDo(FilterTweetsFn(languages_supported=google_languages_supported))
            | 'CleanTweetsFn' >> beam.ParDo(CleanTweetsFn())
            | 'AnalyzeSentimentFn' >> beam.ParDo(AnalyzeSentimentFn())
            | 'WriteSentimentToBigQuery' >> WriteToBigQuery(args.table_name,
                args.dataset, twitter_sentiment_schema))


if __name__ == '__main__':
    logging.getLogger().setLevel(logging.INFO)
    run()
