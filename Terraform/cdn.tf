module "cdn" {
  source              = "terraform-aws-modules/cloudfront/aws"
  create_distribution = true

  aliases = ["thenapkinnotes.com", "www.thenapkinnotes.com"]

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
        http_port              = 8050
        https_port = 443
        origin_protocol_policy = "http-only"
        origin_ssl_protocols   = ["TLSv1", "TLSv1.1", "TLSv1.2"]
      }
    }
  }

  default_cache_behavior = {
    target_origin_id           = "ec2"
    viewer_protocol_policy     = "allow-all"

    allowed_methods = ["GET", "HEAD", "OPTIONS"]
    cached_methods  = ["GET", "HEAD"]
    compress        = true
    query_string    = true
  }

  viewer_certificate = {
    acm_certificate_arn = "arn:aws:acm:us-east-1:485809471371:certificate/335a6c64-6850-42e5-a424-ee071140e173"
    ssl_support_method  = "sni-only"
  }
}

module "zones" {
  source  = "terraform-aws-modules/route53/aws//modules/zones"
  zones = {
    "thenapkinnotes.com" = {
      comment = "my website"
      tags = {
        Name = "thenapkinnotes.com"
      }
    }
  }
}

module "records" {
  source  = "terraform-aws-modules/route53/aws//modules/records"
  zone_name = "thenapkinnotes.com"
  #  zone_id = local.zone_id

  records = [
    {
      name = ""
      type = "A"
      alias = {
        name    = module.cdn.cloudfront_distribution_domain_name
        zone_id = module.cdn.cloudfront_distribution_hosted_zone_id
      }
    },
    {
      name = "www"
      type = "A"
      alias = {
        name    = module.cdn.cloudfront_distribution_domain_name
        zone_id = module.cdn.cloudfront_distribution_hosted_zone_id
      }
    }
  ]

  depends_on = [module.zones]
}

locals {
  zone_id = module.zones.route53_zone_zone_id["thenapkinnotes.com"]
}