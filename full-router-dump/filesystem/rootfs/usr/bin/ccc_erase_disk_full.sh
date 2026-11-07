#!/bin/sh

# Certificate : 0x40 ~ 0x4D
DELETE_INDEX=""
for X in $(seq 64 77)
do
        INDEX=`printf "%x" $X`
        DELETE_INDEX="$DELETE_INDEX $INDEX"
done
mcputil del $DELETE_INDEX

# remove file in app partition
rm -rf /app/*
# remove file in userconfig partition
rm -rf /config/nonvolatile/*

exit 0
