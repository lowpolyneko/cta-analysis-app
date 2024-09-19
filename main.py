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

def command_2(db: sqlite3.Connection):
    """
    Prints weekly ridership of a station
    @param db database
    """
    search = input("Enter the name of the station you would like to analyze: ")
    match = execute(db, f"""
        SELECT Station_ID FROM Stations WHERE Station_Name = '{search}'
    """)

    if not match:
        print("**No data found...")
        return

    # run weekly, saturday, sunday ridership queries
    station_id = match[0][0]

    weekday = execute(db, f"""
        SELECT SUM(Num_Riders) FROM Ridership
        WHERE Station_ID = {station_id}
        AND Type_of_Day = 'W'
    """)[0][0]
    saturday = execute(db, f"""
        SELECT SUM(Num_Riders) FROM Ridership
        WHERE Station_ID = {station_id}
        AND Type_of_Day = 'A'
    """)[0][0]
    sunday = execute(db, f"""
        SELECT SUM(Num_Riders) FROM Ridership
        WHERE Station_ID = {station_id}
        AND Type_of_Day = 'U'
    """)[0][0]

    total = weekday + saturday + sunday

    print(f"Percentage of ridership for the {search} station:")
    print(f"  Weekday ridership: {weekday:,} ({weekday/total:.2%})")
    print(f"  Saturday ridership: {saturday:,} ({saturday/total:.2%})")
    print(f"  Sunday/holiday ridership: {sunday:,} ({sunday/total:.2%})")
    print(f"  Total ridership: {total:,}")

def command_3(db: sqlite3.Connection):
    """
    Prints weekday ridership for all stations
    @param db database
    """
    results = execute(db, """
        SELECT Station_Name, SUM(Num_Riders) FROM Ridership
        JOIN Stations ON Ridership.Station_ID = Stations.Station_ID
        WHERE Ridership.Type_of_day = 'W'
        GROUP BY Ridership.Station_ID
        ORDER BY SUM(Num_Riders) DESC
        """)

    total = sum(n for _, n in results)

    print("Ridership for Weekdays for Each Station")
    for r in results:
        print(f"{r[0]} : {r[1]:,} ({r[1]/total:.2%})")

def command_4(db: sqlite3.Connection):
    """
    Print all stops for line in direction
    @param db database
    """
    color = input("Enter a line color (e.g. Red or Yellow): ")
    line = execute(db, f"""
        SELECT Line_ID FROM Lines
        Where Color = '{color}'
    """)

    if not line:
        print("**No such line...")
        return

    direction = input("Enter a direction (N/S/W/E): ")

    line_id = line[0][0]
    stops = execute(db, f"""
        SELECT Stop_Name, ADA FROM Stops
        JOIN StopDetails ON Stops.Stop_ID = StopDetails.Stop_ID
        WHERE Line_ID = '{line_id}' AND Direction = '{direction}'
        ORDER BY Stop_Name
    """)

    if not stops:
        print("That line does not run in the direction chosen...")
        return

    for s in stops:
        print(f"{s[0]} : direction = {direction} {'(handicap accessible)' if s[1] else ''}")

def command_5(db: sqlite3.Connection):
    """
    Number of stops for each line color grouped by direction
    @param db database
    """
    results = execute(db, """
        SELECT Color, Direction, COUNT(Direction) FROM Stops
        JOIN StopDetails ON Stops.Stop_ID = StopDetails.Stop_ID
        JOIN Lines ON StopDetails.Line_ID = Lines.Line_ID
        GROUP BY Color, Direction
        ORDER BY Color, Direction
    """)

    total = execute(db, """
        SELECT COUNT(Stops.Stop_ID) FROM Stops
    """)[0][0]

    print("Number of Stops For Each Color By Direction")
    for r in results:
        print(f"{r[0]} going {r[1]} : {r[2]} ({r[2]/total:.2%})")

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
            command_2(db)
            continue
        elif i == '3':
            command_3(db)
            continue
        elif i == '4':
            command_4(db)
            continue
        elif i == '5':
            command_5(db)
            continue
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
