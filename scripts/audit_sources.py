"""Read-only extraction audit of prepared Words/Java source repositories."""
import argparse
from collections import Counter
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from adcs_words_java.worker import handle

PRODUCT = 'aspose.words'
PREFIX = 'com.aspose.words.'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--docs-root', type=Path, required=True)
    parser.add_argument('--api-root', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    manifest = json.loads((ROOT / 'plugin.json').read_text())
    report = {'plugin_id': manifest['plugin_id'], 'sources': {}, 'errors': []}
    for kind, repo in [('docs', args.docs_root), ('apiref', args.api_root)]:
        repo = repo.resolve()
        source = manifest['sources'][kind]
        revision = subprocess.check_output(['git', '-C', str(repo), 'rev-parse', 'HEAD'], text=True).strip()
        identity = dict(contract=manifest['contract'], plugin_id=manifest['plugin_id'],
                        product_id=manifest['product_id'], language=manifest['language'], source_kind=kind)
        paths = handle({**identity, 'operation': 'discover', 'repo_root': str(repo),
                        'source_prefix': source['prefix']})['files']
        warnings = Counter()
        counts = dict(revision=revision, discovered=len(paths), extracted=0, chunks=0, symbols=0)
        for relative in paths:
            try:
                # Decode like the engine reader: a few upstream pages contain stray non-UTF-8 bytes.
                raw = (repo / relative).read_bytes().decode('utf-8-sig', errors='replace')
                output = handle(dict(
                    **identity, operation='extract', repo_id=source['repo_id'], product_family='aspose',
                    source_path=source['path'] + '/' + relative, relative_repo_path=relative,
                    source_prefix=source['prefix'], layout_detection=source['layout'],
                    canonical_base_url=source['canonical_base_url'], source_revision=revision,
                    repo_root=str(repo), raw_markdown=raw,
                ))
                if not output['chunk_records']:
                    raise ValueError('No chunks extracted')
                for row in output['symbols']:
                    if row['product'] != PRODUCT or not row['member_fqn'].startswith(PREFIX):
                        raise ValueError('Unexpected API product or package: ' + row['member_fqn'])
                counts['extracted'] += 1
                counts['chunks'] += len(output['chunk_records'])
                counts['symbols'] += len(output['symbols'])
                for warning in output['page']['parse_warnings']:
                    warnings[warning['code']] += 1
            except Exception as exc:
                report['errors'].append({'kind': kind, 'path': relative, 'error': str(exc)})
        counts['warnings'] = dict(warnings)
        report['sources'][kind] = counts
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))
    return 1 if report['errors'] else 0


if __name__ == '__main__':
    raise SystemExit(main())
