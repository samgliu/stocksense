resource "cloudflare_ruleset" "set_csp_header" {
  zone_id     = var.cloudflare_zone_id
  name        = "Add CSP Header"
  description = "Set Content-Security-Policy header for all responses"
  kind        = "zone"
  phase       = "http_response_headers_transform"

  rules = [
    {
      action      = "rewrite"
      expression  = "true"
      enabled     = true
      description = "Add CSP header"
      action_parameters = {
        headers = {
          "Content-Security-Policy" = {
            operation = "set"
            value     = "default-src 'self'; script-src 'self' https://www.gstatic.com https://apis.google.com https://accounts.google.com https://browser.sentry-cdn.com; connect-src 'self' https://*.googleapis.com https://accounts.google.com https://api.samliu.site wss://api.samliu.site https://sentry.io https://*.sentry.io; img-src 'self' data: https://www.gstatic.com https://lh3.googleusercontent.com https://sentry.io; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src 'self' https://fonts.gstatic.com; frame-src https://accounts.google.com; object-src 'none'; base-uri 'self'; form-action 'self';"
          }
        }
      }
    }
  ]
}
