import argparse
import requests
import re
import os
from PIL import Image
from io import BytesIO

# argument parsing for command-line use
parser = argparse.ArgumentParser()
parser.add_argument("blog", help="download images from specified tumblr blog")
parser.add_argument("-f", "--folder", help="save images to specified folder")
parser.add_argument("-s", "--start", help="specify page from blog to start downloading images from (1 by default)", type=int)
parser.add_argument("-p", "--pages", help="specify number of pages from blog to download images from (unlimited by default)", type=int)
parser.add_argument("-v", "--verbose", help="verbose output", action="store_true")
args = parser.parse_args()

print('Looking for images on ', args.blog, '.tumblr.com...', sep='')

folder = ""
if args.folder is not None:
    folder = args.folder

page = 1
if args.start is not None:
    page = args.start

count = -1
if args.pages is not None:
    count = args.pages

hasPosts = True
while hasPosts and count != 0:
    if args.verbose:
        print('requesting page', page)
    url = 'http://' + args.blog + '.tumblr.com/page/' + str(page)
    r = requests.get(url, timeout=10)
    if args.verbose:
       print('on page:', page)
    hasPosts = r.text.find('div id="post') != -1 
    if args.verbose:
       print('tumblr still has posts:', hasPosts)

    # get location of images in page
    imgIndices = [match.start() for match in re.finditer('img src="', r.text)]
    for i in range(len(imgIndices)):
        imgIndices[i] += 9

    # retrieve images
    for imgIndex in imgIndices:
        # get url of image
        imgUrl = ''
        i = imgIndex
        while(r.text[i] != '"'):
            imgUrl += r.text[i]
            i += 1
        # get highest possible resolution of image stored on tumblr
        underscore = imgUrl.rfind('_')
        period = imgUrl.rfind('.')
        # highest resolution is already made available for audio covers
        if imgUrl[underscore+1:period] != "cover":
            imgUrl = imgUrl[:underscore+1] + '1280' + imgUrl[period:]
        if args.verbose:
            print('downloading', imgUrl[imgUrl.rfind('/')+1:])
        # download image
        imgR = requests.get(imgUrl)
        filename = imgUrl[imgUrl.rfind('/')+1:]
        if args.folder is not None:
            filename = folder + '/' + filename
            if not os.path.exists(folder):
                os.makedirs(folder)
        # save gifs differently, PIL can't download animated gifs properly
        if imgUrl[-3:] != 'gif':
            i = Image.open(BytesIO(imgR.content))
            i.save(filename)
        else:
            with open(filename, 'wb') as f:
                f.write(imgR.content)

    page += 1
    if args.pages is not None:
        count -= 1

print('Finished downloading images from ', args.blog, '.tumblr.com', sep='')
