"""CloudFront CDN Extension for CDN"""

from poppy.provider.cloudfront import driver

# Hoist classes into package namespace
Driver = driver.CDNProvider
