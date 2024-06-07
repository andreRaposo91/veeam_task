import os
from pathlib import Path
import shutil
import argparse
import time
from datetime import datetime, UTC

def folder_sync(source_folder, replica_folder, interval, log_file):
    global sync_time

    try:
        source_path = Path(source_folder)
    except:
        raise os.error('Source folder path is not valid') 

    if not source_path.exists():
        raise os.error('Source Folder does not exist')
    else:
        print('Source Folder found.')

    try:
        replica_path = Path(replica_folder)
    except:
        raise os.error('Replica folder path is not valid')

    if not replica_path.exists():
        os.makedirs(replica_path)
        print('Replica Folder created:', replica_path)
    else:
        print('Replica Folder found.')

    if interval < 1:
        raise ValueError('Enter a valid sync interval (positive float or int)')

    try:
        log_path = Path(log_file)
        assert not log_path.is_dir()
    except:
        raise os.error('Log file path is not valid')

    if not log_path.exists():
        open(log_file, 'w').close()
        print('Log file created:', log_file)
    else:
        print('Log file found.')

    c = 0

    # while c < 5:
    while True:
        if not source_path.exists():
            print()
            break
        sync_time = datetime.now(UTC)
        log_lines = [f'\nSync time (UTC): {sync_time}']

        for root, dirs, files in source_path.walk():
            replica_dir = replica_path / root.relative_to(source_path) 
            if replica_dir.exists():
                replica_children = [child.name for child in replica_dir.iterdir()]
            else:
                replica_children = []
            for file in files:
                source_file_path = root / file
                replica_file_path = replica_dir / file
                # print('s - ', source_file_path, '; r - ', replica_file_path)
                if replica_file_path.exists():
                    if source_file_path.stat().st_mtime - replica_file_path.stat().st_mtime > 1.0:
                        shutil.copy2(source_file_path, replica_file_path)
                        log_lines.append(f'\n Update: {source_file_path} -> {replica_file_path}')
                        print(f'Update: {source_file_path} -> {replica_file_path}')
                    else:
                        print(f'Replica Version up to date:', replica_file_path)
                        pass
                else:
                    shutil.copy2(source_file_path, replica_file_path)
                    log_lines.append(f'\n Copy: {source_file_path} -> {replica_file_path}')
                    print(f'Copy: {source_file_path} -> {replica_file_path}')
                try: replica_children.remove(file)
                except:
                    print('file not in replica:', replica_dir / file)
                    pass

            for dire in dirs:
                dire_path = replica_dir / dire
                if not dire_path.exists():
                    os.mkdir(dire_path)
                    log_lines.append(f'\n Create dir: {dire_path}')
                    print(f'Creating dir: {dire_path}')
                try: replica_children.remove(dire)
                except:
                    print('dir not in replica:', replica_dir / dire)
                    pass

            for child in replica_children:
                if (child_path := replica_dir / child).is_dir():
                    shutil.rmtree(child_path)
                    log_lines.append(f'\n Delete dir: {child_path}')
                    print(f'Delete (dir): {child_path}')
                else:
                    os.remove(child_path)
                    log_lines.append(f'\n Delete file: {child_path}')
                    print(f'Delete (file): {child_path}')

        if len(log_lines) > 1:
            log_lines.append('\n')
            open(log_file, 'a').writelines(log_lines)
        c+=1
        time.sleep(interval)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Folder sync util")
    parser.add_argument("source_folder", help="Path to the source folder")
    parser.add_argument("replica_folder", help="Path to the replica folder")
    parser.add_argument("interval", type=float, help="Synchronization interval in seconds (float or int)")
    parser.add_argument("log_file", help="Path to the log file")
    args = parser.parse_args()

    folder_sync(args.source_folder, args.replica_folder, args.interval, args.log_file)
