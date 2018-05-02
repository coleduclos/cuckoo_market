import argparse
from datetime import datetime
import logging
import sys

import apache_beam as beam
from apache_beam.options.pipeline_options import GoogleCloudOptions
from apache_beam.options.pipeline_options import PipelineOptions
from apache_beam.options.pipeline_options import StandardOptions

class WriteToGCS(beam.PTransform):
    """Generate, format, and write BigQuery table row information."""
    def __init__(self, output):
        """Initializes the transform.
        Args:
          output: GCS bucket name and prefix (Ex: "gs://output-bucket/results").
        """
        super(WriteToGCS, self).__init__()
        self.output = output

    def expand(self, pcoll):
        project = pcoll.pipeline.options.view_as(GoogleCloudOptions).project
        current_datetime = datetime.utcnow()
        file_path_prefix = '{}/{}/{}/{}/'.format(self.output,
            current_datetime.year,
            current_datetime.month,
            current_datetime.day)
        return (
            pcoll
            | beam.io.WriteToText(
                file_path_prefix=file_path_prefix,
                file_name_suffix='json',
                append_trailing_newlines=True))

def run(argv=None):
    """Main entry point; defines and runs the hourly_team_score pipeline."""
    parser = argparse.ArgumentParser()
    parser.add_argument('--subscription',
        type=str,
        required=True,
        help='Pub/Sub subscription to use when reading from topic.')
    parser.add_argument('--output',
        type=str,
        required=True,
        help='BigQuery Dataset to write tables to. '
        'Must already exist.')

    args, pipeline_args = parser.parse_known_args(argv)
    options = PipelineOptions(pipeline_args)
    # We also require the --project option to access --dataset
    if options.view_as(GoogleCloudOptions).project is None:
        parser.print_usage()
        print(sys.argv[0] + ': error: argument --project is required')
        sys.exit(1)

    # Enforce that this pipeline is always run in streaming mode
    options.view_as(StandardOptions).streaming = True

    with beam.Pipeline(options=options) as pipeline:
        # Read events from Pub/Sub using custom timestamps
        raw_tweets = (
            pipeline
            | 'ReadPubSub' >> beam.io.gcp.pubsub.ReadStringsFromPubSub(subscription=args.subscription)
            | 'WriteToGCS' >> WriteToGCS(args.output))

if __name__ == '__main__':
    logging.getLogger().setLevel(logging.INFO)
    run()
