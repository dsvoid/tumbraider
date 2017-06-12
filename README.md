# tumbraider
Downloads images off of a tumblr iteratively. Requires Python 2.

## usage
`python tumbraider.py [-h] [-f FOLDER] [-F FORMAT] [-p POSTS] [-s START] [-V] [-v] blog`

```
positional arguments:
  blog                  download images from specified tumblr blog

optional arguments:
  -a, --after           save files after a certain date (in yy-mm-dd format)
  -b, --before          save files before a certain date (in yy-mm-dd format)
  -h, --help            show this help message and exit
  -f FOLDER, --folder FOLDER
                        save images to specified folder
                        (program directory by default)
  -F FORMAT, --format FORMAT
                        use a format for filenames ('$d $b $s' by default)
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
                            $u : blog post's URL
  -m, --metadata        Save downloaded metadata to a JSON file
  -p POSTS, --posts POSTS
                        specify number of posts from blog to download from
                        (unlimited by default)
  -s START, --start START
                        specify post from blog to start downloading from
                        (0 by default)
  -V, --videos          also download tumblr-hosted videos
  -v, --verbose         verbose output
```
