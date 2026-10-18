"""Attacchi riproducibili al valutatore, senza modelli o rete."""
import json
import sys

import pytest

from test_e2e_runner import runner


def source(runner, tool, output, args=None):
    return {'tool': tool, 'output': json.dumps(output, ensure_ascii=False),
            'argomenti': args or {}, 'is_error': False}


def run_ok(runner):
    return runner.Esecuzione(testi=['La risposta è in italiano e considera il caso.'],
                            testo_finale='La risposta è in italiano e considera il caso.')


def test_inventario_ridotto_modifica_solo_il_json(runner, tmp_path):
    original = (runner.SKILL_DIR / 'SKILL.md').read_text()
    dest = runner.prepara_skill('v9-ridotta', tmp_path / 'copy')
    text = (dest / 'SKILL.md').read_text()
    inventory = next(json.loads(m.group(1)) for m in runner.re.finditer(
        r'```json\s*\n(.*?)\n```', text, runner.re.S)
        if 'inventario_tool_buddalaw' in m.group(1))
    assert 'search_similar_cases' not in inventory['inventario_tool_buddalaw']
    assert 'search_similar_cases' in text  # il tool resta nella procedura
    assert (runner.SKILL_DIR / 'SKILL.md').read_text() == original


def test_url_dalle_istruzioni_non_e_fonte(runner):
    url = 'https://platform.buddalaw.com/full-documents/civile/ESEMPIO'
    ex = run_ok(runner)
    ex.testi = [f'[Cass. n. 123/2024]({url})']
    ex.risultati = [f'Istruzioni ed esempio: {url}']
    ex.fonti = [source(runner, 'skill', {'content': url})]
    assert not runner.controlli_generali(ex)[0][1]


def test_url_non_puo_passare_come_prefisso_di_un_altro(runner):
    url = 'https://platform.buddalaw.com/full-documents/civile/123'
    ex = run_ok(runner)
    ex.testi = [f'[Cass. n. 123/2024]({url})']
    ex.fonti = [source(runner, 'search_case_law', {'public_url':url+'4'})]
    ex.risultati = [ex.fonti[0]['output']]
    assert not runner.controlli_generali(ex)[0][1]


def test_virgolette_brevi_non_catturano_prosa_intermedia(runner):
    ex = run_ok(runner)
    ex.testi = ['Scrivo "titolo" e poi un lungo paragrafo di analisi che non è una citazione e termina con la parola "fine".']
    checks = runner.controlli_specifici({'virgolettati_fedeli': True,
                                       'richiede_virgolettato': False}, ex)
    assert all(ok for _, ok, _ in checks)


def test_domanda_di_citazione_senza_virgolettato_non_passa(runner):
    ex = run_ok(runner)
    checks = runner.controlli_specifici({'virgolettati_fedeli': True}, ex)
    assert not all(ok for _, ok, _ in checks)


def test_virgolettato_dalla_sintesi_non_e_testo_della_fonte(runner):
    quote = 'Questa frase compare soltanto nella sintesi automatica della decisione.'
    ex = run_ok(runner)
    ex.testi = ['«'+quote+'»']
    ex.fonti = [source(runner, 'search_case_law', {'results':[{'sintesi':quote, 'testo':'Diverso testo della motivazione.'}]})]
    ex.risultati = [ex.fonti[0]['output']]
    assert not all(ok for _,ok,_ in runner.controlli_specifici({'virgolettati_fedeli': True},ex))


def test_numero_e_anno_devono_appartenere_alla_stessa_fonte(runner):
    ex = run_ok(runner)
    ex.testi = ['Cass. n. 123/2024']
    ex.fonti = [source(runner, 'search_case_law', {'results':[
        {'numero':'123','anno':2023}, {'numero':'999','anno':2024}]})]
    ex.risultati = [ex.fonti[0]['output']]
    assert not all(ok for _,ok,_ in runner.controlli_specifici({'estremi_da_tool': True},ex))


def test_schema_errato_non_passa_i_controlli_generali(runner):
    ex = run_ok(runner)
    ex.chiamate = [{'tool':'search_case_law','nome_originale':'buddalaw_search_case_law',
                    'argomenti':{'query':'tema','search_category':'civile','anno':'2025'}}]
    assert not runner.valuta({'id':'X'},'v9',ex,[])['promosso']


def test_limite_ricerche_si_controlla_anche_senza_regola_del_caso(runner):
    ex = run_ok(runner)
    ex.chiamate = [{'tool':'search_case_law','nome_originale':'buddalaw_search_case_law',
                    'argomenti':{'query':'tema','search_category':'civile'},'turno':1} for _ in range(5)]
    assert not runner.valuta({'id':'X'},'v9',ex,[])['promosso']


def test_limite_ricerche_si_rinnova_al_nuovo_quesito(runner):
    ex = run_ok(runner)
    ex.chiamate = [{'tool':'search_case_law','nome_originale':'buddalaw_search_case_law',
                    'argomenti':{'query':'tema','search_category':'civile'},'turno':turn} for turn in [1,1,1,2,2,2]]
    assert runner.valuta({'id':'X'},'v9',ex,[])['promosso']


def test_errore_lungo_non_evade_lo_stop(runner):
    with pytest.raises(runner.Blocco):
        runner.controlla_blocco(json.dumps({'error':'Circuit breaker aperto','detail':'x'*6000}),False)


def test_blocco_live_non_esegue_l_azione_successiva(runner,tmp_path):
    marker = tmp_path/'non-deve-esistere'
    event = {'type':'tool_use','part':{'tool':'buddalaw_search_case_law',
             'state':{'status':'completed','input':{},'output':'{"error":"HTTP 500: backend non disponibile"}'}}}
    script = ('import json,time;from pathlib import Path;'
              f'print({json.dumps(json.dumps(event))},flush=True);'
              f'time.sleep(1);Path({str(marker)!r}).write_text("ritento")')
    with pytest.raises(runner.Blocco):
        runner._stdout_su_file([sys.executable,'-u','-c',script],timeout=5,
                              salva=tmp_path/'trace.jsonl',controlla=True)
    assert not marker.exists()


def test_suite_vuota_non_passa(runner):
    assert runner.codice_uscita([]) != 0


def test_copertura_incompleta_non_passa(runner):
    assert runner.codice_uscita([{'promosso':True}],completo=False) != 0


def test_un_link_alterato_non_viene_nascosto_da_due_run_buoni(runner):
    assert runner.codice_uscita([{'promosso':True,'falliti':['fedeltà link (URL identici ai tool_result)']}]) != 0


def test_caso_sconosciuto_si_ferma_prima_di_spendere(runner,monkeypatch):
    monkeypatch.setattr(sys,'argv',['run.py','--casi','NON_ESISTE','--prova'])
    with pytest.raises(SystemExit) as e:
        runner.main()
    assert e.value.code==2


def test_tutti_saltati_non_e_successo(runner,monkeypatch,tmp_path):
    monkeypatch.setattr(sys,'argv',['run.py','--runtime','opencode','--casi','B00'])
    monkeypatch.setattr(runner,'RISULTATI',tmp_path/'results')
    monkeypatch.setattr(runner,'trova_opencode',lambda:'opencode')
    def skip(*args):raise runner.Salta('canale non disponibile')
    monkeypatch.setattr(runner,'preflight_opencode',skip)
    assert runner.main()==2


def test_rivalutazione_non_perde_isolamento(runner,tmp_path):
    root=tmp_path/'results';folder=root/'opencode__provider_model__v9';folder.mkdir(parents=True)
    ev=[{'type':'text','part':{'text':'Skill BuddaLaw 9.0.'}},
        {'type':'step_finish','part':{'reason':'stop','tokens':{},'cost':0.001}}]
    trace=folder/'B00__r1.jsonl'
    trace.write_text(''.join(json.dumps(e)+'\n' for e in ev))
    assert runner.rivaluta(root)!=0
    audit=json.loads(trace.with_suffix('.esito.json').read_text())
    assert not audit['promosso']
    assert any('isolamento' in c['nome'] for c in audit['controlli'])


def test_timeout_con_stdout_muto_non_si_blocca(runner,tmp_path):
    with pytest.raises(runner.subprocess.TimeoutExpired):
        runner._stdout_su_file([sys.executable,'-c','import time;time.sleep(5)'],
                              timeout=0.1,salva=tmp_path/'silent.jsonl',controlla=True)


def test_testo_che_inizia_con_omissis_resta_citabile(runner):
    ex = run_ok(runner)
    quote = '[omissis] La prova deve riguardare il collegamento tra condotta e danno.'
    ex.fonti = [source(runner, 'get_judgement', {'testo': quote})]
    assert quote in runner.corpus_testi(ex)


def test_configurazione_opencode_separata_senza_spostare_credenziali(runner,monkeypatch):
    monkeypatch.setenv('XDG_DATA_HOME','/dati-originali')
    env=runner.env_opencode()
    assert env['XDG_CONFIG_HOME']==str(runner.SANDBOX/'.isolated-config')
    assert env['XDG_DATA_HOME']=='/dati-originali'


def test_prefisso_di_percorso_non_e_la_sandbox(runner,monkeypatch):
    location=str(runner.SANDBOX)+'-altra/.opencode/skills/buddalaw/SKILL.md'
    monkeypatch.setattr(runner,'_stdout_su_file',lambda *a,**k: json.dumps([
        {'name':'buddalaw','location':location}]))
    assert runner.verifica_skill_opencode('opencode','v9')


def test_timeout_claude_non_scompare_nella_rivalutazione(runner,tmp_path,monkeypatch):
    folder=tmp_path/'results'/'claude__haiku__v9';folder.mkdir(parents=True)
    trace=folder/'B00__r1.jsonl'
    trace.write_text(json.dumps({'type':'assistant','message':{'content':[
        {'type':'text','text':'Skill BuddaLaw 9.0.'}]}})+'\n')
    trace.with_suffix('.meta.json').write_text(json.dumps({
        'completata':False, 'errore':'timeout; costo parziale noto conservato'}))
    monkeypatch.setattr(runner,'verifica_init_claude',lambda *args: [])
    runner.rivaluta(folder.parent)
    audit=json.loads(trace.with_suffix('.esito.json').read_text())
    assert audit['classe']=='esecuzione'
    assert not audit['promosso']
