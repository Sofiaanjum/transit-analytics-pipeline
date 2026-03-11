import streamlit as st
import snowflake.connector
import pandas as pd

conn = snowflake.connector.connect(
    user="SOFIA15",
    password="We1c0me@27971501",
    account="OJCRHPF-LJ52395",
    warehouse="SNOWFLAKE_LEARNING_WH",
    database="TRANSIT_DB",
    schema="RAW"
)

query = """
SELECT *
FROM ROUTE_SUMMARY
LIMIT 100
"""

df = pd.read_sql(query, conn)

st.title("Transit Routes Dashboard")

st.dataframe(df)
