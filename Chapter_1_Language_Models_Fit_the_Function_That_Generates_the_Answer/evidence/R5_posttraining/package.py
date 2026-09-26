"""Package only this new experiment and its research-index documents."""
import ast
import datetime as dt
import json
from pathlib import Path
import re
import zipfile
from urllib.parse import unquote


def stamp():
    return dt.datetime.now(dt.timezone.utc).isoformat()


def main():
    root = Path(__file__).resolve().parent
    record = root.parent / 'research/records/P05-RTG-POSTTRAIN-20260925-001'
    archive = root.parent / 'RTG_POSTTRAIN_V01_20260925.zip'
    attempt = root / 'attempts/A-PACKAGE-001'
    attempt.mkdir(exist_ok=False)
    if archive.exists():
        raise FileExistsError(archive)
    (attempt / 'registration.json').write_text(json.dumps({'run_id':'A-PACKAGE-001', 'status':'RUNNING',
        'started_utc':stamp(), 'scope':'current RTG experiment and its four index documents only'}, indent=2)+'\n')
    docs = list(root.glob('*.md')) + list(record.glob('*.md'))
    links = []
    for doc in docs:
        for reference in re.findall(r'!?\[[^\]]*\]\(([^)]+)\)', doc.read_text()):
            target = reference.split('#', 1)[0]
            if not target or '://' in target:
                continue
            path = doc.parent / unquote(target.strip('<>'))
            if not path.exists():
                raise FileNotFoundError(f'{doc}: {reference}')
            links.append({'document':str(doc.relative_to(root.parent)), 'target':reference})
    syntax = []
    for name in ('analyze.py','audit_completed.py','diagnose_saved_traces.py','reproduce.py','package.py'):
        ast.parse((root / name).read_text(), filename=name)
        syntax.append(name)
    checkpoints = list((root / 'checkpoints').rglob('*.ckpt'))
    assert len(checkpoints) == 85
    required = ['REPORT.md','CLOSEOUT.md','README.md','configs/phaseA_v1.json',
                'results/per_episode_predictions.jsonl','results/gate_A.json','results/scoped_audit.json',
                'results/phaseA_accuracy_by_length.csv','results/phase_status.csv',
                'traces/control_failure_examples.jsonl','attempts/A-SMOKE-001/stdout.log']
    assert all((root / name).is_file() for name in required)
    validation = {'status':'PASS', 'markdown_documents':len(docs), 'local_links_checked':len(links),
                  'helper_syntax_checked':syntax, 'formal_checkpoints':len(checkpoints),
                  'requirement':'No new model run or broad repository checks.'}
    (attempt / 'scoped_document_check.json').write_text(json.dumps(validation,indent=2)+'\n')
    files = [p for p in root.rglob('*') if p.is_file() and '__pycache__' not in p.parts
             and p.suffix != '.pyc' and p.name != 'PACKAGE_RECEIPT.json'] + list(record.glob('*.md'))
    files.sort(key=str)
    with zipfile.ZipFile(archive, 'x', compression=zipfile.ZIP_DEFLATED, compresslevel=6) as out:
        for file in files:
            out.write(file, file.relative_to(root.parent).as_posix())
    with zipfile.ZipFile(archive) as z:
        bad = z.testzip()
        if bad is not None:
            raise RuntimeError(f'ZIP CRC failed at {bad}; preserve this failed artifact.')
    receipt = {'run_id':'A-PACKAGE-001', 'status':'COMPLETED', 'recorded_utc':stamp(),
               'archive':str(archive), 'files_before_this_receipt':len(files),
               'first_zip_crc':'PASS', 'document_check':validation,
               'note':'This completion entry is appended, then the entire final ZIP is checked again. Final size/CRC receipt is external.'}
    completion = attempt / 'completion.json'
    completion.write_text(json.dumps(receipt,indent=2)+'\n')
    with zipfile.ZipFile(archive, 'a', compression=zipfile.ZIP_DEFLATED, compresslevel=6) as z:
        z.write(completion, completion.relative_to(root.parent).as_posix())
    with zipfile.ZipFile(archive) as z:
        assert len(z.namelist()) == len(set(z.namelist()))
        bad = z.testzip()
        if bad is not None:
            raise RuntimeError(f'Final ZIP CRC failed at {bad}; preserve this failed artifact.')
        file_count = len(z.namelist())
        assert all('RTG_POSTTRAIN_V01/' + name in z.namelist() for name in required)
    final = {'run_id':'A-PACKAGE-001', 'status':'PASS', 'ended_utc':stamp(), 'archive':str(archive),
             'archive_bytes':archive.stat().st_size, 'files':file_count, 'crc':'PASS',
             'receipt_location':'External, written after final ZIP validation; not inside the ZIP',
             'excluded':'Python bytecode/cache, external virtual environments, and this post-archive receipt',
             'remote_backup':'NOT_PERFORMED', 'hashes':'NOT_COMPUTED'}
    (root / 'PACKAGE_RECEIPT.json').write_text(json.dumps(final,indent=2)+'\n')
    print(json.dumps(final,indent=2))


if __name__ == '__main__':
    main()
