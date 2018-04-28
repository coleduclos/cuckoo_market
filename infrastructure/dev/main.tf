module "bigquery" {
    source = "../modules/bigquery"
}

module "gcs" {
    source = "../modules/gcs"
}

module "pubsub" {
    source = "../modules/pubsub"
}

module "gke" {
    source = "../modules/gke"
    kubernetes_cluster_master_zone = "${var.kubernetes_cluster_master_zone}"
    kubernetes_cluster_default_machine_type = "${var.kubernetes_cluster_default_machine_type}"
}
