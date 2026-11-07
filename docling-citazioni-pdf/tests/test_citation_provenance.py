"""Conservative quote-to-provenance tests; no network, paid dependencies or PDF parser."""
import copy
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

HELPER = Path(__file__).resolve().parents[1] / 'docling-citazioni-pdf/scripts/citation_provenance.py'
spec = importlib.util.spec_from_file_location('citation_provenance', HELPER)
cp = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cp)
JSON_SHA, DOC_SHA = 'a' * 64, 'b' * 64


def profile(**overrides):
    value = {'schema_name':'DoclingDocument', 'schema_version':'1.9.0',
             'source_json_sha256':JSON_SHA, 'document_sha256':DOC_SHA,
             'docling_core_version':'2.105.0', 'span_base':'orig',
             'index_unit':'python_codepoint', 'charspan_semantics':'half_open',
             'page_numbering':'physical_1_based',
             'evidence':{name:{'verified':True,'method':'synthetic_fixture_explicit_offsets',
                               'reference':'tests/test_citation_provenance.py'}
                         for name in ('span_base','index_unit','charspan_semantics','page_numbering')}}
    value.update(overrides)
    return value


def document(text='prima seconda', spans=None, orig=None):
    return {'schema_name':'DoclingDocument', 'version':'1.9.0',
            'pages':{str(page):{'page_no':page} for page in range(1,7)},
            'texts':[{'self_ref':'#/texts/0', 'label':'text', 'orig':text if orig is None else orig,
                      'text':text, 'prov':spans if spans is not None else [
                          {'page_no':1,'charspan':[0,5],'bbox':{'l':0,'t':1,'r':4,'b':5}},
                          {'page_no':2,'charspan':[6,13],'bbox':{'l':1,'t':2,'r':3,'b':4}}]}]}


def analyze(doc, quote=None, **kwargs):
    supplied = kwargs.pop('profile', profile())
    return cp.analyze(doc, quote=quote, profile=supplied, document_sha256=DOC_SHA,
                      source_json_sha256=JSON_SHA, **kwargs)


class CitationProvenanceTests(unittest.TestCase):
    def test_first_and_last_quote_use_intersecting_record_not_first_page(self):
        doc = document()
        self.assertEqual(analyze(doc,'prima')['candidate_physical_pages'],[1])
        last = analyze(doc,'seconda')
        self.assertEqual(last['candidate_physical_pages'],[2])
        self.assertFalse(last['citation_verified'])
        self.assertEqual(last['original_verification']['method'],'not_performed')
        self.assertEqual(len(last['matches'][0]['all_provenance']),2)

    def test_spanning_quote_retains_unassigned_space(self):
        result = analyze(document(),'prima seconda')
        self.assertEqual(result['candidate_physical_pages'],[1,2])
        self.assertEqual(result['status'],'partial_provenance_requires_original_check')
        self.assertEqual(result['matches'][0]['uncovered_intervals'],
                         [{'source_interval':[5,6],'text':' ','whitespace_only':True}])

    def test_two_real_world_shapes_do_not_attribute_tail_to_first_page(self):
        for prefix_length, pages in [(198,(4,5)),(204,(5,6))]:
            text = 'A'*prefix_length + ' ' + 'passo finale'
            spans = [{'page_no':pages[0],'charspan':[0,prefix_length]},
                     {'page_no':pages[1],'charspan':[prefix_length+1,len(text)]}]
            doc = document(text,spans)
            result = analyze(doc,'passo finale')
            self.assertEqual(result['candidate_physical_pages'],[pages[1]])

    def test_list_marker_orig_is_used_only_with_evidenced_base(self):
        orig = '1. contenuto con marker'
        doc = document('contenuto con marker',[{'page_no':2,'charspan':[0,len(orig)]}],orig)
        result = analyze(doc,'contenuto')
        self.assertEqual(result['matches'][0]['source_interval'],[3,12])
        self.assertEqual(result['candidate_physical_pages'],[2])
        self.assertEqual(analyze(doc,'contenuto',profile=None)['candidate_physical_pages'],[])

    def test_text_length_fit_never_proves_profile(self):
        for p in [None, {}, profile(index_unit=None), profile(evidence={}), profile(schema_version='9.9')]:
            with self.subTest(profile=p):
                result = analyze(document(),'seconda',profile=p)
                self.assertEqual(result['candidate_physical_pages'],[])
                self.assertFalse(result['citation_verified'])

    def test_hash_binding_and_interval_evidence_are_required(self):
        for field in ['document_sha256','source_json_sha256','schema_name','docling_core_version','charspan_semantics']:
            p = profile()
            p.pop(field)
            result = analyze(document(),'prima',profile=p)
            self.assertTrue(result['profile_errors'])
            self.assertEqual(result['candidate_physical_pages'],[])

    def test_missing_provenance_stays_unverified(self):
        doc = document()
        doc['texts'][0].pop('prov')
        result = analyze(doc,'prima')
        self.assertEqual(result['status'],'unverified_provenance')
        self.assertEqual(result['candidate_physical_pages'],[])

    def test_invalid_records_are_not_silently_discarded(self):
        for bad in [[0,1000],[4,2],[-1,3],[True,3],['0',3]]:
            doc = document(spans=[{'page_no':1,'charspan':[0,5]}, {'page_no':2,'charspan':bad}])
            result = analyze(doc,'prima')
            self.assertEqual(result['status'],'unverified_provenance')
            self.assertTrue(result['matches'][0]['invalid_provenance'])

    def test_invalid_physical_pages_never_become_candidates(self):
        for page in [0,-1,True,'1',999]:
            result = analyze(document('test',[{'page_no':page,'charspan':[0,4]}]),'test')
            self.assertEqual(result['candidate_physical_pages'],[])
            self.assertEqual(result['status'],'unverified_provenance')

    def test_overlapping_provenance_is_partial(self):
        doc = document('abcdef',[{'page_no':1,'charspan':[0,5]},{'page_no':2,'charspan':[3,6]}])
        result = analyze(doc,'cdef')
        self.assertEqual(result['candidate_physical_pages'],[1,2])
        self.assertTrue(result['matches'][0]['overlapping_intervals'])
        self.assertEqual(result['status'],'partial_provenance_requires_original_check')

    def test_quote_ambiguity_returns_all_and_no_selected_page(self):
        doc = document('citato e citato',[{'page_no':1,'charspan':[0,14]}])
        result = analyze(doc,'citato')
        self.assertEqual(result['status'],'ambiguous_quote')
        self.assertEqual(len(result['matches']),2)
        self.assertEqual(result['candidate_physical_pages'],[])
        self.assertNotIn('selected_match_index',result)

    def test_anchor_restriction_resolves_duplicate_quote_between_items(self):
        doc = document('citato',[{'page_no':1,'charspan':[0,6]}])
        other = copy.deepcopy(doc['texts'][0]); other['self_ref']='#/texts/1'; other['prov'][0]['page_no']=2
        doc['texts'].append(other)
        self.assertEqual(analyze(doc,'citato')['status'],'ambiguous_quote')
        self.assertEqual(analyze(doc,'citato',anchors=['#/texts/1'])['candidate_physical_pages'],[2])

    def test_duplicate_anchor_is_rejected(self):
        doc = document(); doc['texts'].append(copy.deepcopy(doc['texts'][0]))
        self.assertEqual(analyze(doc,'prima')['status'],'unverified_duplicate_anchors')

    def test_canonical_accents_quotes_whitespace_and_nonbmp_map_back(self):
        text = '😀 «L’acqua»\n  e\u0301 qui'
        quote = '"L\'acqua" é qui'
        doc = document(text,[{'page_no':2,'charspan':[0,len(text)]}])
        result = analyze(doc,quote)
        match = result['matches'][0]
        self.assertEqual(match['source_interval'],[2,len(text)])
        self.assertEqual(text[slice(*match['source_interval'])],match['source_fragment'])
        self.assertEqual(result['candidate_physical_pages'],[2])

    def test_canonical_reordering_preserves_original_intervals(self):
        text = 'a\u0315\u0300'
        normalized, mapping = cp.normalize_with_map(text)
        self.assertEqual(normalized,'a\u0300\u0315')
        self.assertEqual(mapping,[(0,1),(2,3),(1,2)])
        result = analyze(document(text,[{'page_no':1,'charspan':[0,3]}]),'à\u0315')
        self.assertEqual(result['matches'][0]['source_interval'],[0,3])

    def test_accent_is_not_removed_and_partial_casefold_expansion_is_uncertain(self):
        result = analyze(document('é',[{'page_no':1,'charspan':[0,1]}]),'e')
        self.assertEqual(result['status'],'unverified_normalization_boundary')
        self.assertEqual(result['candidate_physical_pages'],[])

    def test_composed_and_decomposed_partial_accents_fail_identically(self):
        for text in ['é','e\u0301']:
            doc = document(text,[{'page_no':1,'charspan':[0,len(text)]}])
            for quote in ['e','\u0301']:
                with self.subTest(text=repr(text),quote=repr(quote)):
                    result=analyze(doc,quote)
                    self.assertEqual(result['status'],'unverified_normalization_boundary')
                    self.assertEqual(result['candidate_physical_pages'],[])
            self.assertEqual(analyze(doc,'é')['candidate_physical_pages'],[1])
        doc=document('e\u0301',[{'page_no':1,'charspan':[0,2]}])
        for start,end in [(0,1),(1,2)]:
            result=analyze(doc,ranges=[{'anchor':'#/texts/0','base':'orig','index_unit':'python_codepoint',
                                       'start':start,'end':end}])
            self.assertEqual(result['candidate_physical_pages'],[])
            self.assertEqual(result['status'],'unverified_provenance')
        ligature = analyze(document('ﬁ',[{'page_no':1,'charspan':[0,1]}]),'f',casefold=True)
        self.assertEqual(ligature['status'],'unverified_normalization_boundary')
        self.assertEqual(ligature['candidate_physical_pages'],[])
        result = analyze(document('ß',[{'page_no':1,'charspan':[0,1]}]),'s',casefold=True)
        self.assertEqual(result['status'],'unverified_normalization_boundary')
        self.assertEqual(result['candidate_physical_pages'],[])

    def test_casefold_requires_explicit_optin(self):
        doc = document('STRAẞE',[{'page_no':1,'charspan':[0,6]}])
        self.assertEqual(analyze(doc,'strasse')['status'],'quote_not_found')
        self.assertEqual(analyze(doc,'strasse',casefold=True)['candidate_physical_pages'],[1])

    def test_utf16_conversion_and_invalid_surrogate_boundary(self):
        text = 'A😀BC'
        self.assertEqual(cp.index_to_codepoint(text,3,'utf16_code_unit'),2)
        self.assertEqual(cp.codepoint_to_index(text,2,'utf16_code_unit'),3)
        with self.assertRaisesRegex(ValueError,'surrogate'):
            cp.index_to_codepoint(text,2,'utf16_code_unit')
        doc = document(text,[{'page_no':1,'charspan':[0,3]},{'page_no':2,'charspan':[3,5]}])
        result = analyze(doc,'BC',profile=profile(index_unit='utf16_code_unit'))
        self.assertEqual(result['candidate_physical_pages'],[2])
        doc['texts'][0]['prov'][0]['charspan']=[0,2]
        self.assertEqual(analyze(doc,'BC',profile=profile(index_unit='utf16_code_unit'))['status'],'unverified_provenance')

    def test_profile_scope_prevents_unproven_anchor_attribution(self):
        result = analyze(document(),'prima',profile=profile(anchors=['#/texts/99']))
        self.assertEqual(result['candidate_physical_pages'],[])
        self.assertEqual(result['status'],'unverified_provenance')

    def test_malformed_profile_and_inconsistent_page_metadata_fail_closed(self):
        for p in [profile(evidence=[]), profile(anchors='not-a-list'), profile(printed_page_labels=[])]:
            self.assertTrue(analyze(document(),'prima',profile=p)['profile_errors'])
        doc = document()
        doc['pages']['1']['page_no'] = 2
        self.assertEqual(analyze(doc,'prima')['candidate_physical_pages'],[])
        with self.assertRaisesRegex(ValueError,'root_must_be_object'):
            analyze([],'x')
        for metadata in [None,{}, {'page_no':True},{'page_no':1.0},{'page_no':'1'}]:
            doc = document(); doc['pages']['1']=metadata
            result=analyze(doc,'prima')
            self.assertEqual(result['candidate_physical_pages'],[])
            self.assertEqual(result['status'],'unverified_provenance')

    def test_evidence_and_search_scope_are_explicit_not_claims_of_visual_verification(self):
        result=analyze(document(),'absent')
        self.assertEqual(result['status'],'quote_not_found')
        self.assertEqual(result['evidence_status'],'caller_declared_not_independently_checked')
        self.assertTrue(result['reference_strings_checked_for_presence_only'])
        self.assertFalse(result['producer_version_verification']['checked_against_runtime_by_helper'])
        self.assertFalse(result['search_scope']['table_cells_without_self_ref_indexed'])
        self.assertIn('not_proof_of_absence',result['search_scope']['not_found_meaning'])

    def test_physical_and_printed_page_labels_are_distinct(self):
        labels = {'2':{'label':'IV','verified':True,'method':'visual_render','reference':'render-p2.png'}}
        result = analyze(document(),'seconda',profile=profile(printed_page_labels=labels))
        self.assertEqual(result['candidate_physical_pages'],[2])
        self.assertEqual(result['matches'][0]['printed_page_labels']['2']['label'],'IV')
        self.assertFalse(result['citation_verified'])

    def test_cross_item_explicit_ranges_preserve_order_and_unassigned_separator(self):
        doc = document('prima',[{'page_no':1,'charspan':[0,5]}])
        other=copy.deepcopy(doc['texts'][0]); other.update(self_ref='#/texts/1',orig='dopo',text='dopo',prov=[{'page_no':2,'charspan':[0,4]}]);doc['texts'].append(other)
        ranges={'segments':[{'anchor':'#/texts/0','base':'orig','index_unit':'python_codepoint','start':0,'end':5},
                            {'anchor':'#/texts/1','base':'orig','index_unit':'python_codepoint','start':0,'end':4}], 'separator':' '}
        result=analyze(doc,'prima dopo',ranges=ranges)
        self.assertEqual(result['candidate_physical_pages'],[1,2])
        self.assertEqual(result['status'],'candidate_cross_item_mapping_requires_original_check')
        self.assertFalse(result['between_item_separators']['assigned_to_page'])
        self.assertEqual(analyze(doc,'wrong',ranges=ranges)['status'],'unverified_quote_range_mismatch')

    def test_cli_hashes_original_bytes_and_json_bytes(self):
        with tempfile.TemporaryDirectory() as temp:
            folder=Path(temp); original=folder/'source.bin'; source=folder/'docling.json'; p=folder/'profile.json'; out=folder/'audit.json'
            original.write_bytes(b'synthetic-original-fixture')
            source.write_text(json.dumps(document()))
            p.write_text(json.dumps(profile(document_sha256=cp.sha256_bytes(original.read_bytes()),
                                            source_json_sha256=cp.sha256_bytes(source.read_bytes()))))
            completed=subprocess.run([sys.executable,str(HELPER),'--json',str(source),'--document',str(original),
                                      '--profile',str(p),'--quote','seconda','--output',str(out)],capture_output=True,text=True)
            self.assertEqual(completed.returncode,0,completed.stderr)
            result=json.loads(out.read_text())
            self.assertEqual(result['candidate_physical_pages'],[2])
            self.assertEqual(result['document_sha256'],cp.sha256_bytes(original.read_bytes()))
            self.assertFalse(result['citation_verified'])
            self.assertFalse(result['producer_version_verification']['checked_against_runtime_by_helper'])

    def test_cli_never_overwrites_inputs_or_any_existing_output_alias(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)
            original, source, p, ranges = [folder/name for name in ('source.bin','docling.json','profile.json','ranges.json')]
            original.write_bytes(b'synthetic-original-fixture')
            source.write_text(json.dumps(document()))
            p.write_text(json.dumps(profile(document_sha256=cp.sha256_bytes(original.read_bytes()),
                                            source_json_sha256=cp.sha256_bytes(source.read_bytes()))))
            ranges.write_text(json.dumps({'segments':[{'anchor':'#/texts/0','base':'orig',
                          'index_unit':'python_codepoint','start':6,'end':13}]}))
            snapshots = {path: path.read_bytes() for path in (original,source,p,ranges)}
            unrelated = folder/'existing-audit.json'; unrelated.write_bytes(b'existing-audit-preserve')
            snapshots[unrelated] = unrelated.read_bytes()
            hardlink, symlink, dangling = [folder/name for name in ('hardlink.json','symlink.json','dangling.json')]
            os.link(original, hardlink)
            symlink.symlink_to(source)
            absent_target = folder/'must-remain-absent.json'
            dangling.symlink_to(absent_target)
            for alias in [original,source,p,ranges,unrelated,hardlink,symlink,dangling]:
                with self.subTest(output=alias.name):
                    completed = subprocess.run([sys.executable,str(HELPER),'--json',str(source),
                           '--document',str(original),'--profile',str(p),'--ranges',str(ranges),
                           '--quote','seconda','--output',str(alias)],capture_output=True,text=True)
                    self.assertEqual(completed.returncode,2,completed.stderr)
                    self.assertIn('fresh_filename',completed.stderr)
                    self.assertEqual({path:path.read_bytes() for path in snapshots},snapshots)
                    self.assertTrue(dangling.is_symlink())
                    self.assertFalse(absent_target.exists())


if __name__=='__main__':
    unittest.main()
