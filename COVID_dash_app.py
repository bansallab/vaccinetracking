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

# from timeit import default_timer as timer

# import time
# from concurrent.futures import ThreadPoolExecutor

#-----------------------------------------------------------------------------------------------------------------------
# Read in data and modifications

# Geojson data with FIPS codes for county
with urlopen('https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json') as response:
    counties = json.load(response)

# vacc data
county_daily_total = pd.read_csv('vacc_data/data_master_county.csv', parse_dates=['DATE'])  # read data
# county_daily_total['DATE'] = pd.to_datetime(county_daily_total['DATE'])  # convert date to datetime object

state_demo = pd.read_csv('vacc_data/data_master_demo.csv', parse_dates=['DATE'])  # read state demographic data
# state_demo['DATE'] = pd.to_datetime(state_demo['DATE'])  # convert to datetime obj

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

# map function to precompute outputs
def US_choropleth(coverage_sel):
    county_daily_total_choro = county_daily_total[county_daily_total['CASE_TYPE'] == coverage_sel]

    val_max = county_daily_total_choro.CASES.max()
    val_90 = np.percentile(list(county_daily_total_choro.CASES), 90) / val_max
    val_92 = np.percentile(list(county_daily_total_choro.CASES), 92) / val_max
    val_94 = np.percentile(list(county_daily_total_choro.CASES), 94) / val_max
    val_96 = np.percentile(list(county_daily_total_choro.CASES), 96) / val_max
    val_15 = np.percentile(list(county_daily_total_choro.CASES), 15) / val_max
    val_30 = np.percentile(list(county_daily_total_choro.CASES), 30) / val_max
    val_45 = np.percentile(list(county_daily_total_choro.CASES), 45) / val_max
    val_60 = np.percentile(list(county_daily_total_choro.CASES), 60) / val_max
    val_75 = np.percentile(list(county_daily_total_choro.CASES), 75) / val_max

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
                        custom_data=['COUNTY_NAME', 'STATE_NAME', 'GEOFLAG', 'DATE'],
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
                      hovertemplate='<b>%{customdata[0]}, %{customdata[1]}</b><br>Coverage: %{z:.1f}%<br>Scale of data: %{customdata[2]}<br>Date: %{customdata[3]|%d %b %Y}'
                      )
    # dash.callback_context.record_timing('updt_trace', timer() - start_5, '5th task')

    # start_6 = timer()
    # 5a5a5a is a slightly lighter shade of gray than above
    fig.update_geos(showsubunits=True, subunitcolor='#5a5a5a')  # hacky: effectively controls state borders

    # dash.callback_context.record_timing('updt_geos', timer() - start_6, '6th task')
    return fig

# define the pre-computed maps
partial_map = US_choropleth('Partial Coverage')
complete_map = US_choropleth('Complete Coverage')

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
                html.P('Hover over a county to see vaccination coverage and the source of the data (state or county).'),
                html.P('Click on a state to see vaccination coverage by demography (where available).',
                       className='mb-0')
            ],
            id='alert-fade',
            dismissable=True,
            is_open=True,
            color='secondary'
        )
    ]
)

# radio buttons row
row_1 = dbc.Row(
        children=[
            dbc.Col(
                children=[
                    html.Div(
                        dcc.RadioItems(
                            id='coverage-buttons',
                            options=[
                                {'label': 'Partial vaccination coverage', 'value': 'Partial Coverage'},
                                {'label': 'Complete vaccination coverage', 'value': 'Complete Coverage'}
                            ],
                            value='Partial Coverage',
                            labelStyle={'display': 'block'}
                        )
                    )
                ], width={'size': 6, 'offset': 3}, className='h-100'
            ),
        ], justify='left', no_gutters=True
    )

# row for map
row_2 = dbc.Row(
    children=[
        dbc.Col(
            children=[
                dbc.Spinner(
                    color='secondary',
                    children=[
                        html.Div(dcc.Graph(
                            id='US-choropleth',
                            # figure=US_choropleth(),
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
            ], width={'size': 8, 'offset': 2}, className='h-100'  # , style={'background-color': 'black'}
        ),
        dbc.Col(
            children=[
                modal,
                html.Div(
                    alert
                    # dbc.Toast(
                    #     [
                    #         html.P(
                    #             'Hover over a county to see vaccination coverage and the source of the data (state or county).'),
                    #         html.P('Click on a state to see vaccination coverage by demography (where available).',
                    #                className='mb-0')
                    #     ],
                    #     id='instruction-toast',
                    #     header='Tips',
                    #     dismissable=True
                    # )
                )
            ], width=2  # , style={'background-color': 'orange'}
        )
    ], justify='left', no_gutters=True  # , className='h-50'
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
    ], justify='around', align='center', no_gutters=True
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
    ], justify='around', align='center', no_gutters=True
)

app.layout = dbc.Container([row_1, row_2, row_3, row_4], fluid=True)  # explicitly give layout

# define multi thread executor
# executor = ThreadPoolExecutor(max_workers=1)
# executor.submit(get_new_data_every)
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

# callback to hide blank map when loading
# @app.callback(
#     Output('map-div', 'style'),
#     [Input('US-choropleth', 'figure')])
# def empty_map(fig):
#     if fig is None:
#         return dict(display='none')
#     else:
#         return dict()

# callback for updating choropleth depending on coverage selection
@app.callback(
    Output('US-choropleth', 'figure'),
    [Input('coverage-buttons', 'value')])
# function for plotting base US choropleth
def update_choropleth(button_value):
    # uses precomputed map data rather than computing on the fly
    if button_value == 'Partial Coverage':
        return partial_map
    else:
        return complete_map

# callback for updating bar plots depending on state clicked
@app.callback(
    [Output('age-bar', 'figure'),
     Output('race-bar', 'figure'),
     Output('gender-bar', 'figure'),
     Output('ethnicity-bar', 'figure')],
    [Input('US-choropleth', 'clickData')])
def update_bar_plots(US_choro_clickData):
    last_triggered_val = dash.callback_context.triggered[0]['value']  # assigns variable to clickData info

    age_class_list = ['CASES_Child', 'CASES_Adult', 'CASES_Elderly', 'CASES_UnknownAge']
    race_class_list = ['CASES_White', 'CASES_Black', 'CASES_Asian', 'CASES_Native', 'CASES_Pacific', 'CASES_UnknownRace']
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

    # case for when user hasn't clicked a county yet; Nebraska default, hidden
    else:
        dff_age = state_demo[(state_demo['STATE_NAME'] == 'Nebraska') & (state_demo['DEMO_GROUP'].isin(age_class_list))]
        dff_race = state_demo[(state_demo['STATE_NAME'] == 'Nebraska') & (state_demo['DEMO_GROUP'].isin(race_class_list))]
        dff_gender = state_demo[(state_demo['STATE_NAME'] == 'Nebraska') & (state_demo['DEMO_GROUP'].isin(gender_class_list))]
        dff_ethnicity = state_demo[(state_demo['STATE_NAME'] == 'Nebraska') & (state_demo['DEMO_GROUP'].isin(ethnicity_class_list))]

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
    y_max = dff_age.CASES[(dff_age['CASE_TYPE'].isin(['Partial Coverage', 'Complete Coverage'])) & (dff_age['DEMO_GROUP'] != 'CASES_UnknownAge')].max()
    y_max = 5 * math.ceil(y_max/5) # round to nearest 5
    for i in ['Partial Coverage', 'Complete Coverage']:
        age_barplot.add_trace(go.Bar(
            x=dff_age.DEMO_GROUP[(dff_age['CASE_TYPE'] == i) & (dff_age['DEMO_GROUP'] != 'CASES_UnknownAge')],
            y=dff_age.CASES[(dff_age['CASE_TYPE'] == i) & (dff_age['DEMO_GROUP'] != 'CASES_UnknownAge')],
            name=i,
            marker_color=age_colors[i],  # overrides the color of the bars
            opacity=0.7,
            text=dff_age.CASES[(dff_age['CASE_TYPE'] == i) & (dff_age['DEMO_GROUP'] != 'CASES_UnknownAge')],
            textposition='auto',
            texttemplate='%{text:.1f}%',
            hoverinfo='skip',
            #width = [0.3,0.3, 0.3]
        ))
    age_barplot.update_layout(
        margin=dict(
            l=0,
            r=0,
            t=30,
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
            pad={'t': 20, 'b': 35, 'l': 40, 'r': 0}
        ),
        xaxis=dict(
            type='category',
            showline=True,
            linecolor='black',
            tickmode='array',  # allows us to use custom tick text
            tickvals=[1, 2, 3],  # essential if we want custom text; denotes positions of tick labels
            ticktext=['Children', 'Adults', 'Older Adults'],  # sets custom group names along x axis
            categoryorder='array',  # allows us to specify custom order
            categoryarray=['NaN','CASES_Child', 'CASES_Adult', 'CASES_Elderly'],  # sets custom order of group names
            fixedrange=True,
            range=[-0.5,5]  # need -0.5 to make sure first bar isn't cut off
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
            hoverformat='.1f',
            range=[0,y_max]
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
    y_max = dff_race.CASES[(dff_race['CASE_TYPE'].isin(['Partial Coverage', 'Complete Coverage'])) & (dff_race['DEMO_GROUP'] != 'CASES_UnknownRace')].max()
    y_max = 5 * math.ceil(y_max/5) # round to nearest 5
    for i in ['Partial Coverage', 'Complete Coverage']:
        race_barplot.add_trace(go.Bar(
            x=dff_race.DEMO_GROUP[(dff_race['CASE_TYPE'] == i) & (dff_race['DEMO_GROUP'] != 'CASES_UnknownRace')],
            y=dff_race.CASES[(dff_race['CASE_TYPE'] == i) & (dff_race['DEMO_GROUP'] != 'CASES_UnknownRace')],
            name=i,
            marker_color=race_colors[i],  # overrides the color of the bars
            opacity=0.7,
            text=dff_race.CASES[(dff_race['CASE_TYPE'] == i) & (dff_race['DEMO_GROUP'] != 'CASES_UnknownRace')],
            textposition='auto',
            texttemplate='%{text:.1f}%',
            hoverinfo='skip',
            #width = [0.3, 0.3, 0.3, 0.3, 0.3, 0.3]
        ))
    race_barplot.update_layout(
        margin=dict(
            l=0,
            r=0,
            t=30,
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
                text='Race was other/<br>unknown for {:.1f}% of <br>partially vaccinated and <br>{:.1f}% of completely <br>vaccinated individuals.'.format(race_NA_part, race_NA_comp)
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
            pad={'t': 20, 'b': 35, 'l': 40, 'r': 0}
        ),
        xaxis=dict(
            type='category',
            showline=True,
            linecolor='black',
            tickmode='array',  # allows us to use custom tick text
            tickvals=[0, 1, 2, 3, 4],  # essential if we want custom text; denotes positions of tick labels
            ticktext=['White', 'Black', 'Asian', 'Native American', 'Pacific Islander'],  # sets custom group names along x axis
            categoryorder='array',  # allows us to specify custom order
            categoryarray=['CASES_White', 'CASES_Black', 'CASES_Asian', 'CASES_Native', 'CASES_Pacific'],  # sets custom order of group names
            fixedrange=True,
            range=[-0.5,5]  # need -0.5 to make sure first bar isn't cut off
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
            hoverformat='.1f',
            range=[0,y_max]
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
    y_max = dff_gender.CASES[(dff_gender['CASE_TYPE'].isin(['Partial Coverage', 'Complete Coverage'])) & (dff_gender['DEMO_GROUP'] != 'CASES_UnknownGender')].max()
    y_max = 5 * math.ceil(y_max/5) # round to nearest 5
    for i in ['Partial Coverage', 'Complete Coverage']:
        gender_barplot.add_trace(go.Bar(
            x=dff_gender.DEMO_GROUP[(dff_gender['CASE_TYPE'] == i) & (dff_gender['DEMO_GROUP'] != 'CASES_UnknownGender')],
            y=dff_gender.CASES[(dff_gender['CASE_TYPE'] == i) & (dff_gender['DEMO_GROUP'] != 'CASES_UnknownGender')],
            name=i,
            marker_color=gender_colors[i],  # overrides the color of the bars
            opacity=0.7,
            text=dff_gender.CASES[(dff_gender['CASE_TYPE'] == i) & (dff_gender['DEMO_GROUP'] != 'CASES_UnknownGender')],
            textposition='auto',
            texttemplate='%{text:.1f}%',
            hoverinfo='skip',
            #width = [0.3, 0.3]
        ))
    gender_barplot.update_layout(
        margin=dict(
            l=0,
            r=0,
            t=30,
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
            pad={'t': 20, 'b': 35, 'l': 40, 'r': 0}
        ),
        xaxis=dict(
            type='category',
            showline=True,
            linecolor='black',
            tickmode='array',  # allows us to use custom tick text
            tickvals=[1,2],  # essential if we want custom text; denotes positions of tick labels
            ticktext=['Female', 'Male'],  # sets custom group names along x axis
            categoryorder='array',  # allows us to specify custom order
            categoryarray=['NaN', 'CASES_Female', 'CASES_Male'],  # sets custom order of group names
            fixedrange=True,
            range=[-0.5,5]  # need -0.5 to make sure first bar isn't cut off

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
            hoverformat='.1f',
            range=[0,y_max]
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
    y_max = dff_ethnicity.CASES[(dff_ethnicity['CASE_TYPE'].isin(['Partial Coverage', 'Complete Coverage'])) & (dff_ethnicity['DEMO_GROUP'] != 'CASES_UnknownEthnicity')].max()
    y_max = 5 * math.ceil(y_max/5) # round to nearest 5
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
            texttemplate='%{text:.1f}%',
            hoverinfo='skip'

        ))
    ethnicity_barplot.update_layout(
        margin=dict(
            l=0,
            r=0,
            t=30,
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
            pad={'t': 20, 'b': 35, 'l': 40, 'r': 0}
        ),
        xaxis=dict(
            type='category',
            showline=True,
            linecolor='black',
            tickmode='array',  # allows us to use custom tick text
            tickvals=[1,2],  # essential if we want custom text; denotes positions of tick labels
            ticktext=['Hispanic', 'Not Hispanic'],  # sets custom group names along x axis
            categoryorder='array',  # allows us to specify custom order
            categoryarray=['NaN','CASES_Hispanic', 'CASES_NotHispanic'],  # sets custom order of group names
            fixedrange=True,
            range=[-0.5,5]  # need -0.5 to make sure first bar isn't cut off

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
            hoverformat='.1f',
            range=[0,y_max]
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

#-----------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':
    app.run_server()
