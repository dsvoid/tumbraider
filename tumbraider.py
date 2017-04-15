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

    def raid(self, blog, count, folder="", start=0, verbose=False):
        if count < 1:
            raise self.InvalidCountError(count)
        print 'Downloading images in ' + str(count) + ' posts from ' + args.blog + '.tumblr.com...'

        if verbose and folder != "":
            print 'Saving images to ' + os.path.abspath(folder)

        while count > 0:
            # request posts from tumblr API
            posts = self.request_posts(blog, count, start)

            # iterate over the results of each request
            for post in posts['posts']:
                # look for images specifically
                if 'photos' in post:
                    photoset = enumerate(post['photos'])
                    for index, photo in photoset:
                        # format filename
                        filename = self.format_filename(post, photo, index)
                        if verbose:
                            print filename,

                        # download image
                        url = photo['original_size']['url']
                        success = True
                        try:
                            self.download_image(filename, folder, url)
                        except Exception, ex:
                            success = False
                            if verbose:
                                print 'ERROR'
                            print 'Exception raised when trying to download ' + url + ' as ' + filename + ':'
                            print ex
                        else:
                            if verbose:
                                print 'OK'
            # advance for next request
            count -= 20
            start += 20

        print 'Finished downloading images from ' + args.blog + '.tumblr.com'

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
        if folder != '':
            if not os.path.exists(folder):
                os.makedirs(folder)
            if folder[-1] == '/':
                folder = folder[:-1]
        imgR = requests.get(url)
        # raise an exception if the request didn't work out
        imgR.raise_for_status()

        i = Image.open(BytesIO(imgR.content))
        # save non-gifs normally...
        if url[-3:] != 'gif':
            i.save(folder + '/' + filename)
        # ...but save gifs by setting save_all=True to get all their frames
        else:
            i.save(folder + '/' + filename, save_all=True)

    def request_posts(self, blog, count, start):
        if count < 1:
            raise self.InvalidCountError(count)
        if start < 0 or start > self.num_posts(blog) - 1:
            raise self.InvalidStartError(start, self.num_posts(blog))
        posts = self.client.posts(blog,
                api_key = keys.consumerKey,
                offset = start,
                limit = count if count < 20 else 20)
        return posts

    def num_posts(self, blog):
        info = self.client.blog_info(blog)
        count = info['blog']['posts']
        return count

    class InvalidCountError(Exception):
        def __init__(self, count):
            print 'ERROR: invalid number of posts. Expected 1 or more, got ' + str(count)

    class InvalidStartError(Exception):
        def __init__(self, start, num_posts):
            print 'ERROR: invalid starting post number. Expected 0 to ' + str(num_posts-1) + ', got ' + str(start)

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
    tr.raid(args.blog, count, folder, start, args.verbose)

