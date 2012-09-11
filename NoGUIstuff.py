import urllib2, urllib
from networking import PacketSenderManager

def loginToMinecraft(username, password):
    try:
        url = 'https://login.minecraft.net'
        header = {'Content-Type' : 'application/x-www-form-urlencoded'}
        data = {'user' : username,
                'password' : password,
                'version' : '13'}
        data = urllib.urlencode(data)
        req = urllib2.Request(url, data, header)
        opener = urllib2.build_opener()
        response = opener.open(req, None, 10)
        response = response.read()
    except urllib2.URLError:
        toReturn = {'Response' : "Can't connect to minecraft.net"}
        return toReturn
    if(response == "Bad login"):
        toReturn = {'Response' : "Incorrect username/password"}
        return toReturn
    if(response == "Account migrated, use e-mail as username."):
        toReturn = {'Response' : "Account migrated, use e-mail as username."}
        return toReturn
    response = response.split(":")
    sessionid = response[3]
    toReturn = {'Response' : "Good to go!",
                'Username' : response[2],
                'SessionID' : sessionid
                }
    return toReturn