#!/bin/bash -x

#Check veriables or set defaults
if [ -z ${WEBDRIVE_USER} ]; then
  echo "Webdrive user is not set"
fi

if [ -z ${WEBDRIVE_PASSWORD} ]; then
  echo "Webdrive password is not set"
fi

if [ -z ${WEBDRIVE_URL} ]; then
  echo "Webdrive url is not set"
fi

USER=${WEBDRIVE_USER}
PASSWORD=${WEBDRIVE_PASSWORD}
URL=${WEBDRIVE_URL}
FOLDER_USER=${SYNC_USERID:-0}

echo "$URL $USER $PASSWORD" >> /etc/davfs2/secrets
cat /etc/davfs2/secrets

# Create user
if [ $FOLDER_USER -gt 0 ]; then
  useradd webdrive -u $FOLDER_USER -N -G users
fi

# Mount the webdav drive 
mkdir -p $WEBDRIVE_DIR
umount $WEBDRIVE_DIR
#ezshare-cli -l /
mount -t davfs $URL $WEBDRIVE_DIR -o uid=$FOLDER_USER,gid=users,dir_mode=755,file_mode=755
ezshare-cli -w -r --live $EZSHARE_LIVE_TIMEOUT -d $EZSHARE_REMOTE_DIR -t $WEBDRIVE_DIR