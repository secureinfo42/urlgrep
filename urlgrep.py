#!/usr/bin/env python3

import os
import getopt
import re
import getopt
import chardet
import colorama as c
from sys import argv, stdin, stderr

try:
  from bs4 import BeautifulSoup as bs
  import requests
except:
  print("ERROR: some modules are missing. To fix it :\npip install bs4 requests")
  exit(1)

APP = __file__.split("/")[-1]



###################################################################################################
#
# Globalz
#
##

PROTOCOLS_P1 = r'(acap|bitcoin|cap|data|dict|finger|fish|magnet|mailto|prospero|xmpp|sip|spotify):'
PROTOCOLS_P2 = r'(about|afp|dhcp|dns|ed2k|ftp|ftps|git\+http|git\+https|git|go|gopher|h323|http|https|icmp|imap|irc6|irc|ircs|ldap|ldaps|mms|ncp|news|nfs|nntp|nntps|ntp|pop|rdp|redis|rlogin|rsync|rtmp|rtsp|sftp|smb|smtp|smtps|snews|snmp|ssh|sshfs|stmp|svn\+ssh|svn|tcp|tel|telnet|tftp|udp|vcap|wais|webcal|ws|wss|xmpp|z39\.50r|z39\.50s)://'

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
UGLY_SEPARATOR = [
  '&quot;',
  '&#039;',
  '?',
  '}',
  '{',
  ';',
  "'",
  '"',
]



###################################################################################################
#
# Regex
#
##

def _build_rgx():
  regex = r'(?i)(\b(?<!-)('+PROTOCOLS_P1+r')|(file:///)|('+PROTOCOLS_P2+r')([a-zA-Z0-9\.\-\+:_]+)([^\<\>\{\}\"][a-zA-Z0-9,;:_/\?\.\#\&\-\+=]+))[\\\'\"\b\s]'
  print(regex)
  return(regex)

def print_rgx():
  print( _build_rgx() )
  exit(0)


###################################################################################################
#
# Checks
#
##

def get_protocol(protocol):
  global PROTOCOLS
  try:
    return(PROTOCOLS[protocol])
  except Exception as e:
    perror(e)
    exit(1)
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def check_protocol(protocol,debug=False):
  global PROTOCOLS
  try:
    proto = PROTOCOLS[protocol]
    if debug:
      print(proto)
    return(0)
  except KeyError:
    return(1)
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def check_clean_mode(mode):
  score = 0
  if mode == "punc":  score += 1
  if mode == "":      score += 1
  if score == 1:
    return(mode)
  else:
    usage(1)
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def list_protocol():
  global PROTOCOLS
  for protocol in PROTOCOLS:
    print(protocol)
  exit(0)
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def unhtmlentities(txt):
  txt = txt.replace('&quote;','"')
  txt = txt.replace('&#039;' ,"'")
  txt = txt.replace('&gt;'   ,">")
  txt = txt.replace('&lt;'   ,"<")
  txt = txt.replace('&nbsp;' ," ")
  txt = txt.replace('&amp;' ,"")
  return(txt)



###################################################################################################
#
# URL treatments
#
##

def _add_url(soup,_tag,_property,hrefs=False):
  array_tmp = []
  for __tag in soup.find_all(_tag, href=True):
    if hrefs == False:
      if '://' in __tag[_property]:
        array_tmp.append(__tag[_property])
    else:
      array_tmp.append(__tag[_property])
  return(array_tmp)
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def unhtml_url(url,clean_mode=""):
  if clean_mode == "all":
    for key in UGLY_SEPARATOR:
      if key in url:
        url = url.split(key)[0]
  if clean_mode == "punc":
    for key in UGLY_SEPARATOR[2:]:
      if key in url:
        url = url.split(key)[0]
  if clean_mode == "quote":
    for key in UGLY_SEPARATOR[:2]:
      if key in url:
        url = url.split(key)[0]
  return(url)
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def grab_urls(data,clean_mode="",hrefs=False):
  global PROTOCOLS
  urls = []
  soup = bs("<html>"+data+"</html>",features="html5lib")
  regex = _build_rgx()
  tmp_urls  = re.findall(regex, data)
  tmp_urls  = [u[0] for u in tmp_urls ]
  tmp_urls += _add_url(soup, 'a',   'href',hrefs)
  tmp_urls += _add_url(soup, 'src', 'img',hrefs)
  tmp_urls += _add_url(soup, 'src', 'script',hrefs)
  for url in tmp_urls:
    url = unhtmlentities(url)
    if re.findall(r";\w+://",url):
      for sub_url in url.split(';'):
        urls.append(unhtml_url(sub_url,clean_mode))
    else:
      urls.append(unhtml_url(url,clean_mode))
  return set(urls)



###################################################################################################
#
# Data treatments
#
##

def sanitize_file(data):
  encoding = chardet.detect(data)
  try:
    encoding = encoding['encoding'].lower()
    if encoding != 'utf-8':
      data = data.decode(encoding).encode('utf-8')
  except:
    try:
      data = data.replace(b"\x00",b"")
    except:
      pass
  return(str(data))
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def read_file(filename):
  try:
    data = open(filename,"rb").read()
    return(data)
  except Exception as e:
    perror(e)
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def read_url(url):
  try:
    s = requests.session()
    r = s.get(url)
    return( r.content.encode() )
  except Exception as e:
    perror(e)
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def read_stdin():
  try:
    ret = stdin.read().encode()
    return(ret)
  except Exception as e:
    perror(e)



###################################################################################################
#
# Main
#
##


def url_grep(data,protocol=".",url="",filetype="",clean_mode="",hrefs=False):
  """
  data : data to treat
  protocol : extract only protocol 'https, http, ...' - cf. PROTOCOLS
  url : in case data are retrieved from URL
  clean_mode : 'punc' = cut at punctuation 
  hrefs : retrieve also relative URLS in src, href
  """
  urls = []
  if data:
    data = sanitize_file(data)

    for url in set(grab_urls(data,clean_mode,hrefs)):
      if re.match(r"^"+protocol,url) : # if rgx == "", then match all
        if filetype:
          if re.findall(r"\."+filetype+r"(\?|$)",url):
            if url not in urls:
              urls.append(url)
        else:
          if url not in urls:
            urls.append(url)
  return(urls)

if __name__ == '__main__':

  # Functions only called in CLI ######################################################################################

  def usage(errcode=1):
    global APP
    app = f"{c.Fore.MAGENTA}{c.Style.BRIGHT}{APP}{c.Style.NORMAL}{c.Fore.RESET}"
    print(f"\nUsage:")
    print(f"------")
    print("%s [-u url|-f file] [-p protocol|-l] [-t extension] [-c clean_mode] [-C] [-x]" % app)
    print("")
    print(f"\nOptions:")
    print(f"--------")
    print("-u | --url        : retrieve HTML from URL and grep into")
    print("-f | --filename   : read file and try to find matches")
    print("-p | --protocol   : match one if the known protocols")
    print("-l | --list       : list known protocols")
    print("-C | --check      : check if protocol is known")
    print(f"-c | --clean_mode : the way URL are cleaned : {c.Fore.YELLOW}punc (cut at ?,&,#…){c.Fore.RESET} or nothing")
    print(f"-H | --href       : include hrefs, src with relative URL inside")
    print("-t | --filetype   : match for file type (regex: pdf$)")
    print("-x | --regex      : print regex")
    print("                  : default, read stding and grab any urls from any protocols")
    print("")
    print("Notes:")
    print("------")
    print(f"{c.Fore.YELLOW}filename{c.Fore.RESET}, {c.Fore.YELLOW}protocol{c.Fore.RESET} and {c.Fore.YELLOW}stdin{c.Fore.RESET} can be cumulative" )
    print("" )
    print("" )
    print("Exemples:")
    print("---------")
    print("%s -u 'http://www.monsite.com'" % app)
    print("curl -s 'http://www.monsite.com' | %s -t pdf" % app)
    print("cat grabme.html | %s -p https -t pdf -f grabme2.html -s -u 'http://www.monsite.com/" % app)
    print("%s -c mailto" % app)
    exit(errcode)

  def parse_args(argv):

    data, protocol, url, filetype, clean_mode = b"", ".", "", "", ""
    got_src, include_href = False, False

    for i in range(1,len(argv)):

      try:
        opt,arg = argv[i],argv[i+1]
      except IndexError:
        opt = argv[i]

      if opt in ("-p","--protocol"):  protocol = get_protocol(arg)
      if opt in ("-t","--filetype"):  filetype = arg
      if opt in ("-f","--file"):      data += read_file(arg)
      if opt in ("-u","--url"):       data += read_url(arg)
      if opt in ("-s","--stdin"):     data += read_stdin()
      if opt in ("-c","--clean"):     clean_mode = check_clean_mode(arg)
      if opt in ("-C","--check"):     exit( check_protocol(arg,debug=True) )
      if opt in ("-H","--href"):      include_href=True
      if opt in ("-x","--regex"):     print_rgx()
      if opt in ("-h","--help"):      usage(0)
      if opt in ("-l","--list"):      list_protocol()

    return( data, protocol, url, filetype, clean_mode, include_href )

  # Input processing ##################################################################################################

  data,protocol,url,filetype,clean_mode,hrefs = parse_args(argv)

  urls = url_grep(data, protocol, url, filetype, clean_mode, hrefs)
  for url in sorted(urls):
    print(url)

