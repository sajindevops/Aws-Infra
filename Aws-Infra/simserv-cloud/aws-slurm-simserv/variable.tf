variable "AWS_ACCESS_KEY" {
default = "AKIAQFPAJ4CKQMB4AHRP"
}

variable "AWS_SECRET_KEY" {
default = "otwUTksQWOLi25hLSmvDyNFBQb06mZguzaS4Tvs4"
}

variable "AWS_REGION" {
  default = "eu-west-3"
}

variable "AMIS" {
    default = "ami-0cb72d2e599cffbf9"
  }

variable "keyname" {
    default = "Slurm-key-2020"
}

variable "vpc" {
    default = "vpc-03b7e3a3768f9f316"
}

variable "subnet" {
    default = "subnet-07fd3a799b83fa30c"
}
