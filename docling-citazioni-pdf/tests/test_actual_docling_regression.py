"""Regression on a sanitized copy of real MCP output from a synthetic PDF."""
from pathlib import Path
import hashlib
import json
import sys
import unittest

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent/'docling-citazioni-pdf/scripts'))
import citation_provenance as cp
import export_page_references as pages


class ActualDoclingRegressionTests(unittest.TestCase):
    def setUp(self):
        self.raw = (ROOT/'fixtures/fascicolo-sintetico.docling.json').read_bytes()
        self.doc = json.loads(self.raw)
        self.quote = 'Importo richiesto: 1.200,00 euro; importo non liquidato.'

    def test_real_merged_item_does_not_become_a_single_first_page_citation(self):
        item = next(v for v in self.doc['texts'] if self.quote in v['text'])
        self.assertEqual(sorted({v['page_no'] for v in item['prov']}), [2, 3])
        markdown, index = pages.build(self.doc, hashlib.sha256(self.raw).hexdigest())
        record = next(v for v in index['blocks'] if v['anchor'] == item['self_ref'])
        self.assertEqual(record['status'], 'multiple_candidate_pages')
        self.assertEqual(record['candidate_pages'], [2, 3])
        self.assertGreater(markdown.index(self.quote), markdown.index('## Blocchi con provenienza'))
        self.assertFalse(index['pdf_original_verified'])

    def test_real_quote_without_evidenced_profile_stays_unverified(self):
        report = cp.analyze(self.doc, quote=self.quote,
                            source_json_sha256=hashlib.sha256(self.raw).hexdigest(),
                            document_sha256=hashlib.sha256((ROOT/'fixtures/fascicolo-sintetico.pdf').read_bytes()).hexdigest())
        self.assertTrue(report['matches'])
        self.assertEqual(report['candidate_physical_pages'], [])
        self.assertFalse(report['citation_verified'])


if __name__ == '__main__':
    unittest.main()
