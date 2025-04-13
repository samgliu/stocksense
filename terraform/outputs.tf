output "scraper_lambda_name" {
  value = aws_lambda_function.scraper_lambda.function_name
}

output "gcs_lambda_name" {
  value = aws_lambda_function.gcs_lambda.function_name
}
