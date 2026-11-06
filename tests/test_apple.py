import subprocess
import unittest
from unittest.mock import patch
from q_amusik.apple import APPLE_MUSIC_URL, open_apple_music


class AppleTests(unittest.TestCase):
    @patch("q_amusik.apple.subprocess.Popen")
    @patch("q_amusik.apple.shutil.which", return_value="/usr/bin/google-chrome-stable")
    def test_app_mode_only_opens_official_https_site(self, which, popen):
        open_apple_music()
        self.assertEqual(popen.call_args.args[0],
                         ["/usr/bin/google-chrome-stable", "--app=" + APPLE_MUSIC_URL])
        self.assertNotIn("shell", popen.call_args.kwargs)

    @patch("q_amusik.apple.subprocess.run")
    @patch("q_amusik.apple.shutil.which", side_effect=lambda name: "/usr/bin/xdg-open" if name == "xdg-open" else None)
    def test_fallback_uses_default_browser(self, which, run):
        open_apple_music()
        self.assertEqual(run.call_args.args[0], ["/usr/bin/xdg-open", APPLE_MUSIC_URL])
        self.assertTrue(run.call_args.kwargs["check"])

    @patch("q_amusik.apple.shutil.which", return_value=None)
    def test_missing_browser_reports_actionable_error(self, which):
        with self.assertRaises(RuntimeError):
            open_apple_music()
