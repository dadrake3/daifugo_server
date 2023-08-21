terraform {
  backend "s3" {
    bucket = "daifugo_api-terraform-state"
    key    = "terraform.tfstate"
    region = "us-east-1"
  }
}