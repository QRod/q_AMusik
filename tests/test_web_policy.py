import unittest
from q_amusik.web_policy import allowed_navigation


class WebPolicyTests(unittest.TestCase):
    def test_official_player_and_authentication_are_allowed(self):
        for url in ("https://music.apple.com/", "https://idmsa.apple.com/appleauth/auth/authorize",
                    "https://account.apple.com/", "https://appleid.apple.com:443/", "about:blank"):
            self.assertTrue(allowed_navigation(url), url)

    def test_other_hosts_local_files_and_external_protocols_are_blocked(self):
        for url in ("https://music.apple.com.evil.test/", "https://evilapple.com/", "file:///etc/passwd",
                    "javascript:alert(1)", "data:text/html,x", "http://music.apple.com/", "itms://music.apple.com/",
                    "https://user@music.apple.com/", "https://music.apple.com:8080/", "https://music.apple.com:bad/"):
            self.assertFalse(allowed_navigation(url), url)

    def test_loopback_is_not_allowed_in_production(self):
        self.assertFalse(allowed_navigation("http://127.0.0.1:8000/"))

    def test_fixture_origin_is_exact_and_loopback_only(self):
        self.assertTrue(allowed_navigation("http://127.0.0.1:8000/signin", "http://127.0.0.1:8000"))
        self.assertFalse(allowed_navigation("http://127.0.0.1:8001/", "http://127.0.0.1:8000"))
        self.assertFalse(allowed_navigation("http://localhost:8000/", "http://127.0.0.1:8000"))
