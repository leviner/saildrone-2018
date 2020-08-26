
All of the data in this directory are unpublished and being used for other publications, and thus the data themselves are not included in the public respository. All of the data is used in the catch reporting within the manuscript, and thus the following is an overview of the data sources included.

# AIESMarinovichEventData
Export from NOAA/AFSC Clams2ABL using the following SQL:
```SQL
select a.*, b.min_head_rope_depth, c.max_head_rope_depth, d.avg_head_rope_depth, e.avg_net_hori_opening, f.avg_net_vert_opening
from(
select survey, event_id, gear, eq_time, eq_longitude, eq_latitude, hb_time, hb_longitude,
hb_latitude, bottom_depth_start, avg_head_rope_depth, avg_net_vert_opening, avg_net_hori_opening
from v_event_data_v4_final) a
    left join
    (select survey, event_id, min(CAST(measurement_value as FLOAT)) as min_head_rope_depth
    from event_stream_data
    where measurement_type = 'HeadRopeDepth'
    group by survey, event_id) b
    on
    b.survey = a.survey and b.event_id = a.event_id
        left join
        (select survey, event_id, max(CAST(measurement_value as FLOAT)) as max_head_rope_depth
        from event_stream_data
        where measurement_type = 'HeadRopeDepth'
        group by survey, event_id) c
        on
        c.survey = a.survey and c.event_id = a.event_id
            left join
            (select survey, event_id, avg(CAST(measurement_value as FLOAT)) as avg_head_rope_depth
            from event_stream_data
            where measurement_type = 'HeadRopeDepth'
            group by survey, event_id) d
            on
            d.survey = a.survey and d.event_id = a.event_id
                left join
                (select survey, event_id, avg(CAST(measurement_value as FLOAT)) as avg_net_hori_opening
                from event_stream_data
                where measurement_type = 'NetHorizontalOpening'
                group by survey, event_id) e
                on
                e.survey = a.survey and e.event_id = a.event_id
                    left join
                    (select survey, event_id, avg(CAST(measurement_value as FLOAT)) as avg_net_vert_opening
                    from event_stream_data
                    where measurement_type = 'NetVerticalOpening'
                    group by survey, event_id) f
                    on
                    f.survey = a.survey and f.event_id = a.event_id

where (a.survey=201701 or a.survey=201901) and a.gear = 'Marinovich'
order by a.survey, a.event_id
```
Missing values were then filled in with average by year and volume filtered was calculated based on trawl distance.
```python
import pandas as pd
import numpy as np
import math
from geopy.distance import distance

def fillAve(df):
    ys = []
    for y in df.SURVEY.astype('str'):
        ys.append(int(y[:4]))
    df['YEAR'] = ys
    for year in df.YEAR.unique():
        fillVals = {'AVG_NET_VERT_OPENING':np.nanmean(df['AVG_NET_VERT_OPENING'][df.YEAR == year]),
                    'AVG_NET_HORI_OPENING':np.nanmean(df['AVG_NET_HORI_OPENING'][df.YEAR == year])}
        df[df.YEAR == year] = df[df.YEAR == year].fillna(fillVals)
        print('For '+str(year)+': ',fillVals)
    return df
df.AVG_HEAD_ROPE_DEPTH.fillna(df.AVG_HEAD_ROPE_DEPTH_1, inplace=True)
df.AVG_NET_VERT_OPENING.fillna(df.AVG_NET_VERT_OPENING_1, inplace=True)
df.AVG_NET_HORI_OPENING.fillna(df.AVG_NET_HORI_OPENING_1, inplace=True)
df = df.drop(columns=['AVG_HEAD_ROPE_DEPTH_1', 'AVG_NET_VERT_OPENING_1','AVG_NET_HORI_OPENING_1'])
df

df = fillAve(df) # fill in missing vert/horiz opening measurements by taking the average for each unique year (see above)
df['NET_AREA'] = pd.Series(df.AVG_NET_VERT_OPENING*df.AVG_NET_HORI_OPENING) #calculate the area of the mouth of the net
dist = []
for i in range(len(df.EQ_LATITUDE.values)): # calculate the distance trawled for each path, see function above, in meters
    dist.append(distance((df.EQ_LATITUDE.values[i],df.EQ_LONGITUDE.values[i]),(df.HB_LATITUDE.values[i],df.HB_LONGITUDE.values[i])).m)
df['TRAWL_DIST'] = pd.Series(dist)
df['VOL_FILTERED'] = df.TRAWL_DIST*df.NET_AREA
df.head() # Show the final dataset head
```

# OS201701MidwaterCatchSummary & OS201901MidwaterCatchSummary
Direct Exports of NOAA/AFSC Clams2ABL v_AIES_CATCH_SUMMARY view

# MethotCatch
Reformatted catch data from HLY1801 fish catches to include station/lat/lon along with species.

# EventRatios
Courtesy of Sharon Wildes. Ratios of genetic identification for gadids (Arctic cod vs. not Arctic cod) collected on OS201701 and OS201901. These data are used in the catchData notebook to adjust CPUE by genetic ratios.
