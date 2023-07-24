# What is it?

A python library and commandline tool to access and sync data from a ezShare WIFI SD Card.

[![asciicast](https://asciinema.org/a/R7jcHXTVy1rP97TQdyQfSFwf8.svg)](https://asciinema.org/a/R7jcHXTVy1rP97TQdyQfSFwf8)


# How to install?

```
    pip install ezshare
```

# How to use the commandline?

The commandline is really dead simple. It allows to list the card contents (_-l_, _--list_) and download (_-d_, _--download_) files
off the card. _-r_, _--recursive_ makes these operations recursive.

The source can be either a file or a directory (specified with -d). The target directory is the current working directory, 
unless specified otherwise with _-t_ option. The target can be either a file for single-file downloads, or a dir (ending with /)

When downloading directories recursively the behavior is as follows: 

* If the file doesn't exist on the local machine - create it and download

* If the file exists but differs in size - assume a broken download and download it again

* If the file exists and the size is the same as the remote - assume it's been already downloaded and skip it

There are also two weird, but most useful options: 

* _-w_, _--wait_ - Ping the card until it's detected. 
* _--live_ - Live mode. 

See `--help` for up-to-date options. Typical usage examples are below.

```
~# ezshare-cli [-h] [-l LIST] [-d DOWNLOAD] [-r] [-t TARGET] [-w] [--live LIVE]

Unofficial ezShare cli tool

optional arguments:
  -h, --help            show this help message and exit
  -l LIST, --list LIST  List remote directory
  -d DOWNLOAD, --download DOWNLOAD
                        Download a remote file or directory
  -r, --recursive       Recurse to subdirs on list/download
  -t TARGET, --target TARGET
                        Specify target directory for downloads
  -w, --wait            Wait for WiFi SD to appear on the network
  --live LIVE           Live mode. Don't exit after syncronisation.The argument specifies cooldown in seconds
                        between sync. See docs for details
```

## List card contents

In a single directory

```
$ ezshare-cli -l /
Listing remote directory: /
 DCIM/
```

or recursively

```
Listing remote directory: /
 DCIM/
  101CANON/
   IMG_0356.JPG
   IMG_0357.JPG
```


## Download a single file to current directory

```
ezshare-cli -d /DCIM/101CANON/IMG_0356.JPG 
Synchronizing remote /DCIM/101CANON/IMG_0356.JPG -> .
./IMG_0356.JPG: 100%|██████████████████| 4.45M/4.45M [00:02<00:00, 1.71MB/s]

```

## Download a single file to a custom destination

```
Synchronizing remote /DCIM/101CANON/IMG_0356.JPG -> /tmp/
/tmp/IMG_0356.JPG: 100%|███████████████| 4.45M/4.45M [00:02<00:00, 1.68MB/s]
```

## Recursively download a directory

```
$ ezshare-cli -r -d / -t /tmp/SD_CONTENTS/
Synchronizing remote / -> /tmp/SD_CONTENTS/
/tmp/SD_CONTENTS/DCIM/101CANON/IMG_0356.JPG: 100%|███████████████| 4.45M/4.45M [00:05<00:00, 862kB/s]
/tmp/SD_CONTENTS/DCIM/101CANON/IMG_0357.JPG: 100%|███████████████| 2.86M/2.86M [00:02<00:00, 1.04MB/s]
```

## Wait for the card connection and synchronize contents when the card is available


```
$ ezshare-cli -w -r -d / -t /tmp/SD_CONTENTS/
Waiting for ezShare card...ONLINE!
Synchronizing remote / -> /tmp/SD_CONTENTS/
/tmp/SD_CONTENTS/DCIM/101CANON/IMG_0356.JPG: 100%|███████████████| 4.45M/4.45M [00:05<00:00, 862kB/s]
/tmp/SD_CONTENTS/DCIM/101CANON/IMG_0357.JPG: 100%|███████████████| 2.86M/2.86M [00:02<00:00, 1.04MB/s]
0 ✓ necromant @ silverblade /tmp $ 

```


## Continuous sync mode

Now this should be the most useful. In this mode the app pings the card until it's available, syncs the directories as specified, and sleeps for a timeout of seconds that is specified after the live option. You can specify the target directory in your nextcloud/dropbox/whatever directory and all
the photos will automagically sync to the cloud as soon as you connect your card.

```
$ ezshare-cli -w -r -d / -t /tmp/SD_CONTENTS/ --live 10
Waiting for ezShare card.ONLINE!
Synchronizing remote / -> /tmp/SD_CONTENTS/
/tmp/SD_CONTENTS/DCIM/101CANON/IMG_0356.JPG: 100%|████████████████| 4.45M/4.45M [00:05<00:00, 904kB/s]
/tmp/SD_CONTENTS/DCIM/101CANON/IMG_0357.JPG: 100%|████████████████| 2.86M/2.86M [00:02<00:00, 1.08MB/s]
Live mode. Next sync in 10 seconds
Waiting for ezShare card.ONLINE!
Synchronizing remote / -> /tmp/SD_CONTENTS/
Skipping file /tmp/SD_CONTENTS/DCIM/101CANON/IMG_0356.JPG (same size)
Skipping file /tmp/SD_CONTENTS/DCIM/101CANON/IMG_0357.JPG (same size)
Live mode. Next sync in 10 seconds
...
```


# Limitations

* There's no way to actually remove or upload files to the card. This is the hardware limitation;

* There's no way to make the card work in client mode or change the IP address. But you can work this around with an OpenWRT router. 
Check out my blog for a neat trick: TODO

# Extra

Check out the docker-compose.yml and Dockerfile for an automated webdav uploader that I'm running.
It's not yet up at dockerhub, but I plan to fix it soon.

The idea is simple: 

* Mount webdav via fuse inside the docker container, 
* Run the 'live' mode of ezshare, 
* Get all the photos delivered into your cloud file storage.
* ...
* PROFIT!

# Changelog

v0.0.11 - bugfix release

  * Fixed handling empty dirs (#1). Thanks to @gustou.
  * Implement retry logic on buggy cards. Thanks to @dieu

v0.0.10 - initial release.