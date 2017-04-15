import unittest
import os
import shutil
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

    def test_InvalidBlogError(self):
        """Raise exceptions when requesting non-existent blogs"""
        with self.assertRaises(self.tr.InvalidBlogError):
            self.tr.set_current_blog_info('/')

    def test_PrivateBlogError(self):
        """Raise exceptions when requesting private blogs (for now...)"""
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

    def test_plain_raid(self):
        """Make sure the raid() method works as intended"""
        folder = 'tmp'
        self.tr.current_blog_info = None
        n = self.tr.num_posts('staff')
        self.tr.raid('staff', 10, n - 11, folder, True)
        self.assertTrue(os.path.exists(folder))    
        shutil.rmtree(folder)
        self.tr.raid('staff', 9999999, n - 11, folder + '/')
        self.assertTrue(os.path.exists(folder))
        shutil.rmtree(folder)

    def test_bad_raid(self):
        """Raise exceptions when bad arguments are given to raid()"""
        self.tr.current_blog_info = None
        n = self.tr.num_posts('staff')
        with self.assertRaises(self.tr.InvalidCountError):
            self.tr.raid('staff', 0)
        with self.assertRaises(self.tr.InvalidStartError):
            self.tr.raid('staff', 1, -1)
        with self.assertRaises(self.tr.InvalidStartError):
            self.tr.raid('staff', 1, n)
        with self.assertRaises(self.tr.InvalidBlogError):
            self.tr.raid('/', 1)
        with self.assertRaises(self.tr.PrivateBlogError):
            self.tr.raid('iikkssiioovvss', 1)

    def test_plain_download(self):
        """Make sure download_image() method works as intended"""
        folder = 'tmp'
        self.tr.download_image('gif.gif', folder,
            'https://upload.wikimedia.org/wikipedia/commons/e/e1/Graph_Laplacian_Diffusion_Example.gif')
        self.assertTrue(os.path.exists(folder))
        shutil.rmtree(folder)
        self.tr.download_image('png.png', folder + '/',
            'https://upload.wikimedia.org/wikipedia/commons/7/70/Example.png')
        self.assertTrue(os.path.exists(folder))
        shutil.rmtree(folder)

    def test_bad_download(self):
        """Raise exeptions when bad arguments are given to download_image()"""
        folder = 'tmp'
        filename = 'lol.png'
        url = 'bad url'
        self.tr.download_image(filename, folder, url)
        self.assertTrue(not os.path.exists(folder + filename))
        shutil.rmtree(folder)

if __name__ == '__main__':
    unittest.main()
