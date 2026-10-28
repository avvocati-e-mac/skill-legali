"""Validate installable archive identity and portable skill discovery metadata."""
from pathlib import Path
import re
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT/'docling-citazioni-pdf'


class DistributionTests(unittest.TestCase):
    def test_common_frontmatter_and_cowork_description_limit(self):
        text = (SKILL/'SKILL.md').read_text()
        front = text.split('---', 2)[1]
        self.assertEqual(re.findall(r'^(\S+):', front, re.M), ['name', 'description'])
        self.assertIn('name: docling-citazioni-pdf', front)
        description = ' '.join(line.strip() for line in front.split('description: >\n', 1)[1].splitlines())
        self.assertLessEqual(len(description), 1024)
        self.assertTrue(description)

    def test_archive_contains_exact_sources_without_runtime_artifacts(self):
        expected = {str(path.relative_to(ROOT)): path.read_bytes()
                    for path in SKILL.rglob('*') if path.is_file()
                    and '__pycache__' not in path.parts and path.suffix != '.pyc'}
        with zipfile.ZipFile(ROOT/'docling-citazioni-pdf.skill') as archive:
            names = archive.namelist()
            self.assertEqual(len(names), len(set(names)))
            self.assertEqual(set(names), set(expected))
            for name in names:
                self.assertNotIn('..', Path(name).parts)
                self.assertEqual(archive.read(name), expected[name])

    def test_local_resource_links_resolve(self):
        for source in SKILL.rglob('*.md'):
            for target in re.findall(r'\]\(([^)]+)\)', source.read_text()):
                if '://' not in target and not target.startswith('#'):
                    self.assertTrue((source.parent/target).is_file(), (source, target))


if __name__ == '__main__':
    unittest.main()
