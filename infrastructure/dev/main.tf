module "bigquery" {
    source = "../modules/bigquery"
}

module "gcs" {
    source = "../modules/gcs"
}

module "pubsub" {
    source = "../modules/pubsub"
}
