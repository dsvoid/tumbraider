# tumbraider
Downloads images off of a tumblr iteratively. Requires Python 3.

## usage
```
python3 tumbraider.py [-h] [-f FOLDER] [-s START] [-p PAGES] [-v] blog

positional arguments:
	blog                  download images from specified tumblr blog

optional arguments:
  -h, --help            show this help message and exit

  -f FOLDER, --folder FOLDER
                        save images to specified folder

  -s START, --start START
                        specify page from blog to start downloading images
                        from (1 by default)

  -p PAGES, --pages PAGES
                        specify number of pages from blog to download images
                        from (unlimited by default)

  -v, --verbose         verbose output
```
