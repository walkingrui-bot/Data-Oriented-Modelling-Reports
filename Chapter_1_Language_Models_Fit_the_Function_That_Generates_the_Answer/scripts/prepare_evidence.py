"""Restore compressed source artifacts and verify their original byte identity."""
from pathlib import Path
import gzip,hashlib,json,os,shutil,tempfile
ROOT=Path(__file__).resolve().parents[1]
def digest(path):
 h=hashlib.sha256()
 with path.open('rb') as f:
  for block in iter(lambda:f.read(1024*1024),b''):h.update(block)
 return h.hexdigest()
def main():
 mapping=json.loads((ROOT/'metadata/compressed_sources.json').read_text())
 for logical,meta in mapping.items():
  target=ROOT/logical
  if target.exists():
   if digest(target)!=meta['original_sha256']:raise ValueError(f'Existing file differs: {logical}')
   print(f'Already verified: {logical}');continue
  with tempfile.NamedTemporaryFile(dir=target.parent,prefix='restore-',delete=False) as out:
   temporary=Path(out.name)
   try:
    with gzip.open(ROOT/meta['stored_path'],'rb') as source:shutil.copyfileobj(source,out)
   except BaseException:
    temporary.unlink(missing_ok=True);raise
  try:
   if temporary.stat().st_size!=meta['original_size'] or digest(temporary)!=meta['original_sha256']:raise ValueError(f'Identity check failed: {logical}')
   os.replace(temporary,target)
  finally:temporary.unlink(missing_ok=True)
  print(f'Restored and verified: {logical}')
if __name__=='__main__':main()
