# COVID-19 vaccination data

This repository contains US county-level data for COVID-19 vaccination over time, by dose, and by demographic group.

## Updates
- The data was updated on January 28th, 2022 with county-level booster vaccination data. This dataset is constructucted from CDC + state-level data as described below
- As of January 28th, 2022, the data source for WV, NM, VT, and TN  data was changed to the the CDC, and the data source for CA was changed to the CA Dept of Health
- As of the week of April 4th, 2022 (still true as of July 25, 2022), all state data is sourced from CDC except CA, CO, VA, MA, and HI (due to significant deviations between the two data sources, as described below). The state of Colorado does not provide booster coverage data by county, so CDC data is provided there.
- As of June 2022, CDC vaccination data is updated weekly on Thursdays
- As of October 2022, this data repo is no longer being updated.

## Citation:
If you use this data, please cite this repository and the following article:
Andrew Tiu, Zachary Susswein, Alexes Merritt, Shweta Bansal. Characterizing the spatiotemporal heterogeneity of the COVID-19 vaccination landscape. American Journal of Epidemiology, 2022; kwac080, https://doi.org/10.1093/aje/kwac080

## Dashboard
The data in the data_county_timeseries file is visualized in the dashboard at: http://www.vaccinetracking.us/

## Files:
- data_county_timeseries.csv: The file has the compiled CDC& individual state vaccination data at the county level weekly from Jan 1, 2021 to present. The data is then corrected using data from individual states. (More info below)

- data_county_current.csv: This file is the same as the data_county_timeseries file but only contains the latest available data for each state (might be different dates/weeks)

## Codebook:
'STATE_NAME': state name as an abbreviation

'STATE': state fips code as integer

'COUNTY_NAME': county name appended with "County" or "Parish"

'COUNTY': 5-digit county fips code as integer

'GEOFLAG': 'County' denotes county level data; 'State' denotes downscaled state data

'DATE': This date is more representative of data updating processes rather than of the vaccination process. It may also not be the same day of the week every week. Thus we recommend using the WEEK and YEAR column for analyses.

'CASE_TYPE': 'Booster' or 'Booster Coverage': protection with an additional dose for compltely protected individuals; 'Complete'  or 'Complete Coverage" : complete protection with 2-dose Moderna or Pfizer or 1-dose Janssen; 'Partial'  or 'Partial Coverage" : partial protection with 1-dose Moderna or Pfizer  

'CASES': counts for CASE_TYPE = Booster or Complete or Partial; percentages of population for CASE_TYPE = Booster Coverage or Complete Coverage or Partial Coverage

'WEEK' = the ISO week of the year the data is for. (The DATE column is a date within this week, but not always the same day of the week. Thus, we recommend use of the WEEK and YEAR column instead of DATE for all analyses.) 

'YEAR' = the year that the data corresponds to

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

*  Locations where CDC rates > State rates, we use CDC data to capture vaccinations at by Veterans Affairs, the DoD, the Bureau of Prisons or the Indian Health Service.
*  Locations where CDC rates < State rates, we use the state data as described below:

VA, CO, CA
- CA (8 missing counties in CDC data), VA (state-reported rates are at least five percentage points above CDC-reported rates for 83% of counties), CO (state-reported rates are at least five percentage points above CDC-reported rates for 90% of counties).

HI
- Doesn't have county data, but there is little within-state variation, so we have downscaled state coverage values (from CDC state data) using population weighting. (We note that the CDC has added some county-level data for HI since Oct 22 2021, but these data seem to have errors, so we are not currently using them)

MA
- Three counties (Barnstable, Nantucket, Dukes) have incorrect data in CDC. So we scale use the timeseries for a neighboring county and rescale it to match the current corrected value.

#### Data integration & cleaning
- We collate these disparate data sources to produce a single estimate of cumulative vaccination counts for every county.
- We interpolate any weeks of missing data using linear interpolation. (Additional interpolation added on Decembember 16, 2021).
