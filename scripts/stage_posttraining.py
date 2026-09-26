"""Copy the RTG archive into the original importable package layout."""
from pathlib import Path
import argparse,shutil
ROOT=Path(__file__).resolve().parents[1]
def main():
 p=argparse.ArgumentParser();p.add_argument('workspace',type=Path);a=p.parse_args()
 target=a.workspace.resolve()/'RTG_POSTTRAIN_V01'
 if target.exists():raise FileExistsError(f'Refusing to overwrite {target}')
 shutil.copytree(ROOT/'evidence/R5_posttraining',target,ignore=shutil.ignore_patterns('__pycache__'))
 print(target)
if __name__=='__main__':main()
