module "cdn" {
  source = "terraform-aws-modules/cloudfront/aws"
  create_distribution = false

  aliases = ["thenapkinnotes.com","www.thenapkinnotes.com"]

  comment             = "Cloudfront distribution for the EC2 hosting the frontend."
  enabled             = true
  is_ipv6_enabled     = true
  price_class         = "PriceClass_100"
  retain_on_delete    = true
  wait_for_deployment = true

  origin = {
    ec2 = {
      domain_name = module.ec2_instance.public_dns
      custom_origin_config = {
        http_port              = 80
        https_port             = 443
        origin_protocol_policy = "match-viewer"
        origin_ssl_protocols   = ["TLSv1", "TLSv1.1", "TLSv1.2"]
      }
    }
  }

  viewer_certificate = {
    acm_certificate_arn = "arn:aws:acm:us-east-1:485809471371:certificate/335a6c64-6850-42e5-a424-ee071140e173"
  }
}