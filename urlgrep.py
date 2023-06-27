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
except:
  print("ERROR: you need to :")
  print("pip install bs4")
  exit(1)

try:
  import requests
except:
  print("ERROR: you need to :")
  print("pip install requests")
  exit(1)

APP = argv[0].split("/")[-1]



###################################################################################################
#
# Funcz
#
##

PROTOCOLS = {
  'about':"about://",
  'acap':"acap:",
  'afp':"afp://",
  'bitcoin':"bitcoin:",
  'cap':"cap:",
  # 'data':"data:",
  'dhcp':"dhcp://",
  'dict':"dict:",
  'dns':"dns://",
  'ed2k':"ed2k://",
  'file':"file:///",
  'finger':"finger:",
  'fish':"fish:",
  'ftp':"ftp://",
  'ftps':"ftps://",
  'git':"git://",
  'git+http':'git+http://',
  'git+https':'git+https://',
  'go':"go://",
  'gopher':"gopher://",
  'h323':"h323://",
  'http':"http://",
  'https':"https://",
  'icmp':"icmp://",
  'imap':"imap://",
  'irc':"irc://",
  'irc6':"irc6://",
  'ircs':"ircs://",
  'ldap':"ldap://",
  'ldaps':"ldaps://",
  'magnet':"magnet:",
  'mailto':"mailto:",
  'mms':"mms://",
  'ncp':"ncp://",
  'news':"news://",
  'nfs':"nfs://",
  'nntp':"nntp://",
  'nntps':"nntps://",
  'ntp':"ntp://",
  'pop':"pop://",
  'prospero':"prospero:",
  'rdp':"rdp://",
  'redis':"redis://",
  'rlogin':"rlogin://",
  'rsync':"rsync://",
  'rtmp':"rtmp://",
  'rtsp':"rtsp://",
  'sftp':"sftp://",
  'sip':"sip:",
  'smb':"smb://",
  'smtp':"smtp://",
  'smtps':"smtps://",
  'snews':"snews://",
  'snmp':"snmp://",
  'spotify':"spotify:",
  'ssh':"ssh://",
  'sshfs':"sshfs://",
  'stmp':"stmp://",
  'svn':"svn://",
  'svn+ssh':"svn+ssh://",
  'tcp':"tcp://",
  'tel':"tel://",
  'telnet':"telnet://",
  'tftp':"tftp://",
  'udp':"udp://",
  'vcap':"vcap://",
  'wais':"wais://",
  'webcal':"webcal://",
  'ws':"ws://",
  'wss':"wss://",
  'xmpp':"xmpp:",
  # 'xmpp':"xmpp://",
  'z39.50r':"z39.50r://",
  'z39.50s':"z39.50s://"
}

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

def perror(errtxt):
  errtxt = c.Fore.RED + c.Style.BRIGHT + f"Error: {errtxt}" + c.Style.NORMAL + c.Fore.RESET + "\n"
  stderr.write(errtxt)

def _add_url(soup,_tag,_property,hrefs=False):
  array_tmp = []
  for __tag in soup.find_all(_tag, href=True):
    if hrefs == False:
      if '://' in __tag[_property]:
        array_tmp.append(__tag[_property])
    else:
      array_tmp.append(__tag[_property])
  return(array_tmp)

def _build_rgx():
  # regex = r"(?i)\b(("
  # for protocol in PROTOCOLS:
  #   regex += PROTOCOLS[protocol] + "|"
  # # regex = regex[:-1] + r")[a-zA-Z0-9_,;=\+\%\&\?\-/\(\)\[\]\"\']{1,})[\b\'\"]"
  # regex = regex[:-1] + r")\S+)[^\"][^'][\W+\\\b\S]"
  # # regex = regex[:-1] + r")[a-z0-9_,;=\+\%\&\?\-/]{1,})"
  # regex = re.compile(regex)

  regex = r'(?i)((?=('
  for protocol in PROTOCOLS:
    regex += PROTOCOLS[protocol] + "|"
  regex = regex[:-1] + r'))([a-zA-Z0-9\.\-\+:_]+)(?:([^\<\>\{\}][a-zA-Z0-9,;:_/\?\.\#\&\-\+=]+)))[\'\"\b\s]' # s\W\"\'\b]'
  return(regex)

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

def unhtmlentities(txt):
  txt = txt.replace('&quote;','"')
  txt = txt.replace('&#039;' ,"'")
  txt = txt.replace('&gt;'   ,">")
  txt = txt.replace('&lt;'   ,"<")
  txt = txt.replace('&nbsp;' ," ")
  txt = txt.replace('&amp;' ,"")
  return(txt)

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

def get_protocol(protocol):
  global PROTOCOLS
  try:
    return(PROTOCOLS[protocol])
  except Exception as e:
    perror(e)
    exit(1)

def check_protocol(protocol,debug=False):
  global PROTOCOLS
  try:
    proto = PROTOCOLS[protocol]
    if debug:
      print(proto)
    return(0)
  except KeyError:
    return(1)

def list_protocol():
  global PROTOCOLS
  for protocol in PROTOCOLS:
    print(protocol)
  exit(0)

def usage(errcode=1):
  global APP
  app = f"{c.Fore.MAGENTA}{c.Style.BRIGHT}{APP}{c.Style.NORMAL}{c.Fore.RESET}"
  print(f"\nUsage:")
  print(f"------")
  print("%s [-u url|-f file] [-p protocol|-l] [-t extension] [-c clean_mode] [-C]" % app)
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

def sanitize_to_utf8(data):

  encoding = chardet.detect(data)
  encoding = encoding['encoding'].lower()
  if encoding != 'utf-8':
    data = data.decode(encoding).encode('utf-8')
  return(str(data))

def read_file(filename):
  try:
    return( open(filename,"rb").read() )
  except Exception as e:
    perror(e)

def read_url(url):
  try:
    s = requests.session()
    r = s.get(url)
    return( r.content.encode() )
  except Exception as e:
    perror(e)

def read_stdin():
  try:
    ret = stdin.read().encode()
    return(ret)
  except Exception as e:
    perror(e)

def check_clean_mode(mode):
  score = 0
  if mode == "punc":  score += 1
  if mode == "":      score += 1
  if score == 1:
    return(mode)
  else:
    usage(1)

def url_grep(data,protocol=".",url="",filetype="",clean_mode="",hrefs=False):
  if data:
    urls = []
    for url in set(grab_urls(data,clean_mode,hrefs)):
      if re.match(r"^"+protocol,url) : # if rgx == "", then match all
        if filetype:
          if re.findall(r"\."+filetype+r"(\?|$)",url):
            if url not in urls:
              urls.append(url)
        else:
          if url not in urls:
            urls.append(url)
    for url in sorted(urls):
      print(url)

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
    if opt in ("-h","--help"):      usage(0)
    if opt in ("-l","--list"):      list_protocol()

  return( data, protocol, url, filetype, clean_mode, include_href )



###################################################################################################
#
# Main
#
##

if __name__ == '__main__':

  data,protocol,url,filetype,clean_mode,hrefs = parse_args(argv)
  data = sanitize_to_utf8(data)
  url_grep(data, protocol, url, filetype, clean_mode, hrefs)


