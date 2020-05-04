from sys import *

init = 1


def show_progress(total, message):
    stdout.write('\r')
    global init
    stdout.write(message + ": " + str(init) + "/" + str(total))
    init += 1
    stdout.flush()


def show_progress_percentage(i, total, message):
    stdout.write('\r')
    per = (i*100/total)
    stdout.write(message + " - " + str(int(per)) + "%")
