"""Real PDF structure tests, optional only when pypdfium2 is not installed."""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parent
SCRIPT = ROOT.parent/'docling-citazioni-pdf/scripts/inspect_pdf.py'
FIXTURE = ROOT/'fixtures/tipi-pdf.pdf'
sys.path.insert(0, str(SCRIPT.parent))
import inspect_pdf as inspector


@unittest.skipUnless(importlib.util.find_spec('pypdfium2'), 'requires optional pypdfium2')
class PdfInspectionLiveTests(unittest.TestCase):
    def test_native_image_ocr_layer_and_blank_pages_keep_origin_uncertainty(self):
        result = inspector.inspect_pdf(FIXTURE, [1, 2, 3, 4])
        self.assertEqual(result['scope'], 'all_pages')
        self.assertEqual([v['clue'] for v in result['pages']], [
            'text_layer_present_origin_unknown', 'probable_scan_sparse_or_no_text',
            'dominant_image_and_text_possible_previous_ocr', 'no_text_origin_unknown'])
        self.assertFalse(result['document_origin_certified'])
        self.assertFalse(result['ocr_execution_checked'])
        self.assertFalse(result['visual_verification_performed'])

    def test_sample_never_claims_to_cover_omitted_ocr_page(self):
        result = inspector.inspect_pdf(FIXTURE)
        self.assertEqual(result['pages_examined'], [1, 2, 4])
        self.assertEqual(result['pages_not_examined'], 1)
        self.assertEqual(result['scope'], 'sample_only')

    def test_real_cli_will_not_overwrite_pdf_or_existing_report(self):
        original = FIXTURE.read_bytes()
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)/'report.json'
            command = [sys.executable, '-B', str(SCRIPT), '--pdf', str(FIXTURE)]
            subprocess.run(command+['--output', str(output)], capture_output=True, check=True)
            before = output.read_bytes()
            for destination in [output, FIXTURE]:
                result = subprocess.run(command+['--output', str(destination)], capture_output=True)
                self.assertEqual(result.returncode, 2)
            self.assertEqual(output.read_bytes(), before)
            self.assertEqual(FIXTURE.read_bytes(), original)

    def test_invalid_file_is_not_classified_as_scan(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/'invalid.pdf'
            path.write_bytes(b'not a PDF')
            result = subprocess.run([sys.executable, '-B', str(SCRIPT), '--pdf', str(path)],
                                    capture_output=True, text=True)
            self.assertEqual(result.returncode, 2)
            report = json.loads(result.stderr)
            self.assertEqual(report['status'], 'inspection_unavailable')
            self.assertNotIn('pages', report)


if __name__ == '__main__':
    unittest.main()
