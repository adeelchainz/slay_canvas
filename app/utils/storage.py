import os
from pathlib import Path
from typing import Tuple

BASE_STORAGE = Path.cwd() / 'storage'
BASE_STORAGE.mkdir(parents=True, exist_ok=True)


def save_upload(file_bytes: bytes, filename: str, subfolder: str = '') -> Tuple[str, str]:
    folder = BASE_STORAGE / subfolder
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / filename
    with open(path, 'wb') as f:
        f.write(file_bytes)
    return str(path), str(path.relative_to(Path.cwd()))
