#!/usr/bin/env python3
"""Download and assemble the two verified Report 02 ZIP packages."""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import tempfile
import urllib.request

BASE_URL = ('https://raw.githubusercontent.com/walkingrui-bot/'
            'Data-Oriented-Modelling-Reports/main/'
            'Chapter_5_Data_Oriented_Modelling/releases/')
PACKAGES = {
    'publication': (
        'Data_Oriented_Modelling_02_Publication_v1.0_20260928.zip',
        66349794,
        'da2229b4c7e7ca3e67f9ab37c1fe0f3dfcebdb4977ebfd65934a55e6631f69df'),
    'evidence': (
        'Data_Oriented_Modelling_02_Evidence_v1.0_20260928.zip',
        59436567,
        '63f076932269e8b739f0143e7f284fb5f2a4b180743191a888f1f6f26212e6a7'),
}


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def valid(path, size, sha):
    return path.is_file() and path.stat().st_size == size and digest(path) == sha


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--package', choices=['all', *PACKAGES], default='all')
    parser.add_argument('--directory', type=Path, default=Path.cwd())
    parser.add_argument('--parts-root', type=Path, default=Path(__file__).resolve().parent)
    args = parser.parse_args()
    manifest_path = args.parts_root / 'RELEASE_MANIFEST.json'
    if manifest_path.is_file():
        manifest = json.loads(manifest_path.read_text())
    else:
        with urllib.request.urlopen(BASE_URL + 'RELEASE_MANIFEST.json', timeout=60) as response:
            manifest = json.load(response)
    args.directory.mkdir(parents=True, exist_ok=True)
    selected = PACKAGES if args.package == 'all' else {args.package: PACKAGES[args.package]}
    for label, (name, size, sha) in selected.items():
        target = args.directory / name
        if target.exists():
            if valid(target, size, sha):
                print(f'Already verified: {name}')
                continue
            raise RuntimeError(f'An existing file has a different checksum: {target}')
        record = next(item for item in manifest['downloads'] if item.get('assembled_file') == name)
        assert record['bytes'] == size and record['sha256'] == sha
        parts = record['parts']
        assert sum(item['bytes'] for item in parts) == size
        for number, item in enumerate(parts, 1):
            expected = f'report_02_parts/{name}.part{number:03d}'
            assert item['file'] == expected
            assert 0 < item['bytes'] <= 8 * 1024 * 1024
            assert len(item['sha256']) == 64
        with tempfile.NamedTemporaryFile(dir=args.directory, prefix=name + '.', suffix='.partial', delete=False) as output:
            temporary = Path(output.name)
            try:
                for number, item in enumerate(parts, 1):
                    local = args.parts_root / PurePosixPath(item['file'])
                    if not valid(local, item['bytes'], item['sha256']):
                        cache = args.directory / '.report_02_downloads'
                        cache.mkdir(exist_ok=True)
                        local = cache / PurePosixPath(item['file']).name
                        if not valid(local, item['bytes'], item['sha256']):
                            with urllib.request.urlopen(BASE_URL + item['file'], timeout=60) as response, local.open('wb') as downloaded:
                                for block in iter(lambda: response.read(1024 * 1024), b''):
                                    downloaded.write(block)
                            if not valid(local, item['bytes'], item['sha256']):
                                raise RuntimeError(f'Volume checksum mismatch: {item["file"]}')
                    with local.open('rb') as stream:
                        for block in iter(lambda: stream.read(1024 * 1024), b''):
                            output.write(block)
                    print(f'{label}: verified volume {number}/{len(parts)}')
                output.flush()
                if not valid(temporary, size, sha):
                    raise RuntimeError(f'Assembled checksum mismatch: {name}')
            except BaseException:
                temporary.unlink(missing_ok=True)
                raise
        temporary.replace(target)
        print(f'Complete: {target}\nSHA-256: {sha}')


if __name__ == '__main__':
    main()
