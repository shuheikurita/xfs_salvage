import subprocess
import re
import fire

def get_xfs_db_output(inode, img_file):
    """ Executes xfs_db command and returns the output for a given inode. """
    try:
        cmd = f"xfs_db -F {img_file} -c sb -c 'inode {inode}' -c 'dblock 0' -c 'p'|grep -E \"name =|inumber|filetype\""
        result = subprocess.run(cmd, shell=True, check=True, text=True, capture_output=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error executing xfs_db: {e} at inode ",inode)
        return None

def parse_xfs_db_output(output,inode=0):
    """ Parses the output of xfs_db to extract inode information. """
    entries = []
    for line in output.split('\n'):
        if 'name' in line:
            match = re.search(r'^.*\[(\d+)\]\.name\.?\w* = \"(.*)\"$', line)
            if match:
                number, value = match.groups()
                # assert line[:2] in ["bu","du","u3"], (line,match.group(),inode)
                if line[:2] not in ["bu","du","u3"]: continue
                number = int(number)
                if len(entries)<number+1:
                    entries.append({'name':''})
                entries[number]['name'] = value
        else:
            match = re.search(r'^.*\[(\d+)\]\.(\w+)\.?\w* = (\d+)$', line)
            if match:
                number, name, value = match.groups()
                # assert line[:2] in ["bu","du","u3"], (line,match.group(),inode)
                if line[:2] not in ["bu","du","u3"]: continue
                number = int(number)
                if len(entries)<number+1:
                    entries.append({'name':''})
                assert name in ['inumber','filetype'], name
                entries[number][name] = int(value)
    return entries

def traverse_directory(img_file, root_inode=128, path="", excludes=[], skip_dot_dir=False):
    """ Recursively traverses directories and lists files. """
    inode = root_inode
    output = get_xfs_db_output(inode, img_file)
    # print(output)
    if output is None:
        return

    entries = parse_xfs_db_output(output,inode)
    entries = sorted(entries, key=lambda x: x['name'])
    for entry in entries:
        # skip incomplete info
        if len(entry)!=3: continue
        if len(entry['name'])==0: continue

        # skip curren and up
        if entry['name'] in [".",".."]: continue

        current_path = f"{path}/{entry['name']}"
        if entry['filetype'] == 2:  # Directory
            print(f"{entry['filetype']}\t{entry['inumber']}\t{current_path}/")
            if skip_dot_dir:
                if entry['name'][0]==".": continue
            for skip_path in excludes:
                if skip_path in current_path: break
            else:
                traverse_directory(img_file, entry['inumber'], current_path, excludes, skip_dot_dir)
        else:
            print(f"{entry['filetype']}\t{entry['inumber']}\t{current_path}")

if __name__=='__main__':
    fire.Fire(traverse_directory)
