select
    st.hour_of_day,
    count(st.trip_id)                        as total_trips,
    count(distinct st.trip_id)               as unique_trips,
    count(distinct st.stop_id)               as stops_served,
    case
        when st.hour_of_day between 7 and 9
        then 'Morning Peak'
        when st.hour_of_day between 16 and 19
        then 'Evening Peak'
        when st.hour_of_day between 22 and 23
            or st.hour_of_day between 0 and 5
        then 'Off Peak'
        else 'Regular Service'
    end                                      as service_period,
    round(count(st.trip_id) * 100.0 /
        nullif(sum(count(st.trip_id))
        over (), 0), 2)                      as pct_of_daily_trips
from {{ ref('stg_stop_times') }} st
where st.hour_of_day between 0 and 23
group by
    st.hour_of_day
order by
    st.hour_of_day