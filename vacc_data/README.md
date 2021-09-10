# COVID-19 vaccination data

This directory contains US county-level data for COVID-19 vaccination over time, by dose, and by demographic group.

## Authors
Shweta Bansal, Andrew Tiu, Alexes Merritt, Zack Susswein; Georgetown University

## Files:
- data_county_timeseries.csv: The file has the compiled CDC& individual state vaccination data at the county level weekly from December 13 to present. The data is then corrected using data from individual states. (More info below)

- data_county_current.csv: This file is the same as the data_master_county file except it only has the latest available data for each state (might be different dates/weeks)

## Codebook:
'STATE_NAME': state name as an abbreviation
'STATE': state fips code as integer
'COUNTY_NAME': county name appended with "County" or "Parish"
'COUNTY': 5-digit county fips code as integer
'GEOFLAG': 'County' denotes county level data; 'State' denotes downscaled state data
'DATE': date from Dec 13, 2020 to present
'CASE_TYPE': 'Complete'  or 'Complete Coverage" : complete protection with 2-dose Moderna or Pfizer or 1-dose Janssen; 'Partial'  or 'Partial Coverage" : partial protection with 1-dose Moderna or Pfizer  
'CASES': counts for CASE_TYPE = Complete or Partial; percentages of population for CASE_TYPE = Complete Coverage or Partial Coverage
'WEEK' = the week of 2021 the data is for (the DATE column is a date within this week, but not always the same day of the week).
'DEMO_GROUP' = racial/ethnic group


## Details of data integration 
#### CDC Data:
- Removed "Unknown County" entries. These are entires for which vaccination counts are available but they cannot be attributed to a county of residence
- Some counties are listed as strings rather than integers. All are converted to integers
- Data duplicates are dropped
- State fips code is added
- The date is formatted
- The data is translated from wide to long format

#### State Data
CA,  NM, VT, TN:
Added from https://data.news-leader.com/covid-19-vaccine-tracker/
- The dates for which this data is available for each state is used; for any dates before the earliest available date for each state, the CDC data is used. Additionally there are a handful of counties [35031, 35045] where CDC > State so we use CDC data for those to capture vaccinations at by Veterans Affairs, the DoD, the Bureau of Prisons or the Indian Health Service.

GA, VA, TX, CO, NC, OH,
Added from respective state health dept. However, in GA and NC, there are a handful of counties (13039, 13053, 13179, 37173, 37133, 37051, 37117, 51001, 51105,51520,51740, 51710) where CDC > State so we use CDC data for those to capture vaccinations at by Veterans Affairs, the DoD, the Bureau of Prisons or the Indian Health Service.

HI
Doesn't have county data, but there is little within-state variation, so just downscaled state coverage values (from CDC state data)

WV
We only have most recent weeks of corrected data. So we scale up incorrect CDC data time series to corrected end points.

MA
Three counties (Barnstable, Nantucket, Dukes) have incorrect data in CDC. So we scale use the timeseries for a neighboring county and rescale it to match the current corrected value.


## Citation:


