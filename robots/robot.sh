#!/bin/bash

echo Switching to robot $1

ROBOT_PATH=~/opentrons/robots
OT_PATH=~/.config/OT\ One\ App\ 2/otone_data

rm "$OT_PATH"
ln -s $ROBOT_PATH/$1 "$OT_PATH"

export APP_DATA_DIR=$ROBOT_PATH/$1
export ROBOT_DEV=/dev/ttyACM-$1

if [ -v OLD_PS1 ]; then
	export PS1="$OLD_PS1"
fi

export OLD_PS1="$PS1"
export PS1="[$1] $PS1"
