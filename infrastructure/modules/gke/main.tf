data "google_project" "project" {}

resource "google_container_cluster" "kubernetes_cluster" {
    name     = "${data.google_project.project.name}-kubernetes-cluster"
    zone     = "${var.kubernetes_cluster_master_zone}"
    initial_node_count = 1
    node_config {
        preemptible  = true
        machine_type = "${var.kubernetes_cluster_default_machine_type}"
        oauth_scopes = [
            "https://www.googleapis.com/auth/cloud-platform"
        ]
        service_account = "${var.kubernetes_cluster_default_service_account}"
    }
}

resource "google_container_node_pool" "kubernetes_node_pool" {
    name       = "${data.google_project.project.name}-primary-node-pool"
    zone       = "${var.kubernetes_cluster_master_zone}"
    cluster    = "${google_container_cluster.kubernetes_cluster.name}"
    autoscaling {
        min_node_count = 0
        max_node_count = 3
    }
    node_config {
        preemptible  = true
        machine_type = "${var.kubernetes_cluster_default_machine_type}"
        oauth_scopes = [
            "https://www.googleapis.com/auth/cloud-platform"
        ]
        service_account = "${var.kubernetes_cluster_default_service_account}"
    }
}
