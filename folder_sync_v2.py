import os
import shutil
import time
import argparse
from datetime import datetime, UTC
from pathlib import Path
from multiprocessing import Pool, cpu_count
import hashlib
from itertools import chain


def hash_file(file_path):
    hash_fun = hashlib.blake2b()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_fun.update(chunk)
    return hash_fun.hexdigest()

def create_directory(src_repl_tuple):
    replica_dir = src_repl_tuple[1]
    if not replica_dir.exists():
        os.makedirs(replica_dir)
        return f'\n Create dir: {replica_dir}'
    return None

def safe_copy(src_repl_tuple):
    source_file, destination_file = src_repl_tuple
    temp_destination = destination_file.with_suffix('.tmp')
    try:
        shutil.copy2(source_file, temp_destination)
        shutil.move(temp_destination, destination_file)
    except Exception as e:
        if temp_destination.exists():
            temp_destination.unlink()
        # raise e
        print("Copy Error:", e)

def copy_file(src_repl_tuple):
    source_file, replica_file = src_repl_tuple
    if not replica_file.exists() or hash_file(source_file) != hash_file(replica_file):
        safe_copy((source_file, replica_file))
        return f'\n Copy: {source_file} -> {replica_file}'
    return None

def del_dir(path):
    deleted_items = []
    if path.exists():
        try:
            deleted_temp = []
            for root, _, files in path.walk():
                deleted_temp.append(f'\n Delete dir: {root}')
                deleted_temp.extend((f'\n Delete file: {root / file}' for file in files))
            shutil.rmtree(path)
            deleted_items.extend(deleted_temp)
        except Exception as e:
            print(f'Failed to delete dir and children {path}: {e}')
            # yield None
        return deleted_items
    else:
        return None

def del_file(path):
    try:
        if path.exists():
            path.unlink()
            return f'\n Delete file: {path}'
    except Exception as e:
        print(f'Failed to delete file {path}: {e}')
        return None

def clean_subdirs(paths): # remove children of dirs in list
    paths.sort()
    top_paths = []
    seen_paths = set()
    
    for path in paths:
        if not any(parent in path.parents for parent in seen_paths):
            top_paths.append(path)
            seen_paths.add(path)
    
    return top_paths

def folder_sync(source_folder, replica_folder, interval, log_file):

    MAX_TRIES = 5

    source_path = Path(source_folder)
    if not source_path.exists():
        raise FileNotFoundError('Source Folder does not exist')
    else:
        print('Source Folder found.')

    replica_path = Path(replica_folder)
    if not replica_path.exists():
        os.makedirs(replica_path)
        print('Replica Folder created:', replica_path)
    else:
        print('Replica Folder found.')

    if interval < 1:
        raise ValueError('Enter a valid sync interval (positive float or int)')

    log_path = Path(log_file)
    assert(not log_path.is_dir())

    if not log_path.exists():
        open(log_file, 'w').close()
        print('Log file created:', log_file)
    else:
        print('Log file found.')

    tries = 0
    while True:
        try: 
            if not source_path.exists():
                print("Source Folder not found, stopping syncing")
                break
            sync_time = datetime.now(UTC)
            log_lines = [f'\nSync time (UTC): {sync_time}']

            # source_walk = source_path.walk()

            # CREATE SUBDIRS IN REPLICA
            # print("create subdirs in replica")
            directories = [(root, replica_path / root.relative_to(source_path)) for root, _, _ in source_path.walk()]
            with Pool(cpu_count()) as pool:
                dir_results = pool.map(create_directory, directories)
                log_lines.extend(filter(None, dir_results))

            # COPY FILES TO REPLICA
            # print("copy files to replica")
            files_to_compare = [
                (root / file, replica_path / root.relative_to(source_path) / file)
                for root, _, files in source_path.walk() for file in files
            ]
            with Pool(cpu_count()) as pool:
                copy_results = pool.map(copy_file, files_to_compare)
                log_lines.extend(filter(None, copy_results))

            # DELETE OLD REPLICA SUBDIRS
            # print("delete old replica subdirs")
            rel_source_dirs = [root.relative_to(source_path) for root, _, _ in source_path.walk() if root != source_path]
            # print('rel_source_dirs\n', '\n'.join(map(str, rel_source_dirs)))
            replica_dirs_to_rm = [
                root for root, _, _ in replica_path.walk() if
                not (source_path / root.relative_to(replica_path)).exists() and
                root != replica_path
                ]
            print('replica_dirs_to_rm\n', '\n'.join(map(str, replica_dirs_to_rm)))
            with Pool(cpu_count()) as pool:
                dirs_del = filter(None, pool.map(del_dir, clean_subdirs(replica_dirs_to_rm)))
                log_lines.extend(chain(*dirs_del))

            # DELETE OLD REPLICA FILES NOT IN OLD SUBDIRS
            # print("delete old replica files not in old subdirs")
            replica_files_to_rm = [
                root / file for root, _, files in replica_path.walk() for file in files
                if root not in replica_dirs_to_rm and not (source_path / root.relative_to(replica_path) / file).exists()]
            print('replica_files_to_rm\n', '\n'.join(map(str, replica_files_to_rm)))
            with Pool(cpu_count()) as pool:
                files_del = pool.map(del_file, replica_files_to_rm)
                log_lines.extend(filter(None, files_del))

            if len(log_lines) > 1:
                log_lines.append('\n')
                with open(log_file, 'a') as lf:
                    lf.writelines(log_lines)
            time.sleep(interval)

        except KeyboardInterrupt or OSError:
            print("Sync interrupted by user.")
            break
        except Exception as e:
            print(f'Synchronization error: {e}')
            tries += 1
            if tries > MAX_TRIES:
                print(f'Syncing failed {MAX_TRIES}, exiting')
                break

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Folder sync util")
    parser.add_argument("source_folder", help="Path to the source folder")
    parser.add_argument("replica_folder", help="Path to the replica folder")
    parser.add_argument("interval", type=float, help="Synchronization interval in seconds (float or int)")
    parser.add_argument("log_file", help="Path to the log file")
    args = parser.parse_args()

    folder_sync(args.source_folder, args.replica_folder, args.interval, args.log_file)
