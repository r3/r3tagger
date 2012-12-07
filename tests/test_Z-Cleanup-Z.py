import os
import shutil


def test_Remove_temporary_folders():
    for path in os.listdir('/tmp'):
        if path[:3] == 'tmp':
            full_path = os.path.join('/tmp', path)
            shutil.rmtree(full_path)
