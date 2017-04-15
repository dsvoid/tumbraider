import unittest
from tumbraider import tumbraider

class TumbRaiderTests(unittest.TestCase):
    """Tests for tumbraider.py"""

    def test_plain_request(self):
        """Make sure the plain request_posts method works"""
        tr = tumbraider()
        blog = 'staff'
        posts = tr.request_posts(blog, 5, tr.num_posts(blog) - 5)
        self.assertTrue(len(posts['posts']) == 5)

    def test_invalid_requests(self):
        """Raise exceptions when a bad start or count is specified"""
        tr = tumbraider()
        blog = 'staff'
        with self.assertRaises(tr.InvalidCountError):
            tr.request_posts(blog, 0, 0)
        with self.assertRaises(tr.InvalidCountError):
            tr.request_posts(blog, -1, 0)
        with self.assertRaises(tr.InvalidStartError):
            tr.request_posts(blog, 1, -1)
        with self.assertRaises(tr.InvalidStartError):
            tr.request_posts(blog, 1, tr.num_posts(blog))
        with self.assertRaises(tr.InvalidStartError):
            tr.request_posts(blog, 1, tr.num_posts(blog) + 1)

if __name__ == '__main__':
    unittest.main()

