import os
import pandas as pd
import snowflake.connector
from dotenv import load_dotenv
from snowflake.connector.pandas_tools import write_pandas

load_dotenv()

conn = snowflake.connector.connect(
    user=os.getenv("SNOWFLAKE_USER"),
    password=os.getenv("SNOWFLAKE_PASSWORD"),
    account=os.getenv("SNOWFLAKE_ACCOUNT"),
    warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
    database=os.getenv("SNOWFLAKE_DATABASE"),
    schema=os.getenv("SNOWFLAKE_SCHEMA")
)

GTFS_PATH = "../gtfs_ttc"

print("Connected to Snowflake")

# ROUTES
routes = pd.read_csv(f"{GTFS_PATH}/routes.txt")
routes = routes[[
    "route_id",
    "agency_id",
    "route_short_name",
    "route_long_name",
    "route_type"
]]
routes.columns = routes.columns.str.upper()

write_pandas(conn, routes, "ROUTES")
print("ROUTES loaded")


# STOPS
stops = pd.read_csv(f"{GTFS_PATH}/stops.txt")
stops = stops[["stop_id", "stop_name", "stop_lat", "stop_lon"]]
stops.columns = stops.columns.str.upper()

write_pandas(conn, stops, "STOPS")
print("STOPS loaded")


# TRIPS
trips = pd.read_csv(f"{GTFS_PATH}/trips.txt", dtype=str)
trips = trips[[
    "route_id",
    "service_id",
    "trip_id",
    "trip_headsign",
    "direction_id",
    "block_id",
    "shape_id"
]]
trips.columns = trips.columns.str.upper()

write_pandas(conn, trips, "TRIPS")
print("TRIPS loaded")


# STOP_TIMES
stop_times = pd.read_csv(f"{GTFS_PATH}/stop_times.txt", dtype=str)
stop_times = stop_times[[
    "trip_id",
    "arrival_time",
    "departure_time",
    "stop_id",
    "stop_sequence"
]]
stop_times.columns = stop_times.columns.str.upper()

write_pandas(conn, stop_times, "STOP_TIMES")
print("STOP_TIMES loaded")


# CALENDAR
calendar = pd.read_csv(f"{GTFS_PATH}/calendar.txt", dtype=str)
calendar.columns = calendar.columns.str.upper()

write_pandas(conn, calendar, "CALENDAR")
print("CALENDAR loaded")


# AGENCY
agency = pd.read_csv(f"{GTFS_PATH}/agency.txt", dtype=str)
agency = agency[[
    "agency_id",
    "agency_name",
    "agency_url",
    "agency_timezone"
]]
agency.columns = agency.columns.str.upper()

write_pandas(conn, agency, "AGENCY")
print("AGENCY loaded")


# CALENDAR_DATES
calendar_dates = pd.read_csv(f"{GTFS_PATH}/calendar_dates.txt", dtype=str)
calendar_dates.columns = calendar_dates.columns.str.upper()

write_pandas(conn, calendar_dates, "CALENDAR_DATES")
print("CALENDAR_DATES loaded")


# SHAPES
shapes = pd.read_csv(f"{GTFS_PATH}/shapes.txt", dtype=str)
shapes = shapes[[
    "shape_id",
    "shape_pt_lat",
    "shape_pt_lon",
    "shape_pt_sequence"
]]
shapes.columns = shapes.columns.str.upper()

write_pandas(conn, shapes, "SHAPES")
print("SHAPES loaded")


conn.close()
print("Finished loading GTFS data")