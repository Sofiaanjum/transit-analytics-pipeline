select
    s.stop_id,
    s.stop_name,
    s.stop_lat,
    s.stop_lon,
    count(st.trip_id)                    as total_visits,
    count(distinct t.route_id)           as routes_served,
    round(count(st.trip_id) * 100.0 /
        nullif(sum(count(st.trip_id))
        over (), 0), 4)                  as activity_pct,
    case
        when count(st.trip_id) >=
            percentile_cont(0.90)
            within group (order by count(st.trip_id))
            over ()
        then 'Major Hub'
        when count(st.trip_id) >=
            percentile_cont(0.70)
            within group (order by count(st.trip_id))
            over ()
        then 'High Activity'
        when count(st.trip_id) >=
            percentile_cont(0.50)
            within group (order by count(st.trip_id))
            over ()
        then 'Moderate'
        else 'Low Activity'
    end                                  as stop_classification
from {{ ref('stg_stops') }} s
left join {{ ref('stg_stop_times') }} st
    on s.stop_id = st.stop_id
left join {{ ref('stg_trips') }} t
    on st.trip_id = t.trip_id
group by
    s.stop_id,
    s.stop_name,
    s.stop_lat,
    s.stop_lon