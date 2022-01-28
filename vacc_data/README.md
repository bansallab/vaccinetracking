# COVID-19 vaccination data

This repository contains US county-level data for COVID-19 vaccination over time, by dose, and by demographic group.

## Updates
- The data was updated on January 28th, 2022 with county-level booster vaccination data. This dataset is constructucted from CDC + state-level data as described below
- As of January 28th, 2022, the data source for California data was changed to the CA Dept of Health

## Citation:
If you use this data, please cite:

- Merritt, Alexes; Tiu, Andrew; Bansal, Shweta, 2021, "Integrated US COVID-19 Vaccination Data", https://doi.org/10.7910/DVN/BFRIKI, Harvard Dataverse, V1.

- Andrew Tiu, Zachary Susswein, Alexes Merritt, Shweta Bansal. Characterizing the spatiotemporal heterogeneity of the COVID-19 vaccination landscape. MedRxiv.

## Data source
For more information about the data, see 

- http://www.vaccinetracking.us/data.html
- Andrew Tiu, Zachary Susswein, Alexes Merritt, Shweta Bansal. Characterizing the spatiotemporal heterogeneity of the COVID-19 vaccination landscape. MedRxiv.

## Files:
- data_county_timeseries.csv: The file has the compiled CDC& individual state vaccination data at the county level weekly from December 13 to present. The data is then corrected using data from individual states. (More info below)

- data_county_current.csv: This file is the same as the data_county_timeseries file except it only has the latest available data for each state (might be different dates/weeks)

## Codebook:
'STATE_NAME': state name as an abbreviation

'STATE': state fips code as integer

'COUNTY_NAME': county name appended with "County" or "Parish"

'COUNTY': 5-digit county fips code as integer

'GEOFLAG': 'County' denotes county level data; 'State' denotes downscaled state data

'DATE': date from Dec 13, 2020 to present. This date is more representative of data updating processes rather than of the vaccination process. It may also not be the same day of the week every week.

'CASE_TYPE': 'Booster' or 'Booster Coverage': protection with an additional dose for compltely protected individuals; 'Complete'  or 'Complete Coverage" : complete protection with 2-dose Moderna or Pfizer or 1-dose Janssen; 'Partial'  or 'Partial Coverage" : partial protection with 1-dose Moderna or Pfizer  

'CASES': counts for CASE_TYPE = Booster or Complete or Partial; percentages of population for CASE_TYPE = Booster Coverage or Complete Coverage or Partial Coverage

'WEEK' = the week of 2021 the data is for. (The DATE column is a date within this week, but not always the same day of the week. Thus, we recommend use of the WEEK column instead of DATE for all analyses.

'DEMO_GROUP' = racial/ethnic group


## Details of data processing
#### CDC Data:
- Removed "Unknown County" entries. These are entires for which vaccination counts are available but they cannot be attributed to a county of residence
- Some counties are listed as strings rather than integers. All are converted to integers
- Data duplicates are dropped
- State fips code is added
- The date is formatted
- The data is translated from wide to long format

#### State Data
GA, VA, TX, CO, NC, OH, CA
- Added from respective state health dept. However, in GA and NC, there are a handful of counties (13039, 13053, 13179, 37173, 37133, 37051, 37117, 51001, 51105,51520,51740, 51710) where CDC > State so we use CDC data for those to capture vaccinations at by Veterans Affairs, the DoD, the Bureau of Prisons or the Indian Health Service.

NM, VT, TN:
- The data for these states are from a data aggregator. The dates for which this data is available for each state is used; for any dates before the earliest available date for each state, the CDC data is used. Additionally there are a handful of counties where CDC > State so we use CDC data for those to capture vaccinations at by Veterans Affairs, the DoD, the Bureau of Prisons or the Indian Health Service.
- These states do not provide booster vaccination data at the county-level, so we rely on CDC data for booster coverage levels.

HI
- Doesn't have county data, but there is little within-state variation, so we have downscaled state coverage values (from CDC state data) using population weighting. (We note that the CDC has added some county-level data for HI since Oct 22 2021, but these data seem to have errors, so we are not currently using them)

WV
- We only have most recent weeks of corrected data. So we scale up incorrect CDC data time series to corrected end points.

MA
- Three counties (Barnstable, Nantucket, Dukes) have incorrect data in CDC. So we scale use the timeseries for a neighboring county and rescale it to match the current corrected value.

#### Data integration & cleaning
- We collate these disparate data sources to produce a single estimate of cumulative vaccination counts for every county.
- We interpolate any weeks of missing data using linear interpolation. (Additional interpolation added on Decembember 16, 2021).
