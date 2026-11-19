import os
import shutil
from pathlib import Path

asset = Path(__file__).resolve().parent / 'assets' / 'entry.png'
destination = Path(os.environ.get('MAKEFUN_OUTPUT_DIR', 'out'))
destination.mkdir(parents=True, exist_ok=True)
shutil.copyfile(asset, destination / 'entry.png')
