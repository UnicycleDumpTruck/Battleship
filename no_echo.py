import termios
import atexit
import sys
from time import sleep


def enable_echo(fd, enabled):
    (iflag, oflag, cflag, lflag, ispeed, ospeed, cc) = termios.tcgetattr(fd)

    if enabled:
        lflag |= termios.ECHO
    else:
        lflag &= ~termios.ECHO

    new_attr = [iflag, oflag, cflag, lflag, ispeed, ospeed, cc]
    termios.tcsetattr(fd, termios.TCSANOW, new_attr)


atexit.register(enable_echo, sys.stdin.fileno(), True)

if __name__ == "__main__":
    enable_echo(sys.stdin.fileno(), False)
    sleep(10)
