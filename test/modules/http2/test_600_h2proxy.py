import pytest

from .env import H2Conf, H2TestEnv


@pytest.mark.skipif(condition=H2TestEnv.is_unsupported, reason="mod_http2 not supported here")
class TestH2Proxy:

    @pytest.fixture(autouse=True, scope='class')
    def _class_scope(self, env):
        conf = H2Conf(env)
        conf.add_vhost_cgi(h2proxy_self=True)
        if env.verbosity > 1:
            conf.add("LogLevel proxy:trace2 proxy_http2:trace2")
        conf.install()
        assert env.apache_restart() == 0

    def test_h2_600_01(self, env):
        url = env.mkurl("https", "cgi", "/h2proxy/hello.py")
        r = env.curl_get(url, 5)
        assert r.response["status"] == 200
        assert r.response["json"]["protocol"] == "HTTP/2.0"
        assert r.response["json"]["https"] == "on"
        assert r.response["json"]["ssl_protocol"] != ""
        assert r.response["json"]["h2"] == "on"
        assert r.response["json"]["h2push"] == "off"
        assert r.response["json"]["host"] == f"cgi.{env.http_tld}"
