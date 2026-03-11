import os
import snowflake.connector
from dotenv import load_dotenv

load_dotenv()

try:
    conn = snowflake.connector.connect(
        user=os.getenv("SNOWFLAKE_USER"),
        password=os.getenv("SNOWFLAKE_PASSWORD"),
        account=os.getenv("SNOWFLAKE_ACCOUNT"),
        warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
        database=os.getenv("SNOWFLAKE_DATABASE"),
        schema=os.getenv("SNOWFLAKE_SCHEMA")
    )

    print("✅ Connected to Snowflake successfully!")

    cur = conn.cursor()
    cur.execute("SELECT CURRENT_VERSION();")
    version = cur.fetchone()
    print("Snowflake version:", version[0])

    cur.close()
    conn.close()

except Exception as e:
    print("❌ Connection failed:")
    print(e)