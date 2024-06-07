import os, sys
from pathlib import Path
import subprocess
import time
import random
# from folder_sync import folder_sync

if __name__ == '__main__':
    if not os.path.exists('./test/source'): os.mkdir('./test/source')
    for root, dirs, files in Path('./test/source').walk(top_down=False):
        for file in files: os.remove(root / file)
        for dire in dirs: os.rmdir(root / dire)

    offset = 0
    for i in range(3):
        open(f'./test/source/file{i+offset}', 'w').close()
    if not os.path.exists('./test/source/dir0'): os.mkdir('./test/source/dir0')
    for i in range(3):
        open(f'./test/source/dir0/file{i+offset}', 'w').close()


    # sys.exit()
    process = subprocess.Popen(
        ['python', 'folder_sync.py', './test/source', './test/replica', '10', './test/log'],
        stdout=subprocess.PIPE,
        text=True,
    )

    time.sleep(5)

    i = 0
    while process.poll() is None or i < 10:
        time.sleep(10)
        for root, dirs, files in Path('./test/source').walk(top_down=False):
            for file in files: os.remove(root / file)
            for dire in dirs: os.rmdir(root / dire)
        i += 1

        offset = random.randint(1, 5)
        for i in range(random.randint(0,10)):
            open(f'./test/source/file{i+offset}', 'w').close()
        if not os.path.exists('./test/source/dir0'): os.mkdir('./test/source/dir0')
        for i in range(random.randint(0,5)):
            if not os.path.exists(f'./test/source/dir{i+offset//2*3}'):
                os.mkdir(f'./test/source/dir{i+offset//2*3}')
            for j in range(random.randint(0,10)):
                open(f'./test/source/dir{i+offset//2*3}/file{j+offset}', 'w').close()

        # if process.stdout is not None:
        #     print(process.stdout.readlines())



    # print(Path('log').is_dir())
    # print(Path('./test/log/').name)
    # time.sleep(20)
    # for i in range(10):
    #     os.remove(f'./source/file{i}', 'w')



