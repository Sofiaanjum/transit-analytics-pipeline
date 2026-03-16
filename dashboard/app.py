import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import snowflake.connector
import os
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="TTC Transit Analytics",
    page_icon="🚇",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
[data-testid="stMetricValue"] { font-size: 2rem; font-weight: 700; }
[data-testid="stMetricLabel"] { font-size: 0.85rem; color: #555; }
.block-container { padding-top: 1.5rem; }
h1 { color: #1F4E79; }
h2 { color: #2E75B6; font-size: 1.1rem; }
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def get_connection():
    return snowflake.connector.connect(
        account=os.getenv("SNOWFLAKE_ACCOUNT"),
        user=os.getenv("SNOWFLAKE_USER"),
        password=os.getenv("SNOWFLAKE_PASSWORD"),
        warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
        database=os.getenv("SNOWFLAKE_DATABASE"),
        schema=os.getenv("SNOWFLAKE_SCHEMA")
    )

@st.cache_data
def run_query(query):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(query)
    columns = [col[0] for col in cursor.description]
    data = cursor.fetchall()
    return pd.DataFrame(data, columns=columns)

BLUE       = "#1F4E79"
MED_BLUE   = "#2E75B6"
LIGHT_BLUE = "#BDD7EE"
ORANGE     = "#F2994A"
TEAL       = "#1D9E75"

with st.sidebar:
    st.markdown("## 🚇 TTC Analytics")
    st.markdown("**Built by Sofia Ahmed**")
    st.markdown("*DE · Snowflake · dbt · Python*")
    st.divider()
    page = st.selectbox(
        "Navigate",
        [
            "Executive Summary",
            "Route Performance",
            "Stop Activity",
            "Service Frequency",
            "Trip Patterns"
        ]
    )
    st.divider()
    st.markdown("**Stack**")
    st.markdown("🔷 Snowflake · dbt · Python")
    st.markdown("📊 TTC GTFS Static Feed")
    st.markdown("🔗 [LinkedIn](https://www.linkedin.com/in/sofiaanjum)")
    st.markdown("🌐 [Portfolio](https://sofiaanjum.github.io/webportfolio/)")

# ════════════════════════════
# PAGE 1 — EXECUTIVE SUMMARY
# ════════════════════════════
if page == "Executive Summary":
    st.title("🚇 TTC Network — Executive Summary")
    st.markdown("*How is the TTC network performing overall?*")
    st.divider()

    network = run_query("SELECT * FROM mart_network_overview")
    total_routes      = int(network["TOTAL_ROUTES"].sum())
    total_trips       = int(network["TOTAL_TRIPS"].sum())
    unique_stops      = int(network["UNIQUE_STOPS"].sum())
    total_stop_events = int(network["TOTAL_STOP_EVENTS"].sum())
    avg_stops         = round(total_stop_events / total_trips, 1)

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Total Routes",      f"{total_routes:,}")
    c2.metric("Total Trips",       f"{total_trips:,}")
    c3.metric("Unique Stops",      f"{unique_stops:,}")
    c4.metric("Stop Events",       f"{total_stop_events:,}")
    c5.metric("Avg Stops/Trip",    f"{avg_stops}")
    st.divider()

    col_l, col_r = st.columns([1, 2])
    with col_l:
        st.subheader("Network Composition")
        fig = px.pie(
            network, names="ROUTE_TYPE", values="TOTAL_ROUTES",
            hole=0.5, color_discrete_sequence=[BLUE, MED_BLUE, TEAL]
        )
        fig.update_layout(height=320, margin=dict(t=20, b=20))
        fig.update_traces(textinfo="percent+label")
        st.plotly_chart(fig, use_container_width=True)

    with col_r:
        st.subheader("Route Type Performance Breakdown")
        fig2 = go.Figure()
        fig2.add_trace(go.Bar(
            name="Total Trips", x=network["ROUTE_TYPE"],
            y=network["TOTAL_TRIPS"], marker_color=BLUE
        ))
        fig2.add_trace(go.Bar(
            name="Unique Stops", x=network["ROUTE_TYPE"],
            y=network["UNIQUE_STOPS"], marker_color=TEAL
        ))
        fig2.update_layout(
            barmode="group", height=320,
            margin=dict(t=20, b=20),
            legend=dict(orientation="h", y=1.1)
        )
        st.plotly_chart(fig2, use_container_width=True)

    st.divider()
    st.subheader("Network Summary Table")
    display = network.copy()
    display.columns = [
        "Route Type", "Total Routes", "Total Trips", "Unique Stops",
        "Stop Events", "% Network Trips", "% Network Stops", "Avg Stops/Trip"
    ]
    st.dataframe(
        display.style
        .background_gradient(subset=["Total Trips"], cmap="Blues")
        .format({
            "Total Routes": "{:,}", "Total Trips": "{:,}",
            "Unique Stops": "{:,}", "Stop Events": "{:,}",
            "% Network Trips": "{:.1f}%", "% Network Stops": "{:.1f}%",
            "Avg Stops/Trip": "{:.1f}"
        }),
        use_container_width=True, hide_index=True
    )
    st.caption("TTC GTFS Static Feed · Python · Snowflake · dbt · Sofia Ahmed")


# ════════════════════════════
# PAGE 2 — ROUTE PERFORMANCE
# ════════════════════════════
elif page == "Route Performance":
    st.title("📊 Route Performance Intelligence")
    st.markdown("*Which routes are carrying the most load?*")
    st.divider()

    routes = run_query("SELECT * FROM mart_route_performance ORDER BY total_trips DESC")
    color_map = {"Bus": BLUE, "Subway": ORANGE, "Streetcar": TEAL}

    c1, c2 = st.columns(2)
    type_filter = c1.multiselect(
        "Filter by Route Type",
        options=routes["ROUTE_TYPE"].unique().tolist(),
        default=routes["ROUTE_TYPE"].unique().tolist()
    )
    top_n = c2.slider("Show Top N Routes", 5, 50, 15)
    filtered = routes[routes["ROUTE_TYPE"].isin(type_filter)].head(top_n)
    st.divider()

    col_l, col_r = st.columns([3, 2])
    with col_l:
        st.subheader(f"Top {top_n} Routes by Total Trips")
        fig = px.bar(
            filtered, x="TOTAL_TRIPS", y="ROUTE_SHORT_NAME",
            color="ROUTE_TYPE", orientation="h",
            color_discrete_map=color_map,
            hover_data=["ROUTE_LONG_NAME", "UNIQUE_STOPS", "AVG_STOPS_PER_TRIP"],
            labels={"TOTAL_TRIPS": "Total Trips", "ROUTE_SHORT_NAME": "Route"}
        )
        fig.update_layout(
            height=500, yaxis=dict(autorange="reversed"),
            legend=dict(orientation="h", y=1.05)
        )
        st.plotly_chart(fig, use_container_width=True)

    with col_r:
        st.subheader("Route Scorecard")
        scorecard = filtered[[
            "ROUTE_SHORT_NAME", "ROUTE_TYPE",
            "TOTAL_TRIPS", "UNIQUE_STOPS", "AVG_STOPS_PER_TRIP"
        ]].copy()
        scorecard["PERFORMANCE"] = pd.cut(
            scorecard["TOTAL_TRIPS"], bins=3,
            labels=["Needs Review", "Average", "High Performer"]
        )
        scorecard.columns = ["Route", "Type", "Trips", "Stops", "Avg Stops", "Performance"]

        def color_perf(val):
            if val == "High Performer":  return "background-color: #C6EFCE; color: #276221"
            elif val == "Average":       return "background-color: #FFEB9C; color: #9C6500"
            else:                        return "background-color: #FFC7CE; color: #9C0006"

        st.dataframe(
            scorecard.style
            .applymap(color_perf, subset=["Performance"])
            .format({"Trips": "{:,}", "Stops": "{:,}", "Avg Stops": "{:.1f}"}),
            use_container_width=True, hide_index=True, height=500
        )

    st.divider()
    st.subheader("Route Complexity — Avg Stops vs Total Trips")
    fig2 = px.scatter(
        routes.head(50), x="AVG_STOPS_PER_TRIP", y="TOTAL_TRIPS",
        color="ROUTE_TYPE", size="UNIQUE_STOPS",
        hover_data=["ROUTE_SHORT_NAME", "ROUTE_LONG_NAME"],
        color_discrete_map=color_map,
        labels={"AVG_STOPS_PER_TRIP": "Avg Stops per Trip", "TOTAL_TRIPS": "Total Trips"}
    )
    fig2.update_layout(height=380)
    st.plotly_chart(fig2, use_container_width=True)
    st.caption("TTC GTFS Static Feed · Python · Snowflake · dbt · Sofia Ahmed")


# ════════════════════════════
# PAGE 3 — STOP ACTIVITY
# ════════════════════════════
elif page == "Stop Activity":
    st.title("📍 Stop and Ridership Intelligence")
    st.markdown("*Where are the highest demand stops?*")
    st.divider()

    stops = run_query("SELECT * FROM mart_stop_activity ORDER BY total_visits DESC")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Stops",    f"{len(stops):,}")
    c2.metric("Major Hubs",     f"{len(stops[stops['STOP_CLASSIFICATION']=='Major Hub']):,}")
    c3.metric("High Activity",  f"{len(stops[stops['STOP_CLASSIFICATION']=='High Activity']):,}")
    c4.metric("Avg Routes/Stop",f"{stops['ROUTES_SERVED'].mean():.1f}")
    st.divider()

    class_filter = st.multiselect(
        "Filter by Classification",
        options=stops["STOP_CLASSIFICATION"].unique().tolist(),
        default=stops["STOP_CLASSIFICATION"].unique().tolist()
    )
    filtered_stops = stops[stops["STOP_CLASSIFICATION"].isin(class_filter)]

    col_l, col_r = st.columns([2, 3])
    with col_l:
        st.subheader("Top 15 Busiest Stops")
        fig = px.bar(
            filtered_stops.head(15), x="TOTAL_VISITS", y="STOP_NAME",
            color="STOP_CLASSIFICATION", orientation="h",
            color_discrete_map={
                "Major Hub": BLUE, "High Activity": MED_BLUE,
                "Moderate": LIGHT_BLUE, "Low Activity": "#E0E0E0"
            },
            labels={"TOTAL_VISITS": "Total Visits", "STOP_NAME": "Stop"}
        )
        fig.update_layout(
            height=500, yaxis=dict(autorange="reversed"),
            legend=dict(orientation="h", y=1.05)
        )
        st.plotly_chart(fig, use_container_width=True)

    with col_r:
        st.subheader("Stop Location Map — Toronto")
        map_data = filtered_stops.dropna(subset=["STOP_LAT", "STOP_LON"])
        map_data = map_data[
            (map_data["STOP_LAT"].between(43.5, 43.9)) &
            (map_data["STOP_LON"].between(-79.7, -79.1))
        ]
        fig2 = px.scatter_mapbox(
            map_data, lat="STOP_LAT", lon="STOP_LON",
            color="STOP_CLASSIFICATION", size="TOTAL_VISITS",
            hover_name="STOP_NAME",
            hover_data=["ROUTES_SERVED", "TOTAL_VISITS"],
            color_discrete_map={
                "Major Hub": BLUE, "High Activity": MED_BLUE,
                "Moderate": TEAL, "Low Activity": "#AAAAAA"
            },
            zoom=10, mapbox_style="carto-positron", size_max=20
        )
        fig2.update_layout(height=500, margin=dict(t=0, b=0))
        st.plotly_chart(fig2, use_container_width=True)

    st.divider()
    st.subheader("Stop Classification Breakdown")
    class_summary = stops.groupby("STOP_CLASSIFICATION").agg(
        Total_Stops=("STOP_ID", "count"),
        Avg_Visits=("TOTAL_VISITS", "mean"),
        Avg_Routes=("ROUTES_SERVED", "mean")
    ).reset_index()
    class_summary.columns = ["Classification", "Total Stops", "Avg Visits", "Avg Routes Served"]
    st.dataframe(
        class_summary.style
        .background_gradient(subset=["Avg Visits"], cmap="Blues")
        .format({"Total Stops": "{:,}", "Avg Visits": "{:,.0f}", "Avg Routes Served": "{:.1f}"}),
        use_container_width=True, hide_index=True
    )
    st.caption("TTC GTFS Static Feed · Python · Snowflake · dbt · Sofia Ahmed")


# ════════════════════════════
# PAGE 4 — SERVICE FREQUENCY
# ════════════════════════════
elif page == "Service Frequency":
    st.title("⏰ Service Frequency Analysis")
    st.markdown("*Is TTC providing adequate service during peak hours?*")
    st.divider()

    freq = run_query("SELECT * FROM mart_service_frequency ORDER BY hour_of_day")

    peak    = int(freq[freq["SERVICE_PERIOD"].isin(["Morning Peak","Evening Peak"])]["TOTAL_TRIPS"].sum())
    offpeak = int(freq[freq["SERVICE_PERIOD"] == "Off Peak"]["TOTAL_TRIPS"].sum())
    regular = int(freq[freq["SERVICE_PERIOD"] == "Regular Service"]["TOTAL_TRIPS"].sum())
    busiest = int(freq.loc[freq["TOTAL_TRIPS"].idxmax(), "HOUR_OF_DAY"])

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Peak Hour Trips",  f"{peak:,}")
    c2.metric("Off Peak Trips",   f"{offpeak:,}")
    c3.metric("Regular Trips",    f"{regular:,}")
    c4.metric("Busiest Hour",     f"{busiest:02d}:00")
    st.divider()

    col_l, col_r = st.columns([3, 2])
    with col_l:
        st.subheader("Service Frequency by Hour of Day")
        fig = px.area(
            freq, x="HOUR_OF_DAY", y="TOTAL_TRIPS",
            color="SERVICE_PERIOD",
            color_discrete_map={
                "Morning Peak": ORANGE, "Evening Peak": ORANGE,
                "Off Peak": "#AAAAAA", "Regular Service": BLUE
            },
            labels={"HOUR_OF_DAY": "Hour of Day", "TOTAL_TRIPS": "Total Trips"}
        )
        fig.update_layout(
            height=380,
            xaxis=dict(tickmode="linear", tick0=0, dtick=1),
            legend=dict(orientation="h", y=1.05)
        )
        st.plotly_chart(fig, use_container_width=True)

    with col_r:
        st.subheader("Service Period Summary")
        period_summary = freq.groupby("SERVICE_PERIOD").agg(
            Hours=("HOUR_OF_DAY", "count"),
            Total_Trips=("TOTAL_TRIPS", "sum"),
            Pct_Daily=("PCT_OF_DAILY_TRIPS", "sum")
        ).reset_index()
        fig2 = px.pie(
            period_summary, names="SERVICE_PERIOD", values="Total_Trips",
            hole=0.4, color_discrete_sequence=[ORANGE, BLUE, TEAL, "#AAAAAA"]
        )
        fig2.update_layout(height=380)
        st.plotly_chart(fig2, use_container_width=True)

    st.divider()
    st.subheader("Hourly Service Detail")
    display_freq = freq[[
        "HOUR_OF_DAY", "SERVICE_PERIOD", "TOTAL_TRIPS",
        "UNIQUE_TRIPS", "STOPS_SERVED", "PCT_OF_DAILY_TRIPS"
    ]].copy()
    display_freq["HOUR_OF_DAY"] = display_freq["HOUR_OF_DAY"].apply(lambda x: f"{int(x):02d}:00")
    display_freq.columns = ["Hour", "Service Period", "Total Trips", "Unique Trips", "Stops Served", "% of Daily"]
    st.dataframe(
        display_freq.style
        .background_gradient(subset=["Total Trips"], cmap="Blues")
        .format({"Total Trips": "{:,}", "Unique Trips": "{:,}", "Stops Served": "{:,}", "% of Daily": "{:.2f}%"}),
        use_container_width=True, hide_index=True
    )
    st.caption("TTC GTFS Static Feed · Python · Snowflake · dbt · Sofia Ahmed")


# ════════════════════════════
# PAGE 5 — TRIP PATTERNS
# ════════════════════════════
elif page == "Trip Patterns":
    st.title("🔄 Trip Patterns and Network Coverage")
    st.markdown("*How well does TTC cover the network?*")
    st.divider()

    patterns = run_query("SELECT * FROM mart_trip_patterns ORDER BY total_trips DESC")

    total_trips    = int(patterns["TOTAL_TRIPS"].sum())
    avg_stops      = round(patterns["AVG_STOPS_PER_TRIP"].mean(), 1)
    inbound_trips  = int(patterns[patterns["DIRECTION"]=="Inbound"]["TOTAL_TRIPS"].sum())
    outbound_trips = int(patterns[patterns["DIRECTION"]=="Outbound"]["TOTAL_TRIPS"].sum())

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Trips",        f"{total_trips:,}")
    c2.metric("Avg Stops/Trip",     f"{avg_stops}")
    c3.metric("Inbound Trips",      f"{inbound_trips:,}")
    c4.metric("Outbound Trips",     f"{outbound_trips:,}")
    st.divider()

    color_map = {"Bus": BLUE, "Subway": ORANGE, "Streetcar": TEAL}
    col_l, col_r = st.columns(2)

    with col_l:
        st.subheader("Inbound vs Outbound by Route Type")
        dir_summary = patterns.groupby(["ROUTE_TYPE","DIRECTION"])["TOTAL_TRIPS"].sum().reset_index()
        fig = px.bar(
            dir_summary, x="ROUTE_TYPE", y="TOTAL_TRIPS",
            color="DIRECTION", barmode="group",
            color_discrete_sequence=[BLUE, TEAL],
            labels={"ROUTE_TYPE": "Route Type", "TOTAL_TRIPS": "Total Trips"}
        )
        fig.update_layout(height=380, legend=dict(orientation="h", y=1.05))
        st.plotly_chart(fig, use_container_width=True)

    with col_r:
        st.subheader("Route Complexity Scatter")
        fig2 = px.scatter(
            patterns.head(30), x="AVG_STOPS_PER_TRIP", y="TOTAL_TRIPS",
            color="ROUTE_TYPE", size="MAX_STOPS",
            hover_data=["ROUTE_SHORT_NAME", "DIRECTION"],
            color_discrete_map=color_map,
            labels={"AVG_STOPS_PER_TRIP": "Avg Stops/Trip", "TOTAL_TRIPS": "Total Trips"}
        )
        fig2.update_layout(height=380, legend=dict(orientation="h", y=1.05))
        st.plotly_chart(fig2, use_container_width=True)

    st.divider()
    st.subheader("Top 20 Routes — Trip Comparison")
    top20 = patterns.groupby("ROUTE_SHORT_NAME")["TOTAL_TRIPS"].sum().reset_index()
    top20 = top20.sort_values("TOTAL_TRIPS", ascending=False).head(20)
    fig3 = px.line(
        top20, x="ROUTE_SHORT_NAME", y="TOTAL_TRIPS",
        markers=True, color_discrete_sequence=[BLUE],
        labels={"ROUTE_SHORT_NAME": "Route", "TOTAL_TRIPS": "Total Trips"}
    )
    fig3.update_layout(height=350)
    st.plotly_chart(fig3, use_container_width=True)

    st.divider()
    st.subheader("Full Trip Patterns Table")
    display = patterns[[
        "ROUTE_SHORT_NAME", "ROUTE_LONG_NAME", "ROUTE_TYPE",
        "DIRECTION", "TOTAL_TRIPS", "AVG_STOPS_PER_TRIP", "MAX_STOPS", "MIN_STOPS"
    ]].copy()
    display.columns = ["Route", "Route Name", "Type", "Direction", "Total Trips", "Avg Stops", "Max Stops", "Min Stops"]
    st.dataframe(
        display.style
        .background_gradient(subset=["Total Trips"], cmap="Blues")
        .format({"Total Trips": "{:,}", "Avg Stops": "{:.1f}", "Max Stops": "{:,}", "Min Stops": "{:,}"}),
        use_container_width=True, hide_index=True
    )
    st.caption("TTC GTFS Static Feed · Python · Snowflake · dbt · Sofia Ahmed")