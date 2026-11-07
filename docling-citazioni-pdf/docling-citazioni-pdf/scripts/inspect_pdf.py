#!/usr/bin/env python3
"""Read page structure without OCR; report clues, never certify PDF origin.

Requires pypdfium2. By default samples first/middle/last physical pages. Text
may come from previous OCR. Image bounding rectangles approximate coverage;
they neither prove a scan nor identify readable content. No network is used.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import math
import os
from pathlib import Path
import sys

IMAGE_THRESHOLD = 0.75
SPARSE_TEXT_THRESHOLD = 40


def page_clue(characters, largest_image_fraction):
    if not isinstance(characters, int) or isinstance(characters, bool) or characters < 0:
        raise ValueError('characters_must_be_a_nonnegative_integer')
    if (not isinstance(largest_image_fraction, (int, float))
            or isinstance(largest_image_fraction, bool)
            or not math.isfinite(largest_image_fraction)
            or not 0 <= largest_image_fraction <= 1):
        raise ValueError('image_fraction_must_be_finite_between_zero_and_one')
    if largest_image_fraction >= IMAGE_THRESHOLD:
        return ('probable_scan_sparse_or_no_text' if characters < SPARSE_TEXT_THRESHOLD
                else 'dominant_image_and_text_possible_previous_ocr')
    return 'text_layer_present_origin_unknown' if characters else 'no_text_origin_unknown'


def selected_pages(page_count, requested=None):
    if not isinstance(page_count, int) or isinstance(page_count, bool) or page_count < 1:
        raise ValueError('page_count_must_be_positive')
    if requested is None:
        return sorted({1, (page_count + 1) // 2, page_count})
    if (not requested or any(not isinstance(p, int) or isinstance(p, bool) or not 1 <= p <= page_count
                             for p in requested) or len(set(requested)) != len(requested)):
        raise ValueError('requested_pages_must_be_unique_physical_pages_in_range')
    return sorted(requested)


def sha(path):
    digest = hashlib.sha256()
    with path.open('rb') as source:
        for block in iter(lambda: source.read(1024*1024), b''):
            digest.update(block)
    return digest.hexdigest()


def inspect_pdf(path, pages=None):
    import pypdfium2 as pdfium
    import pypdfium2.raw as raw

    path = Path(path).resolve(strict=True)
    before = sha(path)
    records = []
    pdf = pdfium.PdfDocument(str(path))
    try:
        count = len(pdf)
        examined = selected_pages(count, pages)
        for number in examined:
            page = pdf[number - 1]
            try:
                width, height = page.get_size()
                if width <= 0 or height <= 0:
                    raise ValueError('invalid_page_dimensions')
                text = page.get_textpage()
                try:
                    reported = text.count_chars()
                    useful = sum(not c.isspace() for c in text.get_text_bounded())
                finally:
                    text.close()
                areas = []
                for obj in page.get_objects(filter=[raw.FPDF_PAGEOBJ_IMAGE], max_depth=15):
                    # The same PDFium bounds API is exposed under different names.
                    if hasattr(obj, 'get_bounds'):
                        left, bottom, right, top = obj.get_bounds()
                    elif hasattr(obj, 'get_pos'):  # pypdfium2 4.30: left/bottom/right/top.
                        left, bottom, right, top = obj.get_pos()
                    else:
                        raise RuntimeError('pdf_reader_object_bounds_api_unavailable')
                    area = max(0, min(width, right)-max(0, left)) * max(0, min(height, top)-max(0, bottom))
                    areas.append(min(1.0, area / (width * height)))
                fraction = max(areas, default=0.0)
                records.append({'physical_page': number, 'characters_reported': reported,
                                'non_whitespace_characters': useful, 'image_objects_seen': len(areas),
                                'largest_image_bbox_fraction': round(fraction, 6),
                                'clue': page_clue(useful, fraction)})
            finally:
                page.close()
    finally:
        pdf.close()
    if before != sha(path):
        raise ValueError('source_changed_during_inspection')
    return {'format_version': 1, 'pdf_path': str(path), 'pdf_sha256': before,
            'physical_page_count': count, 'pages_examined': examined,
            'pages_not_examined': count - len(examined),
            'scope': 'all_pages' if len(examined) == count else 'sample_only',
            'pages': records, 'sample_has_different_clues': len({p['clue'] for p in records}) > 1,
            'document_origin_certified': False, 'visual_verification_performed': False,
            'ocr_execution_checked': False, 'ocr_performed_by_helper': False,
            'heuristics': {'dominant_image_bbox_fraction': IMAGE_THRESHOLD,
                           'sparse_text_below_non_whitespace_characters': SPARSE_TEXT_THRESHOLD},
            'limitations': ['Text can be a previous OCR layer; no origin is certified.',
                            'Largest image bbox is approximate; tiles, clipping, rotation, nested forms and overlaps can hide or overstate coverage.',
                            'Blank pages, outlined text and vector graphics can have no extracted text.',
                            'Sampled pages do not establish the type of unexamined pages.'],
            'reader': {'name': 'pypdfium2', 'version': importlib.metadata.version('pypdfium2')}}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pdf', required=True, type=Path)
    parser.add_argument('--pages', type=int, nargs='+')
    parser.add_argument('--output', type=Path, help='Create a new report; no overwrite.')
    args = parser.parse_args()
    try:
        result = inspect_pdf(args.pdf, args.pages)
        payload = json.dumps(result, ensure_ascii=False, indent=2) + '\n'
        if args.output:
            with open(args.output, 'x', encoding='utf-8',
                      opener=lambda path, flags: os.open(path, flags, 0o600)) as stream:
                stream.write(payload)
        else:
            sys.stdout.write(payload)
    except (OSError, ValueError, TypeError, ImportError, RuntimeError) as error:
        parser.exit(2, json.dumps({'status': 'inspection_unavailable', 'error': str(error)}, ensure_ascii=False) + '\n')


if __name__ == '__main__':
    main()
