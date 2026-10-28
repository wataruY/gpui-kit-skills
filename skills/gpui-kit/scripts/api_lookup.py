#!/usr/bin/env python3
"""Inspect GPUI symbols in lock-matching crates.io cache sources; no Cargo run."""
import argparse
import json
import os
from pathlib import Path
import re
import tomllib

CRATES = ('gpui-kit', 'gpui-base', 'gpui-component', 'gpui-pre')
CRATES_IO = 'registry+https://github.com/rust-lang/crates.io-index'


def cached_source(project, cargo_home, crate, version=None):
    lock_path = Path(project).resolve() / 'Cargo.lock'
    lock = tomllib.loads(lock_path.read_text())
    packages = [p for p in lock.get('package', []) if p['name'] == crate
                and (version is None or p['version'] == version)]
    if len(packages) != 1:
        raise ValueError(f'Need one locked {crate} package; found '
                         f'{[(p["version"], p.get("source", "path")) for p in packages]}; '
                         'select --version or inspect the actual source manually')
    package = packages[0]
    if package.get('source') != CRATES_IO:
        raise ValueError('Only crates.io cache lookup is supported; inspect git/path/vendor source manually')
    cache = Path(cargo_home).expanduser() / 'registry' / 'src'
    matches = []
    for index in cache.glob('index.crates.io-*'):
        path = index / f'{crate}-{package["version"]}'
        manifest = path / 'Cargo.toml'
        if not manifest.is_file():
            continue
        meta = tomllib.loads(manifest.read_text()).get('package', {})
        if meta.get('name') == crate and meta.get('version') == package['version']:
            matches.append(path.resolve())
    matches = sorted(set(matches))
    if len(matches) != 1:
        raise ValueError(f'Need exactly one matching cached source, found {len(matches)}: '
                         f'{[str(p) for p in matches]}; no download or first-match fallback')
    return package, matches[0]


def lookup(source, symbol, limit=6, context=4):
    if not re.fullmatch(r'[A-Za-z_][A-Za-z0-9_]*', symbol):
        raise ValueError('--symbol must be a Rust identifier')
    definition = re.compile(r'\b(?:fn|struct|enum|trait|type|const)\s+' + re.escape(symbol) + r'\b')
    variant = re.compile(r'^\s*' + re.escape(symbol) + r'\s*(?:,|\(|\{|=)')
    owner_pattern = re.compile(r'^\s*(?:(?:pub(?:\([^)]*\))?)\s+)?(?:impl\b|trait\b|enum\b)')
    results = []
    total = 0
    for path in sorted((source / 'src').rglob('*.rs')):
        lines = path.read_text().splitlines()
        owner = None
        for ix, line in enumerate(lines):
            if owner_pattern.search(line):
                owner = {'line': ix + 1, 'text': line.strip()}
            if not (definition.search(line) or variant.search(line)):
                continue
            total += 1
            if len(results) < limit:
                begin = max(0, ix - context)
                end = min(len(lines), ix + context + 1)
                results.append({'file': str(path), 'line': ix + 1,
                                'nearby_textual_owner_not_type_resolution': owner,
                                'excerpt': [{'line': n + 1, 'text': lines[n]} for n in range(begin, end)]})
    return {'textual_matches': total, 'shown': len(results), 'candidates': results}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project', type=Path, default=Path.cwd())
    parser.add_argument('--cargo-home', type=Path,
                        default=Path(os.environ.get('CARGO_HOME', '~/.cargo')).expanduser())
    parser.add_argument('--crate', choices=CRATES, required=True)
    parser.add_argument('--version')
    parser.add_argument('--symbol', required=True)
    parser.add_argument('--limit', type=int, default=6)
    parser.add_argument('--context', type=int, default=4)
    args = parser.parse_args()
    if not 1 <= args.limit <= 50 or not 0 <= args.context <= 20:
        parser.error('limit must be 1..50 and context 0..20')
    try:
        package, source = cached_source(args.project, args.cargo_home, args.crate, args.version)
        result = {'mode': 'lock-matching local cache, not Cargo resolve/type checking',
                  'crate': args.crate, 'version': package['version'], 'source': str(source),
                  **lookup(source, args.symbol, args.limit, args.context)}
    except (OSError, ValueError) as error:
        parser.exit(2, f'{error}\n')
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
