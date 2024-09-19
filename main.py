#!/usr/bin/env python
import matplotlib.pyplot as plt
import sqlite3

def command_1(db: sqlite3.Connection):
    """
    Matches a partial station name
    @param db database
    """
    search = input("\n\nEnter partial station name (wildcards _ and %): ")
    matches = execute(db, f"""
        SELECT * FROM Stations
        WHERE Station_Name LIKE "{search}"
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
    search = input("\n\nEnter the name of the station you would like to analyze: ")
    match = execute(db, f"""
        SELECT Station_ID FROM Stations WHERE Station_Name = "{search}"
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

    print("Ridership on Weekdays for Each Station")
    for r in results:
        print(f"{r[0]} : {r[1]:,} ({r[1]/total:.2%})")

def command_4(db: sqlite3.Connection):
    """
    Print all stops for line in direction
    @param db database
    """
    color = input("\nEnter a line color (e.g. Red or Yellow): ")
    line = execute(db, f"""
        SELECT Line_ID FROM Lines
        Where Color = "{color}"
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

def command_6(db: sqlite3.Connection):
    """
    Matches a partial station name and outputs yearly total ridership
    @param db database
    """
    search = input("Enter a station name (wildcards _ and %): ")
    matches = execute(db, f"""
        SELECT * FROM Stations
        WHERE Station_Name LIKE "{search}"
        ORDER BY Station_Name ASC
    """)

    if not matches:
        print("**No stations found...")
        return

    if len(matches) > 1:
        print("**Multiple stations found...")
        return

    station_id, station_name = matches[0]
    
    ridership = execute(db, f"""
        SELECT CAST(Ride_Date AS DATE), SUM(Num_Riders) FROM Ridership
        WHERE Station_ID = {station_id}
        GROUP BY CAST(Ride_Date AS DATE)
        ORDER BY CAST(Ride_Date AS DATE)
    """)

    print(f"Yearly Ridership at {station_name}")
    for r in ridership:
        print(f"{r[0]} : {r[1]:,}")

    if input("\n\nPlot? (y/n) ") == "y":
        # generate plot
        plt.title(f"Yearly Ridership at {station_name} Station")
        plt.xlabel("Year")
        plt.ylabel("Number of Riders")

        # unpair points
        x, y = zip(*ridership)
        plt.xticks(x, rotation=90)
        plt.plot(x, y)
        plt.savefig("command_6.png")

def command_7(db: sqlite3.Connection):
    """
    Matches a partial station name and outputs monthly ridership for a year
    @param db database
    """
    search = input("Enter a station name (wildcards _ and %): ")
    matches = execute(db, f"""
        SELECT * FROM Stations
        WHERE Station_Name LIKE "{search}"
        ORDER BY Station_Name ASC
    """)

    if not matches:
        print("**No stations found...")
        return

    if len(matches) > 1:
        print("**Multiple stations found...")
        return

    year = input("\n\nEnter a year: ")

    station_id, station_name = matches[0]
    
    ridership = execute(db, f"""
        SELECT CAST(strftime('%m', Ride_Date) AS INT) AS Month, SUM(Num_Riders) FROM Ridership
        WHERE Station_ID = {station_id} AND CAST(Ride_Date AS DATE) = {year}
        GROUP BY Month
        ORDER BY Month
    """)

    print(f"Monthly Ridership at {station_name} for {year}")
    for r in ridership:
        print(f"{r[0]}/{year} : {r[1]:,}")

    if input("\n\nPlot? (y/n) ") == "y":
        # generate plot
        plt.title(f"Monthly Ridership at {station_name} Station ({year})")
        plt.xlabel("Month")
        plt.ylabel("Number of Riders")

        # unpair points
        x, y = zip(*ridership)
        plt.xticks(x)
        plt.plot(x, y)
        plt.savefig("command_7.png")

def command_8(db: sqlite3.Connection):
    """
    Compares the ridership of two stations within a year
    @param db database
    """
    year = input("\n\nYear to compare against? ")

    search = input("Enter station 1 (wildcards _ and %): ")
    matches = execute(db, f"""
        SELECT * FROM Stations
        WHERE Station_Name LIKE "{search}"
        ORDER BY Station_Name ASC
    """)

    if not matches:
        print("**No stations found...")
        return

    if len(matches) > 1:
        print("**Multiple stations found...")
        return

    station_1_id, station_1_name = matches[0]

    search = input("Enter station 2 (wildcards _ and %): ")
    matches = execute(db, f"""
        SELECT * FROM Stations
        WHERE Station_Name LIKE "{search}"
        ORDER BY Station_Name ASC
    """)

    if not matches:
        print("**No stations found...")
        return

    if len(matches) > 1:
        print("**Multiple stations found...")
        return

    station_2_id, station_2_name = matches[0]
    
    ridership_1 = execute(db, f"""
        SELECT DATE(Ride_Date), CAST(strftime('%j', Ride_Date) AS INT), SUM(Num_Riders) FROM Ridership
        WHERE Station_ID = {station_1_id} AND CAST(Ride_Date AS DATE) = {year}
        GROUP BY DATE(Ride_Date)
        ORDER BY DATE(Ride_Date)
    """)

    ridership_2 = execute(db, f"""
        SELECT DATE(Ride_Date), CAST(strftime('%j', Ride_Date) AS INT), SUM(Num_Riders) FROM Ridership
        WHERE Station_ID = {station_2_id} AND CAST(Ride_Date AS DATE) = {year}
        GROUP BY DATE(Ride_Date)
        ORDER BY DATE(Ride_Date)
    """)

    print(f"Station 1: {station_1_id} {station_1_name}")
    for r in ridership_1[:5]: # first 5
        print(f"{r[0]} {r[2]}")
    for r in ridership_1[-5:]: # last 5
        print(f"{r[0]} {r[2]}")

    print(f"Station 2: {station_2_id} {station_2_name}")
    for r in ridership_2[:5]: # first 5
        print(f"{r[0]} {r[2]}")
    for r in ridership_2[-5:]: # last 5
        print(f"{r[0]} {r[2]}")

    if input("\n\nPlot? (y/n) ") == "y":
        # generate plot
        plt.title(f"Ridership Each Day of {year}")
        plt.xlabel("Day")
        plt.ylabel("Number of Riders")
        plt.xticks(range(0, 400, 50))

        # station 1
        # the first tuple value is ignored as that is the full date
        _, x, y = zip(*ridership_1)
        plt.plot(x, y, label=station_1_name)

        # station 2
        _, x, y = zip(*ridership_2)
        plt.plot(x, y, label=station_2_name)

        plt.legend()
        plt.savefig("command_8.png")

def command_9(db: sqlite3.Connection):
    """
    Given a set of lat/long, find all stations within a square mile
    @param db database
    """
    lat = float(input("Enter a latitude: "))
    long = float(input("Enter a longitude: "))

    if lat < 40 or lat > 43:
        print("**Latitude entered is out of bounds...")
        return

    if long < -88 or long > -87:
        print("**Longitude entered is out of bounds...")
        return

    # each lat is 69 miles apart
    # each long is 51 miles apart
    min_lat = round(lat-(1/69), 3)
    max_lat = round(lat+(1/69), 3)

    min_long = round(long-(1/51), 3)
    max_long = round(long+(1/51), 3)

    # run query
    stations = execute(db, f"""
        SELECT Station_Name, Latitude, Longitude FROM Stops
        JOIN Stations ON Stops.Station_ID = Stations.Station_ID
        WHERE Latitude BETWEEN {min_lat} AND {max_lat}
        AND Longitude BETWEEN {min_long} AND {max_long}
        GROUP BY Stations.Station_ID
        ORDER BY Station_Name
    """)

    print("List of Stations Within a Mile")
    for name, x, y in stations:
        print(f"{name} : ({x}, {y})")

    # create plot
    if input("\n\nPlot? (y/n) ") == "y":
        image = plt.imread("chicago.png")
        xydims = [-87.9277, -87.5569, 41.7012, 42.0868] # area covered by map
        plt.imshow(image, extent=xydims)
        plt.title("Stations Near You")
        plt.xlim(xydims[:2])
        plt.ylim(xydims[-2:])
    
        # plot points
        _, x_list, y_list = zip(*stations)
        plt.plot(x_list, y_list)

        # plot names
        for name, x, y in stations:
            plt.annotate(name, (x, y))

        plt.savefig("command_9.png")

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
    print(f"  # of ride entries: {rides:,}")
    print(f"  date range: {date_range[0]} - {date_range[1]}")
    print(f"  Total ridership: {total_ridership:,}")

def main():
    # open db connection
    db = sqlite3.connect("CTA2_L_daily_ridership.db")

    print("** Welcome to CTA L analysis app **\n")
    print_stats(db)

    # main eval loop
    while True:
        i = input("\nPlease enter a command (1-9, x to exit): ")

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
            command_6(db)
            continue
        elif i == '7':
            command_7(db)
            continue
        elif i == '8':
            command_8(db)
            continue
        elif i == '9':
            command_9(db)
            continue
        elif i == 'x':
            break

        print("**Error, unknown command, try again...\n")

if __name__ == '__main__':
    main()
