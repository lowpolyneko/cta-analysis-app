#!/usr/bin/env python
import sqlite3

def command_1(db: sqlite3.Connection):
    """
    Matches a partial station name
    @param db database
    """
    search = input("Enter partial station name (wildcards _ and %): ")
    matches = execute(db, f"""
        SELECT * FROM Stations
        WHERE Station_Name LIKE '{search}'
        ORDER BY Station_Name ASC
    """)

    if not matches:
        print("**No stations found...")
        return

    for m in matches:
        print(f"{m[0]} : {m[1]}")

def execute(db: sqlite3.Connection, query: str) -> list:
    """
    Helper function that executes query in db
    @param db database
    @param query SQL query
    @return results
    """
    cur = db.cursor()
    res = cur.execute(query)

    return res.fetchall()

def print_stats(db: sqlite3.Connection):
    """
    Prints general statistics
    @param db database
    """
    # Run queries for data
    stations = execute(db, """
        SELECT COUNT(Station_ID) FROM Stations
    """)[0][0]

    stops = execute(db, """
        SELECT COUNT(Stop_ID) FROM Stops
    """)[0][0]

    rides = execute(db, """
        SELECT COUNT(*) FROM Ridership
    """)[0][0]

    date_range = execute(db, """
        SELECT DATE(MIN(Ride_Date)), DATE(MAX(Ride_Date)) FROM Ridership
    """)[0]

    total_ridership = execute(db, """
        SELECT SUM(Num_Riders) FROM Ridership
    """)[0][0]

    print("General Statistics:")
    print(f"  # of stations: {stations:,}")
    print(f"  # of stops: {stops:,}")
    print(f"  # of rides: {rides:,}")
    print(f"  date range: {date_range[0]} - {date_range[1]}")
    print(f"  Total ridership: {total_ridership:,}")

def main():
    # open db connection
    db = sqlite3.connect("CTA2_L_daily_ridership.db")

    print("** Welcome to CTA L analysis app **")
    print_stats(db)

    # main eval loop
    while True:
        i = input("Please enter a command (1-9, x to exit): ")

        if i == '1':
            command_1(db)
            continue
        elif i == '2':
            pass
        elif i == '3':
            pass
        elif i == '4':
            pass
        elif i == '5':
            pass
        elif i == '6':
            pass
        elif i == '7':
            pass
        elif i == '8':
            pass
        elif i == '9':
            pass
        elif i == 'x':
            break

        print("**Error, unknown command, try again...\n")

if __name__ == '__main__':
    main()
