import unittest
from tumbraider import tumbraider

class TumbRaiderTests(unittest.TestCase):
    """Tests for tumbraider.py"""

    def __init__(self, *args, **kwargs):
        super(TumbRaiderTests, self).__init__(*args, **kwargs)
        self.tr = tumbraider()

    def test_plain_requests(self):
        """Make sure request_posts() and set_current_blog_info() work"""
        self.tr.set_current_blog_info('staff')
        self.assertTrue(self.tr.current_blog_info['blog']['name'] == 'staff')
        posts = self.tr.request_posts(5, self.tr.num_posts() - 5)
        self.assertTrue(len(posts['posts']) == 5)

    def test_BlogErrors(self):
        """Raise exceptions when requesting private or non-existent blogs"""
        # blogs must exist
        with self.assertRaises(self.tr.InvalidBlogError):
            self.tr.set_current_blog_info('/')
        # blogs cannot be private (for now...)
        with self.assertRaises(self.tr.PrivateBlogError):
            # note: this blog is empty and I only made it for this test
            self.tr.set_current_blog_info('iikkssiioovvss')

    def test_InvalidCountError(self):
        """Raise exceptions when count is invalid for request_posts()"""
        self.tr.set_current_blog_info('staff')
        # count must be > 0
        with self.assertRaises(self.tr.InvalidCountError):
            self.tr.request_posts(0, 0)
        with self.assertRaises(self.tr.InvalidCountError):
            self.tr.request_posts(-1, 0)

    def test_InvalidStartError(self):
        """Raise exceptions when start is invalid for request_posts()"""
        self.tr.set_current_blog_info('staff')
        # start must be between 0 and num_posts() - 1, inclusive.
        with self.assertRaises(self.tr.InvalidStartError):
            self.tr.request_posts(1, -1)
        with self.assertRaises(self.tr.InvalidStartError):
            self.tr.request_posts(1, self.tr.num_posts())
        with self.assertRaises(self.tr.InvalidStartError):
            self.tr.request_posts(1, self.tr.num_posts() + 1)

    def test_NoCurrentBlogError(self):
        """Raise exceptions when current_blog_info is needed but isn't there"""
        self.tr.current_blog_info = None
        with self.assertRaises(self.tr.NoCurrentBlogError):
            self.tr.request_posts(1,1)
        with self.assertRaises(self.tr.NoCurrentBlogError):
            self.tr.num_posts()

if __name__ == '__main__':
    unittest.main()

