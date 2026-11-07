"""Reject workstation identifiers in publishable text and packaged resources.

Generic placeholders, public documentation URLs and loopback/unspecified
addresses are allowed. This is a leak guard, not proof of anonymization.
"""
import ipaddress
from pathlib import Path
import re
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[1]
TEXT_SUFFIXES = {'.md', '.py', '.json', '.yaml', '.yml', '.toml'}
PATTERNS = {
    'absolute_home_path': re.compile(r"/(?:Users|home)/[^/\s`'\"<>]+/"),
    'private_tailnet_hostname': re.compile(r'\b[a-z0-9-]+(?:\.[a-z0-9-]+)*\.ts\.net\b', re.I),
    'email_address': re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b'),
    'mac_address': re.compile(r'\b(?:[0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}\b'),
}
IPV4 = re.compile(r'(?<![\w.])(?:\d{1,3}\.){3}\d{1,3}(?![\w.])')
# Construct the CGNAT network numerically so the guard does not flag its own source.
CGNAT = ipaddress.ip_network(((100 << 24) | (64 << 16), 10))


def identifier_types(text):
    found = {label for label, pattern in PATTERNS.items() if pattern.search(text)}
    for match in IPV4.finditer(text):
        try:
            address = ipaddress.ip_address(match.group())
        except ValueError:
            continue
        if ((address.is_private or address in CGNAT)
                and not address.is_loopback and not address.is_unspecified):
            found.add('private_or_tailnet_ipv4')
    return found


class ReleasePrivacyTests(unittest.TestCase):
    def test_guard_detects_synthetic_identifiers_without_storing_real_configuration(self):
        examples = {
            'absolute_home_path': '/' + 'Users/' + 'persona-esempio/' + 'file.pdf',
            'private_tailnet_hostname': 'host' + '.rete-esempio' + '.ts' + '.net',
            'email_address': 'persona' + '@' + 'example.org',
            'private_or_tailnet_ipv4': str(ipaddress.IPv4Address((100 << 24) | (65 << 16) | 258)),
        }
        for expected, value in examples.items():
            with self.subTest(category=expected):
                self.assertIn(expected, identifier_types(value))

    def test_guard_allows_reserved_examples_and_loopback(self):
        self.assertEqual(identifier_types(
            'https://server-docling.example/mcp IP_VPN_DEL_SERVER 127.0.0.1 0.0.0.0'), set())

    def test_publishable_files_and_archive_have_no_workstation_identifiers(self):
        for path in ROOT.rglob('*'):
            if (path.is_file() and path.suffix in TEXT_SUFFIXES
                    and not {'.DS_Store', '__pycache__', '__MACOSX'}.intersection(path.parts)):
                with self.subTest(file=str(path.relative_to(ROOT))):
                    # Report categories and filenames, never the matched secret/value.
                    self.assertEqual(identifier_types(path.read_text(encoding='utf-8')), set())
        with zipfile.ZipFile(ROOT/'docling-citazioni-pdf.skill') as archive:
            for name in archive.namelist():
                if Path(name).suffix in TEXT_SUFFIXES:
                    with self.subTest(archive_member=name):
                        self.assertEqual(identifier_types(archive.read(name).decode('utf-8')), set())


if __name__ == '__main__':
    unittest.main()
