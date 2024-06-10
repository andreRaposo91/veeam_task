# Veeam Test Task - Internal Development Team QA

## Folder Synchronization CLI Tool

When running, this cli tool will keep a replica of the chosen source folder up to date at a constant time interval, defined by the user, and log the changes in a logfile.

### How it works

First, it checks if the input arguments are valid, if the source folder exists and if the replica folder needs to be created. Then it walks through the source folder, checking if files are already in the replica folder and up to date or if they need to be copied. If there are files and directories that are on the replica folder but not on the source folder, they are deleted. All actions are logged on the log file.

### Usage

On Windows

```
python folder_sync_v1.py source_folder replica_folder sync_interval logfile_path
```

On Unix-style systems
```
python3 folder_sync_v1.py source_folder replica_folder sync_interval logfile_path
```

Notes:
- the paths can be absolute or relative paths
- the *sync interval* is in seconds

### Testing

The **test.py** file creates some files and directories inside the **test/source** folder and launches a new process running the CLI tool. Between syncs, the source folder is updated randomly with files and directories.

### Versions

- v1 is simpler implementation, efficient for small folder and file sizes
- v2 is a parallelization attempt, but it is not optimized, so its slower for small folders
