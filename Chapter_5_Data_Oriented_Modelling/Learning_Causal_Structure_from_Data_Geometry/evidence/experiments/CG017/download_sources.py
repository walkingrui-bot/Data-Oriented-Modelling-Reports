"""Fetch external Sachs inputs locally; these inputs are not redistributed in the evidence ZIP."""
from pathlib import Path
from urllib.request import urlretrieve
import hashlib, json, os

root=Path(__file__).resolve().parent
out=Path(os.environ.get('CG017_DATA_DIR',str(root/'external_data')))
out.mkdir(exist_ok=True)
sources=json.loads((root/'source_provenance.json').read_text())['files']
for item in sources:
    path=out/item['local_name']
    urlretrieve(item['url'],path)
    digest=hashlib.sha256(path.read_bytes()).hexdigest()
    if digest!=item['sha256']: raise RuntimeError(f'Source changed: {path.name}; expected hash does not match.')
    print(path.name, digest)
