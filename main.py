from resources.correlation import operation_all
from resources.helpers import reinit_files
import sys


if len(sys.argv) > 1:
    if sys.argv[1] == "re_init":
        reinit_files.re_init()              # re initialises table and data and splits the data from scratch
    else:
        print("argument unrecognizable, please enter the following argument :-")
        print("re_init")
else:
    operation_all.operation_main()          # starts the operation main function
