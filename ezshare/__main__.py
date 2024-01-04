import binascii
from lxml.html import parse as parse_url
from parse import parse
import requests
from tqdm import tqdm
from os import path
import os
import io
import time
import sys

class ezshare():
    def __init__(self, url="http://ezshare.card/dir?dir=A:", num_retries=5):
        self.base = url
        self.num_retries = num_retries

    def is_dir(self, href):
        r = parse("{}/download?file={name}", href)
        return r == None

    def is_file(self, href):
        return not self.is_dir(href)

    def _get(self, url):
        #print(f"GET {url}")
        return parse_url(url)

    def ping(self):
        try:
            self._get(self.base)
            return True
        except:
            return False

    def listdir(self, dir, recursive=False, shift=0):
        ret = {}
        is_root = False
        if dir=="/":
            dir=""
            is_root = True
        dir=dir.replace("/","\\")
        soup = self._get(f"{self.base}{dir}")
        has_dotiles=False
        for a in soup.xpath("//pre/a"):
            href = a.get("href")
            name = a.text.strip()
            if name == "." or name == ".." or name == "ezshare.cfg":
                has_dotiles=True
                continue
            if self.is_dir(href):
                ret[name] = {}
                if recursive:
                    dir_content = self.listdir(f"{dir}/{name}", recursive=recursive)
                    if dir_content is not None:
                        ret[name] = dir_content
            else:
                ret[name] = href
        #No dotfiles or ezshare.cfg and is not root? This must not be a directory
        if not has_dotiles and not is_root: 
            return None
        return ret

    def print_list(self, dirlist, shift=0):
        shiftstr = " " * shift
        for k,v in dirlist.items():
            if type(v) is dict:
                print(f"{shiftstr} {k}/")
                self.print_list(v, shift=shift+1)
            else:
                print(f"{shiftstr} {k}")


    def stream_size(self, stream):
        pos = stream.tell()
        stream.seek(0,2)
        ln = stream.tell()
        stream.seek(pos)
        return ln - pos

    def _dload(self, link, file_name, crc):
        with open(file_name, "a+b") as f:
            f.seek(0)
            response = requests.head(link)
            curlength = self.stream_size(f)
            total_length = int(response.headers.get('content-length'))
            if not crc and curlength == total_length:
                print(f"Skipping file {file_name} (same size)")
                return True        

            response = requests.get(link, stream=True)
            if total_length is None: # no content length header
                f.truncate()
                f.write(response.content)
                return True
            elif crc and curlength == total_length:
                f_crc32_hash = binascii.crc32(f.read())
                r_crc32_hash = binascii.crc32(response.content)
                if f_crc32_hash == r_crc32_hash:
                    print(f"Skipping file {file_name} (same crc32 sum)")
                    return True

            total_length = int(total_length)
            with tqdm(desc=file_name, total=total_length, unit='B', unit_scale=True, unit_divisor=1024, miniters=1) as pbar:
                f.truncate(0)
                for data in response.iter_content(chunk_size=4096):
                    f.write(data)
                    pbar.update(len(data))
            return True

    def _dload_with_retry(self, link, file_name, crc):
        last_exception = None
        for retries in range(self.num_retries):
            try:
                return self._dload(link, file_name, crc)
            except (requests.exceptions.ConnectionError, requests.exceptions.ChunkedEncodingError) as err:
                print(f"Retrying link: {link} ({retries} times)")
                last_exception = err
        if last_exception is not None:
            print(f"Failed to download {link}: {last_exception}")
        return False

    def download(self, remote_file, local_file=None, recursive=False, crc=False):
        if local_file == None:
            local_file = path.basename(remote_file)
        if local_file[-1]=="/":
            os.makedirs(local_file, exist_ok=True)
        if path.isdir(local_file):
            local_file = path.join(local_file, path.basename(remote_file))
        remote_dir = path.dirname(remote_file)
        basename = path.basename(remote_file)
        link = self.listdir(remote_dir, recursive)[basename]
        self._dload_with_retry(link, local_file, crc)

    def _sync_list(self, todo, local_dir, crc):
        os.makedirs(local_dir, exist_ok=True)
        for k,v in todo.items():
            if type(v) is dict:
                self._sync_list(v, path.join(local_dir, k), crc)
            elif v:
                self._dload_with_retry(v, path.join(local_dir, k), crc)
            else:
                print(f"Skipping sync of {k} because link is {v}")

    def sync(self, remote_dir, local_dir=".", recursive=False, crc=False):
        if local_dir == None:
            local_dir = "."

        todo = self.listdir(remote_dir, recursive=recursive)
        if todo is None:
            self.download(remote_dir, local_dir, crc=crc)
        else:
            self._sync_list(todo, local_dir, crc)

def _handle_args_once(args, s):
    if args.wait:
        print("Waiting for ezShare card.", end='')
        while True:
            if s.ping():
                break
            time.sleep(1)
            print(".", end='')
            sys.stdout.flush()
        print("ONLINE!")

    if not args.list is None:
        print(f"Listing remote directory: {args.list}")
        d = s.listdir(args.list, recursive=args.recursive)
        s.print_list(d)
    if not args.download is None:
        print(f"Synchronizing remote {args.download} -> {args.target}")
        s.sync(args.download, args.target, recursive=args.recursive, crc=args.crc)
    
def main():
    import argparse

    parser = argparse.ArgumentParser(description='Unofficial ezShare cli tool')
    parser.add_argument('-n', '--number_retries', type=int, default=5, help="Number of retries on failed downloads")
    parser.add_argument('-l', '--list', help="List remote directory")
    parser.add_argument('-d', '--download', help="Download a remote file or directory")
    parser.add_argument('-r', '--recursive', action="store_true", default=False, help="Recurse to subdirs on list/download")
    parser.add_argument('-t', '--target', default=".", help="Specify target directory for downloads")
    parser.add_argument('-w', '--wait',  action="store_true", default=False, help="Wait for WiFi SD to appear on the network")
    parser.add_argument('-c', '--crc', action="store_true", default=False, help="Enable CRC check on files")
    parser.add_argument('--live', type=int, default=-1, help="Live mode. Don't exit after syncronisation."
                                                             "The argument specifies cooldown in seconds between sync. See docs for details")

    args = parser.parse_args()
    s = ezshare(num_retries=args.number_retries)
    while True:
        _handle_args_once(args, s)
        if args.live >= 0:
            print(f"Live mode. Next sync in {args.live} seconds")
            time.sleep(args.live)
        else:
            break

if __name__ == "__main__":
    main()

