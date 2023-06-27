# Synopsis

```sh
Usage: urlgrep [-f|-u|-s] [-H] [-h]

 -f  : read file
 -s  : read stdin
 -u  : read url
 -H  : grab href,src
 -h  : this sheet

Note: read args can be cumulative

Exemple:
dmesg |urlgrep -f /var/log/apache2/site.com.log.1 -u 'https://logger.site.com/?t=20230101'
```

# What 

Script can grab URL into binary file, from URL, stdin, file

# RegEx

```py
PROTOCOLS_P1 = r'((afp|ed2k|ftps?|git|git\+https?|go|gopher|h323|https?|imaps?|irc[s6]?|ldaps?|mms|ncp|news|nfs|nntps?|ntp|rdp|rsync|rtsp|sftp|smb|smtp?s|snmps?|ssh|sshfs|stmp|svn|tcp|tel|telnet|tftp|vnc|webcal|wss?|xmpp|(ms|xcon)\-\w+(\-\w+)?)://)'
### word:adresse
PROTOCOLS_P2  = r'((about|magnet|mailto|prospero|xmpp|sip|tel|phone|market|itms|spotify):)'
###  
PROTOCOLS_P3  = r'(file:///)'

```
