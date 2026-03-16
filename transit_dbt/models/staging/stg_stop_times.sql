select
    trip_id,
    stop_id,
    stop_sequence,
    arrival_time,
    departure_time,
    case
        when split_part(arrival_time, ':', 1)::int > 23
        then split_part(arrival_time, ':', 1)::int - 24
        else split_part(arrival_time, ':', 1)::int
    end as hour_of_day
from TRANSIT_DB.RAW.STOP_TIMES
where arrival_time is not null