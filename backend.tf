terraform {
  backend "s3" {
    bucket = "${var.prefix}-terraform-state"
    key    = "terraform.tfstate"
    region = "${var.region}"
  }
}