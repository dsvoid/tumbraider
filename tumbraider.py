import keys # would-be devs: get your own keys for now and put them in a keys.py
import argparse
from argparse import RawTextHelpFormatter
import time
import datetime
import requests
import pytumblr
import calendar
import re
import os
import json
from pprint import pprint
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
        self.filename_format = '$d - $b - $s'

    def raid(self, blog, count, start=0, folder='', filename_format=None,
             metadata=False, videos=False, verbose=False,
             after=None, before=None):

        # set the blog's info once to minimize requests to the tumblr API
        self.set_current_blog_info(blog)

        if folder != '' and folder[-1] != '/':
            folder = folder + '/'

        json_data = None
        if metadata:
            json_data = self.current_blog_info
            json_data['downloads'] = []

        if filename_format is not None:
            self.set_filename_format(filename_format)

        # handle invalid count and start input
        if count < 1:
            raise self.InvalidCountError(count)
        if start < 0 or start > self.num_posts() - 1:
            raise self.InvalidStartError(start, self.num_posts())

        # correct count if it exceeds number of posts
        if count > self.num_posts() - start:
            count = self.num_posts() - start

        # parse date inputs for 'before' and 'after' arguments
        if after is not None:
            after = self.parse_date(after, 'after')
        if before is not None:
            before = self.parse_date(before, 'before')
        if before is not None and after is not None:
            if before[0] < after[0]:
                raise self.DateMismatchError()
            elif before[0] == after[0]:
                if before[1] < after[1]:
                    raise self.DateMismatchError()
                elif before[1] == after[1]:
                    if before[2] < after[2]:
                        raise self.DateMismatchError()

        # determine which post to start with if 'before' is specified,
        # change count if necessary
        if before is not None:
            new_start = self.binary_search(start, count, before)
            count = count - (new_start - start)
            start = new_start
            print [start,count]

        print 'Downloading images in ' + str(count) + ' posts from ' + blog + '.tumblr.com...'
        if verbose and folder != "":
            print 'Saving images to ' + os.path.abspath(folder)

        within_date = True
        while count > 0 and within_date:
            # request posts from tumblr API
            posts = self.request_posts(count, start)

            # iterate over the results of each request
            for post in posts['posts']:
                if after is not None:
                    post_date = post['date']
                    y = int(post_date[2:4])
                    m = int(post_date[5:7])
                    d = int(post_date[8:10])
                    if y < after[0]:
                        within_date = False
                    elif y == after[0]:
                        if m < after[1]:
                            within_date = False
                        elif m == after[1]:
                            if d <= after[2]:
                                within_date = False
                if within_date:
                    # look for images
                    if 'photos' in post:
                        photoset = enumerate(post['photos'])
                        for index, photo in photoset:
                            # format filename
                            filename = self.format_image_filename(post, photo, index)
                            if verbose:
                                print filename
                            # download image
                            url = photo['original_size']['url']
                            self.download_file(filename, folder, url)
                            if metadata:
                                json_data['downloads']+=[{filename:post}]
                    # look for videos
                    if videos and 'player' in post and type(post['player'][0]) is dict:
                        embed_code = post['player'][0]['embed_code']
                        src_index = embed_code.find('<source src="') + 13
                        if src_index != 12:
                            filename = self.format_video_filename(post)
                            if verbose:
                                print filename
                            # download video
                            url = embed_code[src_index:embed_code.find('"', src_index)]
                            self.download_file(filename, folder, url)
                            if metadata:
                                json_data['downloads']+=[{filename:post}]
                    # look for images in text posts
                    if post['type'] == 'text':
                        content = str(post['reblog'])
                        imgIndices = [match.start() for match in re.finditer('img src="', content)]
                        for i in range(len(imgIndices)):
                            imgIndices[i] += 9
                            url = content[imgIndices[i]:content.find('"',imgIndices[i])]
                            if url.find('media.tumblr.com') != -1:
                                underscore = url.rfind('_')
                                period = url.rfind('.')
                                url = url[:underscore+1] + '1280' + url[period:]
                            filename = self.format_txtimg_filename(post, i, len(imgIndices), url)
                            if verbose:
                                print filename
                            self.download_file(filename, folder, url)
                            if metadata:
                                json_data['downloads']+=[{filename:post}]

            # advance for next request
            count -= 20
            start += 20
        
        if metadata:
            m_filename = 'tumbraider ' + time.strftime('%Y-%m-%d %H-%M-%S') + '.json'
            with open(folder + m_filename, 'w') as outfile:
                json.dump(json_data, outfile, indent=2)
            if verbose:
                print 'Wrote download metadata to ' + folder + m_filename

        print 'Finished downloading images from ' + blog + '.tumblr.com'

    def parse_date(self, date, marker):
        date = date.split('-')
        if len(date) != 3:
            raise self.InvalidDateError(marker)
        for i in range(len(date)):
            if len(date[i]) > 2:
                raise self.InvalidDateError(marker)
            date[i] = int(date[i])
        if date[1] > 12:
            date[1] = 12
        if date[1] < 1:
            date[1] = 1
        if date[1] == 2:
            if calendar.isleap(2000 + date[0]) and date[2] > 29:
                date[2] = 29
            elif date[2] > 28:
                date[2] = 28
        elif date[1] in [1, 3, 5, 7, 8, 10, 12] and date[2] > 31:
            date[2] = 31
        elif date[2] > 30:
            date[2] = 30
        if date[2] < 1:
            date[2] = 1
        return date

    def binary_search(self, start, count, before):
        s = start
        c = count + start - 1
        m = None
        while c > s :
            m = c//2 + s
            post_date = self.request_posts(1, m)['posts'][0]['date']
            year = int(post_date[2:4])
            month = int(post_date[5:7])
            day = int(post_date[8:10])
            if year == before[0]:
                if month == before[1]:
                    if day == before[2]:
                        return m
                    elif day > before[2]:
                        s = m + 1
                    else:
                        c = m - s
                elif month > before[1]:
                    s = m + 1
                else:
                    c = m - s
            elif year > before[0]:
                s = m + 1
            else:
                c = m - s
        return m

    def set_filename_format(self, filename_format):
        self.filename_format = filename_format

    def format_image_filename(self, post, photo, index):
        filename = self.format_base_filename(post)

        if len(post['photos']) > 1:
            sigfigs = len(str(len(post['photos'])))
            filename = filename + ' ' + str(index+1).zfill(sigfigs)

        url = photo['original_size']['url']
        ext = url[url.rfind('.'):]
        filename = filename + ext
        return filename

    def format_video_filename(self, post):
        filename = self.format_base_filename(post) + '.mp4'
        return filename

    def format_txtimg_filename(self, post, index, length, url):
        filename = self.format_base_filename(post)
        if length > 1:
            sigfigs = len(str(length))
            filename = filename + ' ' + str(index+1).zfill(sigfigs)
        ext = url[url.rfind('.'):]
        filename = filename + ext
        return filename

    def format_base_filename(self, post):
        # find instances of '$' in the filename_format
        filename = self.filename_format
        indices = [match.start() for match in re.finditer('\$', filename[:-1])]
        l = len(post['summary'])
        replacement_dict = {
            'b' : post['blog_name'],
            'c' : post['caption'] if 'caption' in post else '[no caption]',
            'd' : post['date'][:-4],
            'i' : str(post['id']),
            'n' : str(post['note_count']),
            's' : post['summary'][:min(50, l)],
            't' : ' '.join(post['tags']) if len(post['tags']) > 0 else '[no tags]',
            'T' : post['title'] if 'title' in post else '[no title]',
            'u' : post['post_url']
        }
        # iterate over those instances until none are left to process
        while indices != []:
            replacement = ''
            code = filename[indices[0]+1]
            if code in replacement_dict:
                replacement = replacement_dict[code]
                if indices[0]+2 == len(filename):
                    filename = filename[:indices[0]] + replacement
                else:
                    filename = filename[:indices[0]] + replacement + filename[indices[0]+2:]
                for i in range(len(indices)):
                    indices[i] += len(replacement) - 2
            if len(indices) == 1:
                indices = []
            else:
                indices = indices[1:]

        # strip illegal characters from filename like <>:"/\|?*
        bad_chars = [match.start() for match in re.finditer('[<>:"/\\|?*]', filename)]
        filename = list(filename)
        for i in range(len(bad_chars)):
            filename[bad_chars[i]] = '_'
        filename = ''.join(filename)
        # strip excessive whitespace
        filename = filename.replace('\n','')
        filename = filename.replace('\r','')
        filename = filename.replace('\t','')
        filename = ' '.join(filename.split())
        return filename
        
    def download_file(self, filename, folder, url):
        # raise an exception if the request didn't work out
        try:
            if folder != '':
                if not os.path.exists(folder):
                    os.makedirs(folder)
                if folder[-1] != '/':
                    folder = folder + '/'
            r = requests.get(url)
            r.raise_for_status()
            with open(folder + filename, 'wb') as f:
                for chunk in r.iter_content(1024):
                    f.write(chunk)
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

    class InvalidDateError(Exception):
        def __init__(self, marker):
            print "ERROR: invalid '" + marker + "' date specified, expected yy-mm-dd format"
    
    class DateMismatchError(Exception):
        def __init__(self):
            print "ERROR: 'before' date should not be before 'after' date"


if __name__ == '__main__':
    # argument parsing for command-line use
    parser = argparse.ArgumentParser(formatter_class=RawTextHelpFormatter)
    parser.add_argument("blog", help="download images from specified tumblr blog")
    parser.add_argument("-a", "--after", help="""save files after a certain datei (in yy-mm-dd format)""")
    parser.add_argument("-b", "--before", help="""save images before a certain date (in yy-mm-dd format)""")
    parser.add_argument("-f", "--folder", help="""save images to specified folder
(program directory by default)""")
    parser.add_argument("-F", "--format", help="""use a format for filenames ('$d - $b - $s' by default)
    USEFUL CODES:
    $b : blog name
    $c : caption of blog post
    $d : date and time of blog post
    $i : id of blog post
    (as in [blog name].tumblr.com/post/[id of post])
    $n : number of notes in blog post
    $s : summary of blog post
    $t : blog post's tags
    $T : blog post's title
    $u : blog post's URL""",
    type=str)
    parser.add_argument("-m", "--metadata", help="""Save downloaded metadata to a JSON file""", action="store_true")
    parser.add_argument("-p", "--posts", help="""specify number of posts from blog to download from
(unlimited by default)""", type=int)
    parser.add_argument("-s", "--start", help="""specify post from blog to start downloading from
(0 by default)""", type=int)
    parser.add_argument("-V", "--videos", help="also download tumblr-hosted videos", action="store_true")
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

    filename_format = '$d - $b - $s'
    if args.format is not None:
        filename_format = args.format
    
    # begin raiding the tumb
    tr.raid(args.blog, count, start, folder, filename_format, args.metadata,
            args.videos, args.verbose, args.after, args.before)

