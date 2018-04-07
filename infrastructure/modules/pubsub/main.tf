data "google_project" "project" {}

resource "google_pubsub_topic" "twitter_stream_topic" {
    name = "${data.google_project.project.name}_twitter_stream_topic"
}
