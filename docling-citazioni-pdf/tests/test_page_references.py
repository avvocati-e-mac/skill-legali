import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1]/'docling-citazioni-pdf/scripts/export_page_references.py'
spec = importlib.util.spec_from_file_location('page_refs', SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def fixture():
    return {'schema_name':'DoclingDocument','version':'test',
            'pages':{'1':{'page_no':1},'2':{'page_no':2},'3':{'page_no':3}},
            'body':{'children':[{'$ref':'#/texts/1'},{'$ref':'#/texts/0'}]},
            'texts':[{'self_ref':'#/texts/0','label':'text','text':'secondo 😀',
                      'prov':[{'page_no':1,'charspan':[0,9]}]},
                     {'self_ref':'#/texts/1','label':'text','text':'primo',
                      'prov':[{'page_no':1,'charspan':[0,5]}]}]}


class PageReferencesTests(unittest.TestCase):
    def test_tree_order_source_unchanged_and_unverified(self):
        doc=fixture(); original=copy.deepcopy(doc)
        md,index=module.build(doc,'abc')
        self.assertLess(md.index('primo'),md.index('secondo 😀'))
        self.assertEqual(doc,original)
        self.assertFalse(index['pdf_original_verified'])
        self.assertIn('non implica pagina vuota',md)

    def test_cross_page_block_is_whole_and_not_assigned_to_first_page(self):
        doc=fixture();doc['texts'][0]['prov']=[{'page_no':1,'charspan':[0,3]},
                                            {'page_no':2,'charspan':[3,9]}]
        md,index=module.build(doc,'abc')
        block=next(x for x in index['blocks'] if x['anchor']=='#/texts/0')
        self.assertEqual(block['candidate_pages'],[1,2])
        self.assertEqual(block['status'],'multiple_candidate_pages')
        self.assertEqual(md.count('secondo 😀'),1)
        self.assertGreater(md.index('secondo 😀'),md.index('## Blocchi con provenienza'))
        self.assertEqual(block['provenance'],doc['texts'][0]['prov'])

    def test_invalid_or_missing_provenance_keeps_uncertainty(self):
        doc=fixture();doc['texts'][0]['prov']=[{'page_no':1},{'page_no':99}]
        doc['texts'][1].pop('prov')
        md,index=module.build(doc,'abc')
        self.assertTrue(all(x['status']=='unattributed' for x in index['blocks']))
        self.assertIn('Pagina non attribuibile',md)
        doc['texts'][0]['prov']=[{'page_no':True}]
        _,index=module.build(doc,'abc')
        self.assertEqual(index['blocks'][1]['candidate_pages'],[])

    def test_unreachable_item_is_retained(self):
        doc=fixture();doc['body']['children'].pop()
        md,index=module.build(doc,'abc')
        self.assertIn('secondo 😀',md)
        self.assertEqual(index['warnings'][0]['anchor'],'#/texts/0')

    def test_table_cells_are_preserved_and_references_checked(self):
        doc=fixture();doc['tables']=[{'self_ref':'#/tables/0','label':'document_index',
                'prov':[{'page_no':2}], 'data':{'table_cells':[{'text':'A | B',
                'start_row_offset_idx':0,'start_col_offset_idx':0,
                'end_row_offset_idx':2,'end_col_offset_idx':1}]}}]
        doc['body']['children'].append({'$ref':'#/tables/0'})
        md,_=module.build(doc,'abc')
        self.assertIn('A | B',md)
        self.assertIn('[0,0] → [2,1)',md)
        doc['body']['children'].append({'$ref':'#/texts/99'})
        with self.assertRaisesRegex(ValueError,'Unresolved'):
            module.build(doc,'abc')

    def test_cli_never_overwrites_input_or_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            source=Path(tmp)/'source.json';raw=json.dumps(fixture()).encode();source.write_bytes(raw)
            args=[sys.executable,str(SCRIPT),'--json',str(source),'--output-prefix',str(Path(tmp)/'out')]
            first=subprocess.run(args,capture_output=True,text=True)
            self.assertEqual(first.returncode,0,first.stderr)
            md=Path(tmp)/'out.pagine.md';before=md.read_bytes()
            second=subprocess.run(args,capture_output=True,text=True)
            self.assertNotEqual(second.returncode,0)
            self.assertEqual(md.read_bytes(),before)
            self.assertEqual(source.read_bytes(),raw)


if __name__=='__main__':
    unittest.main()
