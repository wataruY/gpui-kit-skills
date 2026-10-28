#!/usr/bin/env python3
"""Resolve a local skill reference from its containing file, without reading it."""
import argparse
import json
from pathlib import Path
from urllib.parse import unquote, urlsplit


def contained(root, path):
    resolved = path.resolve()
    if not resolved.is_relative_to(root):
        raise ValueError(f'Reference escapes skill root: {path}')
    return resolved


def resolve_reference(skill, owner, link):
    root = Path(skill).resolve(strict=True)
    source = contained(root, root / owner)
    if not source.is_file():
        raise ValueError(f'Containing file does not exist: {source}')
    url = urlsplit(link)
    if url.scheme or url.netloc or url.query or Path(unquote(url.path)).is_absolute():
        raise ValueError('Only local relative references without query strings are supported')
    target = contained(root, source.parent / unquote(url.path)) if url.path else source
    if not target.is_file():
        raise ValueError(f'Reference does not exist: {target}; use --find to list actual files')
    return {'owner': str(source), 'path': str(target), 'fragment_unchecked': url.fragment or None}


def find_references(skill, filename):
    root = Path(skill).resolve(strict=True)
    if not filename or Path(filename).name != filename or filename in ('.', '..'):
        raise ValueError('--find requires an exact filename, not a path')
    return sorted({str(p.resolve()) for p in root.rglob('*')
                   if p.name == filename and p.is_file() and p.resolve().is_relative_to(root)})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--skill', type=Path, required=True)
    parser.add_argument('--from', dest='owner')
    parser.add_argument('--find', metavar='FILENAME')
    parser.add_argument('link', nargs='?')
    args = parser.parse_args()
    try:
        if args.find:
            if args.owner or args.link:
                raise ValueError('--find cannot be combined with --from/link')
            result = {'matches': find_references(args.skill, args.find)}
        else:
            if not args.owner or args.link is None:
                raise ValueError('--from and a relative link are required')
            result = resolve_reference(args.skill, args.owner, args.link)
    except (OSError, ValueError) as error:
        parser.exit(2, f'{error}\n')
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
