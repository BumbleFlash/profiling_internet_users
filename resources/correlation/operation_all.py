import os
import glob
from resources.Files import dir
from resources.correlation import operations
from resources.sqllite_modules import sqllite_core
import pandas as pd
from resources.helpers import progress_indicator

os.chdir(dir.dirname)

p_10 = {}
p_227 = {}
p_300 = {}
c_10 = {}
c_227 = {}
c_300 = {}


def operation_main():
    print("Starting operation...")
    global p_10, p_227, p_300, c_227, c_10, c_300
    m, j = 1, 1
    tot = 1
    for file1 in glob.glob('*.xlsx'):  # row of users
        if sqllite_core.get_first_date(file1[:-5]) is not None:  # to check if the data is not empty
            for file2 in glob.glob('*.xlsx'):  # column of users
                progress_indicator.show_progress_percentage(tot, 2857, "Percentage completed")
                if sqllite_core.get_first_date(file2[:-5]) is not None:  # to check if the data is not empty
                    for i in range(3):
                        if i == 0:  # window of 10 seconds
                            if not check_for_zero(file1[:-5], file2[:-5], 10):
                                # print("Operating files " + file1[:-5] + " " + file2[:-5] + " for window 10")
                                p_10[m, j] = operations.operations_each_window(file1[:-5],
                                                                               file2[:-5],
                                                                               10)
                                if float(p_10[m, j]) > 0.05:
                                    c_10[m, j] = "No"
                                else:
                                    c_10[m, j] = "Yes"
                            else:
                                p_10[m, j] = "        -"
                                c_10[m, j] = "        -"

                        elif i == 1:
                            if not check_for_zero(file1[:-5], file2[:-5], 227):  # window of 227 seconds
                                # print("Operating files " + file1[:-5] + " " + file2[:-5] + " for window 227")
                                p_227[m, j] = operations.operations_each_window(
                                    file1[:-5], file2[:-5], 227)
                                if float(p_227[m, j]) > 0.05:
                                    c_227[m, j] = "No"
                                else:
                                    c_227[m, j] = "Yes"
                            else:
                                p_227[m, j] = "        -"
                                c_227[m, j] = "        -"

                        else:
                            if not check_for_zero(file1[:-5], file2[:-5], 300):  # window of 300 seconds
                                # print("Operating files " + file1[:-5] + " " + file2[:-5] + " for window 300")
                                p_300[m, j] = operations.operations_each_window(
                                    file1[:-5], file2[:-5], 300)
                                if float(p_300[m, j]) > 0.05:
                                    c_300[m, j] = "No"
                                else:
                                    c_300[m, j] = "Yes"
                            else:
                                p_300[m, j] = "        -"
                                c_300[m, j] = "        -"
                else:
                    p_10[m, j] = "        -"
                    p_227[m, j] = "        -"
                    p_300[m, j] = "        -"
                    c_10[m, j] = "        -"
                    c_227[m, j] = "        -"
                    c_300[m, j] = "        -"
                j += 1
                tot += 1
        else:
            for j in range(1, 55):
                p_10[m, j] = "        -"
                p_227[m, j] = "        -"
                p_300[m, j] = "        -"
                c_10[m, j] = "        -"
                c_227[m, j] = "        -"
                c_300[m, j] = "        -"
        j = 1
        m += 1
    print("\n")
    put_to_excel(p_10, 10)
    put_to_excel(p_227, 227)
    put_to_excel(p_300, 300)
    put_to_excel_choice(c_10, 10)
    put_to_excel_choice(c_227, 227)
    put_to_excel_choice(c_300, 300)


def check_for_zero(file1, file2, window):  # to check if there are any non-zero ratio values
    a = sqllite_core.is_only_zero(file1, window, 1)
    b = sqllite_core.is_only_zero(file1, window, 2)
    c = sqllite_core.is_only_zero(file2, window, 1)
    d = sqllite_core.is_only_zero(file2, window, 2)
    return a or b or c or d


def put_to_excel(p, window):  # exports to excel
    df = pd.DataFrame(p.values(), index=pd.MultiIndex.from_tuples(p.keys())).unstack(level=1)
    df.to_excel("../../p_" + str(window) + ".xlsx")
    print("File exported. Check for p_" + str(window) + ".xlsx" + " in the parent directory")


def put_to_excel_choice(c, window):  # exports choice to excel
    df = pd.DataFrame(c.values(), index=pd.MultiIndex.from_tuples(c.keys())).unstack(level=1)
    df.to_excel("../../c_" + str(window) + ".xlsx")
