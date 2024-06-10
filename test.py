import os, sys
from pathlib import Path
import subprocess
import time
import random
import string

if __name__ == '__main__':

    src_folder = './test/source'
    src_path = Path(src_folder)
    repl_folder = './test/replica'
    repl_path = Path(repl_folder)
    half_interval = 2
    folder_lims = (0, 10)
    file_lims = (5, 20)
    offset_lims = (0, 5)
    max_file_size = int(1e5)
    MAX_SYNCS = 10
    
    if not src_path.exists(): os.mkdir(src_folder)
    for root, dirs, files in src_path.walk(top_down=False):
        for file in files: os.remove(root / file)
        for dire in dirs: os.rmdir(root / dire)

    offset = 0
    for i in range(3):
        with open(f'{src_folder}/file{i+offset}', 'w') as f:
            f.write(''.join(random.choices(string.ascii_letters + string.digits, k=random.randint(0, max_file_size))))
    if not os.path.exists(f'{src_folder}/dir0'): os.mkdir(f'{src_folder}/dir0')
    for i in range(3):
        with open(f'{src_folder}/file{i+offset}', 'w') as f:
            f.write(''.join(random.choices(string.ascii_letters + string.digits, k=random.randint(0, max_file_size))))

    # sys.exit()
    
    process = subprocess.Popen(
        ['python', 'folder_sync_v1.py', src_folder, repl_folder, str(half_interval*2), './test/log'],
        # ['python', 'folder_sync_v2.py', src_folder, repl_folder, str(half_interval*2), './test/log'],
        stdout=subprocess.PIPE,
        text=True,
    )


    i = 0
    while process.poll() is None or i < MAX_SYNCS:
        # time.sleep(half_interval)
        for root, dirs, files in src_path.walk(top_down=False):
            for file in files: os.remove(root / file)
            for dire in dirs: os.rmdir(root / dire)
        i += 1

        offset = random.randint(*offset_lims)
        for i in range(random.randint(*file_lims)):
            with open(f'{src_folder}/file{i+offset}', 'w') as f:
                f.write(''.join(random.choices(string.ascii_letters + string.digits, k=random.randint(0, max_file_size))))
        for i in range(random.randint(*folder_lims)):
            if not os.path.exists(f'{src_folder}/dir{i+offset//2*3}'):
                os.mkdir(f'{src_folder}/dir{i+offset//2*3}')
            for j in range(random.randint(*file_lims)):
                with open(f'{src_folder}/file{i+offset}', 'w') as f:
                    f.write(''.join(random.choices(string.ascii_letters + string.digits, k=random.randint(0, max_file_size))))

        time.sleep(half_interval*3)

        src_files = [str(root.relative_to(src_path) / file) for root, _, files in src_path.walk() for file in files]
        repl_files = [str(root.relative_to(repl_path) / file) for root, _, files in repl_path.walk() for file in files]

        # print(src_files[:5], repl_files[:5])

        assert(all([src_file == repl_file for src_file, repl_file in zip(src_files, repl_files)]))

