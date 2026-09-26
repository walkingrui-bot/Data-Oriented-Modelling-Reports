"""Replay into a new directory; refuse to overwrite any recorded evidence.

Call from the parent of the extracted RTG_POSTTRAIN_V01 package. This wrapper is
not a checkpoint continuation tool. It performs the entire fixed campaign anew.
"""
import argparse
import datetime as dt
import os
from pathlib import Path
import shutil
import subprocess
import sys


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output-root', type=Path, required=True)
    parser.add_argument('--analysis-python', default=sys.executable)
    parser.add_argument('--run-id', default='A-REPLAY-' + dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ'))
    args = parser.parse_args()
    source = Path(__file__).resolve().parent
    destination = args.output_root.resolve()
    if destination == source or destination.exists():
        raise FileExistsError('Provide an entirely new output directory.')
    destination.mkdir(parents=True)
    for directory in ('src', 'configs', 'tests'):
        shutil.copytree(source / directory, destination / directory, ignore=shutil.ignore_patterns('__pycache__'))
    for name in ('__init__.py', 'PLAN.md', 'analyze.py', 'audit_completed.py', 'diagnose_saved_traces.py'):
        shutil.copy2(source / name, destination / name)
    (destination / 'figures').mkdir()
    common = {'cwd': source.parent}
    subprocess.run([sys.executable, '-m', 'RTG_POSTTRAIN_V01.src.campaign',
                    '--config', str(destination / 'configs/phaseA_v1.json'), '--run-id', args.run_id,
                    '--output-root', str(destination)], check=True, **common)
    subprocess.run([sys.executable, '-m', 'RTG_POSTTRAIN_V01.audit_completed',
                    '--root', str(destination), '--run-id', args.run_id], check=True, **common)
    plot_environment = dict(os.environ)
    plot_environment.setdefault('MPLCONFIGDIR', str(destination / 'plot_cache'))
    subprocess.run([args.analysis_python, str(source / 'analyze.py'),
                    '--root', str(destination), '--run-id', args.run_id], check=True, env=plot_environment, **common)
    subprocess.run([sys.executable, str(destination / 'diagnose_saved_traces.py'), '--run-id', args.run_id + '-DIAG'], check=True, **common)
    print(f'Replay complete: {destination / "results/gate_A.json"}')


if __name__ == '__main__':
    main()
