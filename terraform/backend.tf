terraform {
  backend "remote" {
    organization = "samliu"

    workspaces {
      name = "stocksense-lambda"
    }
  }
}
