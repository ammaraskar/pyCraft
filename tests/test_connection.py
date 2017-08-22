from . import fake_server
from minecraft import SUPPORTED_MINECRAFT_VERSIONS


class ConnectTest(fake_server._FakeServerTest):
    def test_connect(self):
        self._test_connect()


class PingTest(ConnectTest):
    def _start_client(self, client):
        def handle_ping(latency_ms):
            assert 0 <= latency_ms < 60000
            raise fake_server.FakeServerTestSuccess
        client.status(handle_status=False, handle_ping=handle_ping)


class ConnectCompressionLowTest(ConnectTest):
    compression_threshold = 0


class ConnectCompressionHighTest(ConnectTest):
    compression_threshold = 256


class AllowedVersionsTest(fake_server._FakeServerTest):
    VERSIONS = sorted(SUPPORTED_MINECRAFT_VERSIONS.items(), key=lambda p: p[1])
    VERSIONS = dict((VERSIONS[0], VERSIONS[len(VERSIONS)//2], VERSIONS[-1]))

    def test_with_version_names(self):
        for version, proto in AllowedVersionsTest.VERSIONS.items():
            client_versions = {
                v for (v, p) in SUPPORTED_MINECRAFT_VERSIONS.items()
                if p <= proto}
            self._test_connect(
                server_version=version, client_versions=client_versions)

    def test_with_protocol_numbers(self):
        for version, proto in AllowedVersionsTest.VERSIONS.items():
            client_versions = {
                p for (v, p) in SUPPORTED_MINECRAFT_VERSIONS.items()
                if p <= proto}
            self._test_connect(
                server_version=version, client_versions=client_versions)
