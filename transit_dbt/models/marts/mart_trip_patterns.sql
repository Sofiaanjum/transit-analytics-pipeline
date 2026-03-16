select
    r.route_short_name,
    r.route_long_name,
    case r.route_type
        when 0 then 'Streetcar'
        when 1 then 'Subway'
        when 3 then 'Bus'
        else 'Other'
    end                                      as route_type,
    t.direction_id,
    case t.direction_id
        when 0 then 'Outbound'
        when 1 then 'Inbound'
        else 'Unknown'
    end                                      as direction,
    count(distinct t.trip_id)                as total_trips,
    round(avg(trip_stops.stop_count), 1)     as avg_stops_per_trip,
    max(trip_stops.stop_count)               as max_stops,
    min(trip_stops.stop_count)               as min_stops
from {{ ref('stg_trips') }} t
join {{ ref('stg_routes') }} r
    on t.route_id = r.route_id
join (
    select
        trip_id,
        count(stop_id) as stop_count
    from {{ ref('stg_stop_times') }}
    group by trip_id
) trip_stops
    on t.trip_id = trip_stops.trip_id
group by
    r.route_short_name,
    r.route_long_name,
    r.route_type,
    t.direction_id