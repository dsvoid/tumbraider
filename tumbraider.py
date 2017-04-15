import keys # would-be devs: get your own keys for now and put them in a keys.py
import argparse
import requests
import pytumblr
import re
import os
from PIL import Image
from io import BytesIO


class tumbraider:
    def __init__(self):
        # connect to tumblr API
        self.client = pytumblr.TumblrRestClient(
            keys.consumerKey,       # grab these from your keys.py file
            keys.consumerSecret,
            keys.OAuthKey,
            keys.OAuthSecret
        )
        self.current_blog_info = None

    def raid(self, blog, count, start=0, folder='', verbose=False):
        # set the blog's info once to minimize requests to the tumblr API
        self.set_current_blog_info(blog)

        # handle invalid input
        if count < 1:
            raise self.InvalidCountError(count)
        if start < 0 or start > self.num_posts() - 1:
            raise self.InvalidStartError(start, self.num_posts())

        # correct count if it exceeds number of posts
        if count > self.num_posts() - start:
            count = self.num_posts() - start

        print 'Downloading images in ' + str(count) + ' posts from ' + blog + '.tumblr.com...'
        if verbose and folder != "":
            print 'Saving images to ' + os.path.abspath(folder)

        while count > 0:
            # request posts from tumblr API
            posts = self.request_posts(count, start)

            # iterate over the results of each request
            for post in posts['posts']:
                # look for images specifically
                if 'photos' in post:
                    photoset = enumerate(post['photos'])
                    for index, photo in photoset:
                        # format filename
                        filename = self.format_filename(post, photo, index)
                        if verbose:
                            print filename

                        # download image
                        url = photo['original_size']['url']
                        self.download_image(filename, folder, url)
            # advance for next request
            count -= 20
            start += 20

        print 'Finished downloading images from ' + blog + '.tumblr.com'

    def format_filename(self, post, photo, index):
        # format filename: timestamp, date, summary, photoset index, ext
        filename = str(post['timestamp']) + ' ' + post['date'][:10]

        if post['summary'] != '':
            l = len(post['summary'])
            # strip illegal characters from summary like <>:"/\|?*
            summary = post['summary'][:min(50, l)]
            summary = summary.replace('<', '_')
            summary = summary.replace('>', '_')
            summary = summary.replace(':', '_')
            summary = summary.replace('"', '_')
            summary = summary.replace('/', '_')
            summary = summary.replace('\\','_')
            summary = summary.replace('|', '_')
            summary = summary.replace('?', '_')
            summary = summary.replace('*', '_')
            summary = summary.replace('\n', '')
            filename = filename + ' ' + summary

        if len(post['photos']) > 1:
            sigfigs = len(str(len(post['photos'])))
            filename = filename + ' ' + str(index+1).zfill(sigfigs)

        url = photo['original_size']['url']
        ext = url[url.rfind('.'):]
        filename = filename + ext
        return filename

    def download_image(self, filename, folder, url):
        # raise an exception if the request didn't work out
        try:
            if folder != '':
                if not os.path.exists(folder):
                    os.makedirs(folder)
                if folder[-1] == '/':
                    folder = folder[:-1]
            imgR = requests.get(url)
            imgR.raise_for_status()

            i = Image.open(BytesIO(imgR.content))
            # save non-gifs normally...
            if url[-3:] != 'gif':
                i.save(folder + '/' + filename)
            # ...but save gifs by setting save_all=True to get all their frames
            else:
                i.save(folder + '/' + filename, save_all=True)
        except Exception, ex:
            print 'ERROR: Exception raised when trying to download',
            print url + ' as ' + filename + ' to ' + folder + ':'
            print ex
            pass

    def request_posts(self, count, start, blog=None):
        if blog is None:
            blog = self.get_current_blog_name()
        if blog is None:
            raise self.NoCurrentBlogError()
        if count < 1:
            raise self.InvalidCountError(count)
        if start < 0 or start > self.num_posts(blog) - 1:
            raise self.InvalidStartError(start, self.num_posts(blog))
        # limit count
        posts = self.client.posts(blog,
                api_key = keys.consumerKey,
                offset = start,
                limit = count if count < 20 else 20)
        return posts

    def num_posts(self, blog=None):
        if blog is None:
            blog = self.get_current_blog_name()
        if blog is None:
            raise self.NoCurrentBlogError()
        if blog == self.get_current_blog_name():
            return self.current_blog_info['blog']['posts']
        else:
            return self.client.blog_info(blog)['blog']['posts']

    def set_current_blog_info(self, blog):
        # only update the blog info if it's not going to be identical
        info = self.current_blog_info
        if blog != self.get_current_blog_name():
            info = self.client.blog_info(blog)
        # the 'blog' key only exists if the blog exists
        if 'blog' not in info:
            raise self.InvalidBlogError(blog)
        # not all blogs have a 'type', those that do may be private: do a check
        if 'type' in info['blog'] and info['blog']['type'] == 'private':
            raise self.PrivateBlogError(blog)
        self.current_blog_info = info

    def get_current_blog_name(self):
        if self.current_blog_info is not None and 'blog' in self.current_blog_info:
            return self.current_blog_info['blog']['name']
        else:
            return None

    class InvalidCountError(Exception):
        def __init__(self, count):
            print 'ERROR: invalid number of posts. Expected 1 or more, got ' + str(count)

    class InvalidStartError(Exception):
        def __init__(self, start, num_posts):
            print 'ERROR: invalid starting post number. Expected 0 to ' + str(num_posts-1) + ', got ' + str(start)

    class InvalidBlogError(Exception):
        def __init__(self, blog):
            print 'ERROR: the blog named ' + blog + ' does not exist.'

    class PrivateBlogError(Exception):
        def __init__(self, blog):
            print 'ERROR: the blog named ' + blog + ' is private.'

    class NoCurrentBlogError(Exception):
        def __init__(self):
            print 'ERROR: the current blog wasn\'t set when the method was called.'


if __name__ == '__main__':
    # argument parsing for command-line use
    parser = argparse.ArgumentParser()
    parser.add_argument("blog", help="download images from specified tumblr blog")
    parser.add_argument("-f", "--folder", help="save images to specified folder (program directory by default)")
    parser.add_argument("-s", "--start", help="specify post from blog to start downloading images from (0 by default)", type=int)
    parser.add_argument("-p", "--posts", help="specify number of posts from blog to download images from (unlimited by default)", type=int)
    parser.add_argument("-v", "--verbose", help="verbose output", action="store_true")
    args = parser.parse_args()

    tr = tumbraider()

    # set arguments
    folder = ""
    if args.folder is not None:
        folder = args.folder

    start = 0
    if args.start is not None:
        start = args.start

    count = tr.num_posts(args.blog)
    if args.posts is not None and args.posts < count:
        count = args.posts
    
    # begin raiding the tumb
    tr.raid(args.blog, count, start, folder, args.verbose)

