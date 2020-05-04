from resources.Files import dir
import os
import sqlite3
import csv
import time

os.chdir(dir.dirname)

db = sqlite3.connect("users.db")


def get_data_check():
    cur = db.cursor()
    query = "SELECT real_first_packet, duration FROM ajb9b3"
    cur.execute(query)
    rows = cur.fetchall()
    for real_first_packet, duration in rows:
        start = time.strftime("%H:%M:%S %w", time.gmtime(int(real_first_packet[:-3])))
        print(str(start))


def get_window_data_check(file, window):
    cur = db.cursor()
    query = "SELECT day, start, end, ratio FROM " + file + "_" + str(window)
    cur.execute(query)
    rows = cur.fetchall()
    for day, start, end, ratio in rows:
        start_time = time.strftime("%H:%M:%S", time.gmtime(int(float(start))))
        end_time = time.strftime("%H:%M:%S", time.gmtime(int(float(end))))
        print(str(day) + " " + start_time + " " + end_time + " " + str(ratio))


def get_window_count_check(file, window):
    cur = db.cursor()
    query = "SELECT count(*) as count from " + file + "_" + str(window)
    cur.execute(query)
    rows = cur.fetchall()
    for count in rows:
        print(count)


def create_copy():
    cur = db.cursor()
    query = "CREATE table if not exists ajb9b3_copy (Day text, Start text, End text, ratio decimal)"
    cur.execute(query)
    db.commit()


def copy_data():
    cur = db.cursor()
    query = "INSERT into ajb9b3_copy select * from ajb9b3_10"
    cur.execute(query)
    db.commit()


def update_copy(op):
    cur = db.cursor()
    query = ""
    if op == 1:
        query = "Update ajb9b3_copy set Start = strftime('%H:%M:%S', cast(Start as integer), 'unixepoch')"
    if op == 2:
        query = "Update ajb9b3_copy set End = strftime('%H:%M:%S', cast(End as integer) , 'unixepoch')"
    cur.execute(query)
    db.commit()


def delete_data():
    cur = db.cursor()
    query = "Delete from ajb9b3_copy"
    cur.execute(query)
    db.commit()


def export_data_csv():
    cursor = db.cursor()
    cursor.execute("select * from ajb9b3_copy")
    with open("ajb9b3_copy.csv", "w") as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(['day', 'start', 'end', 'ratio'])
        csv_writer.writerows(cursor)


def get_data_copy():
    cur = db.cursor()
    query = "select * from ajb9b3_copy"
    cur.execute(query)
    for row in cur.fetchall():
        print(row)


def get_time_zone_check(file):
    cur = db.cursor()
    query = "Select real_first_packet from " + file + " where  cast(strftime('%w',datetime(substr(real_first_packet, 1, " \
                                     "length(real_first_packet)-3), " \
                                     "'unixepoch', 'localtime')) as decimal) = 0 OR cast(strftime('%w',datetime(substr(" \
                                     "real_first_packet, 1, " \
                                     "length(real_first_packet)-3), " \
                                     "'unixepoch', 'localtime')) as decimal) = 6"
    cur.execute(query)
    rows = cur.fetchall()
    for row in rows:
        print(row)
