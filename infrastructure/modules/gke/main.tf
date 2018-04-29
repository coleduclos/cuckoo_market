data "google_project" "project" {}

resource "google_container_cluster" "kubernetes_cluster" {
    name     = "${data.google_project.project.name}-kubernetes-cluster"
    zone     = "${var.kubernetes_cluster_master_zone}"
    initial_node_count = 1
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
}
