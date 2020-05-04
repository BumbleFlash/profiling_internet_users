from resources.sqllite_modules import sqllite_core
from resources.correlation import operation_all


def re_init():
    sqllite_core.create_and_insert_files()  # inserts data into sqlite
    print("\nFiles created and inserted")
    sqllite_core.delete_after_hours_main()  # deletes non 8 - 5 data
    print("\nDeleted after hours")
    sqllite_core.delete_weekends_main()  # deletes weekends
    print("\nDeleted weekends")
    sqllite_core.create_window_files()  # creates tables for each window for week 1 and 2
    print("\nCreated windows")
    sqllite_core.split_main()  # splits data and stores them in the window table
    print("\nData Splitting Complete")
    operation_all.operation_main()  # starts operation
