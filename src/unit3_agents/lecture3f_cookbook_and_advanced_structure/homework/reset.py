"""Wipe all agent memory (graph, MemGPT, and saved conversations) for testing."""

import shutil
from pathlib import Path

DIRS = [
    Path('.graph_memory'),
    Path('.memories'),
    Path('conversations'),
]


def reset():
    for d in DIRS:
        if d.exists():
            shutil.rmtree(d)
            print(f'Deleted {d}/')
        else:
            print(f'Skipped {d}/ (not found)')
    print('\nAll memory wiped.')


if __name__ == '__main__':
    reset()
