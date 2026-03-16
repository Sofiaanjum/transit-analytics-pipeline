select
    case route_type
        when 0 then 'Streetcar'
        when 1 then 'Subway'
        when 3 then 'Bus'
        else 'Other'
    end                                          as route_type,
    count(distinct r.route_id)                   as total_routes,
    count(distinct t.trip_id)                    as total_trips,
    count(distinct st.stop_id)                   as unique_stops,
    count(st.trip_id)                            as total_stop_events,
    round(count(distinct t.trip_id) * 100.0 /
        nullif(sum(count(distinct t.trip_id))
        over (), 0), 2)                          as pct_of_network_trips,
    round(count(distinct st.stop_id) * 100.0 /
        nullif(sum(count(distinct st.stop_id))
        over (), 0), 2)                          as pct_of_network_stops,
    round(count(st.trip_id) * 1.0 /
        nullif(count(distinct t.trip_id), 0), 1) as avg_stops_per_trip
from {{ ref('stg_routes') }} r
left join {{ ref('stg_trips') }} t
    on r.route_id = t.route_id
left join {{ ref('stg_stop_times') }} st
    on t.trip_id = st.trip_id
group by
    r.route_type