variable "storage_location" {
  description = "Location for GCS bucket and BigQuery dataset"
  default     = "EUROPE-WEST1"
}

variable "bq_dataset_name" {
  description = "Name of the BigQuery dataset"
  default     = "my_bq_dataset"
}

variable "gcs_bucket_name" {
  description = "Name of the GCS bucket"
  default     = "pure-highlander-495016-t1-bucket-mv"
}

variable "gcs_storage_class" {
  description = "Storage class for the GCS bucket"
  default     = "STANDARD"
}

variable "project_id" {
  description = "GCP project ID"
  default     = "pure-highlander-495016-t1"
}