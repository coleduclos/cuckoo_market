data "google_project" "project" {}

resource "google_container_cluster" "kubernetes_cluster" {
    name     = "${data.google_project.project.name}-kubernetes-cluster"
    zone     = "${var.kubernetes_cluster_master_zone}"
    initial_node_count = 1
}

resource "google_container_node_pool" "default_node_pool" {
    name       = "${data.google_project.project.name}-default-node-pool"
    zone       = "us-central1-a"
    cluster    = "${google_container_cluster.kubernetes_cluster.name}"

    node_config {
        preemptible  = true
        machine_type = "${var.kubernetes_cluster_default_machine_type}"
        oauth_scopes = [
            "https://www.googleapis.com/auth/compute",
            "https://www.googleapis.com/auth/devstorage.read_only",
            "https://www.googleapis.com/auth/logging.write",
            "https://www.googleapis.com/auth/monitoring"
        ]
    }
    autoscaling {
        min_node_count = 0
        max_node_count = 1
    }

    management {
        auto_repair = true
        auto_upgrade = true
    }
}
