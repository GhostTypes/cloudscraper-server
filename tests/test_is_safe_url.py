import unittest
from unittest.mock import patch
from server import is_safe_url
import socket

class TestIsSafeUrl(unittest.TestCase):

    @patch('server.socket.getaddrinfo')
    def test_public_ipv4(self, mock_getaddrinfo):
        mock_getaddrinfo.return_value = [
            (socket.AF_INET, socket.SOCK_STREAM, 6, '', ('8.8.8.8', 80))
        ]
        is_safe, msg = is_safe_url('http://example.com')
        self.assertTrue(is_safe)
        self.assertIsNone(msg)

    @patch('server.socket.getaddrinfo')
    def test_private_ipv4(self, mock_getaddrinfo):
        mock_getaddrinfo.return_value = [
            (socket.AF_INET, socket.SOCK_STREAM, 6, '', ('127.0.0.1', 80))
        ]
        is_safe, msg = is_safe_url('http://example.com')
        self.assertFalse(is_safe)
        self.assertIn("Access to private/local network is forbidden", msg)

    @patch('server.socket.getaddrinfo')
    def test_dual_stack_ipv6_private(self, mock_getaddrinfo):
        # Scenario: DNS has public IPv4 (8.8.8.8) and private IPv6 (::1)
        mock_getaddrinfo.return_value = [
            (socket.AF_INET, socket.SOCK_STREAM, 6, '', ('8.8.8.8', 80)),
            (socket.AF_INET6, socket.SOCK_STREAM, 6, '', ('::1', 80, 0, 0))
        ]

        is_safe, msg = is_safe_url('http://example.com')

        # We expect this to be False (Blocked) because of the private IPv6 address.
        self.assertFalse(is_safe, "Should block if ANY resolved IP is private (IPv6 loopback)")
