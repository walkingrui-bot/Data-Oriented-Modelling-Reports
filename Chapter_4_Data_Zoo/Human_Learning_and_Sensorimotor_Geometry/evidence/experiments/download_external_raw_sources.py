#!/usr/bin/env python3
"""Retrieve the pinned public sources for Human Geometry Studies 001–004.

Examples:
    python download_external_raw_sources.py
    python download_external_raw_sources.py --experiment 003

Existing files are reused after Git blob verification. GITHUB_TOKEN is optional
and is sent only to the GitHub API. The original supplied utility is preserved
in the publication's source collection.
"""
from pathlib import Path
import argparse
import base64
import csv
import hashlib
import json
import os
import urllib.request

ROOT = Path(__file__).resolve().parent
MANIFEST = ROOT / '00_EXTERNAL_RAW_SOURCE_LOCKS.csv'


def git_blob_sha(data: bytes) -> str:
    return hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()


def fetch_blob(repository: str, blob: str) -> bytes:
    headers = {
        'Accept': 'application/vnd.github+json',
        'User-Agent': 'human-geometry-source-retrieval',
    }
    token = os.environ.get('GITHUB_TOKEN')
    if token:
        headers['Authorization'] = f'Bearer {token}'
    url = f'https://api.github.com/repos/{repository}/git/blobs/{blob}'
    request = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(request, timeout=120) as response:
        payload = json.load(response)
    if payload.get('encoding') != 'base64':
        raise RuntimeError(f'Unexpected encoding for {repository}:{blob}')
    return base64.b64decode(payload['content'])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--experiment', choices=['001', '002', '003', '004'],
                        action='append', help='Retrieve only this study; may be repeated.')
    args = parser.parse_args()
    with MANIFEST.open(newline='', encoding='utf-8') as stream:
        rows = list(csv.DictReader(stream))
    for row in rows:
        if args.experiment and row['experiment'] not in args.experiment:
            continue
        target = ROOT / row['archive_destination']
        expected = row['git_blob_sha']
        if target.exists():
            data = target.read_bytes()
            if git_blob_sha(data) == expected:
                print(f'VERIFIED {target.relative_to(ROOT)} {len(data):,} bytes {expected}')
                continue
            raise RuntimeError(f'Existing file has a different blob identity: {target}. '
                               'Move that file aside before retrieving the pinned source.')
        data = fetch_blob(row['repository'], expected)
        actual = git_blob_sha(data)
        if actual != expected:
            raise RuntimeError(f'Blob mismatch for {row["repository"]} {row["path"]}: '
                               f'expected {expected}, got {actual}')
        target.parent.mkdir(parents=True, exist_ok=True)
        temporary = target.with_suffix(target.suffix + '.download')
        temporary.write_bytes(data)
        temporary.replace(target)
        print(f'RETRIEVED {target.relative_to(ROOT)} {len(data):,} bytes {expected}')


if __name__ == '__main__':
    main()
