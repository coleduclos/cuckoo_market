data "google_project" "project" {}

resource "google_storage_bucket" "data_lake_bucket" {
    name     = "${data.google_project.project.name}_data_lake_bucket"
}
