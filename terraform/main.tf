terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "7.30.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.storage_location
}

resource "google_storage_bucket" "demo_marc" {
  name                        = var.gcs_bucket_name
  location                    = var.storage_location
  uniform_bucket_level_access = true
  force_destroy               = true

  lifecycle_rule {
    condition {
      age = 3
    }
    action {
      type = "Delete"
    }
  }
}

resource "google_bigquery_dataset" "demo_dataset" {
  dataset_id = var.bq_dataset_name
  project    = var.project_id
  location   = var.storage_location
}