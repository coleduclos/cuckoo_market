data "google_project" "project" {}

resource "google_pubsub_topic" "twitter_stream_topic" {
    name = "${data.google_project.project.name}_twitter_stream_topic"
}

resource "google_pubsub_subscription" "twitter_stream_bigquery_subscription" {
    name  = "${data.google_project.project.name}_twitter_stream_bigquery_subscription"
    topic = "${google_pubsub_topic.twitter_stream_topic.name}"
}

resource "google_pubsub_subscription" "twitter_stream_gcs_subscription" {
    name  = "${data.google_project.project.name}_twitter_stream_gcs_subscription"
    topic = "${google_pubsub_topic.twitter_stream_topic.name}"
}
