"""I file MCP lunghi restano fonti, senza ammettere letture arbitrarie."""
import json

from test_e2e_runner import runner


URL = 'https://platform.buddalaw.com/full-documents/privacy/123'
FILE = '/home/test/.claude/projects/test/session/tool-results/toolu_123.txt'


def esecuzione(runner, path=FILE, errore=False):
    ex = runner.Esecuzione(testi=[f'[Garante privacy, doc. web n. 123]({URL})'])
    ex.fonti = [
        {'tool':'search_case_law', 'output':f'<persisted-output>\nOutput too large (60.3KB). Full output saved to: {FILE}\n', 'is_error':False},
        {'tool':'Read', 'argomenti':{'file_path':path}, 'output':'1\t'+json.dumps({'public_url':URL}), 'is_error':errore},
    ]
    return ex


def test_read_di_output_mcp_claude_prova_il_link(runner):
    ex = esecuzione(runner)
    assert runner.controlli_generali(ex)[0][1]
    assert any(obj.get('public_url') == URL for obj in runner.oggetti_fonte(ex))


def test_percorso_solo_prefisso_non_prova_la_fonte(runner):
    ex = esecuzione(runner, path=FILE[:-4])
    assert not runner.controlli_generali(ex)[0][1]


def test_read_fallito_non_prova_la_fonte(runner):
    assert not runner.controlli_generali(esecuzione(runner, errore=True))[0][1]


def test_read_non_restituito_da_mcp_non_prova_la_fonte(runner):
    ex = esecuzione(runner)
    ex.fonti[0]['output'] = 'La fonte non ha restituito alcun file.'
    assert not runner.controlli_generali(ex)[0][1]


def test_output_opencode_da_metadata_resta_fonte(runner):
    ex = esecuzione(runner, path='/dati/tool-output/tool_123')
    ex.fonti[0].update(output='Output troncato', metadata={'outputPath':'/dati/tool-output/tool_123'})
    assert runner.controlli_generali(ex)[0][1]
