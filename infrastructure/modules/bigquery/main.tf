data "google_project" "project" {}

resource "google_bigquery_dataset" "twitter_dataset" {
    dataset_id  = "twitter_dataset"
}
