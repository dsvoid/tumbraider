import argparse
import requests
import pytumblr
import re
import os
from PIL import Image
from io import BytesIO

# argument parsing for command-line use
parser = argparse.ArgumentParser()
parser.add_argument("blog", help="download images from specified tumblr blog")
parser.add_argument("-f", "--folder", help="save images to specified folder")
parser.add_argument("-s", "--start", help="specify post from blog to start downloading images from (0 by default)", type=int)
parser.add_argument("-p", "--posts", help="specify number of posts from blog to download images from (unlimited by default)", type=int)
parser.add_argument("-v", "--verbose", help="verbose output", action="store_true")
args = parser.parse_args()

client = pytumblr.TumblrRestClient(
# DELETE SECRETS BEFORE PUBLISHING ^^^^^^^^^^
)

folder = ""
if args.folder is not None:
    folder = args.folder

start = 0
if args.start is not None:
    start = args.start

info = client.blog_info(args.blog)
count = info['blog']['posts']
if args.posts is not None and args.posts < count:
    count = args.posts

print 'Downloading images in ' + str(count) + ' posts from ' + args.blog + '.tumblr.com...'

if args.verbose and args.folder is not None:
    print 'Saving images to ' + folder

while count > 0:
    posts = client.posts('iksiovs',
            api_key = 'EpOrfPgSIE2v64yez9hWozCL8xLJ5eb4IbH4FX4abfMEI4Ix1x',
            offset = start,
            limit = count if count < 20 else 20)
    for post in posts['posts']:
        if 'photos' in post:
            photoset = enumerate(post['photos'])
            for index, photo in photoset:
                url = photo['original_size']['url']
                imgR = requests.get(url)

                filename = str(post['timestamp']) + ' ' + post['date'][:10]

                if post['summary'] != '':
                    l = len(post['summary'])
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

                ext = url[url.rfind('.'):]
                filename = filename + ext

                if args.verbose:
                    print filename

                if folder != '':
                    if folder[-1] == '/':
                        folder = folder[:-1]
                    filename = folder + '/' + filename

                if not os.path.exists(folder):
                    os.makedirs(folder)
                i = Image.open(BytesIO(imgR.content))
                i.save(filename, save_all=True)
    count -= 20
    start += 20


print 'Finished downloading images from ' + args.blog + '.tumblr.com'
