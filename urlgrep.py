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
# Regex
#
##

### word://adresse
PROTOCOLS_P1 = r'((afp|ed2k|ftps?|git|git\+https?|go|gopher|h323|https?|imaps?|irc[s6]?|ldaps?|mms|ncp|news|nfs|nntps?|ntp|rdp|rsync|rtsp|sftp|smb|smtp?s|snmps?|ssh|sshfs|stmp|svn|tcp|tel|telnet|tftp|vnc|webcal|wss?|xmpp|(ms|xcon)\-\w+(\-\w+)?)://)'
### word:adresse
PROTOCOLS_P2  = r'((about|magnet|mailto|prospero|xmpp|sip|tel|phone|market|itms|spotify):)'
###  
PROTOCOLS_P3  = r'(file:///)'
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

def _build_rgx():
  regex  = r'(?i)\b((?<=)('
  regex += PROTOCOLS_P1
  regex += r'|'
  regex += PROTOCOLS_P2
  regex += r'|'
  regex += PROTOCOLS_P3
  regex += r')([a-zA-Z0-9_/=%\+\-\.\?\&\;,\[\]\(\)])+)\b'
  regex  = re.compile(regex)
  return(regex)
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def print_rgx():
  msg  = ""
  msg += "\nRegex : "+c.Fore.CYAN
  msg +=  _build_rgx() 
  msg += "\n"+c.Fore.RESET
  stderr.write(msg)



###################################################################################################
#
# Checks
#
##

def perror(errmsg,errcode=0):

  errmsg = c.Fore.RED + f"\nError : {errmsg}" + c.Fore.RESET
  stderr.write(errmsg)
  if errcode:
    exit(errcode)
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def clean_htmlentities(txt,options=""):
  # txt = txt.replace('%20'    , " ")
  txt = txt.replace('%25'    , "%")
  txt = txt.replace('%26'    , "&")
  txt = txt.replace('%2B'    , "+")
  txt = txt.replace('%2D'    , "-")
  txt = txt.replace('%2E'    , ".")
  txt = txt.replace('%2F'    , "/")
  txt = txt.replace('%3A'    , ":")
  txt = txt.replace('%3D'    , "=")
  txt = txt.replace('%3F'    , "?")
  txt = txt.replace('&#039;' , "'")
  txt = txt.replace('&amp;'  , "&")
  txt = txt.replace('&gt;'   , ">")
  txt = txt.replace('&lt;'   , "<")
  txt = txt.replace('&nbsp;' , " ")
  txt = txt.replace('&quot;' , '"')
  txt = txt.replace('\\n'    , "\n")
  # txt = txt.replace(')'      , "\n")
  txt = txt.replace(';https://', ";\nhttps://")
  txt = txt.replace('=https://', "\nhttps://")
  return(txt)



###################################################################################################
#
# Reading data
#
##

def read_strings(data):
  out = b""
  authorized_bytes  = [0x09, 0x0A, 0x0D]
  authorized_bytes += range(0x20,0x7f)
  for i in data:
    if i in authorized_bytes:
      out += bytes([i])
  return(out)
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def sanitize_data(data):
  try:
    encoding = chardet.detect(data)
    encoding = encoding['encoding'].lower()
    if encoding != 'utf-8':
      data = data.decode(encoding).encode('utf-8')
  except:
    try:
      data = read_strings(data)
    except Exception as e:
      perror(e,1)
      pass
  data = str(data)
  data = clean_htmlentities(data,"&")
  return(data)
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def read_file(filename):
  data = b""
  try:
    data = open(filename,"rb").read()
  except Exception as e:
    perror(e)
  return(data)
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def read_url(url):
  data = b""
  try:
    s   = requests.session()
    r   = s.get(url)
    data = r.content
  except Exception as e:
    perror(e)
  return(data)
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def read_stdin():
  data = b""
  try:
    data = stdin.buffer.read()
  except Exception as e:
    perror(e)
  return(data)



###################################################################################################
#
# Parsing engine
#
##

def print_urls(urls):
  for url in sorted(set(urls)):
    print(url)
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def grep_urls(data,include_href=False):

  urls = []
  data = sanitize_data(data)

  found = re.findall(_build_rgx(),data)
  for url in sorted(set(found)):
    urls.append(url[0])
    
  if include_href == True:

    found = re.findall(r"=[\"\'](//?\S+)(?<!-)(?!-)[\'\"]",data)
    for url in sorted(set(found)):
      urls.append(url)

    soup  = bs(data,features="html5lib")
    found  = [ x['href'] for x in soup.find_all('a',      href=True) ]
    found += [ x['src']  for x in soup.find_all('img',    href=True) ]
    found += [ x['src']  for x in soup.find_all('script', href=True) ]
    for url in sorted(set(found)):
      urls.append(url)

  return(urls)


###################################################################################################
#
# Main
#
##

if __name__ == '__main__':

  ### Arguments parsing ###########################################################################

  def usage(errcode):
    print("\nUsage: %s [-f|-u|-s] [-H] [-h]" % APP)
    print("")
    print(" -f  : read file")
    print(" -s  : read stdin")
    print(" -u  : read url")
    print(" -H  : grab href,src")
    print(" -h  : this sheet")
    print("")
    print("Note: read args can be cumulative")
    print("")
    print("Exemple:\ndmesg |%s -f /var/log/apache2/site.com.log.1 -u 'https://logger.site.com/?t=20230101'" % APP)
    print("")
    exit(errcode)

  def parse_args(argv):

    data = b""
    include_href = False

    if len(argv) == 2:
      if argv[1][0] != "-" and not data:
        data = read_file(argv[1])
        return(data,include_href)

    if len(argv) == 1:
      data = read_stdin()
      return(data,include_href)

    for i in range(1,len(argv)):

      try: opt,arg = argv[i],argv[i+1]
      except IndexError: opt = argv[i]

      if opt in ("-f","--file"):          data += read_file(arg)
      if opt in ("-u","--url"):           data += read_url(arg)
      if opt in ("-s","--stdin"):         data += read_stdin()
      if opt in ("-H","--href"):          include_href=True
      if opt in ("-h","--help"):          usage(0)

    return(data,include_href)

  ### Main ########################################################################################

  data, include_href = parse_args(argv)

  print_urls( 
    grep_urls(
      data,
      include_href
    )
  )

