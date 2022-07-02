import pandas as pd
import numpy as np
import math
import plotly.express as px
import plotly.graph_objects as go
from urllib.request import urlopen
import json
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State

# import dash_table

# from timeit import default_timer as timer

# import time
# from concurrent.futures import ThreadPoolExecutor

#-----------------------------------------------------------------------------------------------------------------------
# Read in data and modifications

# geojson data with FIPS codes for county
with urlopen('https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json') as response:
    counties = json.load(response)

# vacc data
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

# setup multithreading
# UPDATE_INTERVAL = 86400  # update interval in seconds; 86400 s --> 24 hrs

# function for getting new global data and some mods
# def get_new_data():
#     global county_daily_total, state_demo
#
#     county_daily_total = pd.read_csv('https://drive.google.com/uc?export=download&id=1PGHvsyPK61qimnmLX9VGpfD-3tkXjAqD')
#     state_demo = pd.read_csv('https://drive.google.com/uc?export=download&id=1PF_ytpTnvzM4rilygLLUsD7LVF95YgrQ')
#
#     county_daily_total['DATE'] = pd.to_datetime(county_daily_total['DATE'])  # convert date to datetime object
#     state_demo['DATE'] = pd.to_datetime(state_demo['DATE'])  # convert to datetime obj
#
#     county_daily_total['COUNTY'] = county_daily_total['COUNTY'].apply(pad_fips_county)
#     county_daily_total['STATE'] = county_daily_total['STATE'].apply(pad_fips_state)
#     state_demo['STATE'] = state_demo['STATE'].apply(pad_fips_state)

# function for updating data after every interval
# def get_new_data_every(period=UPDATE_INTERVAL):
#     while True:
#         get_new_data()
#         print('data updated')
#         time.sleep(period)

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

    # dash.callback_context.record_timing('read data', timer() - start_1, '1st task')

    # start_2 = timer()

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

    # dash.callback_context.record_timing('1st fig block', timer()-start_2, '2nd task')

    # start_3 = timer()
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

    # dash.callback_context.record_timing('updt_layout', timer()-start_3, '3rd task')

    # start_4 = timer()

    fig.update_coloraxes(colorbar_title_font=dict(size=14))

    # dash.callback_context.record_timing('updt-colorax', timer() - start_4, '4th task')

    # start_5 = timer()
    fig.update_traces(marker_line_width=0.3,  # controls county border line width
                      marker_opacity=0.85,  # changes fill color opacity to let state borders through
                      marker_line_color='#262626',  # controls county border color; needs to be darker than "states"
                      # denotes custom template for what hover text should say
                      hovertemplate='<b>%{customdata[0]}, %{customdata[1]}</b><br>Coverage: %{z:.1f}%<br>Population: %{customdata[2]:,}<br>Date: %{customdata[3]|%d %b %Y}'
                      )
    # dash.callback_context.record_timing('updt_trace', timer() - start_5, '5th task')

    # start_6 = timer()
    # 5a5a5a is a slightly lighter shade of gray than above
    fig.update_geos(showsubunits=True, subunitcolor='#5a5a5a')  # hacky: effectively controls state borders

    # dash.callback_context.record_timing('updt_geos', timer() - start_6, '6th task')
    return fig

# define the pre-computed maps
complete_map = US_choropleth('Complete Coverage')
partial_map = US_choropleth('Partial Coverage')
booster_map = US_choropleth('Booster Coverage')

# disparity maps --> awaiting new data and mapping function
# black_map =
# hispanic_map =

# ----------------------------------------------------------------------------------------------------------------------
# initializes Dash app
app = dash.Dash(__name__)
server = app.server
# get_new_data()  # read data upon app initialization

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
                html.H5('Tips', className='mb-0'),
                html.Hr(className='mb-0'),
                html.P('Hover over a county to see vaccination coverage and the source of the data (state or county).')
            ],
            id='alert-fade',
            dismissable=True,
            is_open=True,
            color='secondary'
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

# new tab2_content --> awaiting final data
# tab2_content = html.Div(
#                     children=[
#                         html.Div(
#                             dcc.RadioItems(
#                                 id='disp-buttons',
#                                 options=[
#                                     {'label': 'Black disparity', 'value': 'Black_Disparity'},
#                                     {'label': 'Hispanic disparity', 'value': 'Hispanic_Disparity'}
#                                     ],
#                                 value='Black_Disparity',
#                                 labelStyle={'display': 'block'}
#                             ),
#                             className='mt-3'
#                         ),
#                         dbc.Spinner(
#                             color='secondary',
#                             children=[
#                                 html.Div(dcc.Graph(
#                                     id='disp-choropleth',
#                                     figure=complete_map,
#                                     style={'marginBottom': 0, 'height': 500},  # plot container sizing, etc.
#                                     config={'modeBarButtonsToRemove': ['select2d',
#                                                                        'lasso2d',
#                                                                        'zoom2d',
#                                                                        'autoScale2d',
#                                                                        'toggleSpikelines',
#                                                                        'toggleHover',
#                                                                        'sendDataToCloud',
#                                                                        'toImage',
#                                                                        'hoverClosestGeo'],
#                                             'scrollZoom': False,
#                                             'displayModeBar': True,
#                                             'displaylogo': False}
#                                 ))
#                             ]
#                         )
#                     ]
#                 )

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
    ], justify='left', no_gutters=True, className='h-100'
)


app.layout = dbc.Container([row_2], fluid=True)

# define multi thread executor
# executor = ThreadPoolExecutor(max_workers=1)
# executor.submit(get_new_data_every)
#-----------------------------------------------------------------------------------------------------------------------
# CALLBACK STRUCTURE

# callback for looking at callback_context contents
# @app.callback(
#     Output('selected-values', 'children'),
#     [Input('US-choropleth', 'clickData')])
# def display_trigger(US_choro_clickData):
#     # last_triggered = dash.callback_context.triggered[0]['prop_id']
#     # last_triggered_val = dash.callback_context.triggered[0]['value']
#     last_trig = US_choro_clickData['points'][0]['location'][:2]
#     # returned_val = str(state_demo.CASES[state_demo['STATE']==last_trig][0])
#     return json.dumps(last_trig)

# callback for modal and fade revealing bar plots
# @app.callback(
#     [Output('race-fade', 'is_in'),
#      Output('ethnicity-fade', 'is_in'),
#      Output('warning-modal', 'is_open')],
#     [Input('rac-disp-choropleth', 'clickData'), Input('close', 'n_clicks')],
#     [State('race-fade', 'is_in'), State('warning-modal', 'is_open')])
# def update_collapse(US_choro_clickData, n, is_in, is_open):
#     last_triggered_val = dash.callback_context.triggered[0]['value']  # assigns variable to clickData info
#     unknown_list = ['CASES_UnknownRace', 'CASES_UnknownEthnicity']
#
#     # if a county/state has been clicked
#     if last_triggered_val:
#         fips_code = US_choro_clickData['points'][0]['location']  # grabs the county FIPS code from clickData
#         fips_code = fips_code[:2]  # grab the state part of FIPS code
#
#         # check if any state demographic data available
#         if state_demo.CASES[(state_demo['STATE'] == fips_code) & (~state_demo['DEMO_GROUP'].isin(unknown_list))].sum() == 0 and not n:
#             return False, False, not is_open
#         if state_demo.CASES[(state_demo['STATE'] == fips_code) & (~state_demo['DEMO_GROUP'].isin(unknown_list))].sum() == 0 and n:
#             return False, False, not is_open
#         else:
#             return True, True, is_open
#     else:
#         return is_in, is_in, is_open

# callback for updating disparity choropleth depending on disp selection
# @app.callback(
#     Output('disp-choropleth', 'figure'),
#     [Input('disp-buttons', 'value')])
# # function for plotting base US choropleth
# def update_vacc_map(button_value):
#     # uses precomputed map data rather than computing on the fly
#     if button_value == 'Hispanic_Disparity':
#         return hispanic_map
#     else:
#         return black_map

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

# @app.callback(
#     [Output('race-bar', 'children'),
#      Output('ethnicity-bar', 'children')],
#     [Input('rac-disp-choropleth', 'clickData')])
# def update_bar_area(US_choro_clickData):
#     last_triggered_val = dash.callback_context.triggered[0]['value']
#
#     if last_triggered_val:
#         fips_code = US_choro_clickData['points'][0]['location']  # grabs the county FIPS code from clickData
#         # fips_code = fips_code[:2]  # grab the state part of FIPS code
#         fips_code = html.H5(fips_code)
#
#     else:
#         fips_code = html.H5('01001')
#
#     return fips_code, fips_code

# callback for updating bar plots depending on state clicked
# @app.callback(
#     [Output('race-bar', 'figure'),
#      Output('ethnicity-bar', 'figure')],
#     [Input('rac-disp-choropleth', 'clickData')])
# def update_bar_plots(US_choro_clickData):
#     last_triggered_val = dash.callback_context.triggered[0]['value']  # assigns variable to clickData info
#
#     race_class_list = ['CASES_White', 'CASES_Black', 'CASES_Asian', 'CASES_Native', 'CASES_Pacific', 'CASES_UnknownRace']
#     ethnicity_class_list = ['CASES_Hispanic', 'CASES_NotHispanic', 'CASES_UnknownEthnicity']
#
#     # defines custom colors for the barplot
#     race_colors = {'Partial Coverage': '#f5b5a3', 'Complete Coverage': '#ea6a47'}  # orange
#     ethnicity_colors = {'Partial Coverage': '#c0b9d9', 'Complete Coverage': '#8172b3'}  # purple
#
#     # case for when user clicks county
#     if last_triggered_val:
#         fips_code = US_choro_clickData['points'][0]['location']  # grabs the county FIPS code from clickData
#         fips_code = fips_code[:2]  # grab the state part of FIPS code
#
#         # subset main demo df by the selected state and the type of variable
#         dff_race = state_demo[(state_demo['STATE'] == fips_code) & (state_demo['DEMO_GROUP'].isin(race_class_list))]
#         dff_ethnicity = state_demo[(state_demo['STATE'] == fips_code) & (state_demo['DEMO_GROUP'].isin(ethnicity_class_list))]
#
#     # case for when user hasn't clicked a county yet; Nebraska default, hidden
#     else:
#         dff_race = state_demo[(state_demo['STATE_NAME'] == 'Nebraska') & (state_demo['DEMO_GROUP'].isin(race_class_list))]
#         dff_ethnicity = state_demo[(state_demo['STATE_NAME'] == 'Nebraska') & (state_demo['DEMO_GROUP'].isin(ethnicity_class_list))]
#
#     # race_NA_part = dff_race.CASES[(dff_race['DEMO_GROUP'] == 'CASES_UnknownRace') & (
#     #         dff_race['CASE_TYPE'] == 'Partial Coverage')].unique()[0]
#     race_NA_comp = dff_race.CASES[(dff_race['DEMO_GROUP'] == 'CASES_UnknownRace') & (
#             dff_race['CASE_TYPE'] == 'Complete Coverage')].unique()[0]
#     # ethnicity_NA_part = dff_ethnicity.CASES[(dff_ethnicity['DEMO_GROUP'] == 'CASES_UnknownEthnicity') & (
#     #             dff_ethnicity['CASE_TYPE'] == 'Partial Coverage')].unique()[0]
#     ethnicity_NA_comp = dff_ethnicity.CASES[(dff_ethnicity['DEMO_GROUP'] == 'CASES_UnknownEthnicity') & (
#                 dff_ethnicity['CASE_TYPE'] == 'Complete Coverage')].unique()[0]
#
#     # creating the race bar plot
#     race_barplot = go.Figure()
#     y_max = dff_race.CASES[(dff_race['CASE_TYPE'].isin(['Partial Coverage', 'Complete Coverage'])) & (dff_race['DEMO_GROUP'] != 'CASES_UnknownRace')].max()
#     y_max = 5 * math.ceil(y_max/5) # round to nearest 5
#     for i in ['Complete Coverage']:
#         race_barplot.add_trace(go.Bar(
#             x=dff_race.DEMO_GROUP[(dff_race['CASE_TYPE'] == i) & (dff_race['DEMO_GROUP'] != 'CASES_UnknownRace')],
#             y=dff_race.CASES[(dff_race['CASE_TYPE'] == i) & (dff_race['DEMO_GROUP'] != 'CASES_UnknownRace')],
#             name=i,
#             marker_color=race_colors[i],  # overrides the color of the bars
#             opacity=0.7,
#             text=dff_race.CASES[(dff_race['CASE_TYPE'] == i) & (dff_race['DEMO_GROUP'] != 'CASES_UnknownRace')],
#             textposition='auto',
#             texttemplate='%{text:.1f}%',
#             hoverinfo='skip',
#             #width = [0.3, 0.3, 0.3, 0.3, 0.3, 0.3]
#         ))
#     race_barplot.update_layout(
#         margin=dict(
#             l=0,
#             r=0,
#             t=30,
#             b=50
#         ),
#         barmode='group',  # designates grouped bar plot
#         annotations=[
#             dict(
#                 x=1.04,
#                 y=0.6,
#                 xanchor='left',
#                 yanchor='top',
#                 xref='paper',
#                 yref='paper',
#                 align='left',
#                 showarrow=False,
#                 bgcolor='rgba(0,0,0,0)',
#                 text='Race was other/<br>unknown <br>{:.1f}% of completely <br>vaccinated individuals.'.format(race_NA_comp)
#             )
#         ],
#         title=dict(
#             text='<b>{}</b>: Vaccination by Race'.format(dff_race['STATE_NAME'].unique()[0]),
#             font=dict(
#                 size=16
#             ),
#             yref='paper',  # sets plotting area height as y ref point
#             y=0.9,
#             yanchor='bottom',  # ref point on title for what sits at y
#             pad={'t': 20, 'b': 35, 'l': 40, 'r': 0}
#         ),
#         xaxis=dict(
#             type='category',
#             showline=True,
#             linecolor='black',
#             tickmode='array',  # allows us to use custom tick text
#             tickvals=[0, 1, 2, 3, 4],  # essential if we want custom text; denotes positions of tick labels
#             ticktext=['White', 'Black', 'Asian', 'Native American', 'Pacific Islander'],  # sets custom group names along x axis
#             categoryorder='array',  # allows us to specify custom order
#             categoryarray=['CASES_White', 'CASES_Black', 'CASES_Asian', 'CASES_Native', 'CASES_Pacific'],  # sets custom order of group names
#             fixedrange=True,
#             range=[-0.5,5]  # need -0.5 to make sure first bar isn't cut off
#         ),
#         yaxis=dict(
#             type='linear',
#             ticks='outside',
#             title=dict(
#                 text='Vaccination Coverage in Group (%)',
#                 font=dict(
#                     size=12
#                 )
#             ),
#             showgrid=False,
#             showline=True,
#             linecolor='black',
#             automargin=True,
#             rangemode='nonnegative',
#             fixedrange=True,
#             hoverformat='.1f',
#             range=[0,y_max]
#         ),
#         legend=dict(
#             bgcolor='rgba(0,0,0,0)',
#             font=dict(
#                 size=12
#             )
#         ),
#         plot_bgcolor='rgba(0,0,0,0)',
#         hovermode='x',
#         hoverlabel=dict(namelength=0),  # removes the trace title next to the hover label (shortens)
#     )
#
#     # creating the ethnicity bar plot
#     ethnicity_barplot = go.Figure()
#     y_max = dff_ethnicity.CASES[(dff_ethnicity['CASE_TYPE'].isin(['Partial Coverage', 'Complete Coverage'])) & (dff_ethnicity['DEMO_GROUP'] != 'CASES_UnknownEthnicity')].max()
#     y_max = 5 * math.ceil(y_max/5) # round to nearest 5
#     for i in ['Complete Coverage']:
#         ethnicity_barplot.add_trace(go.Bar(
#             x=dff_ethnicity.DEMO_GROUP[(dff_ethnicity['CASE_TYPE'] == i) & (dff_ethnicity['DEMO_GROUP'] != 'CASES_UnknownEthnicity')],
#             y=dff_ethnicity.CASES[(dff_ethnicity['CASE_TYPE'] == i) & (dff_ethnicity['DEMO_GROUP'] != 'CASES_UnknownEthnicity')],
#             name=i,
#             marker_color=ethnicity_colors[i],  # overrides the color of the bars
#             opacity=0.7,
#             text=dff_ethnicity.CASES[
#                 (dff_ethnicity['CASE_TYPE'] == i) & (dff_ethnicity['DEMO_GROUP'] != 'CASES_UnknownEthnicity')],
#             textposition='auto',
#             texttemplate='%{text:.1f}%',
#             hoverinfo='skip'
#
#         ))
#     ethnicity_barplot.update_layout(
#         margin=dict(
#             l=0,
#             r=0,
#             t=30,
#             b=50
#         ),
#         barmode='group',  # designates grouped bar plot
#         annotations=[
#             dict(
#                 x=1.04,
#                 y=0.6,
#                 xanchor='left',
#                 yanchor='top',
#                 xref='paper',
#                 yref='paper',
#                 align='left',
#                 showarrow=False,
#                 bgcolor='rgba(0,0,0,0)',
#                 text='Ethnicity was not <br>reported for <br>{:.1f}% of completely <br>vaccinated individuals.'.format(ethnicity_NA_comp)
#             )
#         ],
#         title=dict(
#             text='<b>{}</b>: Vaccination by Ethnicity'.format(dff_ethnicity['STATE_NAME'].unique()[0]),
#             font=dict(
#                 size=16
#             ),
#             yref='paper',  # sets plotting area height as y ref point
#             y=0.9,
#             yanchor='bottom',  # ref point on title for what sits at y
#             pad={'t': 20, 'b': 35, 'l': 40, 'r': 0}
#         ),
#         xaxis=dict(
#             type='category',
#             showline=True,
#             linecolor='black',
#             tickmode='array',  # allows us to use custom tick text
#             tickvals=[1,2],  # essential if we want custom text; denotes positions of tick labels
#             ticktext=['Hispanic', 'Not Hispanic'],  # sets custom group names along x axis
#             categoryorder='array',  # allows us to specify custom order
#             categoryarray=['NaN','CASES_Hispanic', 'CASES_NotHispanic'],  # sets custom order of group names
#             fixedrange=True,
#             range=[-0.5,5]  # need -0.5 to make sure first bar isn't cut off
#
#         ),
#         yaxis=dict(
#             type='linear',
#             ticks='outside',
#             title=dict(
#                 text='Vaccination Coverage in Group (%)',
#                 font=dict(
#                     size=12
#                 )
#             ),
#             showgrid=False,
#             showline=True,
#             linecolor='black',
#             automargin=True,
#             rangemode='nonnegative',
#             fixedrange=True,
#             hoverformat='.1f',
#             range=[0,y_max]
#         ),
#         legend=dict(
#             bgcolor='rgba(0,0,0,0)',
#             font=dict(
#                 size=12
#             )
#         ),
#         plot_bgcolor='rgba(0,0,0,0)',
#         hovermode='x',
#         hoverlabel=dict(namelength=0),  # removes the trace title next to the hover label (shortens)
#     )
#
#     return race_barplot, ethnicity_barplot

#-----------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':
    app.run_server()
