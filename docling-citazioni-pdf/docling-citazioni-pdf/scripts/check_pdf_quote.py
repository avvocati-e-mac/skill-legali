#!/usr/bin/env python3
"""Check quoted text against selected physical PDF pages, not visual/semantic truth.

Requires pypdfium2. Never performs OCR, uses Docling offsets or sends network
requests. Quote normalization and boundary checks are shared with the provenance
helper. JSON reports deliberately never certify a citation or its meaning.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import sys

from citation_provenance import find_matches


def match_pages(page_texts, quote):
    """Map all matches to actual extracted page intervals, keeping ambiguity."""
    pages = list(page_texts)
    if (not pages or any(not isinstance(p, int) or isinstance(p, bool) or p < 1 for p in pages)
            or pages != list(range(pages[0], pages[-1] + 1))):
        raise ValueError('pages_must_be_positive_contiguous_and_in_ascending_order')
    fragments, boundaries, offset = [], [], 0
    for page, text in page_texts.items():
        if not isinstance(text, str):
            raise ValueError('page_text_must_be_string')
        boundaries.append((page, offset, offset + len(text)))
        fragments.append(text)
        offset += len(text) + 1  # A newline separates pages; it has no page owner.
    combined = '\n'.join(fragments)
    matches = []
    for match in find_matches(combined, quote):
        start, end = match['source_interval']
        locations = [{'physical_page': page,
                      'page_text_interval': [max(start, left) - left, min(end, right) - left]}
                     for page, left, right in boundaries if max(start, left) < min(end, right)]
        matches.append({**match, 'physical_pages': [v['physical_page'] for v in locations],
                        'page_locations': locations})
    usable = [m for m in matches if m['mapping_boundary_valid'] and m['physical_pages']]
    status = ('text_not_found' if not matches else
              'unverified_text_boundaries' if len(usable) != len(matches) else
              'ambiguous_text_match' if len(matches) > 1 else 'text_match_found')
    return {'status': status, 'pages_examined': pages, 'matches': matches,
            'selected_physical_pages': usable[0]['physical_pages']
                if status == 'text_match_found' else [],
            'method': 'pdf_text_layer', 'citation_verified': False,
            'visual_verification_performed': False, 'semantic_support_checked': False,
            'printed_page_labels_checked': False,
            'normalization': 'NFD; listed quote equivalences; collapsed whitespace; case/accents/numbers preserved',
            'not_found_scope': 'selected_pages_and_PDF_text_layer_only; not_OCR_or_image_content'}


def check_pdf(path, pages, quote):
    import pypdfium2 as pdfium

    path = Path(path).resolve(strict=True)
    before = hashlib.sha256(path.read_bytes()).hexdigest()
    # Validate before opening pages. A non-contiguous selection could join
    # unrelated paragraphs while pretending that they form one quotation.
    match_pages(dict.fromkeys(pages, ''), quote)
    if len(set(pages)) != len(pages):
        raise ValueError('duplicate_pages_not_allowed')
    texts = {}
    pdf = pdfium.PdfDocument(str(path))
    try:
        count = len(pdf)
        if any(page > count for page in pages):
            raise ValueError('physical_page_out_of_range')
        for number in pages:
            page = pdf[number - 1]
            try:
                text = page.get_textpage()
                try:
                    texts[number] = text.get_text_range()
                finally:
                    text.close()
            finally:
                page.close()
    finally:
        pdf.close()
    after = hashlib.sha256(path.read_bytes()).hexdigest()
    if after != before:
        raise ValueError('source_changed_during_verification')
    return {'format_version': 1, 'pdf_path': str(path), 'pdf_sha256': before,
            'physical_page_count': count, 'quote_requested': quote,
            'reader': {'name': 'pypdfium2', 'version': importlib.metadata.version('pypdfium2')},
            **match_pages(texts, quote)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pdf', required=True, type=Path)
    parser.add_argument('--pages', required=True, type=int, nargs='+')
    parser.add_argument('--quote', required=True)
    parser.add_argument('--output', type=Path, help='Create a new report; never overwrite.')
    args = parser.parse_args()
    try:
        result = check_pdf(args.pdf, args.pages, args.quote)
        payload = json.dumps(result, ensure_ascii=False, indent=2) + '\n'
        if args.output:
            with open(args.output, 'x', encoding='utf-8',
                      opener=lambda path, flags: os.open(path, flags, 0o600)) as stream:
                stream.write(payload)
        else:
            sys.stdout.write(payload)
    except (OSError, ValueError, TypeError, ImportError, RuntimeError) as error:
        parser.exit(2, json.dumps({'status': 'check_unavailable', 'error': str(error)}, ensure_ascii=False) + '\n')


if __name__ == '__main__':
    main()
