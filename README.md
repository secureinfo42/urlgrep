# Synopsis

```
Usage:
------
urlgrep [-u url|-f file] [-p protocol|-l] [-t extension] [-c clean_mode] [-C]


Options:
--------
-u | --url        : retrieve HTML from URL and grep into
-f | --filename   : read file and try to find matches
-p | --protocol   : match one if the known protocols
-l | --list       : list known protocols
-C | --check      : check if protocol is known
-c | --clean_mode : the way URL are cleaned : punc (cut at ?,&,#…) or nothing
-H | --href       : include hrefs, src with relative URL inside
-t | --filetype   : match for file type (regex: pdf$)
                  : default, read stding and grab any urls from any protocols

Notes:
------
filename, protocol and stdin can be cumulative


Exemples:
---------
urlgrep -u 'http://www.monsite.com'
curl -s 'http://www.monsite.com' | urlgrep -t pdf
cat grabme.html | urlgrep -p https -t pdf -f grabme2.html -s -u 'http://www.monsite.com/
urlgrep -c mailto
```
