from resources.sqllite_modules import sqllite_core
import datetime
import time

epoch_8 = 0

records = []


def create_epoch_8(first):  # creates the first window 8'0 clock for the particular date in local time
    year = time.strftime("%Y", time.localtime(int(first[:-3])))
    month = time.strftime("%m", time.localtime(int(first[:-3])))
    day = time.strftime("%d", time.localtime(int(first[:-3])))
    hour = 8
    minute = 0
    global epoch_8
    epoch_8 = datetime.datetime(int(year), int(month), int(day), hour, minute).timestamp()


def split(file, window):  # this is where data split magic happens.
    global records
    records = []
    rows = sqllite_core.get_data(file)
    first_data = sqllite_core.get_first_date(file)
    create_epoch_8(first_data)
    start = epoch_8
    epoch = epoch_8
    end = start + window
    doctets_total = 0
    day_count = 0
    total = 0
    week = 1
    reset_day_count = True
    first_day = time.strftime("%w", time.localtime(int(first_data[:-3])))
    check_done = True
    if int(first_day) == 5 or int(first_day) == 4:
        check_done = False
        reset_day_count = False
    for doctets, real_first_packet, duration in rows:
        day_check = time.strftime("%w", time.localtime(int(real_first_packet[:-3])))
        doctets = int(doctets)
        duration = int(duration)
        real = int(real_first_packet[:-3])
        end = float(end)
        if not check_done and (int(day_check) != 1):  # Skips to Monday when the start is Friday
            continue
        if day_count > 14:
            break
        check_done = True

        while real >= end:
            if total != 0:
                avg = doctets_total / total
            else:
                avg = 0
            if avg != 0:
                ratio = float(avg)
            else:
                ratio = 0
            if reset_day_count:
                put_data(ratio, start, end)
            start += window
            end = float(end)
            end += window
            doctets_total = 0
            hour = time.strftime("%H", time.localtime(int(end)))
            if int(hour) >= 17:  # this condition check is to switch to next day when hour exceeds 17
                epoch += 86400
                start = epoch
                end = start + window
                doctets_total = 0
                day_count += 1
                if day_count == 7:  # to insert data for the first week
                    insert_data(file, window, week)
                    week += 1
                start_day = time.strftime("%w", time.localtime(int(start)))
                if not reset_day_count:
                    day_count = 0
                    if int(start_day) == 1:
                        reset_day_count = True
            if day_count > 13:
                insert_data(file, window, week)
                return
        if real < end:
            if duration != 0:
                doctets_total = doctets_total + float(doctets / duration)
                total += 1

            else:
                doctets_total = 0
                total = 0
            hour = time.strftime("%H", time.localtime(int(end)))
            if int(hour) >= 17:
                epoch += 86400
                start = epoch
                end = start + window
                doctets_total = 0
                day_count += 1
                if day_count == 7:
                    insert_data(file, window, week)
                    week += 1
                start_day = time.strftime("%w", time.localtime(int(start)))
                if not reset_day_count:
                    day_count = 0
                    if start_day == 1:
                        reset_day_count = True
            if day_count > 13:
                insert_data(file, window, week)
                return


def put_data(ratio, start, end):  # puts all data into a temporary array. Fastens the
    start_day = time.strftime("%w", time.localtime(int(start)))  # insertion of data into the tables
    global records
    record = (str(start_day), str(start), str(end), ratio)
    records.append(record)


def get_data():
    global records
    print(records)


def insert_data(file, window, week):  # inserts the split data with the corresponding ratios into the table
    global records
    sqllite_core.insert_table_windows(file, window, week, records)
    del records[:]
