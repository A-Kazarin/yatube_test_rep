from django.test import TestCase, Client


class StaticURLTests(TestCase):
    def test_homepage(self):
        # Создаем экземпляр клиента
        guest_client = Client()
        response = guest_client.get('/')
        self.assertEqual(response.status_code, 200)
