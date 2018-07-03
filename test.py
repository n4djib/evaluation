from app import app
import unittest

class FlaskTestCase(unittest.TestCase):

    # ensude that flask was setup correctly
    def test_login(self):
        tester = app.test_client(self)
        response = tester.get('/login/')
        self.assertEqual(response.status_code, 200)

    # ensude that the login page loads correctly
    def test_login_page_loads(self):
        tester = app.test_client(self)
        response = tester.get('/login/')
        self.assertTrue(b'Sign In' in response.data)

    # ensude that the login page loads correctly
    def test_correct_login(self):
        tester = app.test_client(self)
        response = tester.get('/login/',
            data=dict(username="nad", password="nad"),
            follow_redirects=True)
        self.assertIn(b'Sign In', response.data)

if __name__ == '__main__':
    unittest.main()
