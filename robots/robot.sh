#!/bin/bash

echo Switching to robot $1

ROBOT_PATH=~/opentrons/robots
OT_PATH=~/.config/OT\ One\ App\ 2/otone_data

if [ -v APP_DATA_DIR ]; then
	# We were already switched to a robot
	# back it up
	cp $APP_DATA_DIR/calibrations/calibrations.json $APP_DATA_DIR/calibrations/calibrations-`date -Iseconds`.json.bak
fi

for robotdev in `ls /dev/ttyACM-*`; do
	if [ -h $robotdev ]; then
		echo "Removing $robotdev"
		sudo rm $robotdev
	fi
done

rm "$OT_PATH"
ln -s $ROBOT_PATH/$1 "$OT_PATH"

export CURRENT_ROBOT=$1
export APP_DATA_DIR=$ROBOT_PATH/$1
export ROBOT_DEV=/dev/$1

sudo ln -s $ROBOT_DEV /dev/ttyACM-$1

if [ -v OLD_PS1 ]; then
	export PS1="$OLD_PS1"
fi

export OLD_PS1="$PS1"
export PS1="[$1] $PS1"
