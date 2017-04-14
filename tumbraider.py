import keys # would-be devs: get your own keys for now and put them in a keys.py
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

# connect to tumblr API
client = pytumblr.TumblrRestClient(
    keys.consumerKey,       # grab these from your keys.py file
    keys.consumerSecret,
    keys.OAuthKey,
    keys.OAuthSecret
)

# set arguments
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
    print 'Saving images to ' + os.path.abspath(folder)

while count > 0:
    # request posts from tumblr API
    posts = client.posts('iksiovs',
            api_key = 'EpOrfPgSIE2v64yez9hWozCL8xLJ5eb4IbH4FX4abfMEI4Ix1x',
            offset = start,
            limit = count if count < 20 else 20)

    # iterate over the results of each request
    for post in posts['posts']:
        # look for images specifically
        if 'photos' in post:
            photoset = enumerate(post['photos'])
            for index, photo in photoset: 
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

                if args.verbose:
                    print filename

                if folder != '':
                    if not os.path.exists(folder):
                        os.makedirs(folder)
                    if folder[-1] == '/':
                        folder = folder[:-1]
                    filename = folder + '/' + filename

                # download image
                imgR = requests.get(url)
                i = Image.open(BytesIO(imgR.content))
                if url[-3:] != 'gif':
                    i.save(filename)
                else:
                    i.save(filename, save_all=True)
    # advance for next request
    count -= 20
    start += 20


print 'Finished downloading images from ' + args.blog + '.tumblr.com'
