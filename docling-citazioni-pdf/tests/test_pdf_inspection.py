"""Conservative per-page clues, sample coverage and preservation; no PDF dependency."""
from contextlib import redirect_stderr
import io
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'docling-citazioni-pdf/scripts'))
import inspect_pdf as inspector


class PdfInspectionTests(unittest.TestCase):
    def test_dominant_image_without_text_is_probable_not_certain_scan(self):
        self.assertEqual(inspector.page_clue(0, .99), 'probable_scan_sparse_or_no_text')

    def test_page_number_only_does_not_masquerade_as_native_text(self):
        self.assertEqual(inspector.page_clue(2, 1.0), 'probable_scan_sparse_or_no_text')

    def test_dominant_image_with_text_keeps_previous_ocr_uncertainty(self):
        self.assertEqual(inspector.page_clue(200, .9), 'dominant_image_and_text_possible_previous_ocr')

    def test_selectable_text_does_not_certify_digital_origin(self):
        self.assertEqual(inspector.page_clue(200, 0), 'text_layer_present_origin_unknown')

    def test_logo_and_blank_page_do_not_become_certain_scans(self):
        self.assertEqual(inspector.page_clue(200, .1), 'text_layer_present_origin_unknown')
        self.assertEqual(inspector.page_clue(0, 0), 'no_text_origin_unknown')
        self.assertEqual(inspector.page_clue(0, .1), 'no_text_origin_unknown')

    def test_invalid_counts_are_rejected(self):
        for value in [-1, True, 1.5, '200']:
            with self.subTest(value=value), self.assertRaises(ValueError):
                inspector.page_clue(value, 1)

    def test_invalid_areas_are_rejected(self):
        for value in [-.1, 1.1, True, float('nan'), float('inf'), '1']:
            with self.subTest(value=value), self.assertRaises(ValueError):
                inspector.page_clue(0, value)

    def test_default_sample_does_not_inspect_every_page_of_long_document(self):
        self.assertEqual(inspector.selected_pages(1), [1])
        self.assertEqual(inspector.selected_pages(2), [1, 2])
        self.assertEqual(inspector.selected_pages(10), [1, 5, 10])

    def test_requested_pages_are_sorted_validated_and_not_silently_duplicated(self):
        self.assertEqual(inspector.selected_pages(10, [10, 2, 6]), [2, 6, 10])
        for requested in [[], [0], [11], [True], [1, 1], ['2']]:
            with self.subTest(requested=requested), self.assertRaises(ValueError):
                inspector.selected_pages(10, requested)

    def test_cli_refuses_to_overwrite_existing_output(self):
        with tempfile.TemporaryDirectory() as folder:
            output = Path(folder)/'original.pdf'
            output.write_bytes(b'original PDF bytes')
            with patch.object(inspector, 'inspect_pdf', return_value={'scope': 'sample_only'}), \
                 patch.object(sys, 'argv', ['inspect_pdf', '--pdf', 'input.pdf', '--output', str(output)]), \
                 redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as caught:
                inspector.main()
            self.assertEqual(caught.exception.code, 2)
            self.assertEqual(output.read_bytes(), b'original PDF bytes')


if __name__ == '__main__':
    unittest.main()
