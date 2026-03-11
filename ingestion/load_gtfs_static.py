import os
import pandas as pd
import snowflake.connector
from dotenv import load_dotenv
from snowflake.connector.pandas_tools import write_pandas

# Load environment variables
load_dotenv()

# Snowflake connection
conn = snowflake.connector.connect(
    user=os.getenv("SNOWFLAKE_USER"),
    password=os.getenv("SNOWFLAKE_PASSWORD"),
    account=os.getenv("SNOWFLAKE_ACCOUNT"),
    warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
    database=os.getenv("SNOWFLAKE_DATABASE"),
    schema=os.getenv("SNOWFLAKE_SCHEMA")
)

# Path to your GTFS static CSV files
GTFS_PATH = "../gtfs_ttc/"  # e.g., "./gtfs_ttc/"

# ----------------------
# 1. Load routes.txt
# ----------------------
routes_file = os.path.join(GTFS_PATH, "routes.txt")
routes_df = pd.read_csv(routes_file)

# Keep only important columns
routes_df = routes_df[[
    "route_id",
    "agency_id",
    "route_short_name",
    "route_long_name",
    "route_type"
]]
# Uppercase all columns
routes_df.columns = [c.upper() for c in routes_df.columns]

# Load into Snowflake
write_pandas(conn, routes_df, "ROUTES")
print("✅ ROUTES table loaded successfully!")

# ----------------------
# 2. Load stops.txt
# ----------------------
stops_file = os.path.join(GTFS_PATH, "stops.txt")
stops_df = pd.read_csv(stops_file)

# Keep only important columns
stops_df = stops_df[[
    "stop_id",
    "stop_name",
    "stop_lat",
    "stop_lon"
]]
stops_df.columns = [c.upper() for c in stops_df.columns]
# Load into Snowflake
write_pandas(conn, stops_df, "STOPS")
print("✅ STOPS table loaded successfully!")


# ----------------------
# 3. Load trips.txt
# ----------------------

trips_file = os.path.join(GTFS_PATH, "trips.txt")
# trips_df = pd.read_csv(trips_file) (giving dtype error due to nan and pyarrow fails to convert it to float)
trips_df = pd.read_csv(trips_file, dtype=str, low_memory=False)

trips_df.columns = [c.upper() for c in trips_df.columns]

write_pandas(conn, trips_df, "TRIPS")
print("✅ TRIPS table loaded successfully!")

# ----------------------
# 4. Load stop_times.txt
# ----------------------

stop_times_file = os.path.join(GTFS_PATH, "stop_times.txt")
# stop_times_df = pd.read_csv(stop_times_file)
stop_times_df = pd.read_csv(stop_times_file, dtype=str, low_memory=False)

stop_times_df.columns = [c.upper() for c in stop_times_df.columns]

write_pandas(conn, stop_times_df, "STOP_TIMES")
print("✅ STOP_TIMES table loaded successfully!")

# ----------------------
# 5. Load calendar.txt
# ----------------------

calendar_file = os.path.join(GTFS_PATH, "calendar.txt")
# calendar_df = pd.read_csv(calendar_file)
calendar_df = pd.read_csv(calendar_file, dtype=str, low_memory=False)

calendar_df.columns = [c.upper() for c in calendar_df.columns]

write_pandas(conn, calendar_df, "CALENDAR")
print("✅ CALENDAR table loaded successfully!")

# Close connection
conn.close()