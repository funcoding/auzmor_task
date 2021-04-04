import base64

from rest_framework import status
from rest_framework.test import APIRequestFactory, APITestCase
from rest_framework.test import APIClient
from requests.auth import HTTPBasicAuth
from django.core.cache import cache



# Create your tests here.
from account.models import Account
from phone_number.models import PhoneNumber


class InboundSmsTests(APITestCase):
    def setUp(self) -> None:
        self.url = '/api/inbound/sms'
        self.account = Account.objects.first()
        self.phone_number = PhoneNumber.objects.filter(account_id=self.account.id)
        self.encoded_credentials = base64.b64encode(f"{self.account.username}:{self.account.auth_id}".encode()).decode()

    def set_auth(self):
        self.client.defaults['HTTP_AUTHORIZATION'] = self.encoded_credentials

    def test_without_auth(self):
        response = self.client.get(self.url, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_success(self):
        self.set_auth()
        response = self.client.post(self.url, format='json', data={
            "from": self.phone_number[0].number,
            "to": self.phone_number[1].number,
            "text": "testing",
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'inbound sms ok')

    def test_form_error(self):
        self.set_auth()
        response = self.client.post(self.url, format='json', data={})
        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)
        self.assertEqual(len(response.data['error']), 3)

        response = self.client.post(self.url, format='json', data={
            "from": self.phone_number[0].number,
            "text": "testing",
        })
        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)
        self.assertEqual(len(response.data['error']), 1)

    def test_stored_in_cache(self):
        self.set_auth()
        response = self.client.post(self.url, format='json', data={
            "from": self.phone_number[0].number,
            "to": self.phone_number[1].number,
            "text": "STOP\r\n",
        })

        cached_record = cache.get(f"{self.account.id}_{self.phone_number[0].number}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'inbound sms ok')
        self.assertNotEqual(cached_record, None)


class OutboundSmsTests(APITestCase):
    def setUp(self) -> None:
        self.url = '/api/outbound/sms'
        self.account = Account.objects.first()
        self.phone_number = PhoneNumber.objects.filter(account_id=self.account.id)
        self.encoded_credentials = base64.b64encode(f"{self.account.username}:{self.account.auth_id}".encode()).decode()

    def tearDown(self) -> None:
        cache.delete(f"{self.account.id}_{self.phone_number[0].number}")

    def set_auth(self):
        self.client.defaults['HTTP_AUTHORIZATION'] = self.encoded_credentials

    def test_without_auth(self):
        response = self.client.get(self.url, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_success(self):
        self.set_auth()
        response = self.client.post(self.url, format='json', data={
            "from": self.phone_number[0].number,
            "to": self.phone_number[1].number,
            "text": "testing",
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'outbound sms ok')
        cached_record = cache.get(f"{self.account.id}_{self.phone_number[0].number}")
        self.assertEqual(cached_record, None)

    def test_form_error(self):
        self.set_auth()
        response = self.client.post(self.url, format='json', data={})
        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)
        self.assertEqual(len(response.data['error']), 3)

        response = self.client.post(self.url, format='json', data={
            "from": self.phone_number[0].number,
            "text": "testing",
        })
        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)
        self.assertEqual(len(response.data['error']), 1)

    # def test_stored_in_cache(self):
    #     self.set_auth()
    #     response = self.client.post(self.url, format='json', data={
    #         "from": self.phone_number[0].number,
    #         "to": self.phone_number[1].number,
    #         "text": "STOP\r\n",
    #     })
    #
    #     cached_record = cache.get(f"{self.account.id}_{self.phone_number[0].number}")
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     self.assertEqual(response.data['message'], 'outbound sms ok')
    #     self.assertNotEqual(cached_record, None)
