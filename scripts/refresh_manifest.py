"""Refresh checksums after deliberate publication edits; standard library only."""
from pathlib import Path
import csv,hashlib
ROOT=Path(__file__).resolve().parents[1]
skip={'__pycache__','.git','.venv','work','reruns','output','rendered'}
files=sorted(p for p in ROOT.rglob('*') if p.is_file() and (p.relative_to(ROOT).parts[0] in {'evidence','source'} or not (set(p.relative_to(ROOT).parts)&skip)) and p.name!='FILE_MANIFEST.csv' and p.relative_to(ROOT).as_posix()!='evidence/R5_posttraining/results/per_episode_predictions.jsonl')
with (ROOT/'FILE_MANIFEST.csv').open('w',encoding='utf-8-sig',newline='') as f:
    w=csv.writer(f);w.writerow(['relative_path','size_bytes','sha256'])
    for p in files:w.writerow([p.relative_to(ROOT).as_posix(),p.stat().st_size,hashlib.sha256(p.read_bytes()).hexdigest()])
print(f'Indexed {len(files)} files.')
