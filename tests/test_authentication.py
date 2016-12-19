from minecraft.authentication import Profile
from minecraft.authentication import AuthenticationToken
from minecraft.authentication import _make_request
from minecraft.authentication import _raise_from_request
from minecraft.exceptions import YggdrasilError

import requests
import json
import unittest
from .compat import mock

FAKE_DATA = {
    "id_": "85e2c12b9eab4a7dabf61babc11354c2",
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


class InitProfile(unittest.TestCase):
    def test_init_no_values(self):
        p = Profile()
        self.assertIs(p.id_, None)
        self.assertIs(p.name, None)

    def test_init_id(self):
        p = Profile(id_=FAKE_DATA["id_"])
        self.assertEqual(p.id_, FAKE_DATA["id_"])

    def test_init_name(self):
        p = Profile(name=FAKE_DATA["username"])
        self.assertEqual(p.name, FAKE_DATA["username"])

    def test_init_positional(self):
        p = Profile(FAKE_DATA["id_"], FAKE_DATA["username"])
        self.assertEqual(p.id_, FAKE_DATA["id_"])
        self.assertEqual(p.name, FAKE_DATA["username"])


class ToDictProfile(unittest.TestCase):
    def test_to_dict_no_data(self):
        p = Profile()
        with self.assertRaises(AttributeError):
            p.to_dict()

    def test_to_dict_only_id(self):
        p = Profile(id_=FAKE_DATA["id_"])
        with self.assertRaises(AttributeError):
            p.to_dict()

    def test_to_dict_only_name(self):
        p = Profile(name=FAKE_DATA["username"])
        with self.assertRaises(AttributeError):
            p.to_dict()

    def test_to_dict(self):
        p = Profile(FAKE_DATA["id_"], FAKE_DATA["username"])
        d = p.to_dict()

        self.assertEqual(FAKE_DATA["id_"], d["id"])
        self.assertEqual(FAKE_DATA["username"], d["name"])


class BoolProfile(unittest.TestCase):
    # Checks for boolean state is done via __bool__ on Python 3
    # We need also to check for the Python 2 version, __nonzero__
    # and explicitly try __bool__ in case test is run on python 2
    def test_bool_no_data(self):
        p = Profile()
        self.assertFalse(p)
        self.assertFalse(p.__bool__())
        self.assertFalse(p.__nonzero__())

    def test_bool_only_id(self):
        p = Profile(id_=FAKE_DATA["id_"])
        self.assertFalse(p)
        self.assertFalse(p.__bool__())
        self.assertFalse(p.__nonzero__())

    def test_bool_only_name(self):
        p = Profile(name=FAKE_DATA["username"])
        self.assertFalse(p)
        self.assertFalse(p.__bool__())
        self.assertFalse(p.__nonzero__())

    def test_bool_with_data(self):
        p = Profile(FAKE_DATA["id_"], FAKE_DATA["username"])
        self.assertTrue(p)
        self.assertTrue(p.__bool__())
        self.assertTrue(p.__nonzero__())


class InitAuthenticationToken(unittest.TestCase):
    def test_init_no_values(self):
        a = AuthenticationToken()
        self.assertIs(a.username, None)
        self.assertIs(a.access_token, None)
        self.assertIs(a.client_token, None)

    def test_init_username(self):
        a = AuthenticationToken(username=FAKE_DATA["username"])
        self.assertEqual(a.username, FAKE_DATA["username"])

    def test_init_access_token(self):
        a = AuthenticationToken(access_token=FAKE_DATA["access_token"])
        self.assertEqual(a.access_token, FAKE_DATA["access_token"])

    def test_init_client_token(self):
        a = AuthenticationToken(client_token=FAKE_DATA["client_token"])
        self.assertEqual(a.client_token, FAKE_DATA["client_token"])

    def test_init_positional(self):
        a = AuthenticationToken(FAKE_DATA["username"],
                                FAKE_DATA["access_token"],
                                FAKE_DATA["client_token"])

        self.assertEqual(a.username, FAKE_DATA["username"])
        self.assertEqual(a.access_token, FAKE_DATA["access_token"])
        self.assertEqual(a.client_token, FAKE_DATA["client_token"])


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

    def test_raise_invalid_json(self):
        err_req = requests.Request()
        err_req.status_code = 401
        err_req.json = mock.MagicMock(
            side_effect=ValueError("no json could be decoded")
        )

        with self.assertRaises(YggdrasilError) as e:
            _raise_from_request(err_req)
            self.assertTrue("Unknown requests error" in e)

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


class NormalConnectionProcedure(unittest.TestCase):
    def test_login_connect_and_logout(self):
        a = AuthenticationToken()

        successful_req = requests.Request()
        successful_req.status_code = 200
        successful_req.json = mock.MagicMock(
            return_value={"accessToken": "token",
                          "clientToken": "token",
                          "selectedProfile": {
                              "id": "1",
                              "name": "asdf"
                          }}
        )

        error_req = requests.Request()
        error_req.status_code = 400
        error_req.json = mock.MagicMock(
            return_value={
                "error": "invalid request",
                "errorMessage": "invalid request"
            }
        )

        def mocked_make_request(server, endpoint, data):
            if endpoint == "authenticate":
                return successful_req
            if endpoint == "refresh" and data["accessToken"] == "token":
                return successful_req
            if (endpoint == "validate" and data["accessToken"] == "token") \
                    or endpoint == "join":
                r = requests.Request()
                r.status_code = 204
                r.raise_for_status = mock.MagicMock(return_value=None)
                return r
            if endpoint == "signout":
                return successful_req
            if endpoint == "invalidate":
                return successful_req

            return error_req

        # Test a successful sequence of events
        with mock.patch("minecraft.authentication._make_request",
                        side_effect=mocked_make_request) as _make_request_mock:

            self.assertFalse(a.authenticated)
            self.assertTrue(a.authenticate("username", "password"))

            self.assertTrue(a.authenticated)

            self.assertTrue(a.refresh())
            self.assertTrue(a.validate())

            self.assertTrue(a.authenticated)

            self.assertTrue(a.join(123))
            self.assertTrue(a.sign_out("username", "password"))

            self.assertTrue(a.invalidate())

            self.assertEqual(_make_request_mock.call_count, 6)

        a = AuthenticationToken(username="username",
                                access_token="token",
                                client_token="token")

        # Failures
        with mock.patch("minecraft.authentication._make_request",
                        return_value=error_req) as _make_request_mock:
            self.assertFalse(a.authenticated)

            a.client_token = "token"
            a.access_token = None
            self.assertRaises(ValueError, a.refresh)

            a.client_token = None
            a.access_token = "token"
            self.assertRaises(ValueError, a.refresh)

            a.access_token = None
            self.assertRaises(ValueError, a.validate)

            self.assertRaises(YggdrasilError, a.join, 123)
            self.assertRaises(YggdrasilError, a.invalidate)
