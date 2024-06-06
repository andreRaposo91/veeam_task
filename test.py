import os
from pathlib import Path
from main import sync_folders

if __name__ == '__main__':
    os.chdir('./test/')
    if not os.path.exists('./source'): os.mkdir('./source')
    for i in range(3):
        open(f'./source/file{i}', 'w').close()
    if not os.path.exists('./source/dir0'): os.mkdir('./source/dir0')
    for i in range(3):
        open(f'./source/dir0/file{i}', 'w').close()

    os.chdir('..')
    print(os.getcwd())
    print(Path('./test/source').exists())

    sync_folders('./test/source', './test/replica', 1, './test/log')
    # print(Path('log').is_dir())
    # print(Path('./test/log/').name)
    # time.sleep(20)
    # for i in range(10):
    #     os.remove(f'./source/file{i}', 'w')



