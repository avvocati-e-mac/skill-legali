"""Opt-in real local MCP smoke on make_fixture.py's synthetic PDF only.

Run with a Python containing mcp and pypdfium2, pass an installed Docling server
and already downloaded models explicitly. No package installation or client
configuration is performed. Output/cache are confined to a NEW work directory.
This is a direct SDK connection, not proof of connection in any product UI.
"""
import argparse
import asyncio
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

SKILL = Path(__file__).resolve().parents[1] / 'docling-citazioni-pdf'


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def package_versions():
    versions = {}
    for name in ('docling', 'docling-mcp', 'docling-slim', 'docling-core', 'mcp', 'pypdfium2'):
        try:
            versions[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            versions[name] = None
    return versions


def value(result):
    if getattr(result, 'is_error', getattr(result, 'isError', False)):
        raise RuntimeError('MCP tool failed: ' + str(result))
    structured = getattr(result, 'structured_content', getattr(result, 'structuredContent', None))
    if structured is not None:
        return structured
    for item in result.content:
        if item.type == 'text':
            try:
                return json.loads(item.text)
            except ValueError:
                return item.text
    raise ValueError('No MCP payload')


async def run(args):
    args.output_dir.mkdir(parents=True, exist_ok=False)
    work = args.output_dir.resolve()
    original = args.pdf.resolve(strict=True)
    before = sha(original)
    # The caller supplies a synthetic fixture explicitly; no directory scanning.
    env = dict(os.environ)
    env.update(DOCLING_MCP_CONVERSION_MODE='local', DOCLING_MCP_FALLBACK_TO_LOCAL='false',
               DOCLING_MCP_DO_PICTURE_DESCRIPTION='false', DOCLING_ARTIFACTS_PATH=str(args.models.resolve(strict=True)),
               HF_HUB_OFFLINE='1', TRANSFORMERS_OFFLINE='1', DO_NOT_TRACK='1',
               HF_HUB_DISABLE_TELEMETRY='1', CACHE_DIR=str(work/'exports'),
               HF_HOME=str(work/'hf-cache'), PYTHONDONTWRITEBYTECODE='1',
               DOCLING_DEVICE='cpu', DOCLING_NUM_THREADS='4')
    parameters = StdioServerParameters(command=str(args.server.resolve(strict=True)),
        args=['--transport', 'stdio', 'conversion', 'generation', 'manipulation'], env=env, cwd=str(work))
    with (work/'server.log').open('w') as log:
        async with stdio_client(parameters, errlog=log) as (reader, writer):
            async with ClientSession(reader, writer, read_timeout_seconds=300.0) as session:
                await session.initialize()
                catalog = await session.list_tools()
                names = [t.name for t in catalog.tools]
                conversion = value(await session.call_tool('convert_document_into_docling_document', {'source': str(original)}))
                key = conversion['document_key']
                saved = value(await session.call_tool('save_docling_document', {'document_key': key}))
                (work/'conversion-receipt.json').write_text(json.dumps({'conversion': conversion, 'save': saved}, indent=2))
                for field, filename in [('json_file', 'D01.docling.json'), ('md_file', 'D01.original.md')]:
                    source = Path(saved[field]).resolve(strict=True)
                    destination = work/filename
                    shutil.copyfile(source, destination)
                    assert sha(source) == sha(destination)
    doc = json.loads((work/'D01.docling.json').read_text())
    assert len(doc['pages']) == 3
    for page in range(1, 4):
        assert doc['pages'][str(page)]['page_no'] == page
    subprocess.run([sys.executable, str(SKILL/'scripts/export_page_references.py'), '--json',
                    str(work/'D01.docling.json'), '--output-prefix', str(work/'D01')], check=True, capture_output=True)
    sys.path.insert(0, str(SKILL/'scripts'))
    from check_pdf_quote import check_pdf
    cases = []
    for quote, expected in [('Il fornitore dichiara: consegna avvenuta il 12 marzo 2026.', [2]),
                            ('La perizia non accerta il completamento del collaudo.', [3]),
                            ('Documento dimostrativo', [])]:
        report = check_pdf(original, [2, 3], quote)
        assert report['selected_physical_pages'] == expected, report
        assert not report['citation_verified'] and not report['visual_verification_performed']
        if not expected:
            assert report['status'] == 'ambiguous_text_match'
        cases.append({'quote': quote, 'selected_physical_pages': expected, 'status': report['status']})
    (work/'text-checks.json').write_text(json.dumps(cases, ensure_ascii=False, indent=2))
    # Exercise CLI persistence and preservation of existing reports/originals.
    quote_command = [sys.executable, '-B', str(SKILL/'scripts/check_pdf_quote.py'),
                     '--pdf', str(original), '--pages', '3', '--quote',
                     'La perizia non accerta il completamento del collaudo.']
    output = work/'C01.cli.json'
    subprocess.run(quote_command + ['--output', str(output)], check=True, capture_output=True)
    previous = output.read_bytes()
    for destination in (output, original):
        refused = subprocess.run(quote_command + ['--output', str(destination)], capture_output=True)
        assert refused.returncode == 2
        assert output.read_bytes() == previous and sha(original) == before
    invalid = subprocess.run([sys.executable, '-B', str(SKILL/'scripts/check_pdf_quote.py'),
                              '--pdf', str(original), '--pages', '99', '--quote', 'test'], capture_output=True)
    assert invalid.returncode == 2
    assert before == sha(original)
    summary = {'passed': True, 'pdf_sha256': before, 'json_sha256': sha(work/'D01.docling.json'),
               'page_count': 3, 'source_unchanged': True, 'tools': names, 'cases': cases,
               'versions': package_versions(),
               'cli_preservation_checks': 3,
               'client_scope': 'direct_MCP_SDK_not_product_UI', 'visual_check': 'not_performed_by_script'}
    (work/'summary.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2))
    print(json.dumps(summary, ensure_ascii=False))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--server', type=Path, required=True)
    parser.add_argument('--models', type=Path, required=True)
    parser.add_argument('--pdf', type=Path, required=True)
    parser.add_argument('--output-dir', type=Path, required=True)
    asyncio.run(run(parser.parse_args()))
