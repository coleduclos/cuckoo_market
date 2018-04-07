terraform {
        backend "gcs" {
        bucket  = "cuckoo-market-dev_ops"
        prefix  = "terraform/state"
    }
}

provider "google" {
    project     = "cuckoo-market-dev"
    region      = "us-central1"
}
