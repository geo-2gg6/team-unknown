import unittest
from app import app

class BasicTests(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_home(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Welcome to the Privacy Protection App', response.data)

    def test_privacy(self):
        response = self.app.get('/privacy')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Privacy Settings', response.data)

    def test_about(self):
        response = self.app.get('/about')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'About This App', response.data)

if __name__ == "__main__":
    unittest.main()
