from minecraft.authentication import _raise_from_request
from minecraft.authentication import _make_request
from minecraft.authentication import AuthenticationToken
from minecraft.exceptions import YggdrasilError
import requests
import json
import unittest
from .compat import mock

FAKE_DATA = {
    "access_token": "9c771b61cef241808e129e33d51ea745",
    "client_token": "74076db55d8b4087a607fdeace60a94a",
    "username": "TheBadassMCrafter"
}

CREDENTIALS_LOCATION = "credentials"
AUTHSERVER = "https://authserver.mojang.com"


def get_mc_credentials():
    """
    Loads username and password from the credentials file.

    The credentials file should be stored in `credentials` in the root of the
    project folder.

    The credentials file should have the following format:
        `
        username
        password
        `
    """
    try:
        with open(CREDENTIALS_LOCATION, "r") as f:
            username = f.readline().lstrip().rstrip()
            password = f.readline().lstrip().rstrip()

        return (username, password)
    except IOError:
        return (None, None)

username, password = get_mc_credentials()


def should_skip_cred_test():
    """
    Returns `True` if a test requiring credentials should be skipped.
    Otherwise returns `False`
    """
    if username is None or password is None:
        return True
    return False


class Yggdrasil(unittest.TestCase):
    def test_init_no_values(self):
        a = AuthenticationToken()  # noqa

    def test_init_access_token(self):
        a = AuthenticationToken(access_token=FAKE_DATA["access_token"])  # noqa

    def test_init_client_token(self):
        a = AuthenticationToken(client_token=FAKE_DATA["client_token"])  # noqa

    def test_init_username(self):
        a = AuthenticationToken(client_token=FAKE_DATA["username"])  # noqa

    def test_init_positional(self):
        a = AuthenticationToken(FAKE_DATA["username"],
                                FAKE_DATA["access_token"],
                                FAKE_DATA["client_token"])

        self.assertEqual(a.username, FAKE_DATA["username"])
        self.assertEqual(a.access_token, FAKE_DATA["access_token"])
        self.assertEqual(a.client_token, FAKE_DATA["client_token"])


class MakeRequest(unittest.TestCase):
    def test_make_request_http_method(self):
        req = _make_request(AUTHSERVER, "authenticate", {"Billy": "Bob"})
        self.assertEqual(req.request.method, "POST")

    def test_make_request_json_dump(self):
        data = {"Marie": "McGee",
                "George": 1,
                "Nestly": {
                    "Nestling": "Nestling's tail"
                    },
                "Listly": ["listling1", 2, "listling 3"]
                }

        req = _make_request(AUTHSERVER, "authenticate", data)
        self.assertEqual(req.request.body, json.dumps(data))

    def test_make_request_url(self):
        URL = "https://authserver.mojang.com/authenticate"
        req = _make_request(AUTHSERVER, "authenticate", {"Darling": "Diary"})
        self.assertEqual(req.request.url, URL)


class RaiseFromRequest(unittest.TestCase):
    def test_raise_from_erroneous_request(self):
        err_req = requests.Request()
        err_req.status_code = 401
        err_req.json = mock.MagicMock(
            return_value={"error": "ThisIsAnException",
                          "errorMessage": "Went wrong."})

        with self.assertRaises(YggdrasilError) as e:
            _raise_from_request(err_req)
            self.assertEqual(e, "[401]) ThisIsAnException: Went Wrong.")

    def test_raise_from_erroneous_request_without_error(self):
        err_req = requests.Request()
        err_req.status_code = 401
        err_req.json = mock.MagicMock(return_value={"goldfish": "are pretty."})

        with self.assertRaises(YggdrasilError) as e:
            _raise_from_request(err_req)

            self.assertEqual(e, "Malformed error message.")

    def test_raise_from_healthy_request(self):
        req = requests.Request()
        req.status_code = 200
        req.json = mock.MagicMock(return_value={"vegetables": "are healthy."})

        self.assertIs(_raise_from_request(req), None)


class AuthenticatedAuthenticationToken(unittest.TestCase):
    pass


class AuthenticateAuthenticationToken(unittest.TestCase):
    def test_authenticate_no_username(self):
        a = AuthenticationToken()

        with self.assertRaises(TypeError):
            a.authenticate()

    def test_authenticate_no_password(self):
        a = AuthenticationToken()

        with self.assertRaises(TypeError):
            a.authenticate("username")

    def test_authenticate_wrong_credentials(self):
        a = AuthenticationToken()

        # We assume these aren't actual, valid credentials.
        with self.assertRaises(YggdrasilError) as e:
            a.authenticate("Billy", "The Goat")

            err = "Invalid Credentials. Invalid username or password."
            self.assertEqual(e.error, err)

    @unittest.skipIf(should_skip_cred_test(),
                     "Need credentials to perform test.")
    def test_authenticate_good_credentials(self):
        a = AuthenticationToken()

        resp = a.authenticate(username, password)
        self.assertTrue(resp)


class RefreshAuthenticationToken(unittest.TestCase):
    # TODO: Make me!
    pass


class ValidateAuthenticationToken(unittest.TestCase):
    # TODO: Make me!
    pass


class SignOutAuthenticationToken(unittest.TestCase):
    # TODO: Make me!
    pass


class InvalidateAuthenticationToken(unittest.TestCase):
    # TODO: Make me!
    pass


class JoinAuthenticationToken(unittest.TestCase):
    # TODO: Make me!
    pass
