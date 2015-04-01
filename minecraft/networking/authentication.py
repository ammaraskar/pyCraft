import urllib2
import json

#: The base url for Yggdrasil requests
BASE_URL = 'https://authserver.mojang.com/'
AGENT_INFO = {"name": "Minecraft", "version": 1}


class YggdrasilError(Exception):
    """Signals some sort of problem while handling a request to
    the Yggdrasil service

    :ivar human_error: A human readable description of the problem
    :ivar error: A short description of the problem
    """

    def __init__(self, error, human_readable_error):
        self.error = error
        self.human_readable_error = human_readable_error


def make_request(url, payload):
    """Makes an http request to the Yggdrasil authentication service
    If there is an error then it will raise a :exc:`.YggdrasilError`

    :param url: The fully formed url to the Yggdrasil endpoint, for example:
                https://authserver.mojang.com/authenticate
                You may use the :attr:`.BASE_URL` constant here as a shortcut
    :param payload: The payload to send with the request, will be interpreted
                as a JSON object so be careful.
                Example: {"username": username, "password": password, "agent": AGENT_INFO}
    :return: A :class:`.Response` object.
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


class Response(object):
    """Class to hold responses from Yggdrasil

    :ivar payload: The raw payload returned by Yggdrasil
    """
    payload = None


class LoginResponse(object):
    """A container class to hold information received from Yggdrasil
    upon logging into an account.

    :ivar username: The actual in game username of the user
    :ivar access_token: The access token of the user, used in place of the password
    :ivar profile_id: The selected profile id
    """
    pass


def login_to_minecraft(username, password):
    """
    Logs in to a minecraft account
    Will raise a :exc:`.YggdrasilError` on failure

    :param username: The mojang account username
    :param password: The password for the account
    :return: A :class:`.LoginResponse` object
    """
    payload = {"username": username, "password": password, "agent": AGENT_INFO}
    response = make_request(BASE_URL + "authenticate", payload)

    login_response = LoginResponse()
    payload = response.payload

    login_response.access_token = payload["accessToken"]
    login_response.profile_id = payload["selectedProfile"]["id"]
    login_response.username = payload["selectedProfile"]["name"]

    return login_response
