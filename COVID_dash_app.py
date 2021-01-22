import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

import plotly.express as px
import plotly.graph_objects as go
from urllib.request import urlopen

import json

import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State

# import time
# from concurrent.futures import ThreadPoolExecutor

##########################################################################################################
# Read in data and modifications

# Geojson data with FIPS codes for county
with urlopen('https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json') as response:
    counties = json.load(response)

# vacc data
county_daily_total = pd.read_csv('vacc_data/data_master_county.csv')  # read data
#county_daily_total = pd.read_csv('https://www.dropbox.com/s/noolrmta6qhla1c/data_master_county.csv?dl=1')
county_daily_total['DATE'] = pd.to_datetime(county_daily_total['DATE'])  # convert date to datetime object

state_demo = pd.read_csv('vacc_data/data_master_demo.csv')  # read state demographic data
#state_demo = pd.read_csv('https://www.dropbox.com/s/21t09561e1dilno/data_master_demo.csv?dl=1')
state_demo['DATE'] = pd.to_datetime(state_demo['DATE'])  # convert to datetime obj

# function to zero pad county FIPS codes
def pad_fips_county(x):
    return str(int(x)).zfill(5)

def pad_fips_state(x):
    return str(int(x)).zfill(2)

# zero padding FIPS codes
county_daily_total['COUNTY'] = county_daily_total['COUNTY'].apply(pad_fips_county)
county_daily_total['STATE'] = county_daily_total['STATE'].apply(pad_fips_state)
state_demo['STATE'] = state_demo['STATE'].apply(pad_fips_state)

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

# static choropleth function (no dropdown)
def US_choropleth():
    county_daily_total_choro = county_daily_total[county_daily_total['CASE_TYPE'] == 'Partial Coverage']
    #max_color = round(np.percentile(list(county_daily_total_choro.CASES), 95))
    #print(max_color)
    
    # define custom color scale for choropleth
    # custom_colorscale = [[0.0, '#d2dce6'],
    #                      [0.1, '#bbcad9'],
    #                      [0.2, '#a4b8cc'],
    #                      [0.3, '#8ea7c0'],
    #                      [0.4, '#7795b3'],
    #                      [0.5, '#6083a6'],
    #                      [0.6, '#497199'],
    #                      [0.7, '#33608d'],
    #                      [0.8, '#1c4e80'],
    #                      [0.9, '#194673'],
    #                      [1.0, '#163e66']]

    custom_colorscale = [[0.0, '#e8edf2'],
                         [0.1, '#d2dce6'],
                         [0.2, '#bbcad9'],
                         [0.3, '#a4b8cc'],
                         [0.4, '#8ea7c0'],
                         [0.5, '#7795b3'],
                         [0.6, '#6083a6'],
                         [0.7, '#33608d'],
                         [0.8, '#1c4e80'],
                         [0.9, '#194673'],
                         [1.0, '#163e66']]

    fig = px.choropleth(county_daily_total_choro,
                        geojson=counties,
                        locations='COUNTY',
                        color='CASES',
                        color_continuous_scale=custom_colorscale,
                        range_color=[0, 7],  # restrict colorbar range so that more color variation shows
                        scope='usa',
                        custom_data=['COUNTY_NAME', 'STATE_NAME', 'CASES', 'GEOFLAG', 'DATE'],  # data available for hover
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
                      ),
                      # map annotation for when dashboard data were updated/latest date in the sheet
                      # annotations=[
                      #     dict(
                      #         x=1,
                      #         y=0,
                      #         xanchor='right',
                      #         yanchor='bottom',
                      #         xref='paper',
                      #         yref='paper',
                      #         align='left',
                      #         showarrow=False,
                      #         bgcolor='rgba(0,0,0,0)',
                      #         text='Latest date: {:%d %b %Y}'.format(county_daily_total_choro['DATE'].max())
                      #     )
                      # ]
                      )
    fig.update_coloraxes(colorbar_title_font=dict(size=14))
    fig.update_traces(marker_line_width=0.3,  # controls county border line width
                      marker_opacity=0.85,  # changes fill color opacity to let state borders through
                      marker_line_color='#262626',  # controls county border color; needs to be darker than "states"
                      # denotes custom template for what hover text should say
                      hovertemplate='<br>'.join([
                          '<b>%{customdata[0]}, %{customdata[1]}</b>',
                          'Coverage: %{customdata[2]:.1f}%',
                          'Scale of data: %{customdata[3]}',
                          'Date: %{customdata[4]|%d %b %Y}'
                      ]))
    # 5a5a5a is a slightly lighter shade of gray than above
    fig.update_geos(showsubunits=True, subunitcolor='#5a5a5a')  # hacky: effectively controls state borders
    return fig

# define app layout as a function
def make_layout():
    # row for title, dropdown
    # row_1 = dbc.Row(
    #     children=[
    #         dbc.Col(
    #             children=[
    #                 # map title
    #                 # html.Div(children='US Vaccination Coverage', style={'font-weight': 'bold', 'font-size': 20}),
    #                 # dropdown menu
    #                 html.Div(
    #                     dcc.Dropdown(
    #                         id='coverage-dropdown',
    #                         options=[
    #                             {
    #                                 'label': 'Partial vaccination coverage: proportion of population vaccinated with 1 dose',
    #                                 'value': 'Partial Coverage'},
    #                             {
    #                                 'label': 'Complete vaccination coverage: proportion of population vaccinated with 2 doses',
    #                                 'value': 'Complete Coverage'}
    #                         ],
    #                         value='Partial Coverage',
    #                         clearable=False,
    #                         searchable=False
    #                     ), style={'margin-bottom': 0}  # dropdown styling
    #                 ),
    #             ], width={'size': 4, 'offset': 2}, className='h-100'
    #             # column width, height should be 100% of the row height
    #         )
    #     ], justify='left', no_gutters=True  # justify elements in row, height of row (h-70 doesn't exist)
    # )

    # warning modal
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

    # row for map
    row_2 = dbc.Row(
        children=[
            dbc.Col(
                children=[
                    # dcc.Store(id='data-memory', storage_type='session'),
                    # html.Div(id='hidden-div', style={'display': 'none'}),
                    dcc.Graph(
                        id='US-choropleth',
                        figure=US_choropleth(),
                        style={'height': '100%'},  # seems to control graph height within the row?
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
                    )], width={'size': 8, 'offset': 2}, className='h-100'  # , style={'background-color': 'black'}
            ),
            dbc.Col(
                children=[
                    modal,
                    html.Div(
                        dbc.Toast(
                            [
                                html.P(
                                    'Hover over a county to see vaccination coverage and the source of the data (state or county).'),
                                html.P('Click on a state to see vaccination coverage by demography (where available).',
                                       className='mb-0')
                            ],
                            id='instruction-toast',
                            header='Tips',
                            dismissable=True
                        )
                        # dbc.Alert(
                        #     [
                        #         html.P('Hover over a county to see vaccination coverage and the source of the data (state or county).'),
                        #         html.P('Click on a state to see vaccination coverage by demography (where available).', className='mb-0')
                        #     ],
                        #     id='instruction-alert',
                        #     color='secondary',
                        #     dismissable=True,
                        #     is_open=True
                        # )
                    )
                ], width=2  # , style={'background-color': 'orange'}
            )
        ], justify='left', no_gutters=True, className='h-50'
        # justify elements in a row, height of row restricted to 75%
    )

    # row for barplots
    row_3 = dbc.Row(
        children=[
            dbc.Col([
                dbc.Fade(
                    dcc.Graph(
                        id='age-bar',
                        config={'displayModeBar': False},
                        className='h-100'
                    ),
                    id='age-fade',
                    is_in=False
                )], width=12, lg=5, className='h-100'  # , style={'background-color': 'green'}
            ),
            dbc.Col(
                dbc.Fade(
                    dcc.Graph(
                        id='gender-bar',
                        config={'displayModeBar': False},
                        className='h-100'
                    ),
                    id='gender-fade',
                    is_in=False
                ), width=12, lg=5, className='h-100'  # , style={'background-color': 'cyan'}
            )
        ], justify='around', align='center'
    )

    row_4 = dbc.Row(
        children=[
            dbc.Col(
                dbc.Fade(
                    dcc.Graph(
                        id='race-bar',
                        config={'displayModeBar': False},
                        className='h-100'
                    ),
                    id='race-fade',
                    is_in=False
                ), width=12, lg=5, className='h-100'  # , style={'background-color': 'blue'}
            ),
            dbc.Col(
                dbc.Fade(
                    dcc.Graph(
                        id='ethnicity-bar',
                        config={'displayModeBar': False},
                        className='h-100'
                    ),
                    id='ethnicity-fade',
                    is_in=False
                ), width=12, lg=5, className='h-100'  # , style={'background-color': 'red'}
            )
        ], justify='around', align='center'
    )
    return dbc.Container([row_2, row_3, row_4], style={'height': '100vh'}, fluid=True)

# ----------------------------------------------------------------------------------------------------------------------
# initializes Dash app
#app = dash.Dash(__name__)
app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])  # uses standard bootswatch theme
server = app.server
# get_new_data()  # read data upon app initialization
app.layout = make_layout  # provide layout function

# define multi thread executor
# executor = ThreadPoolExecutor(max_workers=1)
# executor.submit(get_new_data_every)

# regular, non-function layout
# row for title, dropdown, and alert
# row_1 = dbc.Row(
#     children=[
#         dbc.Col(
#             children=[
#                 # map title
#                 html.Div(children='US Vaccination Coverage', style={'font-weight': 'bold', 'font-size': 20}),
#                 # dropdown menu
#                 html.Div(
#                     dcc.Dropdown(
#                         id='coverage-dropdown',
#                         options=[
#                             {'label': 'Partial vaccination coverage: proportion of population vaccinated with 1 dose',
#                              'value': 'Partial Coverage'},
#                             {'label': 'Complete vaccination coverage: proportion of population vaccinated with 2 doses',
#                              'value': 'Complete Coverage'}
#                         ],
#                         value='Partial Coverage',
#                         clearable=False,
#                         searchable=False
#                     ), style={'margin-bottom': 0}  # dropdown styling
#                 ),
#             ], width={'size': 4, 'offset': 2}, className='h-100'  # column width, height should be 100% of the row height
#         )
#     ], justify='left', no_gutters=True  # justify elements in row, height of row (h-70 doesn't exist)
# )

# warning modal
# modal = html.Div(
#     [
#         dbc.Modal(
#             [
#                 dbc.ModalHeader('Warning'),
#                 dbc.ModalBody('No demographic data available for this state. Please make a different selection.'),
#                 dbc.ModalFooter(
#                     dbc.Button('Close', id='close', className='ml-auto')
#                 )
#             ],
#             id='warning-modal',
#             backdrop=False
#         )
#     ]
# )
#
# # row for map
# row_2 = dbc.Row(
#     children=[
#         dbc.Col(
#             dbc.Spinner(
#                 size='lg',
#                 type='border',
#                 fullscreen=True,
#                 children=[dcc.Graph(
#                     id='US-choropleth',
#                     figure=US_choropleth(),
#                     style={'height': '100%'},  # seems to control graph height within the row?
#                     config={'modeBarButtonsToRemove': ['select2d',
#                                                        'lasso2d',
#                                                        'zoom2d',
#                                                        'autoScale2d',
#                                                        'toggleSpikelines',
#                                                        'toggleHover',
#                                                        'sendDataToCloud',
#                                                        'toImage',
#                                                        'hoverClosestGeo'],
#                             'scrollZoom': False,
#                             'displayModeBar': True,
#                             'displaylogo': False}
#                     )]), width={'size': 8, 'offset': 2}, className='h-100'#, style={'background-color': 'black'}
#         ),
#         dbc.Col(
#             children=[
#                 modal,
#                 html.Div(
#                     dbc.Toast(
#                         [
#                             html.P('Hover over a county to see vaccination coverage and the source of the data (state or county).'),
#                             html.P('Click on a state to see vaccination coverage by demography (where available).', className='mb-0')
#                         ],
#                         id='instruction-toast',
#                         header='Tips',
#                         dismissable=True
#                     )
#                     # dbc.Alert(
#                     #     [
#                     #         html.P('Hover over a county to see vaccination coverage and the source of the data (state or county).'),
#                     #         html.P('Click on a state to see vaccination coverage by demography (where available).', className='mb-0')
#                     #     ],
#                     #     id='instruction-alert',
#                     #     color='secondary',
#                     #     dismissable=True,
#                     #     is_open=True
#                     # )
#                 )
#             ], width=2#, style={'background-color': 'orange'}
#         )
#     ], justify='left', no_gutters=True, className='h-50'  # justify elements in a row, height of row restricted to 75%
# )
#
# # row for barplots
# row_3 = dbc.Row(
#     children=[
#         dbc.Col([
#             dbc.Fade(
#                 dcc.Graph(
#                     id='age-bar',
#                     config={'displayModeBar': False},
#                     className='h-100'
#                 ),
#                 id='age-fade',
#                 is_in=False
#             )], width=12, lg=5, className='h-100'#, style={'background-color': 'green'}
#         ),
#         dbc.Col(
#             dbc.Fade(
#                 dcc.Graph(
#                     id='gender-bar',
#                     config={'displayModeBar': False},
#                     className='h-100'
#                 ),
#                 id='gender-fade',
#                 is_in=False
#             ), width=12, lg=5, className='h-100'#, style={'background-color': 'cyan'}
#         )
#     ], justify='around', align='center'
# )
#
# row_4 = dbc.Row(
#     children=[
#         dbc.Col(
#             dbc.Fade(
#                 dcc.Graph(
#                     id='race-bar',
#                     config={'displayModeBar': False},
#                     className='h-100'
#                 ),
#                 id='race-fade',
#                 is_in=False
#             ), width=12, lg=5, className='h-100'#, style={'background-color': 'blue'}
#         ),
#         dbc.Col(
#             dbc.Fade(
#                 dcc.Graph(
#                     id='ethnicity-bar',
#                     config={'displayModeBar': False},
#                     className='h-100'
#                 ),
#                 id='ethnicity-fade',
#                 is_in=False
#             ), width=12, lg=5, className='h-100'#, style={'background-color': 'red'}
#         )
#     ], justify='around', align='center'
# )
#
# # sets full app container; full screen width and length
# app.layout = dbc.Container([row_2, row_3, row_4], style={'height': '100vh'}, fluid=True)

#-----------------------------------------------------------------------------------------------------------------------
# CALLBACK STRUCTURE

# callback for looking at callback_context contents
# @app.callback(
#     Output('display-selected-values2', 'children'),
#     [Input('US-choropleth', 'clickData')])
# def display_trigger(US_choro_clickData):
#     last_triggered = dash.callback_context.triggered[0]['prop_id']
#     last_triggered_val = dash.callback_context.triggered[0]['value']
#     return json.dumps(dash.callback_context.triggered)

# callback for modal and fade revealing bar plots
@app.callback(
    [Output('age-fade', 'is_in'),
     Output('gender-fade', 'is_in'),
     Output('race-fade', 'is_in'),
     Output('ethnicity-fade', 'is_in'),
     Output('warning-modal', 'is_open')],
    [Input('US-choropleth', 'clickData'), Input('close', 'n_clicks')],
    [State('age-fade', 'is_in'), State('warning-modal', 'is_open')])
def update_collapse(US_choro_clickData, n, is_in, is_open):
    last_triggered_val = dash.callback_context.triggered[0]['value']  # assigns variable to clickData info
    unknown_list = ['CASES_UnknownGender','CASES_UnknownRace','CASES_UnknownEthnicity','CASES_UnknownAge']

    # if a county/state has been clicked
    if last_triggered_val:
        fips_code = US_choro_clickData['points'][0]['location']  # grabs the county FIPS code from clickData
        fips_code = fips_code[:2]  # grab the state part of FIPS code

        # check if any state demographic data available
        if state_demo.CASES[(state_demo['STATE'] == fips_code) & (~state_demo['DEMO_GROUP'].isin(unknown_list))].sum() == 0 and not n:
            return False, False, False, False, not is_open
        if state_demo.CASES[(state_demo['STATE'] == fips_code) & (~state_demo['DEMO_GROUP'].isin(unknown_list))].sum() == 0 and n:
            return False, False, False, False, not is_open
        else:
            return True, True, True, True, is_open
    else:
        return is_in, is_in, is_in, is_in, is_open

# callback for updating choropleth depending on coverage selection
# @app.callback(
#     Output('US-choropleth', 'figure'),
#     [Input('coverage-dropdown', 'value')])
# # function for plotting base US choropleth
# def update_choropleth(dropdown_value):
#     county_daily_total_choro = county_daily_total[county_daily_total['CASE_TYPE'] == dropdown_value]
#
#     # define custom color scale for choropleth
#     # custom_colorscale = [[0.0, '#d2dce6'],
#     #                      [0.1, '#bbcad9'],
#     #                      [0.2, '#a4b8cc'],
#     #                      [0.3, '#8ea7c0'],
#     #                      [0.4, '#7795b3'],
#     #                      [0.5, '#6083a6'],
#     #                      [0.6, '#497199'],
#     #                      [0.7, '#33608d'],
#     #                      [0.8, '#1c4e80'],
#     #                      [0.9, '#194673'],
#     #                      [1.0, '#163e66']]
#
#     custom_colorscale = [[0.0, '#e8edf2'],
#                          [0.1, '#d2dce6'],
#                          [0.2, '#bbcad9'],
#                          [0.3, '#a4b8cc'],
#                          [0.4, '#8ea7c0'],
#                          [0.5, '#7795b3'],
#                          [0.6, '#6083a6'],
#                          [0.7, '#33608d'],
#                          [0.8, '#1c4e80'],
#                          [0.9, '#194673'],
#                          [1.0, '#163e66']]
#
#     fig = px.choropleth(county_daily_total_choro,
#                         geojson=counties,
#                         locations='COUNTY',
#                         color='CASES',
#                         color_continuous_scale=custom_colorscale,
#                         range_color=[0, 7],  # restrict colorbar range so that more color variation shows
#                         scope='usa',
#                         custom_data=['COUNTY_NAME', 'STATE_NAME', 'CASES', 'GEOFLAG', 'DATE'],  # data available for hover
#                         )
#     fig.update_layout(margin=dict(b=0, t=0, l=0, r=0),  # sets the margins of the plot w/in its div
#                       # controls appearance of hover label
#                       hoverlabel=dict(
#                           bgcolor='white',
#                           font_size=16
#                       ),
#                       # controls appearance of color bar & title
#                       coloraxis_colorbar=dict(
#                           lenmode='pixels', len=500,
#                           thicknessmode='pixels', thickness=40,
#                           ticks='outside',
#                           title='Vaccination <br>coverage (%)'
#                       ),
#                       # modifications to the map appearance (special geo settings)
#                       geo=dict(
#                           showlakes=False,
#                           showland=True, landcolor='white'
#                       ),
#                       # map annotation for when dashboard data were updated/latest date in the sheet
#                       # annotations=[
#                       #     dict(
#                       #         x=1,
#                       #         y=0,
#                       #         xanchor='right',
#                       #         yanchor='bottom',
#                       #         xref='paper',
#                       #         yref='paper',
#                       #         align='left',
#                       #         showarrow=False,
#                       #         bgcolor='rgba(0,0,0,0)',
#                       #         text='Latest date: {:%d %b %Y}'.format(county_daily_total_choro['DATE'].max())
#                       #     )
#                       # ]
#                       )
#     fig.update_coloraxes(colorbar_title_font=dict(size=14))
#     fig.update_traces(marker_line_width=0.3,  # controls county border line width
#                       marker_opacity=0.85,  # changes fill color opacity to let state borders through
#                       marker_line_color='#262626',  # controls county border color; needs to be darker than "states"
#                       # denotes custom template for what hover text should say
#                       hovertemplate='<br>'.join([
#                           '<b>%{customdata[0]}, %{customdata[1]}</b>',
#                           'Coverage: %{customdata[2]:.1f}%',
#                           'Scale of data: %{customdata[3]}',
#                           'Date: %{customdata[4]|%d %b %Y}'
#                       ]))
#     # 5a5a5a is a slightly lighter shade of gray than above
#     fig.update_geos(showsubunits=True, subunitcolor='#5a5a5a')  # hacky: effectively controls state borders
#     return fig

# callback for updating bar plots depending on county clicked
@app.callback(
    [Output('age-bar', 'figure'),
     Output('race-bar', 'figure'),
     Output('gender-bar', 'figure'),
     Output('ethnicity-bar', 'figure')],
    [Input('US-choropleth', 'clickData')])
def update_bar_plots(US_choro_clickData):
    last_triggered_val = dash.callback_context.triggered[0]['value']  # assigns variable to clickData info

    age_class_list = ['CASES_Child', 'CASES_Adult', 'CASES_Elderly', 'CASES_UnknownAge']
    race_class_list = ['CASES_White', 'CASES_Black', 'CASES_Asian', 'CASES_Native', 'CASES_Pacific', 'CASES_OtherRace', 'CASES_UnknownRace']
    gender_class_list = ['CASES_Male', 'CASES_Female', 'CASES_UnknownGender']
    ethnicity_class_list = ['CASES_Hispanic', 'CASES_NotHispanic', 'CASES_UnknownEthnicity']

    # defines custom colors for the barplot
    gender_colors = {'Partial Coverage': '#b5d8c3', 'Complete Coverage': '#6ab187'}  # green
    race_colors = {'Partial Coverage': '#f5b5a3', 'Complete Coverage': '#ea6a47'}  # orange
    ethnicity_colors = {'Partial Coverage': '#c0b9d9', 'Complete Coverage': '#8172b3'}  # purple
    age_colors = {'Partial Coverage': '#c9bcb0', 'Complete Coverage': '#937860'}  # brown

    # case for when user clicks county
    if last_triggered_val:
        fips_code = US_choro_clickData['points'][0]['location']  # grabs the county FIPS code from clickData
        fips_code = fips_code[:2]  # grab the state part of FIPS code

        # subset main demo df by the selected state and the type of variable (age)
        dff_age = state_demo[(state_demo['STATE'] == fips_code) & (state_demo['DEMO_GROUP'].isin(age_class_list))]
        dff_race = state_demo[(state_demo['STATE'] == fips_code) & (state_demo['DEMO_GROUP'].isin(race_class_list))]
        dff_gender = state_demo[(state_demo['STATE'] == fips_code) & (state_demo['DEMO_GROUP'].isin(gender_class_list))]
        dff_ethnicity = state_demo[(state_demo['STATE'] == fips_code) & (state_demo['DEMO_GROUP'].isin(ethnicity_class_list))]

    # case for when user hasn't clicked a county yet; Nebraska default for now
    else:
        dff_age = state_demo[(state_demo['STATE_NAME'] == 'Nebraska') & (state_demo['DEMO_GROUP'].isin(age_class_list))]
        dff_race = state_demo[(state_demo['STATE_NAME'] == 'Nebraska') & (state_demo['DEMO_GROUP'].isin(race_class_list))]
        dff_gender = state_demo[(state_demo['STATE_NAME'] == 'Nebraska') & (state_demo['DEMO_GROUP'].isin(gender_class_list))]
        dff_ethnicity = state_demo[(state_demo['STATE_NAME'] == 'Nebraska') & (state_demo['DEMO_GROUP'].isin(ethnicity_class_list))]

        # for now
        fips_code = '31'

    age_NA_part = dff_age.CASES[(dff_age['DEMO_GROUP'] == 'CASES_UnknownAge') & (
            dff_age['CASE_TYPE'] == 'Partial Coverage')].unique()[0]
    age_NA_comp = dff_age.CASES[(dff_age['DEMO_GROUP'] == 'CASES_UnknownAge') & (
            dff_age['CASE_TYPE'] == 'Complete Coverage')].unique()[0]
    race_NA_part = dff_race.CASES[(dff_race['DEMO_GROUP'] == 'CASES_UnknownRace') & (
            dff_race['CASE_TYPE'] == 'Partial Coverage')].unique()[0]
    race_NA_comp = dff_race.CASES[(dff_race['DEMO_GROUP'] == 'CASES_UnknownRace') & (
            dff_race['CASE_TYPE'] == 'Complete Coverage')].unique()[0]
    gender_NA_part = dff_gender.CASES[(dff_gender['DEMO_GROUP'] == 'CASES_UnknownGender') & (
                dff_gender['CASE_TYPE'] == 'Partial Coverage')].unique()[0]
    gender_NA_comp = dff_gender.CASES[(dff_gender['DEMO_GROUP'] == 'CASES_UnknownGender') & (
                dff_gender['CASE_TYPE'] == 'Complete Coverage')].unique()[0]
    ethnicity_NA_part = dff_ethnicity.CASES[(dff_ethnicity['DEMO_GROUP'] == 'CASES_UnknownEthnicity') & (
                dff_ethnicity['CASE_TYPE'] == 'Partial Coverage')].unique()[0]
    ethnicity_NA_comp = dff_ethnicity.CASES[(dff_ethnicity['DEMO_GROUP'] == 'CASES_UnknownEthnicity') & (
                dff_ethnicity['CASE_TYPE'] == 'Complete Coverage')].unique()[0]

    # creating the age bar plot
    age_barplot = go.Figure()
    for i in ['Partial Coverage', 'Complete Coverage']:
        age_barplot.add_trace(go.Bar(
            x=dff_age.DEMO_GROUP[(dff_age['CASE_TYPE'] == i) & (dff_age['DEMO_GROUP'] != 'CASES_UnknownAge')],
            y=dff_age.CASES[(dff_age['CASE_TYPE'] == i) & (dff_age['DEMO_GROUP'] != 'CASES_UnknownAge')],
            name=i,
            marker_color=age_colors[i],  # overrides the color of the bars
            opacity=0.7,
            text=dff_age.CASES[(dff_age['CASE_TYPE'] == i) & (dff_age['DEMO_GROUP'] != 'CASES_UnknownAge')],
            textposition='auto',
            texttemplate='%{text:.1f}%'
        ))
    age_barplot.update_layout(
        margin=dict(
            l=0,
            r=0,
            t=0,
            b=50
        ),
        barmode='group',  # designates grouped bar plot
        # manage special annotation attributes
        annotations=[
            dict(
                x=1.04,
                y=0.6,
                xanchor='left',
                yanchor='top',
                xref='paper',
                yref='paper',
                align='left',
                showarrow=False,
                bgcolor='rgba(0,0,0,0)',
                text='Age was not reported <br>for {:.1f}% of partially <br>vaccinated and {:.1f}% <br>of completely vaccinated <br>individuals.'.format(age_NA_part, age_NA_comp)
            )
        ],
        # manage title attributes
        title=dict(
            text='<b>{}</b>: Vaccination by Age'.format(dff_age['STATE_NAME'].unique()[0]),
            font=dict(
                size=16
            ),
            yref='paper',  # sets plotting area height as y ref point
            y=0.9,
            yanchor='bottom',  # ref point on title for what sits at y
            pad={'t':20, 'b':25, 'l':40, 'r':0}
        ),
        xaxis=dict(
            type='category',
            showline=True,
            linecolor='black',
            tickmode='array',  # allows us to use custom tick text
            tickvals=[0, 1, 2],  # essential if we want custom text; denotes positions of tick labels
            ticktext=['Children', 'Adults', 'Older Adults'],  # sets custom group names along x axis
            categoryorder='array',  # allows us to specify custom order
            categoryarray=['CASES_Child', 'CASES_Adult', 'CASES_Elderly'],  # sets custom order of group names
            fixedrange=True
        ),
        yaxis=dict(
            type='linear',
            ticks='outside',
            title=dict(
                text='Vaccination Coverage in Group (%)',
                font=dict(
                    size=12
                )
            ),
            showgrid=False,  # whether to show y axis grid lines
            showline=True,  # whether to show the y axis line
            linecolor='black',
            automargin=True,
            rangemode='nonnegative',
            fixedrange=True,
            hoverformat='.1f'
        ),
        legend=dict(
            bgcolor='rgba(0,0,0,0)',
            font=dict(
                size=12
            )
        ),
        plot_bgcolor='rgba(0,0,0,0)',
        hovermode='x',
        hoverlabel=dict(namelength=0),  # removes the trace title next to the hover label (shortens)
    )

    # creating the race bar plot
    race_barplot = go.Figure()
    for i in ['Partial Coverage', 'Complete Coverage']:
        race_barplot.add_trace(go.Bar(
            x=dff_race.DEMO_GROUP[(dff_race['CASE_TYPE'] == i) & (dff_race['DEMO_GROUP'] != 'CASES_UnknownRace')],
            y=dff_race.CASES[(dff_race['CASE_TYPE'] == i) & (dff_race['DEMO_GROUP'] != 'CASES_UnknownRace')],
            name=i,
            marker_color=race_colors[i],  # overrides the color of the bars
            opacity=0.7,
            text=dff_race.CASES[(dff_race['CASE_TYPE'] == i) & (dff_race['DEMO_GROUP'] != 'CASES_UnknownRace')],
            textposition='auto',
            texttemplate='%{text:.1f}%'
        ))
    race_barplot.update_layout(
        margin=dict(
            l=0,
            r=0,
            t=0,
            b=50
        ),
        barmode='group',  # designates grouped bar plot
        annotations=[
            dict(
                x=1.04,
                y=0.6,
                xanchor='left',
                yanchor='top',
                xref='paper',
                yref='paper',
                align='left',
                showarrow=False,
                bgcolor='rgba(0,0,0,0)',
                text='Race was not reported <br>for {:.1f}% of partially <br>vaccinated and {:.1f}% <br>of completely vaccinated <br>individuals.'.format(race_NA_part, race_NA_comp)
            )
        ],
        title=dict(
            text='<b>{}</b>: Vaccination by Race'.format(dff_age['STATE_NAME'].unique()[0]),
            font=dict(
                size=16
            ),
            yref='paper',  # sets plotting area height as y ref point
            y=0.9,
            yanchor='bottom',  # ref point on title for what sits at y
            pad={'t': 20, 'b': 25, 'l': 40, 'r': 0}
        ),
        xaxis=dict(
            type='category',
            showline=True,
            linecolor='black',
            tickmode='array',  # allows us to use custom tick text
            tickvals=[0, 1, 2, 3, 4, 5],  # essential if we want custom text; denotes positions of tick labels
            ticktext=['White', 'Black', 'Asian', 'Native American', 'Pacific Islander', 'Multiracial'],  # sets custom group names along x axis
            categoryorder='array',  # allows us to specify custom order
            categoryarray=['CASES_White', 'CASES_Black', 'CASES_Asian', 'CASES_Native', 'CASES_Pacific', 'CASES_OtherRace'],  # sets custom order of group names
            fixedrange=True
        ),
        yaxis=dict(
            type='linear',
            ticks='outside',
            title=dict(
                text='Vaccination Coverage in Group (%)',
                font=dict(
                    size=12
                )
            ),
            showgrid=False,
            showline=True,
            linecolor='black',
            automargin=True,
            rangemode='nonnegative',
            fixedrange=True,
            hoverformat='.1f'
        ),
        legend=dict(
            bgcolor='rgba(0,0,0,0)',
            font=dict(
                size=12
            )
        ),
        plot_bgcolor='rgba(0,0,0,0)',
        hovermode='x',
        hoverlabel=dict(namelength=0),  # removes the trace title next to the hover label (shortens)
    )

    # creating the gender bar plot
    gender_barplot = go.Figure()
    for i in ['Partial Coverage', 'Complete Coverage']:
        gender_barplot.add_trace(go.Bar(
            x=dff_gender.DEMO_GROUP[(dff_gender['CASE_TYPE'] == i) & (dff_gender['DEMO_GROUP'] != 'CASES_UnknownGender')],
            y=dff_gender.CASES[(dff_gender['CASE_TYPE'] == i) & (dff_gender['DEMO_GROUP'] != 'CASES_UnknownGender')],
            name=i,
            marker_color=gender_colors[i],  # overrides the color of the bars
            opacity=0.7,
            text=dff_gender.CASES[(dff_gender['CASE_TYPE'] == i) & (dff_gender['DEMO_GROUP'] != 'CASES_UnknownGender')],
            textposition='auto',
            texttemplate='%{text:.1f}%'
        ))
    gender_barplot.update_layout(
        margin=dict(
            l=0,
            r=0,
            t=0,
            b=50
        ),
        barmode='group',  # designates grouped bar plot
        annotations=[
            dict(
                x=1.04,
                y=0.6,
                xanchor='left',
                yanchor='top',
                xref='paper',
                yref='paper',
                align='left',
                showarrow=False,
                bgcolor='rgba(0,0,0,0)',
                text='Sex/Gender was not <br>reported for {:.1f}% of <br>partially vaccinated and <br>{:.1f}% of completely <br>vaccinated individuals.'.format(gender_NA_part, gender_NA_comp)
            )
        ],
        title=dict(
            text='<b>{}</b>: Vaccination by Sex/Gender'.format(dff_gender['STATE_NAME'].unique()[0]),
            font=dict(
                size=16
            ),
            yref='paper',  # sets plotting area height as y ref point
            y=0.9,
            yanchor='bottom',  # ref point on title for what sits at y
            pad={'t': 20, 'b': 25, 'l': 40, 'r': 0}
        ),
        xaxis=dict(
            type='category',
            showline=True,
            linecolor='black',
            tickmode='array',  # allows us to use custom tick text
            tickvals=[0, 1],  # essential if we want custom text; denotes positions of tick labels
            ticktext=['Female', 'Male'],  # sets custom group names along x axis
            categoryorder='array',  # allows us to specify custom order
            categoryarray=['CASES_Female', 'CASES_Male'],  # sets custom order of group names
            fixedrange=True
        ),
        yaxis=dict(
            type='linear',
            ticks='outside',
            title=dict(
                text='Vaccination Coverage in Group (%)',
                font=dict(
                    size=12
                )
            ),
            showgrid=False,
            showline=True,
            linecolor='black',
            automargin=True,
            rangemode='nonnegative',
            fixedrange=True,
            hoverformat='.1f'
        ),
        legend=dict(
            bgcolor='rgba(0,0,0,0)',
            font=dict(
                size=12
            )
        ),
        plot_bgcolor='rgba(0,0,0,0)',
        hovermode='x',
        hoverlabel=dict(namelength=0),  # removes the trace title next to the hover label (shortens)
    )

    # creating the ethnicity bar plot
    ethnicity_barplot = go.Figure()
    for i in ['Partial Coverage', 'Complete Coverage']:
        ethnicity_barplot.add_trace(go.Bar(
            x=dff_ethnicity.DEMO_GROUP[(dff_ethnicity['CASE_TYPE'] == i) & (dff_ethnicity['DEMO_GROUP'] != 'CASES_UnknownEthnicity')],
            y=dff_ethnicity.CASES[(dff_ethnicity['CASE_TYPE'] == i) & (dff_ethnicity['DEMO_GROUP'] != 'CASES_UnknownEthnicity')],
            name=i,
            marker_color=ethnicity_colors[i],  # overrides the color of the bars
            opacity=0.7,
            text=dff_ethnicity.CASES[
                (dff_ethnicity['CASE_TYPE'] == i) & (dff_ethnicity['DEMO_GROUP'] != 'CASES_UnknownEthnicity')],
            textposition='auto',
            texttemplate='%{text:.1f}%'
        ))
    ethnicity_barplot.update_layout(
        margin=dict(
            l=0,
            r=0,
            t=0,
            b=50
        ),
        barmode='group',  # designates grouped bar plot
        annotations=[
            dict(
                x=1.04,
                y=0.6,
                xanchor='left',
                yanchor='top',
                xref='paper',
                yref='paper',
                align='left',
                showarrow=False,
                bgcolor='rgba(0,0,0,0)',
                text='Ethnicity was not <br>reported for {:.1f}% of <br>partially vaccinated and <br>{:.1f}% of completely <br>vaccinated individuals.'.format(ethnicity_NA_part, ethnicity_NA_comp)
            )
        ],
        title=dict(
            text='<b>{}</b>: Vaccination by Ethnicity'.format(dff_ethnicity['STATE_NAME'].unique()[0]),
            font=dict(
                size=16
            ),
            yref='paper',  # sets plotting area height as y ref point
            y=0.9,
            yanchor='bottom',  # ref point on title for what sits at y
            pad={'t': 20, 'b': 25, 'l': 40, 'r': 0}
        ),
        xaxis=dict(
            type='category',
            showline=True,
            linecolor='black',
            tickmode='array',  # allows us to use custom tick text
            tickvals=[0, 1],  # essential if we want custom text; denotes positions of tick labels
            ticktext=['Hispanic', 'Not Hispanic'],  # sets custom group names along x axis
            categoryorder='array',  # allows us to specify custom order
            categoryarray=['CASES_Hispanic', 'CASES_NotHispanic'],  # sets custom order of group names
            fixedrange=True
        ),
        yaxis=dict(
            type='linear',
            ticks='outside',
            title=dict(
                text='Vaccination Coverage in Group (%)',
                font=dict(
                    size=12
                )
            ),
            showgrid=False,
            showline=True,
            linecolor='black',
            automargin=True,
            rangemode='nonnegative',
            fixedrange=True,
            hoverformat='.1f'
        ),
        legend=dict(
            bgcolor='rgba(0,0,0,0)',
            font=dict(
                size=12
            )
        ),
        plot_bgcolor='rgba(0,0,0,0)',
        hovermode='x',
        hoverlabel=dict(namelength=0),  # removes the trace title next to the hover label (shortens)
    )

    return age_barplot, race_barplot, gender_barplot, ethnicity_barplot

##########################################################################################################

if __name__ == '__main__':
    app.run_server(debug=True)
