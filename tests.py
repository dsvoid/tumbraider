import unittest
from tumbraider import tumbraider

class TumbRaiderTests(unittest.TestCase):
    """Tests for tumbraider.py"""

    def test_plain_requests(self):
        """Make sure request_posts and set_current_blog_info methods work"""
        tr = tumbraider()
        tr.set_current_blog_info('staff')
        self.assertTrue(tr.current_blog_info['blog']['name'] == 'staff')
        posts = tr.request_posts(5, tr.num_posts() - 5)
        self.assertTrue(len(posts['posts']) == 5)

    def test_invalid_requests(self):
        """Raise exceptions when a bad start or count is specified"""
        tr = tumbraider()
        # blogs must exist and cannot be private (for now...)
        with self.assertRaises(tr.InvalidBlogError):
            tr.set_current_blog_info('/')
        with self.assertRaises(tr.PrivateBlogError):
            # note: this blog is empty and I only made it for this test
            tr.set_current_blog_info('iikkssiioovvss')

        tr.set_current_blog_info('staff')
        # count must be > 0
        with self.assertRaises(tr.InvalidCountError):
            tr.request_posts(0, 0)
        with self.assertRaises(tr.InvalidCountError):

        # start must be between 0 and num_posts() - 1, inclusive.
            tr.request_posts(-1, 0)
        with self.assertRaises(tr.InvalidStartError):
            tr.request_posts(1, -1)
        with self.assertRaises(tr.InvalidStartError):
            tr.request_posts(1, tr.num_posts())
        with self.assertRaises(tr.InvalidStartError):
            tr.request_posts(1, tr.num_posts() + 1)

if __name__ == '__main__':
    unittest.main()

