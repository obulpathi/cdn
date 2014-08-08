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
import ddt
import mock


from poppy.provider.cloudfront import services
from tests.unit import base


@ddt.ddt
class TestServices(base.TestCase):

    @mock.patch('poppy.provider.cloudfront.services.ServiceController.client')
    @mock.patch('poppy.provider.cloudfront.driver.CDNProvider')
    @ddt.file_data('data_service.json')
    def test_create(self, service_json, mock_get_client, mock_driver):
        service_name = 'myservice'
        driver = mock_driver()

        # instantiate
        controller = services.ServiceController(driver)

        # ASSERTIONS
        # create_distribution: CloudFrontServerError
        controller.client.create_distribution.side_effect = \
            cloudfront.exception.CloudFrontServerError(
                503, "Service Unavailable")
        resp = controller.create(service_name, service_json)
        self.assertIn('error', resp[driver.provider_name])

        controller.client.reset_mock()
        controller.client.create_distribution.side_effect = None

        # generic exception: Exception
        controller.client.create_distribution.side_effect = \
            Exception('Creating service failed.')
        resp = controller.create(service_name, service_json)
        self.assertIn('error', resp[driver.provider_name])

        controller.client.reset_mock()
        controller.client.create_distribution.side_effect = None

        # finally, a clear run
        resp = controller.create(service_name, service_json)
        self.assertIn('domain', resp[driver.provider_name])

    @mock.patch('poppy.provider.cloudfront.services.ServiceController.client')
    @mock.patch('poppy.provider.cloudfront.driver.CDNProvider')
    @ddt.file_data('data_service.json')
    def test_update(self, mock_get_client, mock_driver, service_json):
        service_name = 'myservice'

        driver = mock_driver()
        controller = services.ServiceController(driver)
        resp = controller.update(service_name, service_json)
        self.assertEquals('updated services', resp)

    @mock.patch('poppy.provider.cloudfront.driver.CDNProvider')
    def test_delete(self, mock_driver):
        service_name = 'myservice'
        driver = mock_driver()

        # instantiate
        controller = services.ServiceController(driver)

        # delete_distribution: Exception
        controller.client.delete_distribution.side_effect = \
            Exception('Creating service failed.')
        resp = controller.delete(service_name)
        self.assertIn('error', resp[driver.provider_name])

        controller.client.reset_mock()
        controller.client.delete_distribution.side_effect = None

        # delete_distribution: Clear run
        resp = controller.delete(service_name)
        self.assertIn('domain', resp[driver.provider_name])

    @mock.patch('poppy.provider.cloudfront.driver.CDNProvider')
    def test_client(self, MockDriver):
        driver = MockDriver()
        controller = services.ServiceController(driver)
        self.assertNotEquals(controller.client(), None)
