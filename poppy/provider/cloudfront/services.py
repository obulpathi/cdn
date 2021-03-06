# Copyright (c) 2014 Rackspace, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from boto import cloudfront

from poppy.provider import base


class ServiceController(base.ServiceBase):

    @property
    def client(self):
        return self.driver.client

    def __init__(self, driver):
        super(ServiceController, self).__init__(driver)

        self.driver = driver
        self.current_customer = self.client.get_current_customer()

    def update(self, service_name, service_json):
        return "updated services"

    def create(self, service_name, service_json):
        # TODO(obulpathi): create a single distribution for multiple origins
        distributions = []
        try:
            for origin in service_json['origins']:
                # Create the origins for this domain:
                aws_origin = cloudfront.origin.CustomOrigin(
                    dns_name=origin["origin"],
                    http_port=origin["port"],
                    https_port=origin["ssl"],
                    origin_protocol_policy="match-viewer")
                distribution = self.client.create_distribution(
                    origin=aws_origin,
                    enabled=True)
                distributions.append(distribution)
        except cloudfront.exception.CloudFrontServerError as e:
            return self.responder.failed(str(e))
        except Exception as e:
            return self.responder.failed(str(e))

        return self.responder.created(distributions)

    def delete(self, distribution_id):
        # NOTE(obulpathi): distribution_id is the equivalent of service_name
        try:
            self.client.delete_distribution(distribution_id)

            return self.responder.deleted(distribution_id)
        except Exception as e:
            return self.responder.failed(str(e))
