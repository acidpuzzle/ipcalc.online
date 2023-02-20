from pathlib import Path
from zipfile import ZipFile
import os


ROOT_DIR = Path(__file__).resolve().parent
SRC_DIR = ROOT_DIR / "ipcalc"


def archive(drc_dir: Path) -> None:
    with ZipFile(f'deploy_ipcalc.zip', 'w') as f:
        os.chdir(drc_dir)
        [f.write(file.relative_to(drc_dir)) for file in drc_dir.glob('**/*')]
        os.chdir(drc_dir.parent)


if __name__ == "__main__":
    archive(SRC_DIR)
