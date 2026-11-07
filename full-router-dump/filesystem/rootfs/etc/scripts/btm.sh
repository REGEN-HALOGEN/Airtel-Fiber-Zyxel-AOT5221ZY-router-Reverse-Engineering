#! /bin/sh

start()
{
	/usr/bin/btm normal &
}

stop()
{
	killall -9 btm
}

restart()
{
	stop
	start
}

test()
{
	/usr/bin/btm test &
}

restartTest()
{
	stop
	test
}

case "$1" in
	
	start)
			echo "Starting button monitor in normal mode" > /dev/console
			start
			;;
	stop)
			echo "Stopping button monitor in normal mode" > /dev/console
			stop
			;;
	restart)
			echo "Restarting button monitor in normal mode" > /dev/console
			restart
			;;
	test)
			echo "Starting button monitor in test mode" > /dev/console
			test
			;;
	restartTest)
			echo "Starting button monitor in test mode" > /dev/console
			restartTest
			;;
	*)
			echo "Usage: $0 {start|stop|restart|test|restartTest}" >&2 > /dev/console
			exit 1
			;;
esac

exit 0
