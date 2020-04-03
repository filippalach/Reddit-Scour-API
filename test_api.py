import unittest
import requests
import random

JWT = ''

class TestAPI(unittest.TestCase):
    def _auth(self):
        headers = {
            'accept': 'application/json',
            'Authorization': f'Bearer {self.JWT}'
        }
        return headers

    @classmethod
    def setUpClass(cls):
        r = requests.get('http://0.0.0.0:1129/api/v1/auth/1')
        cls.JWT = r.json()['jwt']

    #/auth
    def test_auth(self):
        r = requests.get('http://0.0.0.0:1129/api/v1/auth/12')
        self.assertEqual(r.status_code, 200)
        self.assertIn('jwt', r.json())

    def test_auth_no_path(self):
        r = requests.get('http://0.0.0.0:1129/api/v1/auth')
        self.assertEqual(r.status_code, 404)
        err = r.json()['title']
        self.assertIn('Not Found', err)


    #/secret
    def test_secret(self):
        r = requests.get('http://0.0.0.0:1129/api/v1/secret', headers=self._auth())
        self.assertEqual(r.status_code, 200)

    def test_secret_no_auth(self):
        r = requests.get('http://0.0.0.0:1129/api/v1/secret')
        self.assertEqual(r.status_code, 401)
        self.assertIsInstance(r.json(), dict)
        self.assertIn('No authorization token provided', r.json()['detail'])        


    #/subscribers
    def test_subscribers(self):
        r = requests.get('http://0.0.0.0:1129/api/v1/subscribers?subreddit=formula1')
        self.assertEqual(r.status_code, 200)
        self.assertIn('subscribers', r.json())

    def test_subscribers_no_param(self):
        r = requests.get('http://0.0.0.0:1129/api/v1/subscribers')
        self.assertEqual(r.status_code, 400)
        err = r.json()['title']
        self.assertIn('Bad Request', err)

    def test_subscribers_wrong_subreddit(self):
        r = requests.get('http://0.0.0.0:1129/api/v1/subscribers?subreddit=notexistenenent')
        self.assertEqual(r.status_code, 404)
        self.assertIn('not found', r.text)
        self.assertIn('error', r.json())

    
    #/picture
    def test_picture(self):
        r = requests.get('http://0.0.0.0:1129/api/v1/picture?post_id=f46jgn')
        self.assertEqual(r.status_code, 200)
        self.assertIn('url', r.json())

    def test_picture_no_param(self):
        r = requests.get('http://0.0.0.0:1129/api/v1/picture')
        self.assertEqual(r.status_code, 400)
        err = r.json()['title']
        self.assertIn('Bad Request', err)

    def test_picture_wrong_subreddit(self):
        r = requests.get('http://0.0.0.0:1129/api/v1/picture?post_id=f46jgnasasasasas')
        self.assertEqual(r.status_code, 404)
        self.assertIn('not found', r.text)
        self.assertIn('error', r.json())

    
    #/retrieve_posts
    def test_retrieve_posts(self):
        r = requests.get('http://0.0.0.0:1129/api/v1/retrieve_posts/subreddit/formula1?number=20')
        self.assertEqual(r.status_code, 200)
        self.assertIn('0', r.json())
        self.assertIn('19', r.json())
        self.assertIsInstance(r.json(), dict)

    def test_retrieve_posts_no_param(self):
        r = requests.get('http://0.0.0.0:1129/api/v1/retrieve_posts/subreddit/formula1')
        self.assertEqual(r.status_code, 400)
        err = r.json()['title']
        self.assertIn('Bad Request', err)

    def test_retrieve_posts_no_path(self):
        r = requests.get('http://0.0.0.0:1129/api/v1/retrieve_posts/subreddit')
        self.assertEqual(r.status_code, 404)
        err = r.json()['title']
        self.assertIn('Not Found', err)

    def test_retrieve_posts_wrong_subreddit(self):
        r = requests.get('http://0.0.0.0:1129/api/v1/retrieve_posts/subreddit/formulalalal1formula1?number=20')
        self.assertEqual(r.status_code, 404)
        self.assertIn('not found', r.text)
        self.assertIn('error', r.json())

    def test_retrieve_posts_wrong_number(self):
        r = requests.get('http://0.0.0.0:1129/api/v1/retrieve_posts/subreddit/formula1?number=nan')
        self.assertEqual(r.status_code, 400)
        err = r.json()['title']
        self.assertIn('Bad Request', err)


    #/find_subreddit
    def test_find_subreddit(self):
        r = requests.get('http://0.0.0.0:1129/api/v1/find/subreddit/formula1/?phrase=it')
        self.assertEqual(r.status_code, 200)
        self.assertIsInstance(r.json(), dict)
        self.assertIn('id', r.json())
        self.assertIn('title', r.json())
        self.assertIn('url', r.json())

    def test_find_subreddit_no_param(self):
        r = requests.get('http://0.0.0.0:1129/api/v1/find/subreddit/formula1')
        self.assertEqual(r.status_code, 400)
        err = r.json()['title']
        self.assertIn('Bad Request', err)

    def test_find_subreddit_no_path(self):
        r = requests.get('http://0.0.0.0:1129/api/v1/find/subreddit')
        self.assertEqual(r.status_code, 404)
        err = r.json()['title']
        self.assertIn('Not Found', err)

    def test_find_subreddit_wrong_subreddit(self):
        r = requests.get('http://0.0.0.0:1129/api/v1/find/subreddit/fortexistanet')
        self.assertEqual(r.status_code, 400)


    #/find_post
    def test_find_post(self):
        r = requests.get('http://0.0.0.0:1129/api/v1/find/post/f48ce1/?phrase=it')
        self.assertEqual(r.status_code, 200)
        self.assertIsInstance(r.json(), int)
            
    def test_find_post_no_param(self):
        r = requests.get('http://0.0.0.0:1129/api/v1/find/post/f48ce1/')
        self.assertEqual(r.status_code, 400)
        err = r.json()['title']
        self.assertIn('Bad Request', err)

    def test_find_post_no_path(self):
        r = requests.get('http://0.0.0.0:1129/api/v1/find/post/')
        self.assertEqual(r.status_code, 404)
        err = r.json()['title']
        self.assertIn('Not Found', err)


    #/drivers
    def test_drivers(self):
        r = requests.get('http://0.0.0.0:1129/api/v1/drivers')
        self.assertEqual(r.status_code, 200)
        self.assertIsInstance(r.json(), dict)
        self.assertIn('vet', r.json())

    
    #/drivers/driver_id flow
    def test_drivers_new_instance_update_instance(self):
        rand_int = str(random.randint(0,1000)) 

        r = requests.put(f'http://0.0.0.0:1129/api/v1/drivers/{rand_int}')
        self.assertEqual(r.status_code, 201)

        r = requests.put(f'http://0.0.0.0:1129/api/v1/drivers/{rand_int}')
        self.assertEqual(r.status_code, 200)

        r = requests.get(f'http://0.0.0.0:1129/api/v1/drivers/{rand_int}')
        self.assertEqual(r.status_code, 200)

        r = requests.delete(f'http://0.0.0.0:1129/api/v1/drivers/{rand_int}')
        self.assertEqual(r.status_code, 204)

        r = requests.delete(f'http://0.0.0.0:1129/api/v1/drivers/{rand_int}')
        self.assertEqual(r.status_code, 404)

        








if __name__ == '__main__':
    unittest.main()