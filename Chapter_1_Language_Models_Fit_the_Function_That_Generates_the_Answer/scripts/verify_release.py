"""Verify stored files, source identities, experiment mappings and safe paths.

Uses the standard library. This checks packaging, not training performance.
"""
from pathlib import Path
import csv,gzip,hashlib,json,sys
ROOT=Path(__file__).resolve().parents[1]
def rows(name):
 with (ROOT/name).open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def resolved(rel):
 path=(ROOT/rel).resolve()
 if not path.is_relative_to(ROOT):raise ValueError(f'Path escapes repository: {rel}')
 if not path.is_file():raise FileNotFoundError(rel)
 return path
def digest(p,compressed=False):
 h=hashlib.sha256();opener=gzip.open if compressed else open
 with opener(p,'rb') as f:
  for block in iter(lambda:f.read(1024*1024),b''):h.update(block)
 return h.hexdigest()
def main():
 catalog=rows('metadata/EXPERIMENT_CATALOG.csv')
 release=json.loads((ROOT/'metadata/release.json').read_text())
 if {r['experiment_id'] for r in catalog}!=set(release['expected_experiment_ids']):raise ValueError('Experiment catalog differs from release metadata')
 checked=0
 for row in rows('FILE_MANIFEST.csv'):
  p=resolved(row['relative_path'])
  if p.stat().st_size!=int(row['size_bytes']) or digest(p)!=row['sha256']:raise ValueError('File changed: '+row['relative_path'])
  checked+=1
 for row in rows('metadata/ARTIFACT_CATALOG.csv'):
  p=resolved(row['stored_path']);compressed=row['stored_path']!=row['source_path']
  if digest(p,compressed)!=row['source_sha256']:raise ValueError('Source identity differs: '+row['source_path'])
 for row in rows('EXPERIMENT_INDEX.csv'):resolved(row['relative_path'])
 for experiment in catalog:
  directory=experiment['directory']
  for name in ['README.md','experiment.json','artifacts.csv']:resolved(directory+'/'+name)
  for artifact in rows(directory+'/artifacts.csv'):
   p=resolved(artifact['stored_path'])
   if digest(p)!=artifact['sha256'] or p.stat().st_size!=int(artifact['size_bytes']):raise ValueError('Experiment artifact changed: '+artifact['stored_path'])
 print(json.dumps({'status':'passed','files_verified':checked,'experiments':len(catalog),'original_artifacts':len(rows('metadata/ARTIFACT_CATALOG.csv')),'model_training_rerun':False},indent=2))
if __name__=='__main__':main()
