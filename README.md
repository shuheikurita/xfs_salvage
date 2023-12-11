# xfs_salvage
A data salvage tool from a damaged xfs file system. This has a possibility to recover a file list in the half-broken xfs drive and file contents even after `xfs_repair -L` fails.  ABSOLUTELY NO WARRANTY.

## Prerequisite
- xfs_metadump
- xfs_mdrestore
- xfs_db

## Usage
1. First extract xfs metadata with xfs_metadump:
```sh
$ sudo xfs_metadump -w -o -a /dev/BROKEN_DRIVE drive.metadump.ao
$ xfs_mdrestore drive.metadump.ao drive.metadump.ao.img
```
Change BROKEN_DRIVE for your drive point.

2. Second recover the file path list from the dumped metadata:
```sh
$ python xfs_inode_salvage.py -i drive.metadump.ao.img \
--excludes="['uninteresting folders','src','bin','etc']" \
--skip_dot_directories=True
```
The results are tuple of filetype, inode and path.

3. Finally, get the original file contents with the (slightly modified) [xfs_undelete](https://github.com/shuheikurita/xfs_undelete) by recovered inodes.
