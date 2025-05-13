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
            value     = "default-src 'self'; script-src 'self' 'unsafe-inline' https://*.gstatic.com https://*.google.com https://browser.sentry-cdn.com https://*.jsdelivr.net; connect-src 'self' https://*.googleapis.com https://accounts.google.com https://api.samliu.site wss://api.samliu.site https://sentry.io https://*.sentry.io; img-src 'self' data: https:; style-src 'self' 'unsafe-inline' https://*.googleapis.com https://*.jsdelivr.net; font-src 'self' https://fonts.gstatic.com; frame-src https://accounts.google.com https://*.firebaseapp.com; object-src 'none'; base-uri 'self'; form-action 'self';"
          }
        }
      }
    }
  ]
}
