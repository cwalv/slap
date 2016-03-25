import unittest
from unittest import TestCase
from ags_publishing_tools.api import Api
from mock import MagicMock, PropertyMock, patch


class TesApi(TestCase):
    api = None

    def create_api(self):
        api = Api(
            ags_url='http://myserver/arcgis/admin',
            token_url=None,
            portal_url=None,
            username='user',
            password='pass'
        )
        return api

    def test_token_url_no_portal(self):
        api = Api(
            ags_url='http://myserver/arcgis/admin',
            token_url=None,
            portal_url=None,
            username='user',
            password='pass'
        )
        self.assertEqual(api._token_url, 'http://myserver/arcgis/admin/generateToken')

    def test_token_url_with_portal(self):
        api = Api(
            ags_url='http://myserver/arcgis/admin',
            token_url='foo/generateToken',
            portal_url='http://myserver/portal/sharing/rest',
            username='user',
            password='pass'
        )
        self.assertEqual(api._token_url, 'foo/generateToken')

    def test_token(self):
        api = self.create_api()
        api._token = 'my_token_value'
        self.assertEqual(api.token, 'my_token_value')
        api._token = None

    @patch.object(Api, 'get_token')
    def test_get_token(self, mock_get_token):
        mock_get_token.return_value = 'my_new_token_value'
        api = self.create_api()
        token = api.token
        self.assertEqual(token, 'my_new_token_value')

    def post_url_test(self, url, method, *args):
        self.url_test('post', url, method, *args)

    def get_url_test(self, url, method, *args):
        self.url_test('get', url, method, *args)

    def url_test(self, mock_method, url, method, *args):
        with patch('ags_publishing_tools.api.Api.token', new_callable=PropertyMock) as mock_token:
            with patch('ags_publishing_tools.api.Api.' + mock_method) as mock_method:
                mock_token.return_value = 'my_token_value'
                api = self.create_api()
                getattr(api, method)(*args)
                mock_token.assert_called_once_with()
                mock_method.assert_called_once_with(url, {'f': 'json', 'token': 'my_token_value'})

    def test_delete_map_service(self):
        self.post_url_test('http://myserver/arcgis/admin/services/myService.MapServer/delete', 'delete_service', 'myService')

    def test_delete_map_service_with_folder(self):
        self.post_url_test('http://myserver/arcgis/admin/services/myFolder/myService.MapServer/delete',
                           'delete_service', 'myService', 'myFolder')

    def test_get_map_service(self):
        self.get_url_test('http://myserver/arcgis/admin/services/myService.MapServer',
                          'get_service_params', 'myService')

    def test_get_map_service_with_folder(self):
        self.get_url_test('http://myserver/arcgis/admin/services/myFolder/myService.MapServer',
                          'get_service_params', 'myService', 'myFolder')

    def test_get_other_service(self):
        self.get_url_test('http://myserver/arcgis/admin/services/myFolder/myService.ImageServer',
                          'get_service_params', 'myService', 'myFolder', 'ImageServer')

    def edit_test(self, url, method, expected, *args):
        with patch('ags_publishing_tools.api.Api.token', new_callable=PropertyMock) as mock_token:
            with patch('ags_publishing_tools.api.Api.post') as mock_method:
                mock_token.return_value = 'my_token_value'
                api = self.create_api()
                getattr(api, method)(*args)
                mock_token.assert_called_once_with()
                mock_method.assert_called_once_with(url, expected)

    def test_edit_map_service(self):
        self.edit_test('http://myserver/arcgis/admin/services/myService.MapServer/edit', 'edit_service',
                       {'service': '{"foo": "bar"}', 'f': 'json', 'token': 'my_token_value'},
                       'myService', {'foo': 'bar'})

    def test_edit_map_service_with_folder(self):
        self.edit_test('http://myserver/arcgis/admin/services/myFolder/myService.MapServer/edit', 'edit_service',
                      {'service': '{"foo": "bar"}', 'f': 'json', 'token': 'my_token_value'},
                      'myService', {'foo': 'bar'}, 'myFolder')

    def test_edit_other_service(self):
        self.edit_test('http://myserver/arcgis/admin/services/myFolder/myService.ImageServer/edit', 'edit_service',
                       {'service': '{"foo": "bar"}', 'f': 'json', 'token': 'my_token_value'},
                        'myService', {'foo': 'bar'}, 'myFolder',
                        'ImageServer')

if __name__ == '__main__':

    unittest.main()
