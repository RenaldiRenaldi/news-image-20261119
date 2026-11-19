import os
import shutil
from pathlib import Path


def main():
    source = Path(__file__).resolve().parent / "assets" / "entry.png"
    output = Path(os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output")
    output.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, output / "entry.png")


if __name__ == "__main__":
    main()
