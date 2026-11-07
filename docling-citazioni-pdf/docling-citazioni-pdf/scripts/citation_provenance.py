#!/usr/bin/env python3
"""Find quote spans and audit candidate Docling provenance; never verify the PDF itself.

Only stdlib is used. Run --help for the CLI. Index semantics are accepted solely
from an explicitly evidenced, schema/version/hash-bound profile, never from fit.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import sys
import unicodedata

UNITS = {'python_codepoint', 'utf16_code_unit'}
QUOTE_MAP = {**dict.fromkeys('‘’‛ʼ＇', "'"), **dict.fromkeys('“”„‟«»＂', '"')}


def sha256_bytes(value):
    return hashlib.sha256(value).hexdigest()


def integer(value):
    return isinstance(value, int) and not isinstance(value, bool)


def check_unicode(text):
    if any(0xD800 <= ord(char) <= 0xDFFF for char in text):
        raise ValueError('unpaired_surrogate_in_source')


def normalize_with_map(text, casefold=False):
    """Canonical NFD, quote equivalence and collapsed whitespace with source spans.

    Every normalized code point maps to a half-open interval in the ORIGINAL
    Python string. Canonical combining-mark reorder preserves each origin.
    Expansion boundaries are validated separately before accepting a match.
    """
    check_unicode(text)
    units = []
    for index, char in enumerate(text):
        replacement = QUOTE_MAP.get(char, char)
        if casefold:
            replacement = replacement.casefold()
        for decomposed in unicodedata.normalize('NFD', replacement):
            entry = (decomposed, (index, index + 1))
            combining = unicodedata.combining(decomposed)
            position = len(units)
            if combining:
                while position and unicodedata.combining(units[position-1][0]) > combining:
                    position -= 1
            units.insert(position, entry)
    output, mapping = [], []
    for char, interval in units:
        if char.isspace():
            if output and output[-1] == ' ':
                previous = mapping[-1]
                mapping[-1] = (min(previous[0], interval[0]), max(previous[1], interval[1]))
            else:
                output.append(' ')
                mapping.append(interval)
        else:
            output.append(char)
            mapping.append(interval)
    return ''.join(output), mapping


def index_to_codepoint(text, index, unit):
    """Convert only valid boundaries; reject a UTF-16 index inside a surrogate pair."""
    check_unicode(text)
    if not integer(index) or index < 0:
        raise ValueError('index_must_be_nonnegative_integer')
    if unit == 'python_codepoint':
        if index > len(text):
            raise ValueError('charspan_out_of_range')
        return index
    if unit != 'utf16_code_unit':
        raise ValueError('index_unit_not_supported')
    offset = 0
    for position, char in enumerate(text):
        if index == offset:
            return position
        width = 2 if ord(char) > 0xFFFF else 1
        if offset < index < offset + width:
            raise ValueError('utf16_boundary_splits_surrogate_pair')
        offset += width
    if index == offset:
        return len(text)
    raise ValueError('charspan_out_of_range')


def codepoint_to_index(text, index, unit):
    index_to_codepoint(text, index, 'python_codepoint')
    if unit == 'python_codepoint':
        return index
    if unit == 'utf16_code_unit':
        return sum(2 if ord(char) > 0xFFFF else 1 for char in text[:index])
    raise ValueError('index_unit_not_supported')


def combining_boundary_flags(text, start, end):
    """Reject partial canonical combining sequences; this is not full UAX #29."""
    flags = []
    if start < len(text) and unicodedata.category(text[start]).startswith('M'):
        flags.append('selection_starts_inside_or_with_combining_sequence')
    if end < len(text) and unicodedata.category(text[end]).startswith('M'):
        flags.append('selection_ends_before_following_combining_mark')
    return flags


def find_matches(text, quote, casefold=False):
    normalized, mapping = normalize_with_map(text, casefold)
    needle, _ = normalize_with_map(quote, casefold)
    if not needle or not needle.strip():
        raise ValueError('quote_must_contain_nonwhitespace_text')
    matches = []
    start = 0
    while True:
        position = normalized.find(needle, start)
        if position < 0:
            break
        selected = mapping[position:position+len(needle)]
        left, right = min(i[0] for i in selected), max(i[1] for i in selected)
        actual, _ = normalize_with_map(text[left:right], casefold)
        flags = combining_boundary_flags(text, left, right)
        if actual != needle:
            flags.append('match_cuts_normalization_expansion_or_combining_cluster')
        matches.append({'normalized_interval': [position, position+len(needle)],
                        'source_interval': [left, right], 'source_index_unit': 'python_codepoint',
                        'source_fragment': text[left:right], 'normalization_mapping': [list(i) for i in selected],
                        'mapping_boundary_valid': not flags, 'mapping_flags': flags})
        start = position + 1  # Include overlapping occurrences rather than selecting the first.
    return matches


def evidence_valid(value):
    return (isinstance(value, dict) and value.get('verified') is True
            and isinstance(value.get('method'), str) and bool(value['method'].strip())
            and isinstance(value.get('reference'), str) and bool(value['reference'].strip()))


def validate_profile(profile, document, source_json_sha256, document_sha256):
    if not isinstance(profile, dict):
        return ['explicit_profile_not_supplied']
    errors = []
    for field, expected in [('schema_name', document.get('schema_name')),
                            ('schema_version', document.get('version')),
                            ('source_json_sha256', source_json_sha256), ('document_sha256', document_sha256)]:
        if not expected or profile.get(field) != expected:
            errors.append(field + '_binding_missing_or_mismatch')
    if not isinstance(profile.get('docling_core_version'), str) or not profile['docling_core_version'].strip():
        errors.append('docling_core_version_evidence_missing')
    if profile.get('span_base') not in ('orig', 'text'):
        errors.append('span_base_not_established')
    if profile.get('index_unit') not in UNITS:
        errors.append('index_unit_not_established')
    if profile.get('charspan_semantics') != 'half_open':
        errors.append('half_open_interval_semantics_not_established')
    if profile.get('page_numbering') != 'physical_1_based':
        errors.append('physical_page_numbering_not_established')
    evidence = profile.get('evidence') if isinstance(profile.get('evidence'), dict) else {}
    for field in ('span_base', 'index_unit', 'page_numbering', 'charspan_semantics'):
        if not evidence_valid(evidence.get(field)):
            errors.append(field + '_supporting_evidence_missing')
    if 'anchors' in profile and (not isinstance(profile['anchors'], list)
            or any(not isinstance(anchor, str) for anchor in profile['anchors'])):
        errors.append('anchor_evidence_scope_must_be_list_of_strings')
    if 'printed_page_labels' in profile and not isinstance(profile['printed_page_labels'], dict):
        errors.append('printed_page_labels_must_be_object')
    return errors


def collect_items(document):
    found = {}
    duplicates = set()

    def visit(value):
        if isinstance(value, dict):
            anchor = value.get('self_ref')
            if isinstance(anchor, str) and any(isinstance(value.get(base), str) for base in ('orig', 'text')):
                if anchor in found:
                    duplicates.add(anchor)
                else:
                    found[anchor] = value
            for child in value.values():
                visit(child)
        elif isinstance(value, list):
            for child in value:
                visit(child)
    visit(document)
    return found, duplicates


def complement(start, end, intervals):
    cursor, gaps = start, []
    for left, right in sorted(intervals):
        left, right = max(start, left), min(end, right)
        if right <= left:
            continue
        if left > cursor:
            gaps.append([cursor, left])
        cursor = max(cursor, right)
    if cursor < end:
        gaps.append([cursor, end])
    return gaps


def provenance_for_match(item, base, match, document, profile, profile_errors):
    text = item[base]
    result = {'anchor': item.get('self_ref'), 'label': item.get('label'), 'span_base': base,
              'raw_orig': item.get('orig'), 'raw_text': item.get('text'), **match,
              'all_provenance': item.get('prov'), 'bbox_is_character_coordinates': False,
              'candidate_physical_pages': [], 'intersections': [], 'uncovered_intervals': [],
              'overlapping_intervals': [], 'invalid_provenance': [], 'printed_page_labels': {},
              'original_verification': {'method': 'not_performed', 'visual_verification_performed': False}}
    if profile_errors:
        result.update(status='unverified_profile', flags=profile_errors)
        return result
    if not match['mapping_boundary_valid']:
        result.update(status='unverified_mapping_boundary', flags=match['mapping_flags'])
        return result
    if base != profile['span_base']:
        result.update(status='unverified_span_base', flags=['selected_base_differs_from_evidenced_base'])
        return result
    anchor_scope = profile.get('anchors')
    if anchor_scope is not None and item.get('self_ref') not in anchor_scope:
        result.update(status='unverified_profile_scope', flags=['anchor_outside_profile_evidence_scope'])
        return result
    raw = item.get('prov')
    if not isinstance(raw, list) or not raw:
        result.update(status='unverified_missing_provenance', flags=['missing_or_empty_provenance'])
        return result
    start, end = match['source_interval']
    intervals, pieces = [], []
    for position, prov in enumerate(raw):
        try:
            if not isinstance(prov, dict):
                raise ValueError('provenance_record_not_object')
            span, page = prov.get('charspan'), prov.get('page_no')
            if not isinstance(span, (list, tuple)) or len(span) != 2:
                raise ValueError('charspan_not_pair')
            left = index_to_codepoint(text, span[0], profile['index_unit'])
            right = index_to_codepoint(text, span[1], profile['index_unit'])
            if right < left:
                raise ValueError('charspan_reversed')
            if not integer(page) or page < 1:
                raise ValueError('page_not_positive_integer')
            pages_metadata = document.get('pages')
            if not isinstance(pages_metadata, dict) or str(page) not in pages_metadata:
                raise ValueError('page_not_present_in_document_metadata')
            page_metadata = pages_metadata[str(page)]
            if (not isinstance(page_metadata, dict) or not integer(page_metadata.get('page_no'))
                    or page_metadata['page_no'] < 1 or page_metadata['page_no'] != page):
                raise ValueError('page_key_and_metadata_disagree')
            overlap = [max(start, left), min(end, right)]
            if overlap[0] < overlap[1]:
                pieces.append({'provenance_index': position, 'page_no_candidate': page,
                               'raw_charspan': list(span), 'raw_index_unit': profile['index_unit'],
                               'source_interval': [left, right], 'quote_intersection': overlap,
                               'bbox_raw': prov.get('bbox'), 'bbox_is_character_coordinates': False})
                intervals.append(tuple(overlap))
        except (ValueError, TypeError) as error:
            result['invalid_provenance'].append({'provenance_index': position, 'reason': str(error), 'raw': prov})
    for i, first in enumerate(pieces):
        for second in pieces[i+1:]:
            left = max(first['quote_intersection'][0], second['quote_intersection'][0])
            right = min(first['quote_intersection'][1], second['quote_intersection'][1])
            if left < right:
                result['overlapping_intervals'].append({'source_interval': [left, right],
                     'provenance_indices': [first['provenance_index'], second['provenance_index']],
                     'page_candidates': [first['page_no_candidate'], second['page_no_candidate']]})
    result['intersections'] = pieces
    result['candidate_physical_pages'] = sorted({piece['page_no_candidate'] for piece in pieces})
    result['uncovered_intervals'] = [{'source_interval': gap, 'text': text[gap[0]:gap[1]],
                                     'whitespace_only': text[gap[0]:gap[1]].isspace()}
                                    for gap in complement(start, end, intervals)]
    for page in result['candidate_physical_pages']:
        supplied = profile.get('printed_page_labels', {}).get(str(page))
        if (evidence_valid(supplied) and supplied.get('method') == 'visual_render'
                and isinstance(supplied.get('label'), str)):
            result['printed_page_labels'][str(page)] = {'label': supplied['label'],
                 'verification': 'visual_evidence_supplied_by_caller_not_checked_by_helper',
                 'reference': supplied['reference']}
    flags = []
    if result['invalid_provenance']:
        flags.append('invalid_provenance_records')
    if result['uncovered_intervals']:
        flags.append('quote_contains_unassigned_characters')
    if result['overlapping_intervals']:
        flags.append('quote_has_overlapping_provenance')
    result['flags'] = flags
    result['status'] = ('unverified_invalid_provenance' if result['invalid_provenance'] else
                        'partial_uncovered_or_overlapping' if flags else 'candidate_mapping_requires_original_check')
    return result


def analyze(document, *, quote=None, profile=None, document_sha256=None, source_json_sha256=None,
            anchors=None, ranges=None, casefold=False):
    """Analyze caller-supplied Docling data. Hashes are verified from bytes by the CLI."""
    if not isinstance(document, dict):
        raise ValueError('docling_json_root_must_be_object')
    profile_errors = validate_profile(profile, document, source_json_sha256, document_sha256)
    items, duplicate_anchors = collect_items(document)
    output = {'format_version': 1, 'document_sha256': document_sha256, 'source_json_sha256': source_json_sha256,
              'hash_verification_method': 'supplied_to_analyze; CLI independently hashes both input files',
              'schema': {'name': document.get('schema_name'), 'version': document.get('version')},
              'profile': profile, 'profile_errors': profile_errors,
              'profile_validation_method': 'explicit_evidence_declarations_and_exact_hash_schema_bindings; no_length_fit_inference',
              'evidence_status': 'caller_declared_not_independently_checked',
              'reference_strings_checked_for_presence_only': True,
              'schema_validation': 'embedded_name_and_version_binding_checked; full_schema_not_validated',
              'producer_version_verification': {'docling_core_version': profile.get('docling_core_version') if isinstance(profile, dict) else None,
                    'source': 'caller_profile_declaration', 'checked_against_runtime_by_helper': False},
              'normalization': {'form': 'NFD', 'unicode_version': unicodedata.unidata_version,
                                'casefold': casefold, 'equivalences': ['listed_curly_apostrophes', 'listed_double_quotes', 'collapsed_unicode_whitespace'],
                                'accents_preserved': True, 'mapping_unit': 'python_codepoint',
                                'boundary_validation_scope': 'canonical_combining_sequences_and_normalization_expansions; not_full_UAX29_grapheme_or_ZWJ_segmentation'},
              'search_scope': {'items': 'unique_self_ref_with_orig_or_text_strings',
                               'table_cells_without_self_ref_indexed': False,
                               'order': 'JSON_traversal_not_visual_reading_order',
                               'not_found_meaning': 'not_found_in_this_scope; not_proof_of_absence_from_document'},
              'quote': quote, 'matches': [], 'candidate_physical_pages': [],
              'original_verification': {'method': 'not_performed', 'visual_verification_performed': False},
              'citation_verified': False, 'status': 'unverified', 'flags': [],
              'bbox_is_character_coordinates': False}
    if duplicate_anchors:
        output.update(status='unverified_duplicate_anchors', flags=sorted(duplicate_anchors))
        return output
    if ranges is not None:
        segments = ranges.get('segments') if isinstance(ranges, dict) else ranges
        if not isinstance(segments, list) or not segments:
            raise ValueError('ranges_requires_nonempty_segments_list')
        fragments = []
        for segment in segments:
            if not isinstance(segment, dict):
                raise ValueError('explicit_range_segment_must_be_object')
            anchor, base, unit = segment.get('anchor'), segment.get('base'), segment.get('index_unit')
            item = items.get(anchor)
            if not item or base not in ('orig', 'text') or not isinstance(item.get(base), str):
                raise ValueError('explicit_range_anchor_or_base_unavailable')
            text = item[base]
            start = index_to_codepoint(text, segment.get('start'), unit)
            end = index_to_codepoint(text, segment.get('end'), unit)
            if start >= end:
                raise ValueError('explicit_range_must_be_nonempty_and_ordered')
            fragment = text[start:end]
            fragments.append(fragment)
            boundary_flags = combining_boundary_flags(text, start, end)
            match = {'source_interval': [start, end], 'source_index_unit': 'python_codepoint',
                     'source_fragment': fragment, 'selection_input': segment,
                     'mapping_boundary_valid': not boundary_flags, 'mapping_flags': boundary_flags,
                     'normalization_mapping': None}
            output['matches'].append(provenance_for_match(item, base, match, document, profile, profile_errors))
        separator = ranges.get('separator', ' ') if isinstance(ranges, dict) else ' '
        if not isinstance(separator, str):
            raise ValueError('range_separator_must_be_string')
        output['selected_text'] = separator.join(fragments)
        output['selection_order'] = 'caller_explicit_ranges; not_inferred_visual_reading_order'
        output['between_item_separators'] = {'text': separator, 'assigned_to_page': False}
        if quote is not None and normalize_with_map(quote, casefold)[0] != normalize_with_map(output['selected_text'], casefold)[0]:
            output.update(status='unverified_quote_range_mismatch', flags=['quote_does_not_match_explicit_ranges'])
            return output
        output['flags'].append('cross_item_selection_requires_original_check')
    else:
        if quote is None:
            raise ValueError('quote_or_explicit_ranges_required')
        for anchor, item in items.items():
            if anchors and anchor not in anchors:
                continue
            bases = [profile['span_base']] if not profile_errors else ['orig', 'text']
            seen_texts = set()
            for base in bases:
                text = item.get(base)
                if not isinstance(text, str) or text in seen_texts:
                    continue
                seen_texts.add(text)
                for match in find_matches(text, quote, casefold):
                    output['matches'].append(provenance_for_match(item, base, match, document, profile, profile_errors))
        exact = [match for match in output['matches'] if match['mapping_boundary_valid']]
        if len(exact) != 1:
            output['status'] = 'ambiguous_quote' if len(exact) > 1 else 'unverified_normalization_boundary' if output['matches'] else 'quote_not_found'
            output['flags'].append('no_automatic_match_selection')
            return output
        output['selected_match_index'] = output['matches'].index(exact[0])
    selected = output['matches'] if ranges is not None else [output['matches'][output['selected_match_index']]]
    output['candidate_physical_pages'] = sorted({page for match in selected for page in match['candidate_physical_pages']})
    statuses = {match['status'] for match in selected}
    if any(status.startswith('unverified') for status in statuses):
        output['status'] = 'unverified_provenance'
    elif any(status.startswith('partial') for status in statuses):
        output['status'] = 'partial_provenance_requires_original_check'
    elif ranges is not None and len(selected) > 1:
        output['status'] = 'candidate_cross_item_mapping_requires_original_check'
    else:
        output['status'] = 'candidate_mapping_requires_original_check'
    return output


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--json', required=True, type=Path, dest='json_path')
    parser.add_argument('--document', required=True, type=Path, help='Original/staged document to hash; no PDF text is parsed by this helper.')
    parser.add_argument('--profile', type=Path, help='Explicit hash-bound index/base/page evidence; absent means no page attribution.')
    parser.add_argument('--quote')
    parser.add_argument('--anchor', action='append', help='Restrict search; repeat for several anchors.')
    parser.add_argument('--ranges', type=Path, help='JSON list or {segments:[{anchor,base,start,end,index_unit}],separator:" "}.')
    parser.add_argument('--casefold', action='store_true', help='Explicitly enable Unicode case folding; expansions retain source spans.')
    parser.add_argument('--output', type=Path, help='Create a NEW audit file only; any existing file or symlink is refused.')
    args = parser.parse_args()
    try:
        source_bytes = args.json_path.read_bytes()
        original_bytes = args.document.read_bytes()
        document = json.loads(source_bytes)
        profile = json.loads(args.profile.read_text()) if args.profile else None
        ranges = json.loads(args.ranges.read_text()) if args.ranges else None
        result = analyze(document, quote=args.quote, anchors=args.anchor, ranges=ranges, casefold=args.casefold,
                         profile=profile, document_sha256=sha256_bytes(original_bytes), source_json_sha256=sha256_bytes(source_bytes))
        result.update(document_path=str(args.document.resolve()), source_json_path=str(args.json_path.resolve()),
                      hash_verification_method='sha256_of_original_document_bytes_and_original_json_bytes')
        text = json.dumps(result, ensure_ascii=False, indent=2) + '\n'
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            try:
                with open(args.output, 'x', encoding='utf-8',
                          opener=lambda path, flags: os.open(path, flags, 0o600)) as stream:
                    stream.write(text)
            except FileExistsError as error:
                raise ValueError('output_already_exists_choose_a_fresh_filename; existing files, hardlinks and symlinks are never overwritten') from error
        else:
            sys.stdout.write(text)
    except (OSError, ValueError, TypeError, KeyError) as error:
        parser.exit(2, json.dumps({'status': 'input_error', 'error': str(error)}, ensure_ascii=False) + '\n')


if __name__ == '__main__':
    main()
