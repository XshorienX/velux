#!/bin/bash
# start.sh
# Download MongoDB binaries if not already installed (Render environments are wiped on deploy)
if [ ! -f $HOME/mongodb_bin/mongod ]; then
    echo "Downloading and installing MongoDB locally..."
    mkdir -p /tmp/mongodb
    cd /tmp/mongodb
    curl -O https://fastdl.mongodb.org/linux/mongodb-linux-x86_64-debian11-7.0.5.tgz
    tar -zxvf mongodb-linux-x86_64-debian11-7.0.5.tgz
    mkdir -p $HOME/mongodb_bin
    cp mongodb-linux-x86_64-debian11-7.0.5/bin/mongod $HOME/mongodb_bin/
    cd $HOME/src
fi

# Ensure data directory exists on the persistent disk
mkdir -p /data/db

# Start MongoDB in the background
echo "Starting MongoDB..."
$HOME/mongodb_bin/mongod --fork --logpath /data/db/mongodb.log --dbpath /data/db --bind_ip 127.0.0.1

# Start the FastAPI server
echo "Starting Uvicorn Server..."
cd $HOME/src
export PYTHONPATH=$HOME/src
uvicorn server:app --host 0.0.0.0 --port $PORT
