from minecraft.authentication import Profile
from minecraft.authentication import AuthenticationToken
from minecraft.authentication import _make_request
from minecraft.authentication import _raise_from_response
from minecraft.exceptions import YggdrasilError

from unittest import mock
import unittest
import requests
import json
import os

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


skipIfNoCredentials = unittest.skipIf(
    username is None or password is None,
    "Need credentials to perform test.")


skipUnlessInternetTestsEnabled = unittest.skipUnless(
    os.environ.get('PYCRAFT_RUN_INTERNET_TESTS'),
    "Tests involving Internet access are disabled.")


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

    @skipUnlessInternetTestsEnabled
    def test_authenticate_wrong_credentials(self):
        a = AuthenticationToken()

        # We assume these aren't actual, valid credentials.
        with self.assertRaises(YggdrasilError) as cm:
            a.authenticate("Billy", "The Goat")

        err = "[403] ForbiddenOperationException: " \
              "'Invalid credentials. Invalid username or password.'"
        self.maxDiff = 5000
        self.assertEqual(str(cm.exception), err)

    @skipIfNoCredentials
    @skipUnlessInternetTestsEnabled
    def test_authenticate_good_credentials(self):
        a = AuthenticationToken()

        resp = a.authenticate(username, password)
        self.assertTrue(resp)


@skipUnlessInternetTestsEnabled
class MakeRequest(unittest.TestCase):
    def test_make_request_http_method(self):
        res = _make_request(AUTHSERVER, "authenticate", {"Billy": "Bob"})
        self.assertEqual(res.request.method, "POST")

    def test_make_request_json_dump(self):
        data = {"Marie": "McGee",
                "George": 1,
                "Nestly": {
                    "Nestling": "Nestling's tail"
                    },
                "Listly": ["listling1", 2, "listling 3"]
                }

        res = _make_request(AUTHSERVER, "authenticate", data)
        self.assertEqual(res.request.body, json.dumps(data))

    def test_make_request_url(self):
        URL = "https://authserver.mojang.com/authenticate"
        res = _make_request(AUTHSERVER, "authenticate", {"Darling": "Diary"})
        self.assertEqual(res.request.url, URL)


class RaiseFromRequest(unittest.TestCase):
    def test_raise_from_erroneous_request(self):
        err_res = mock.NonCallableMock(requests.Response)
        err_res.status_code = 401
        err_res.json = mock.MagicMock(
            return_value={"error": "ThisIsAnException",
                          "errorMessage": "Went wrong."})
        err_res.text = json.dumps(err_res.json())

        with self.assertRaises(YggdrasilError) as cm:
            _raise_from_response(err_res)

        message = "[401] ThisIsAnException: 'Went wrong.'"
        self.assertEqual(str(cm.exception), message)

    def test_raise_invalid_json(self):
        err_res = mock.NonCallableMock(requests.Response)
        err_res.status_code = 401
        err_res.json = mock.MagicMock(
            side_effect=ValueError("no json could be decoded")
        )
        err_res.text = "{sample invalid json}"

        with self.assertRaises(YggdrasilError) as cm:
            _raise_from_response(err_res)

        message_start = "[401] Malformed error message"
        self.assertTrue(str(cm.exception).startswith(message_start))

    def test_raise_from_erroneous_response_without_error(self):
        err_res = mock.NonCallableMock(requests.Response)
        err_res.status_code = 401
        err_res.json = mock.MagicMock(return_value={"goldfish": "are pretty."})
        err_res.text = json.dumps(err_res.json())

        with self.assertRaises(YggdrasilError) as cm:
            _raise_from_response(err_res)

        message_start = "[401] Malformed error message"
        self.assertTrue(str(cm.exception).startswith(message_start))

    def test_raise_from_healthy_response(self):
        res = mock.NonCallableMock(requests.Response)
        res.status_code = 200
        res.json = mock.MagicMock(return_value={"vegetables": "are healthy."})
        res.text = json.dumps(res.json())

        self.assertIs(_raise_from_response(res), None)


class NormalConnectionProcedure(unittest.TestCase):
    def test_login_connect_and_logout(self):
        a = AuthenticationToken()

        successful_res = mock.NonCallableMock(requests.Response)
        successful_res.status_code = 200
        successful_res.json = mock.MagicMock(
            return_value={"accessToken": "token",
                          "clientToken": "token",
                          "selectedProfile": {
                              "id": "1",
                              "name": "asdf"
                          }}
        )
        successful_res.text = json.dumps(successful_res.json())

        error_res = mock.NonCallableMock(requests.Response)
        error_res.status_code = 400
        error_res.json = mock.MagicMock(
            return_value={
                "error": "invalid request",
                "errorMessage": "invalid request"
            }
        )
        error_res.text = json.dumps(error_res.json())

        def mocked_make_request(server, endpoint, data):
            if endpoint == "authenticate":
                if "accessToken" in data:
                    response = successful_res.copy()
                    response.json["accessToken"] = data["accessToken"]
                    return response
                return successful_res
            if endpoint == "refresh" and data["accessToken"] == "token":
                return successful_res
            if (endpoint == "validate" and data["accessToken"] == "token") \
                    or endpoint == "join":
                r = requests.Response()
                r.status_code = 204
                r.raise_for_status = mock.MagicMock(return_value=None)
                return r
            if endpoint == "signout":
                return successful_res
            if endpoint == "invalidate":
                return successful_res

            return error_res

        # Test a successful sequence of events
        with mock.patch("minecraft.authentication._make_request",
                        side_effect=mocked_make_request) as _make_request_mock:

            self.assertFalse(a.authenticated)
            self.assertTrue(a.authenticate("username", "password"))

            self.assertEqual(_make_request_mock.call_count, 1)
            self.assertIn("clientToken", _make_request_mock.call_args[0][2])

            self.assertTrue(a.authenticated)

            self.assertTrue(a.refresh())
            self.assertTrue(a.validate())

            self.assertTrue(a.authenticated)

            self.assertTrue(a.join(123))
            self.assertTrue(a.sign_out("username", "password"))

            self.assertTrue(a.invalidate())

            self.assertEqual(_make_request_mock.call_count, 6)

        # Test that we send a provided clientToken if the authenticationToken
        # is initialized with one
        with mock.patch("minecraft.authentication._make_request",
                        side_effect=mocked_make_request) as _make_request_mock:
            a = AuthenticationToken(client_token="existing_token")

            self.assertTrue(a.authenticate("username", "password",
                                           invalidate_previous=False))

            self.assertEqual(_make_request_mock.call_count, 1)
            self.assertEqual(
                "existing_token",
                _make_request_mock.call_args[0][2]["clientToken"]
            )

        # Test that we invalidate previous tokens properly
        with mock.patch("minecraft.authentication._make_request",
                        side_effect=mocked_make_request) as _make_request_mock:
            a = AuthenticationToken()

            self.assertFalse(a.authenticated)
            self.assertTrue(a.authenticate("username", "password",
                                           invalidate_previous=True))

            self.assertTrue(a.authenticated)
            self.assertEqual(a.access_token, "token")
            self.assertEqual(_make_request_mock.call_count, 1)
            self.assertNotIn("clientToken", _make_request_mock.call_args[0][2])

        a = AuthenticationToken(username="username",
                                access_token="token",
                                client_token="token")

        # Failures
        with mock.patch("minecraft.authentication._make_request",
                        return_value=error_res) as _make_request_mock:
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
