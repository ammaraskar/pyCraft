import re
from hashlib import sha1

# This function courtesy of barneygale
def javaHexDigest(digest):
    d = long(digest.hexdigest(), 16)
    if d >> 39*4 & 0x8:
        d = "-%x" % ((-d) & (2**(40*4)-1))
    else:
        d = "%x" % d
    return d

def translate_escape(m):
    c = m.group(1).lower()
    
    if   c == "0": return "\x1b[30m\x1b[21m" # black
    elif c == "1": return "\x1b[34m\x1b[21m" # dark blue
    elif c == "2": return "\x1b[32m\x1b[21m" # dark green
    elif c == "3": return "\x1b[36m\x1b[21m" # dark cyan
    elif c == "4": return "\x1b[31m\x1b[21m" # dark red
    elif c == "5": return "\x1b[35m\x1b[21m" # purple
    elif c == "6": return "\x1b[33m\x1b[21m" # gold
    elif c == "7": return "\x1b[37m\x1b[21m" # gray
    elif c == "8": return "\x1b[30m\x1b[1m"  # dark gray
    elif c == "9": return "\x1b[34m\x1b[1m"  # blue
    elif c == "a": return "\x1b[32m\x1b[1m"  # bright green
    elif c == "b": return "\x1b[36m\x1b[1m"  # cyan
    elif c == "c": return "\x1b[31m\x1b[1m"  # red
    elif c == "d": return "\x1b[35m\x1b[1m"  # pink
    elif c == "e": return "\x1b[33m\x1b[1m"  # yellow
    elif c == "f": return "\x1b[37m\x1b[1m"  # white
    elif c == "k": return "\x1b[5m"          # random
    elif c == "l": return "\x1b[1m"          # bold
    elif c == "m": return "\x1b[9m"          # strikethrough (escape code not widely supported)
    elif c == "n": return "\x1b[4m"          # underline
    elif c == "o": return "\x1b[3m"          # italic (escape code not widely supported)
    elif c == "r": return "\x1b[0m"          # reset
    
    return ""

def translate_escapes(s):
    return re.sub(ur"\xa7([0-9a-zA-Z])", translate_escape, s) + "\x1b[0m"