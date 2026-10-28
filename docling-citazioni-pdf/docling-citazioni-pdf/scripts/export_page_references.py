#!/usr/bin/env python3
"""Create a block-level page view from Docling JSON, without slicing charspans."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def positive_int(value):
    return isinstance(value, int) and not isinstance(value, bool) and value > 0


def render_content(item):
    if isinstance(item.get('text'), str):
        return item['text']
    if isinstance(item.get('data'), dict) and 'table_cells' in item['data']:
        cells = item.get('data', {}).get('table_cells', [])
        lines = ['[Tabella: celle e coordinate nel JSON originale]']
        for cell in cells:
            row, col = cell.get('start_row_offset_idx'), cell.get('start_col_offset_idx')
            end_row, end_col = cell.get('end_row_offset_idx'), cell.get('end_col_offset_idx')
            text = cell.get('text', '')
            lines.append(f'- Cella riga/colonna a base 0 [{row},{col}] → [{end_row},{end_col}), fine esclusa: {text}')
        return '\n'.join(lines)
    if item.get('label') == 'picture':
        return '[Immagine: contenuto e riferimenti nel JSON originale]'
    return '[Elemento strutturato: contenuto nel JSON originale]'


def build(document, source_hash):
    if document.get('schema_name') != 'DoclingDocument':
        raise ValueError('Expected a DoclingDocument JSON, not an index or tool response.')
    page_map = document.get('pages')
    if not isinstance(page_map, dict) or not page_map:
        raise ValueError('No document page metadata: page attribution is unavailable.')
    pages = set()
    for key, value in page_map.items():
        number = value.get('page_no') if isinstance(value, dict) else None
        if not positive_int(number) or str(number) != key:
            raise ValueError('Page key and page_no disagree; refusing to guess numbering.')
        pages.add(number)
    nodes = {}
    for collection in ('texts', 'tables', 'pictures', 'key_value_items', 'form_items', 'groups'):
        for item in document.get(collection, []):
            anchor = item.get('self_ref')
            if not isinstance(anchor, str) or anchor in nodes:
                raise ValueError('Missing or duplicate self_ref in document items.')
            nodes[anchor] = (collection, item)
    ordered, visited, warnings = [], set(), []

    def visit(anchor, ancestry):
        if anchor in ancestry:
            raise ValueError('Cycle in document children.')
        if anchor in visited:
            return
        if anchor not in nodes:
            raise ValueError(f'Unresolved document reference: {anchor}')
        visited.add(anchor)
        collection, item = nodes[anchor]
        if collection != 'groups':
            ordered.append((item, []))
        for child in item.get('children', []):
            visit(child.get('$ref'), ancestry | {anchor})

    for root in ('body', 'furniture'):
        for child in document.get(root, {}).get('children', []):
            visit(child.get('$ref'), set())
    for anchor, (collection, item) in nodes.items():
        if anchor not in visited and collection != 'groups':
            ordered.append((item, ['item_not_reached_from_document_tree']))
            warnings.append({'anchor': anchor, 'issue': 'item_not_reached_from_document_tree'})

    records = []
    for item, issues in ordered:
        issues = list(issues)
        provenance = item.get('prov')
        candidates = set()
        if not isinstance(provenance, list) or not provenance:
            issues.append('missing_provenance')
        else:
            for prov in provenance:
                number = prov.get('page_no') if isinstance(prov, dict) else None
                if not positive_int(number) or number not in pages:
                    issues.append('invalid_or_unknown_page_in_provenance')
                else:
                    candidates.add(number)
        attribution_issues = [x for x in issues if x != 'item_not_reached_from_document_tree']
        status = ('unattributed' if attribution_issues else
                  'multiple_candidate_pages' if len(candidates) > 1 else 'candidate_page')
        records.append({'anchor': item['self_ref'], 'label': item.get('label'),
                        'candidate_pages': sorted(candidates), 'status': status,
                        'issues': issues, 'provenance': provenance,
                        'original_verification': 'not_performed', 'text': render_content(item)})
    lines = ['# Documento con riferimenti alle pagine', '',
             '> Pagine indicate dai metadati Docling; non verificate sul PDF originale. '
             'La numerazione stampata non è stata accertata. Questa vista non riproduce il layout.', '']

    def emit(record, index):
        lines.extend([f'<!-- docling-block-{index} | {record["anchor"]} -->',
                      f'**Blocco {index} — {record["label"]}**', '', record['text'], ''])

    for page in sorted(pages):
        lines.extend([f'## Pagina PDF {page} — indicazione Docling', ''])
        found = [(i,r) for i,r in enumerate(records,1)
                 if r['status'] == 'candidate_page' and r['candidate_pages'] == [page]]
        if not found:
            lines.extend(['[Nessun blocco attribuito esclusivamente a questa pagina; non implica pagina vuota.]', ''])
        for index, record in found:
            emit(record, index)
    multi = [(i,r) for i,r in enumerate(records,1) if r['status'] == 'multiple_candidate_pages']
    if multi:
        lines.extend(['## Blocchi con provenienza su più pagine', ''])
        for index, record in multi:
            lines.extend(['Pagine PDF candidate: '+', '.join(map(str,record['candidate_pages']))+
                          '. Blocco conservato intero; confine non verificato.', ''])
            emit(record, index)
    missing = [(i,r) for i,r in enumerate(records,1) if r['status'] == 'unattributed']
    if missing:
        lines.extend(['## Pagina non attribuibile', ''])
        for index, record in missing:
            emit(record, index)
    markdown = '\n'.join(lines)
    index = {'schema': 'docling-page-references-v1', 'source_json_sha256': source_hash,
             'docling_schema_version': document.get('version'), 'pdf_original_verified': False,
             'numbering': 'Docling page_no; printed labels not established',
             'markdown_sha256': digest(markdown.encode()), 'pages': sorted(pages),
             'warnings': warnings, 'blocks': [{k:v for k,v in r.items() if k != 'text'} for r in records]}
    return markdown, index


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--json', required=True, type=Path)
    parser.add_argument('--output-prefix', required=True, type=Path)
    args = parser.parse_args()
    source = args.json.resolve(strict=True)
    raw = source.read_bytes()
    markdown, index = build(json.loads(raw), digest(raw))
    md = Path(str(args.output_prefix)+'.pagine.md')
    idx = Path(str(args.output_prefix)+'.riferimenti.json')
    for path in (md,idx):
        if path.resolve() == source or path.exists() or path.is_symlink():
            raise ValueError(f'Output already exists or aliases input: {path}')
    with md.open('x', encoding='utf-8', newline='\n') as handle:
        handle.write(markdown)
    with idx.open('x', encoding='utf-8', newline='\n') as handle:
        json.dump(index, handle, ensure_ascii=False, indent=2)
        handle.write('\n')
    print(json.dumps({'markdown': str(md), 'references': str(idx), 'pages': len(index['pages']),
                      'blocks': len(index['blocks']), 'unattributed_blocks':
                      sum(r['status']=='unattributed' for r in index['blocks']),
                      'original_verification': 'not_performed'},ensure_ascii=False))


if __name__ == '__main__':
    main()
