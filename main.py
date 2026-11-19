import os
import shutil
from pathlib import Path


def main():
    artwork = Path(__file__).resolve().with_name("assets") / "entry.png"
    output = Path(os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output")
    output.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(artwork, output / artwork.name)


if __name__ == "__main__":
    main()
