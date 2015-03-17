import urllib2
import json

BASE_URL = 'https://authserver.mojang.com/'
AGENT_INFO = {"name": "Minecraft", "version": 1}


class Response(object):
    """Class to hold responses from Yggdrasil
    """
    error = False
    payload = None


class YggdrasilError(Exception):

    def __init__(self, error='', human_readable_error=''):
        self.error = error
        self.human_readable_error = human_readable_error


def make_request(url, payload):
    """Makes http requests to the Yggdrasil authentication service

    Returns a Response object.
    If there is an error then it will raise a YggdrasilError.
    """
    response = Response()

    try:
        header = {'Content-Type': 'application/json'}
        data = json.dumps(payload)

        req = urllib2.Request(url, data, header)
        opener = urllib2.build_opener()
        http_response = opener.open(req, None, 10)
        http_response = http_response.read()

    except urllib2.HTTPError, e:
        error = e.read()
        error = json.loads(error)

        response.human_error = error['errorMessage']
        response.error = error['error']
        raise YggdrasilError(error['error'], error['errorMessage'])

    except urllib2.URLError, e:
        raise YggdrasilError(e.reason, e.reason)

    # ohey, everything didn't end up crashing and burning
    if http_response == "":
        http_response = "{}"
    try:
        json_response = json.loads(http_response)
    except ValueError, e:
        raise YggdrasilError(e.message, "JSON parsing exception on data: " + http_response)

    response.payload = json_response
    return response


class LoginResponse(object):
    """Yet another container class, this time to hold login info since it'll probably
    be need to passed around a lot afterwards
    """
    pass


def login_to_minecraft(username, password):
    """Logs in to mineraft 

    Returns a LoginResponse object containing a boolean `error` field.
    If there is an error, it will be accompanied with a `human_error` field.
    Otherwise `access_token`, `profile_id` and `username` fields will be present in the response.
    """
    payload = {"username": username, "password": password, "agent": AGENT_INFO}
    response = make_request(BASE_URL + "authenticate", payload)

    login_response = LoginResponse()
    payload = response.payload

    login_response.error = False
    login_response.access_token = payload["accessToken"]
    login_response.profile_id = payload["selectedProfile"]["id"]
    login_response.username = payload["selectedProfile"]["name"]

    return login_response
