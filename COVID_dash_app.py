import pandas as pd
import numpy as np
import math
import plotly.express as px
import plotly.graph_objects as go
from urllib.request import urlopen
import json
import dash
from dash import dcc
from dash import html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State

# read in data + modifications

# geojson data with FIPS codes for county
with urlopen('https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json') as response:
    counties = json.load(response)

# vacc data
# old way, reading in from local file
# county_daily_total = pd.read_csv('vacc_data/data_county_current.csv', parse_dates=['DATE'])  # read data
# state_demo = pd.read_csv('vacc_data/data_demo.csv', parse_dates=['DATE'])  # read demographic data

# read vacc data directly from GitHub repo
county_daily_total = pd.read_csv('https://media.githubusercontent.com/media/bansallab/vaccinetracking/main/vacc_data/data_county_current.csv', parse_dates=['DATE'])  # read data
state_demo = pd.read_csv('https://media.githubusercontent.com/media/bansallab/vaccinetracking/main/vacc_data/data_demo.csv', parse_dates=['DATE'])  # read demographic data

# function to zero pad county FIPS codes
def pad_fips_county(x):
    return str(int(x)).zfill(5)

def pad_fips_state(x):
    return str(int(x)).zfill(2)

# zero padding FIPS codes
county_daily_total['COUNTY'] = county_daily_total['COUNTY'].apply(pad_fips_county)
county_daily_total['STATE'] = county_daily_total['STATE'].apply(pad_fips_state)
state_demo['STATE'] = state_demo['STATE'].apply(pad_fips_state)

# change some outdated FIPS codes so that they appear on map (2 counties in SD and AK)
county_daily_total.loc[county_daily_total['COUNTY'] == '46102', 'COUNTY'] = '46113'
county_daily_total.loc[county_daily_total['COUNTY'] == '02158', 'COUNTY'] = '02270'

# map function to precompute vaccination maps
def US_choropleth(coverage_sel):
    county_daily_total_choro = county_daily_total[county_daily_total['CASE_TYPE'] == coverage_sel]

    # control for NA values
    val_max = county_daily_total_choro.CASES.max(skipna=True)
    val_90 = np.nanpercentile(list(county_daily_total_choro.CASES), 90) / val_max
    val_92 = np.nanpercentile(list(county_daily_total_choro.CASES), 92) / val_max
    val_94 = np.nanpercentile(list(county_daily_total_choro.CASES), 94) / val_max
    val_96 = np.nanpercentile(list(county_daily_total_choro.CASES), 96) / val_max
    val_15 = np.nanpercentile(list(county_daily_total_choro.CASES), 15) / val_max
    val_30 = np.nanpercentile(list(county_daily_total_choro.CASES), 30) / val_max
    val_45 = np.nanpercentile(list(county_daily_total_choro.CASES), 45) / val_max
    val_60 = np.nanpercentile(list(county_daily_total_choro.CASES), 60) / val_max
    val_75 = np.nanpercentile(list(county_daily_total_choro.CASES), 75) / val_max

    custom_colorscale = [[0.0, '#ffffff'],
                         [val_15, '#e8edf2'],
                         [val_30, '#d2dce6'],
                         [val_45, '#bbcad9'],
                         [val_60, '#a4b8cc'],
                         [val_75, '#8ea7c0'],
                         [val_90, '#7795b3'],
                         [val_92, '#6083a6'],
                         [val_94, '#497199'],
                         [val_96, '#33608d'],
                         [1.0, '#1c4e80']]

    fig = px.choropleth(county_daily_total_choro,
                        geojson=counties,
                        locations='COUNTY',
                        color='CASES',
                        color_continuous_scale=custom_colorscale,
                        # range_color=[0, 7],  # restrict colorbar range so that more color variation shows
                        scope='usa',
                        custom_data=['COUNTY_NAME', 'STATE_NAME', 'POPN', 'DATE'],
                        # data available for hover
                        )
    fig.update_layout(margin=dict(b=0, t=0, l=0, r=0),  # sets the margins of the plot w/in its div
                      # controls appearance of hover label
                      hoverlabel=dict(
                          bgcolor='white',
                          font_size=16
                      ),
                      # controls appearance of color bar & title
                      coloraxis_colorbar=dict(
                          lenmode='pixels', len=400,
                          thicknessmode='pixels', thickness=40,
                          ticks='outside',
                          title='Vaccination <br>coverage (%)'
                      ),
                      # modifications to the map appearance (special geo settings)
                      geo=dict(
                          showlakes=False,
                          showland=True, landcolor='white'
                      )
                      )
    fig.update_coloraxes(colorbar_title_font=dict(size=14))
    fig.update_traces(marker_line_width=0.3,  # controls county border line width
                      marker_opacity=0.85,  # changes fill color opacity to let state borders through
                      marker_line_color='#262626',  # controls county border color; needs to be darker than "states"
                      # denotes custom template for what hover text should say
                      hovertemplate='<b>%{customdata[0]}, %{customdata[1]}</b><br>Coverage: %{z:.1f}%<br>Population: %{customdata[2]:,}<br>Date: %{customdata[3]|%d %b %Y}'
                      )
    fig.update_geos(showsubunits=True, subunitcolor='#5a5a5a')  # hacky: effectively controls state borders
    return fig

# define the pre-computed maps
complete_map = US_choropleth('Complete Coverage')
partial_map = US_choropleth('Partial Coverage')
booster_map = US_choropleth('Booster Coverage')

# initialize Dash app
app = dash.Dash(__name__)
server = app.server

modal = html.Div(
    [
        dbc.Modal(
            [
                dbc.ModalHeader('Warning'),
                dbc.ModalBody('No demographic data available for this state. Please make a different selection.'),
                dbc.ModalFooter(
                    dbc.Button('Close', id='close', className='ml-auto')
                )
            ],
            id='warning-modal',
            backdrop=False
        )
    ]
)

alert = html.Div(
    [
        dbc.Alert(
            [
                # html.H5('Tips', className='mb-0'),
                html.H5('Warning', className='mb-0'),
                html.Hr(className='mb-0'),
                # html.P('Hover over a county to see vaccination coverage and the source of the data (state or county).')
                html.P('With so few states continuing to report COVID vaccination data, we have stopped updating this dashboard after October of 2022. However, this dashboard and the data on GitHub will remain.')
            ],
            id='alert-fade',
            dismissable=True,
            is_open=True,
            color='danger'
        )
    ]
)

tab1_content = html.Div(
                    children=[
                        html.Div(
                            dcc.RadioItems(
                                id='coverage-buttons',
                                options=[
                                    {'label': 'Booster coverage', 'value': 'Booster Coverage'},
                                    {'label': 'Complete vaccination (2 dose) coverage', 'value': 'Complete Coverage'},
                                    {'label': 'Partial vaccination (1+ dose) coverage', 'value': 'Partial Coverage'}
                                    ],
                                value='Booster Coverage',
                                labelStyle={'display': 'block'}
                            ),
                            className='mt-3'
                        ),
                        dbc.Spinner(
                            color='secondary',
                            children=[
                                html.Div(dcc.Graph(
                                    id='US-choropleth',
                                    figure=complete_map,
                                    style={'marginBottom': 0, 'height': 500},  # plot container sizing, etc.
                                    config={'modeBarButtonsToRemove': ['select2d',
                                                                       'lasso2d',
                                                                       'zoom2d',
                                                                       'autoScale2d',
                                                                       'toggleSpikelines',
                                                                       'toggleHover',
                                                                       'sendDataToCloud',
                                                                       'toImage',
                                                                       'hoverClosestGeo'],
                                            'scrollZoom': False,
                                            'displayModeBar': True,
                                            'displaylogo': False}
                                ))
                            ]
                        )
                    ]
                )

tab2_content = dbc.Spinner(
    color='secondary',
    children=[
        html.Div(dcc.Graph(
            id='rac-disp-choropleth',
            figure=complete_map, # placeholder map for now
            style={'marginBottom': 0, 'height': 500},  # plot container sizing, etc.
            config={'modeBarButtonsToRemove': ['select2d',
                                               'lasso2d',
                                               'zoom2d',
                                               'autoScale2d',
                                               'toggleSpikelines',
                                               'toggleHover',
                                               'sendDataToCloud',
                                               'toImage',
                                               'hoverClosestGeo'],
                    'scrollZoom': False,
                    'displayModeBar': True,
                    'displaylogo': False}
        )
        )
    ]
)

tabs = dbc.Tabs(
    [
        dbc.Tab(tab1_content, label='Vaccination coverage'),
        dbc.Tab(tab2_content, label='Demographic disparities', disabled=True)  # disabled for now
    ]
)

# row for map
row_2 = dbc.Row(
    children=[
        dbc.Col(
            children=[
                tabs
            ], width={'size': 8, 'offset': 2}, style={'height': '100%'}
        ),
        dbc.Col(
            children=[
                modal,
                html.Div(
                    alert
                )
            ], width=2, style={'height': '100%'}
        )
    ], justify='left', className='g-0'
)


app.layout = dbc.Container([row_2], fluid=True)

# callback structure

# callback for updating vacc map coverage
@app.callback(
    Output('US-choropleth', 'figure'),
    [Input('coverage-buttons', 'value')])
# function for plotting base US choropleth
def update_disp_map(button_value):
    # uses precomputed map data rather than computing on the fly
    if button_value == 'Partial Coverage':
        return partial_map
    elif button_value == 'Booster Coverage':
        return booster_map
    else:
        return complete_map

if __name__ == '__main__':
    app.run_server()
