select
    service_id,
    monday,
    tuesday,
    wednesday,
    thursday,
    friday,
    saturday,
    sunday,
    start_date,
    end_date,
    case
        when monday = 1 and tuesday = 1
             and wednesday = 1 and thursday = 1
             and friday = 1
        then 'Weekday'
        when saturday = 1 or sunday = 1
        then 'Weekend'
        else 'Special'
    end as service_type
from TRANSIT_DB.RAW.CALENDAR