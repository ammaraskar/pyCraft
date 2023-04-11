import requests
import json
import uuid
import os
from selenium import webdriver
from .exceptions import YggdrasilError

#: The base url for Ygdrassil requests
AUTH_SERVER = "https://authserver.mojang.com"
SESSION_SERVER = "https://sessionserver.mojang.com/session/minecraft"
# Need this content type, or authserver will complain
CONTENT_TYPE = "application/json"
HEADERS = {"content-type": CONTENT_TYPE}


class Profile(object):
    """
    Container class for a MineCraft Selected profile.
    See: `<http://wiki.vg/Authentication>`_
    """

    def __init__(self, id_=None, name=None):
        self.id_ = id_
        self.name = name

    def to_dict(self):
        """
        Returns ``self`` in dictionary-form, which can be serialized by json.
        """
        if self:
            return {"id": self.id_,
                    "name": self.name}
        else:
            raise AttributeError("Profile is not yet populated.")

    def __bool__(self):
        bool_state = self.id_ is not None and self.name is not None
        return bool_state

    # Python 2 support
    def __nonzero__(self):
        return self.__bool__()


class AuthenticationToken(object):
    """
    Represents an authentication token.

    See http://wiki.vg/Authentication.
    """
    AGENT_NAME = "Minecraft"
    AGENT_VERSION = 1

    def __init__(self, username=None, access_token=None, client_token=None):
        """
        Constructs an `AuthenticationToken` based on `access_token` and
        `client_token`.

        Parameters:
            access_token - An `str` object containing the `access_token`.
            client_token - An `str` object containing the `client_token`.

        Returns:
            A `AuthenticationToken` with `access_token` and `client_token` set.
        """
        self.username = username
        self.access_token = access_token
        self.client_token = client_token
        self.profile = Profile()

    @property
    def authenticated(self):
        """
        Attribute which is ``True`` when the token is authenticated and
        ``False`` when it isn't.
        """
        if not self.username:
            return False

        if not self.access_token:
            return False

        if not self.client_token:
            return False

        if not self.profile:
            return False

        return True

    def authenticate(self, username, password, invalidate_previous=False):
        """
        Authenticates the user against https://authserver.mojang.com using
        `username` and `password` parameters.

        Parameters:
            username - An `str` object with the username (unmigrated accounts)
                or email address for a Mojang account.
            password - An `str` object with the password.
            invalidate_previous - A `bool`. When `True`, invalidate
                all previously acquired `access_token`s across all clients.

        Returns:
            Returns `True` if successful.
            Otherwise it will raise an exception.

        Raises:
            minecraft.exceptions.YggdrasilError
        """
        payload = {
            "agent": {
                "name": self.AGENT_NAME,
                "version": self.AGENT_VERSION
            },
            "username": username,
            "password": password
        }

        if not invalidate_previous:
            # Include a `client_token` in the payload to prevent existing
            # `access_token`s from being invalidated. If `self.client_token`
            # is `None` generate a `client_token` using uuid4
            payload["clientToken"] = self.client_token or uuid.uuid4().hex

        res = _make_request(AUTH_SERVER, "authenticate", payload)

        _raise_from_response(res)

        json_resp = res.json()

        self.username = username
        self.access_token = json_resp["accessToken"]
        self.client_token = json_resp["clientToken"]
        self.profile.id_ = json_resp["selectedProfile"]["id"]
        self.profile.name = json_resp["selectedProfile"]["name"]

        return True

    def refresh(self):
        """
        Refreshes the `AuthenticationToken`. Used to keep a user logged in
        between sessions and is preferred over storing a user's password in a
        file.

        Returns:
            Returns `True` if `AuthenticationToken` was successfully refreshed.
            Otherwise it raises an exception.

        Raises:
            minecraft.exceptions.YggdrasilError
            ValueError - if `AuthenticationToken.access_token` or
                `AuthenticationToken.client_token` isn't set.
        """
        if self.access_token is None:
            raise ValueError("'access_token' not set!'")

        if self.client_token is None:
            raise ValueError("'client_token' is not set!")

        res = _make_request(AUTH_SERVER,
                            "refresh", {"accessToken": self.access_token,
                                        "clientToken": self.client_token})

        _raise_from_response(res)

        json_resp = res.json()

        self.access_token = json_resp["accessToken"]
        self.client_token = json_resp["clientToken"]
        self.profile.id_ = json_resp["selectedProfile"]["id"]
        self.profile.name = json_resp["selectedProfile"]["name"]

        return True

    def validate(self):
        """
        Validates the AuthenticationToken.

        `AuthenticationToken.access_token` must be set!

        Returns:
            Returns `True` if `AuthenticationToken` is valid.
            Otherwise it will raise an exception.

        Raises:
            minecraft.exceptions.YggdrasilError
            ValueError - if `AuthenticationToken.access_token` is not set.
        """
        if self.access_token is None:
            raise ValueError("'access_token' not set!")

        res = _make_request(AUTH_SERVER, "validate",
                            {"accessToken": self.access_token})

        # Validate returns 204 to indicate success
        # http://wiki.vg/Authentication#Response_3
        if res.status_code == 204:
            return True

    @staticmethod
    def sign_out(username, password):
        """
        Invalidates `access_token`s using an account's
        `username` and `password`.

        Parameters:
            username - ``str`` containing the username
            password - ``str`` containing the password

        Returns:
            Returns `True` if sign out was successful.
            Otherwise it will raise an exception.

        Raises:
            minecraft.exceptions.YggdrasilError
        """
        res = _make_request(AUTH_SERVER, "signout",
                            {"username": username, "password": password})

        if _raise_from_response(res) is None:
            return True

    def invalidate(self):
        """
        Invalidates `access_token`s using the token pair stored in
        the `AuthenticationToken`.

        Returns:
            ``True`` if tokens were successfully invalidated.

        Raises:
            :class:`minecraft.exceptions.YggdrasilError`
        """
        res = _make_request(AUTH_SERVER, "invalidate",
                            {"accessToken": self.access_token,
                             "clientToken": self.client_token})

        if res.status_code != 204:
            _raise_from_response(res)
        return True

    def join(self, server_id):
        """
        Informs the Mojang session-server that we're joining the
        MineCraft server with id ``server_id``.

        Parameters:
            server_id - ``str`` with the server id

        Returns:
            ``True`` if no errors occured

        Raises:
            :class:`minecraft.exceptions.YggdrasilError`

        """
        if not self.authenticated:
            err = "AuthenticationToken hasn't been authenticated yet!"
            raise YggdrasilError(err)

        res = _make_request(SESSION_SERVER, "join",
                            {"accessToken": self.access_token,
                             "selectedProfile": self.profile.to_dict(),
                             "serverId": server_id})

        if res.status_code != 204:
            _raise_from_response(res)
        return True


def _make_request(server, endpoint, data):
    """
    Fires a POST with json-packed data to the given endpoint and returns
    response.

    Parameters:
        endpoint - An `str` object with the endpoint, e.g. "authenticate"
        data - A `dict` containing the payload data.

    Returns:
        A `requests.Request` object.
    """
    res = requests.post(server + "/" + endpoint, data=json.dumps(data),
                        headers=HEADERS, timeout=15)
    return res


def _raise_from_response(res):
    """
    Raises an appropriate `YggdrasilError` based on the `status_code` and
    `json` of a `requests.Request` object.
    """
    if res.status_code == requests.codes['ok']:
        return None

    exception = YggdrasilError()
    exception.status_code = res.status_code

    try:
        json_resp = res.json()
        if not ("error" in json_resp and "errorMessage" in json_resp):
            raise ValueError
    except ValueError:
        message = "[{status_code}] Malformed error message: '{response_text}'"
        message = message.format(status_code=str(res.status_code),
                                 response_text=res.text)
        exception.args = (message,)
    else:
        message = "[{status_code}] {error}: '{error_message}'"
        message = message.format(status_code=str(res.status_code),
                                 error=json_resp["error"],
                                 error_message=json_resp["errorMessage"])
        exception.args = (message,)
        exception.yggdrasil_error = json_resp["error"]
        exception.yggdrasil_message = json_resp["errorMessage"]
        exception.yggdrasil_cause = json_resp.get("cause")

    raise exception


class Microsoft_AuthenticationToken(object):
    """
    Represents an authentication token.
    See https://wiki.vg/Microsoft_Authentication_Scheme.

    This class was shameless copied from github issue,
      https://github.com/ammaraskar/pyCraft/issues/234.

    The user https://github.com/shikukuya, contributed the comment:
        https://github.com/ammaraskar/pyCraft/issues/234#issuecomment-1365140050

    I have simply created a fork and submitted the changes as they describe
    the usage in their comment.  All credit for this goes to shikukua.
    
    EDIT: Made web request automatic
    """

    oauth20_URL = 'https://login.live.com/oauth20_token.srf'
    XBL_URL = 'https://user.auth.xboxlive.com/user/authenticate'
    XSTS_URL = 'https://xsts.auth.xboxlive.com/xsts/authorize'
    LOGIN_WITH_XBOX_URL = "https://api.minecraftservices.com/" \
        "authentication/login_with_xbox"

    CheckAccount_URL = 'https://api.minecraftservices.com/entitlements/mcstore'
    Profile_URL = 'https://api.minecraftservices.com/minecraft/profile'

    jwt_Token = ''

    def __init__(self, access_token=None):
        self.access_token = access_token
        self.driver = webdriver.Chrome()

    def GetoAuth20(self, code='') -> object:
        UserLoginURL = "https://login.live.com/oauth20_authorize.srf?" \
        "client_id=00000000402b5328&response_type=code" \
        "&scope=service%3A%3Auser.auth.xboxlive.com%3A%3AMBI_SSL&redirect_uri=" \
        "https%3A%2F%2Flogin.live.com%2Foauth20_desktop.srf"
        if code == '':
            print("Opening browser...")
            self.driver.get(UserLoginURL)

            while 'code=' not in self.driver.current_url:
                time.sleep(1)

            code = self.driver.current_url.split('code=')[1].split("&")[0]
            self.driver.quit()
            print(f"Retrieved code: {code}")

        oauth20 = requests.post(
            self.oauth20_URL,
            data={
                "client_id": "00000000402b5328",
                "code": "{}".format(code),
                "grant_type": "authorization_code",
                "redirect_uri": "https://login.live.com/oauth20_desktop.srf",
                "scope": "service::user.auth.xboxlive.com::MBI_SSL"
            },
            headers={"content-type": "application/x-www-form-urlencoded"},
            timeout=15)
        oauth20 = json.loads(oauth20.text)
        if 'error' in oauth20:
            print("Error: %s" % oauth20["error"])
            return 1
        else:
            self.oauth20_access_token = oauth20['access_token']
            self.oauth20_refresh_token = oauth20['refresh_token']
            oauth20_access_token = oauth20['access_token']
            oauth20_refresh_token = oauth20['refresh_token']
        return {
            "access_token": oauth20_access_token,
            "refresh_token": oauth20_refresh_token
        }

    def GetXBL(self, access_token: str) -> object:
        XBL = requests.post(self.XBL_URL,
                            json={
                                "Properties": {
                                    "AuthMethod": "RPS",
                                    "SiteName": "user.auth.xboxlive.com",
                                    "RpsTicket": "{}".format(access_token)
                                },
                                "RelyingParty": "http://auth.xboxlive.com",
                                "TokenType": "JWT"
                            },
                            headers=HEADERS,
                            timeout=15)
        return {
            "Token": json.loads(XBL.text)['Token'],
            "uhs": json.loads(XBL.text)['DisplayClaims']['xui'][0]['uhs']
        }

    def GetXSTS(self, access_token: str) -> object:
        XBL = requests.post(self.XSTS_URL,
                            json={
                                "Properties": {
                                    "SandboxId": "RETAIL",
                                    "UserTokens": ["{}".format(access_token)]
                                },
                                "RelyingParty":
                                "rp://api.minecraftservices.com/",
                                "TokenType": "JWT"
                            },
                            headers=HEADERS,
                            timeout=15)
        return {
            "Token": json.loads(XBL.text)['Token'],
            "uhs": json.loads(XBL.text)['DisplayClaims']['xui'][0]['uhs']
        }

    def GetXBOX(self, access_token: str, uhs: str) -> str:
        mat_jwt = requests.post(
            self.LOGIN_WITH_XBOX_URL,
            json={"identityToken": "XBL3.0 x={};{}".format(uhs, access_token)},
            headers=HEADERS,
            timeout=15)
        self.access_token = json.loads(mat_jwt.text)['access_token']
        return self.access_token

    def CheckAccount(self, jwt_Token: str) -> bool:
        CheckAccount = requests.get(
            self.CheckAccount_URL,
            headers={"Authorization": "Bearer {}".format(jwt_Token)},
            timeout=15)
        CheckAccount = len(json.loads(CheckAccount.text)['items'])
        if CheckAccount != 0:
            return True
        else:
            return False

    def GetProfile(self, access_token: str) -> object:
        if self.CheckAccount(access_token):
            Profile = requests.get(
                self.Profile_URL,
                headers={"Authorization": "Bearer {}".format(access_token)},
                timeout=15)
            Profile = json.loads(Profile.text)
            if 'error' in Profile:
                return False
            self.profile.id_ = Profile["id"]
            self.profile.name = Profile["name"]
            self.username = Profile["name"]
            return True
        else:
            return False

    @property
    def authenticated(self):
        """
        Attribute which is ``True`` when the token is authenticated and
        ``False`` when it isn't.
        """
        if not self.username:
            return False

        if not self.access_token:
            return False

        if not self.oauth20_refresh_token:
            return False

        if not self.profile:
            return False

        return True

    def authenticate(self):
        "Get verification information for a Microsoft account"
        oauth20 = self.GetoAuth20()
        if oauth20 == 1:
            return False
        XBL = self.GetXBL(oauth20['access_token'])
        XSTS = self.GetXSTS(XBL['Token'])
        XBOX = self.GetXBOX(XSTS['Token'], XSTS['uhs'])
        if self.GetProfile(XBOX):
            print('GameID: {}'.format(self.profile.id_))
            self.PersistenceLogoin_w()
            return True
        else:
            print('Account does not exist')
            return False

    def refresh(self):
        """
        Refreshes the `AuthenticationToken`. Used to keep a user logged in
        between sessions and is preferred over storing a user's password in a
        file.
        Returns:
            Returns `True` if `AuthenticationToken` was successfully refreshed.
            Otherwise it raises an exception.
        Raises:
            minecraft.exceptions.YggdrasilError
            ValueError - if `AuthenticationToken.access_token` or
                `AuthenticationToken.client_token` isn't set.
        """
        if self.access_token is None:
            raise ValueError("'access_token' not set!'")

        if self.oauth20_refresh_token is None:
            raise ValueError("'oauth20_refresh_token' is not set!")

        oauth20 = requests.post(
            self.oauth20_URL,
            data={
                "client_id": "00000000402b5328",
                "refresh_token": "{}".format(self.oauth20_refresh_token),
                "grant_type": "refresh_token",
                "redirect_uri": "https://login.live.com/oauth20_desktop.srf",
                "scope": "service::user.auth.xboxlive.com::MBI_SSL"
            },
            headers={"content-type": "application/x-www-form-urlencoded"},
            timeout=15)
        oauth20 = json.loads(oauth20.text)
        if 'error' in oauth20:
            print("Error: %s" % oauth20["error"])
            return False
        else:
            self.oauth20_access_token = oauth20['access_token']
            self.oauth20_refresh_token = oauth20['refresh_token']
            XBL = self.GetXBL(self.oauth20_access_token)
            XSTS = self.GetXSTS(XBL['Token'])
            XBOX = self.GetXBOX(XSTS['Token'], XSTS['uhs'])
            if self.GetProfile(XBOX):
                self.PersistenceLogoin_w()
                print('account: {}'.format(self.profile.id_))
                return True
            else:
                print('Account does not exist')
                return False

    def join(self, server_id):
        """
        Informs the Mojang session-server that we're joining the
        MineCraft server with id ``server_id``.
        Parameters:
            server_id - ``str`` with the server id
        Returns:
            ``True`` if no errors occured
        Raises:
            :class:`minecraft.exceptions.YggdrasilError`
        """
        if not self.authenticated:
            err = "AuthenticationToken hasn't been authenticated yet!"
            raise YggdrasilError(err)

        res = _make_request(
            SESSION_SERVER, "join", {
                "accessToken": self.access_token,
                "selectedProfile": self.profile.to_dict(),
                "serverId": server_id
            })

        if res.status_code != 204:
            _raise_from_response(res)
        return True

    def PersistenceLogoin_w(self):
        "Save access token persistent login"
        ProjectDir = os.path.dirname(os.path.dirname('{}'.format(__file__)))
        PersistenceDir = '{}/Persistence'.format(ProjectDir)
        if not self.authenticated:
            err = "AuthenticationToken hasn't been authenticated yet!"
            raise YggdrasilError(err)
        if not os.path.exists(PersistenceDir):
            os.mkdir(PersistenceDir)
        print(PersistenceDir)
        "Save access_token and oauth20_refresh_token"
        with open("{}/{}".format(PersistenceDir, self.username),
                  mode='w',
                  encoding='utf-8') as file_obj:
            file_obj.write('{{"{}": "{}","{}": "{}"}}'.format(
                'access_token', self.access_token, 'oauth20_refresh_token',
                self.oauth20_refresh_token))
            file_obj.close()
        return True

    def PersistenceLogoin_r(self, GameID: str):
        "Load access token persistent login"
        ProjectDir = os.path.dirname(os.path.dirname('{}'.format(__file__)))
        PersistenceDir = '{}/Persistence'.format(ProjectDir)
        if not os.path.exists(PersistenceDir):
            return False
        "Load access_token and oauth20_refresh_token"
        if os.path.isfile("{}/{}".format(PersistenceDir, GameID)):
            with open("{}/{}".format(PersistenceDir, GameID),
                      mode='r',
                      encoding='utf-8') as file_obj:
                Persistence = file_obj.read()
                file_obj.close()
                Persistence = json.loads(Persistence)
                self.access_token = Persistence["access_token"]
                self.oauth20_refresh_token = Persistence[
                    "oauth20_refresh_token"]
                self.refresh()
            return self.authenticated
        else:
            return False
