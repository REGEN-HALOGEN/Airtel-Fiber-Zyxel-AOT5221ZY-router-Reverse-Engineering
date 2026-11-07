#!/bin/sh
RUN=1
PROCESS="/bin/zywifid"
PROCESS_ARG=""
PROCESS_PID=
kill_process() {
        trap '' INT TERM QUIT
        echo "stop ${PROCESS}......."
        if [ -e "/proc/$PROCESS_PID/status" ]; then
                kill -TERM $PROCESS_PID
        else
                killall ${PROCESS##*/}
        fi
        wait
        RUN=0
        exit
}
trap 'kill_process' INT TERM QUIT
while [ $RUN == 1 ]
do
		killall -9 ${PROCESS##*/}
        (trap - INT TERM QUIT; exec ${PROCESS} ${PROCESS_ARG}) &
        PROCESS_PID=$!
        wait
        sleep 2
        echo "${PROCESS} restart....."
		PROCESS_ARG="auto"
done