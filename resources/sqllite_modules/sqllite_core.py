import glob
import os
import sqlite3

import pandas as pd

from resources.Files import dir
from resources.data_splitter import data_splitter
from resources.helpers import progress_indicator

os.chdir(dir.dirname)

db = sqlite3.connect("users.db")


def split_main():
    tot = 1
    for files in glob.glob('*.xlsx'):
        progress_indicator.show_progress_percentage(tot, 54, "Splitting files")
        if get_first_date(files[:-5]) is not None:
            for i in range(3):
                if i == 0:
                    data_splitter.split(files[:-5], 10)
                elif i == 1:
                    data_splitter.split(files[:-5], 227)
                else:
                    data_splitter.split(files[:-5], 300)
        tot += 1


def create_and_insert_files():
    tot = 1
    for files in glob.glob('*.xlsx'):
        progress_indicator.show_progress_percentage(tot, 54, "Creating files and inserting data")
        create_table(files)
        insert_data(files)
        tot += 1


def create_window_files():
    tot = 1
    for files in glob.glob('*.xlsx'):
        progress_indicator.show_progress_percentage(tot, 54, "Creating window files")
        if get_first_date(files[:-5]) is not None:
            for i in range(3):
                if i == 0:
                    create_table_windows(files[:-5], 10, 1)
                    create_table_windows(files[:-5], 10, 2)
                    # print("\n" + files[:-5] + "_" + str(10) + " split")
                elif i == 1:
                    create_table_windows(files[:-5], 227, 1)
                    create_table_windows(files[:-5], 227, 2)
                    # print("\n" + files[:-5] + "_" + str(227) + " split")
                else:
                    create_table_windows(files[:-5], 300, 1)
                    create_table_windows(files[:-5], 300, 2)
                    # print("\n" + files[:-5] + "_" + str(5) + " split")
        tot += 1


def delete_weekends_main():
    tot = 1
    for files in glob.glob('*.xlsx'):
        delete_weekends(files[:-5])
        progress_indicator.show_progress_percentage(tot, 54, "Deleting weekends")
        tot += 1


def delete_after_hours_main():
    tot = 1
    for files in glob.glob('*.xlsx'):
        delete_unnecessary(files[:-5])
        progress_indicator.show_progress_percentage(tot, 54, "deleting after hours")
        tot += 1


def csv_from_excel(file):
    data_xls = pd.read_excel(file, 'Sheet1', index_col=None)
    data_xls.to_csv(file[:-5] + '.csv', encoding='utf-8')


def create_table(file):
    query = "CREATE TABLE " + file[:-5] + "(ID TEXT, unix_secs TEXT, sysuptime TEXT, dpkts TEXT, doctets TEXT," \
                                          " doctets_" \
                                          "dpkts TEXT, real_first_packet TEXT, real_end_packet TEXT, first TEXT, " \
                                          "last TEXT, duration TEXT)"
    c = db.cursor()
    c.execute(query)
    db.commit()
    insert_data(file)


def insert_data(file):
    read = pd.read_excel(r"" + file, index_col=None)
    read = read.rename(columns=({"doctets/dpkts": "doctets_dpkts", "Real First Packet": "real_first_packet",
                                 "Real End Packet": "real_end_packet"}))
    read.to_sql(file[:-5], db, if_exists="append", index=False)


def get_data(file):
    cur = db.cursor()
    cur.execute("Select doctets, real_first_packet, duration from " + file + " order by real_first_"
                                                                             "packet asc")
    rows = cur.fetchall()
    # for row in rows:
    #     print(row)
    return rows


def get_split_data(file, window, week):
    cur = db.cursor()
    cur.execute("Select * from " + file + "_" + str(window) + "_" + str(week))
    rows = cur.fetchall()
    print(rows)


def get_split_ratio_data(file, window, week):
    cur = db.cursor()
    cur.execute("Select ratio from " + file + "_" + str(window) + "_" + str(week))
    rows = cur.fetchall()
    return rows


def is_only_zero(file, window, week):
    cur = db.cursor()
    cur.execute("Select distinct(ratio) as ratio, start from " + file + "_" + str(window) + "_" + str(week))
    for ratio, start in cur.fetchall():
        if ratio != 0:
            return False
    return True


def get_window_count_week(file, window):
    cur = db.cursor()
    cur.execute("Select count(*) as count, start from " + file + "_" + str(window) + "_1")
    rows = cur.fetchall()
    for count, start in rows:
        return count


def get_first_date(file):
    cur = db.cursor()
    cur.execute("Select real_first_packet, duration from " + file + " order by real_first_packet asc "
                                                                    "limit 1")

    for real_first_packet, duration in cur.fetchall():
        return real_first_packet


def calc_real_first_packet(unix_secs, sysuptime, first):
    unix_secs = int(unix_secs)
    sysuptime = int(sysuptime)
    first = int(first)
    print(((unix_secs * 1000) - sysuptime) + first)
    return str(((unix_secs * 1000) - sysuptime) + first)


def delete_zero(table):
    cur = db.cursor()
    query = "DELETE FROM " + table + " where duration = '0'"
    cur.execute(query)
    db.commit()


def delete_unnecessary(table):  # times before 8 and after 5
    cur = db.cursor()
    query = "Delete from " + table + \
            " where 1 = CASE" \
            " when cast(strftime('%H',datetime(substr(real_first_packet, 1, length(real_first_packet)-3), " \
            "'unixepoch', 'localtime')) as decimal) > 16 " \
            " then 1 " \
            " when cast(strftime('%H',datetime(substr(real_first_packet, 1, length(real_first_packet)-3), " \
            "'unixepoch', 'localtime')) as decimal) < 8 " \
            " then 1 " \
            " else 0 end"
    cur.execute(query)
    db.commit()


def select_check(file):
    cur = db.cursor()
    query = "Select real_first_packet , cast(strftime('%w',datetime(substr(real_first_packet, 1, " \
            "length(real_first_packet)-3), " \
            "'unixepoch')) as decimal) as time from " + file + \
            ""
    cur.execute(query)
    rows = cur.fetchall()
    for row in rows:
        print(row)


def delete_weekends(table):
    cur = db.cursor()
    query = "Delete from " + table + " where  cast(strftime('%w',datetime(substr(real_first_packet, 1, " \
                                     "length(real_first_packet)-3),'unixepoch', 'localtime')) as decimal) = 0 OR " \
                                     "cast(strftime('%w',datetime(substr(real_first_packet, 1, " \
                                     "length(real_first_packet)-3), " \
                                     "'unixepoch', 'localtime')) as decimal) = 6"
    cur.execute(query)
    db.commit()


def create_table_windows(file, window, week):  # creates table for each file wrt to window splits
    cur = db.cursor()
    query = "CREATE table if not exists " + file + "_" + str(window) + "_" + str(week) + \
            " (Day text, Start text, End text, ratio decimal)"
    cur.execute(query)
    db.commit()


def insert_table_windows(file, window, week, records):
    cur = db.cursor()
    query = "Insert into " + file + "_" + str(window) + "_" + str(week) + " values(?, ?, ?, ?)"
    cur.executemany(query, records)
    db.commit()


def delete_table_window(file, window, week):
    cur = db.cursor()
    query = "Delete from " + file + "_" + str(window) + "_" + str(week)
    cur.execute(query)
    db.commit()


def delete_dir_files():
    for files in glob.glob('*.xlsx'):
        print(files)
        if get_first_date(files[:-5]) is not None:
            for i in range(3):
                if i == 0:
                    delete_table_window(files[:-5], 10, 1)
                    delete_table_window(files[:-5], 10, 2)

                    print(files[:-5] + "_" + str(10) + " deleted")
                elif i == 1:
                    delete_table_window(files[:-5], 227, 1)
                    delete_table_window(files[:-5], 227, 2)
                    print(files[:-5] + "_" + str(227) + " deleted")
                else:
                    delete_table_window(files[:-5], 300, 1)
                    delete_table_window(files[:-5], 300, 2)
                    print(files[:-5] + "_" + str(300) + " deleted")
