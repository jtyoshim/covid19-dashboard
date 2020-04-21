import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import folium
from datetime import datetime as dt
import datetime
import math
pd.set_option('display.max_columns',50)

# external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

token = 'pk.eyJ1IjoianR5b3NoaW0iLCJhIjoiY2s5NmR0ZWJoMGpqazNucDJrY3EyOHVjdiJ9.l_asidm_Bb2M6F1KZnNBug'

app = dash.Dash(__name__)
colors = {
    'background': '#111111',
    'text': '#7FDBFF'
}

def gen_tab(scale,list_locations):
    return dcc.Tab(
        label=scale.capitalize()+'-Level Analysis',
        children = [
            html.Div(className='row div-row div-card', children = [
                html.Div(
                    className='one-third column',
                    children = [
                        html.H6('Select '+scale.capitalize()),
                        dcc.Dropdown(
                            id=scale+'-dropdown',
                            options=list_locations,
                            multi=True,
                            value=['US'],
                            style={
                                'backgroundColor':'#0B0C10',
                                'color':'#C5C6C7',
                            }
                        )
                    ]
                ),
                html.Div(
                    className='one-third column',
                    children = [
                        html.H6('Select Raw Or Normalized Data'),
                        dcc.RadioItems(
                            id=scale+'-radio',
                            className='radio',
                            options=[
                                {'label': 'Raw', 'value': 'Raw'}, 
                                {'label': 'Normalized', 'value': 'Norm'}
                            ],
                            value='Raw'
                        ) 
                    ]
                ),
                html.Div(
                    className='one-third column',
                    children=[
                        html.H6('Select Date Range'),
                        dcc.DatePickerRange(
                            id = scale+'-date-picker',
                            start_date='2020-01-22',
                            end_date=last_update_obj,
                            min_date_allowed = '2020-01-22',
                            max_date_allowed = last_update_obj+ datetime.timedelta(days=1),
                            calendar_orientation='horizontal',
                        )
                    ]
                )
            ]),
            html.Div(className='row div-row div-card', children = [
                dcc.Graph(id=scale+'-map',className='two-thirds column'),
                html.Div(className='one-third column', children = [
                    dash_table.DataTable(
                        id=scale+'-table',
                        sort_action="native",
                        sort_mode="multi",
                        style_header={
                            'backgroundColor':'#0B0C10',
                            'color':'#C5C6C7',
                            'border':'1px solid #7CD3F7'
                        },
                        style_data={
                            'backgroundColor':'#0B0C10',
                            'color':'#C5C6C7',
                            'border':'1px solid #7CD3F7'
                        },
                        page_size=12
                    )
                ])
            ]),
            html.Div(className='row div-row div-card', children = [
                html.Div(
                    className='one-half column',
                    children= [
                        dcc.Graph(id=scale+'-scatter')
                    ]
                ),
                html.Div(
                    className='one-half column',
                    children= [
                        dcc.Graph(id=scale+'-bar-daily')
                    ]
                )
            ]),
            html.Div(className='row div-row div-card', children = [
                html.Div(
                    className='one-half column',
                    children= [
                        dcc.Graph(id=scale+'-scatter-deaths')
                    ]
                ),
                html.Div(
                    className='one-half column',
                    children= [
                        dcc.Graph(id=scale+'-bar-deaths-daily')
                    ]
                )
            ]),
            html.Div(className='row div-row div-card', children = [
                html.Div(
                    className='one-half column',
                    children= [
                        dcc.Graph(id=scale+'-scatter-recovered')
                    ]
                ),
                html.Div(
                    className='one-half column',
                    children= [
                        dcc.Graph(id=scale+'-bar-recovered-daily')
                    ]
                )
            ])
        ]
    )

# Read in JHU Data from Github
df_covid19_confirmed_county = pd.read_csv('https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_US.csv')
df_covid19_confirmed_country = pd.read_csv('https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv')
df_covid19_deaths_county = pd.read_csv('https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_US.csv')
df_covid19_deaths_country = pd.read_csv('https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv')
df_covid19_recovered_country = pd.read_csv('https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_recovered_global.csv')
df_fips_lookup = pd.read_csv('https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/UID_ISO_FIPS_LookUp_Table.csv')
df_covid19_confirmed_state_us = df_covid19_confirmed_county.groupby(['Province_State','Country_Region']).sum().drop(columns=['UID','code3','FIPS']).reset_index().rename(columns={'Province_State':'Province/State','Country_Region':'Country/Region','Long_':'Long'})
df_covid19_deaths_state_us = df_covid19_deaths_county.groupby(['Province_State','Country_Region']).sum().drop(columns=['UID','code3','FIPS']).reset_index().rename(columns={'Province_State':'Province/State','Country_Region':'Country/Region','Long_':'Long'})
df_covid19_confirmed_country = pd.concat([df_covid19_confirmed_country,df_covid19_confirmed_state_us])
df_covid19_deaths_country = pd.concat([df_covid19_deaths_country,df_covid19_deaths_state_us])
# print(df_covid19_confirmed_state_us.head())

last_update = df_covid19_confirmed_country.columns[-1]
last_update_obj = dt.strptime(last_update,"%m/%d/%y").date()
last_update_str = dt.strftime(last_update_obj,"%Y-%m-%d")
# print(last_update_str)

# Create geographic input dropdowns for app
df_countries = df_fips_lookup[df_fips_lookup['Province_State'].isnull()]
df_states = df_fips_lookup[(df_fips_lookup['Admin2'].isnull()) & (df_fips_lookup['Province_State'].notnull())]
df_counties = df_fips_lookup[df_fips_lookup['Admin2'].notnull()]
df_countries['value'] = df_countries['Combined_Key']
df_countries['label'] = df_countries['Combined_Key']
df_states['value'] = df_states['Combined_Key']
df_states['label'] = df_states['Combined_Key']
df_counties['value'] = df_counties['Combined_Key']
df_counties['label'] = df_counties['Combined_Key']
list_countries = df_countries[['value','label']].to_dict('records')
list_states = df_states[['value','label']].to_dict('records')
list_counties = df_counties[['value','label']].to_dict('records')

agg_country_list = ['Australia','China','Canada']
for c in agg_country_list:
    temp = df_covid19_confirmed_country[df_covid19_confirmed_country['Country/Region']==c].sum(axis=0)
    temp2 = df_covid19_deaths_country[df_covid19_deaths_country['Country/Region']==c].sum(axis=0)
    temp3 = df_covid19_recovered_country[df_covid19_recovered_country['Country/Region']==c].sum(axis=0)
    temp['Country/Region']=c
    temp2['Country/Region']=c
    if c != 'Canada': temp3['Country/Region']=c
    temp['Province/State']=np.nan
    temp2['Province/State']=np.nan
    if c != 'Canada': temp3['Province/State']=np.nan
    df_covid19_confirmed_country = df_covid19_confirmed_country.append(temp,ignore_index=True).drop_duplicates()
    df_covid19_deaths_country = df_covid19_deaths_country.append(temp2,ignore_index=True).drop_duplicates()
    if c != 'Canada': df_covid19_recovered_country = df_covid19_recovered_country.append(temp3,ignore_index=True).drop_duplicates()
df_covid19_confirmed_country_merged = df_covid19_confirmed_country.merge(df_countries,how='inner',left_on=['Province/State','Country/Region'],right_on=['Province_State','Country_Region']).drop(columns=['Lat_x','Long','Province/State','Country/Region']).drop_duplicates(subset=['UID'])
df_covid19_deaths_country_merged = df_covid19_deaths_country.merge(df_countries,how='inner',left_on=['Province/State','Country/Region'],right_on=['Province_State','Country_Region']).drop(columns=['Lat_x','Long','Province/State','Country/Region']).drop_duplicates(subset=['UID'])
df_covid19_recovered_country_merged = df_covid19_recovered_country.merge(df_countries,how='inner',left_on=['Province/State','Country/Region'],right_on=['Province_State','Country_Region']).drop(columns=['Lat_x','Long','Province/State','Country/Region']).drop_duplicates(subset=['UID'])

df_covid19_confirmed_state_merged = df_covid19_confirmed_country.merge(df_states,how='inner',left_on=['Province/State','Country/Region'],right_on=['Province_State','Country_Region']).drop(columns=['Lat_x','Long','Province/State','Country/Region']).drop_duplicates(subset=['UID'])
df_covid19_deaths_state_merged = df_covid19_deaths_country.merge(df_states,how='inner',left_on=['Province/State','Country/Region'],right_on=['Province_State','Country_Region']).drop(columns=['Lat_x','Long','Province/State','Country/Region']).drop_duplicates(subset=['UID'])
df_covid19_recovered_state_merged = df_covid19_recovered_country.merge(df_states,how='inner',left_on=['Province/State','Country/Region'],right_on=['Province_State','Country_Region']).drop(columns=['Lat_x','Long','Province/State','Country/Region']).drop_duplicates(subset=['UID'])

df_covid19_confirmed_county = df_covid19_confirmed_county.drop(columns=['UID','iso2','iso3','code3','FIPS','Lat','Long_','Combined_Key'])
df_covid19_deaths_county = df_covid19_deaths_county.drop(columns=['UID','iso2','iso3','code3','FIPS','Lat','Long_','Combined_Key'])
df_covid19_confirmed_county_merged = df_covid19_confirmed_county.merge(df_counties,how='inner',left_on=['Admin2','Province_State','Country_Region'],right_on=['Admin2','Province_State','Country_Region']).drop_duplicates(subset=['UID'])
df_covid19_deaths_county_merged = df_covid19_deaths_county.merge(df_counties,how='inner',left_on=['Admin2','Province_State','Country_Region'],right_on=['Admin2','Province_State','Country_Region']).drop_duplicates(subset=['UID'])
df_covid19_recovered_county_merged = df_covid19_deaths_county_merged.iloc[0:0]

df_country_population = df_covid19_confirmed_country_merged.set_index('Combined_Key')['Population']

df_state_population = df_covid19_confirmed_state_merged.set_index('Combined_Key')['Population']

df_county_population = df_covid19_confirmed_county_merged.set_index('Combined_Key')['Population']


app.layout = html.Div(
    className='div-section',
    children = [
        html.Div(
            className='row div-row div-card',
            children= [
                html.Div(
                    className='one-half column',
                    children = [
                        html.H3('COVID-19 Analytic Dashboard')
                    ]
                )
            ]
        ),
        html.Div(id='covid-control-tabs',
            className='row div-row div-card',
            children = [
                dcc.Tabs(
                    children = [
                        # dcc.Tab(
                        #     label='Global-Level Analysis',
                        #     children = [
                        #         # dcc.Graph(id='country-scatter-population')
                        #     ]
                        # ),
                        gen_tab('country',list_countries),
                        gen_tab('state',list_states),
                        gen_tab('county',list_counties)
                    ]
                )
            ]
        ),
    ] 
)

@app.callback(
    [Output('country-scatter','figure'),
     Output('country-bar-daily','figure'),
     Output('country-scatter-deaths','figure'),
     Output('country-bar-deaths-daily','figure'),
     Output('country-scatter-recovered','figure'),
     Output('country-bar-recovered-daily','figure'),
     Output('country-map','figure'),
     Output('country-table','data'),
     Output('country-table','columns')],
    [Input('country-dropdown','value'),
     Input('country-radio','value'),
     Input('country-date-picker','start_date'),
     Input('country-date-picker','end_date')]
)

def update_country(countries,radio,start,end):
    start = dt.strptime(start,'%Y-%m-%d')
    start = dt.strftime(start,"%-m/%-d/%y")
    end = dt.strptime(end,'%Y-%m-%d')
    end = dt.strftime(end,"%-m/%-d/%y")

    df_covid19_confirmed_country_filter, df_covid19_confirmed_country_daily_filter = filter_df(df_covid19_confirmed_country_merged,countries,start,end,radio,'country')
    df_covid19_deaths_country_filter, df_covid19_deaths_country_daily_filter = filter_df(df_covid19_deaths_country_merged,countries,start,end,radio,'country')
    df_covid19_recovered_country_filter, df_covid19_recovered_country_daily_filter = filter_df(df_covid19_recovered_country_merged,countries,start,end,radio,'country')

    df_all = combine_data(df_covid19_confirmed_country_filter,df_covid19_deaths_country_filter,df_covid19_recovered_country_filter,start,end,'country')

    traces1 = []
    traces2 = []
    traces3 = []
    traces4 = []
    traces5 = []
    traces6 = []

    for country in df_covid19_confirmed_country_filter.index:
        traces1.append(gen_trace(df_covid19_confirmed_country_filter,country,'scatter'))
        traces2.append(gen_trace(df_covid19_confirmed_country_daily_filter,country,'bar'))
        traces3.append(gen_trace(df_covid19_deaths_country_filter,country,'scatter'))
        traces4.append(gen_trace(df_covid19_deaths_country_daily_filter,country,'bar'))
        traces5.append(gen_trace(df_covid19_recovered_country_filter,country,'scatter'))
        traces6.append(gen_trace(df_covid19_recovered_country_daily_filter,country,'bar'))

    if radio == 'Raw':
        return  gen_figure(traces1,'Cumulative Daily Confirmed COVID-19 Cases','Date','Number of Cases'), \
                gen_figure(traces2,'New Daily Confirmed COVID-19 Cases','Date','Number of Cases'), \
                gen_figure(traces3,'Cumulative COVID-19 Deaths','Date','Number of Deaths'), \
                gen_figure(traces4,'New Daily COVID-19 Deaths','Date','Number of Deaths'), \
                gen_figure(traces5,'Cumulative Recovered COVID-19 Cases','Date','Number of Deaths'), \
                gen_figure(traces6,'New Daily Recovered COVID-19 Cases','Date','Number of Deaths'), \
                gen_map(df_covid19_confirmed_country_filter,df_covid19_deaths_country_filter,df_covid19_recovered_country_filter,start,end,'country'), \
                gen_table_data(df_all), \
                gen_table_columns(df_all)
    
    else:
        return  gen_figure(traces1,'Cumulative Daily Confirmed COVID-19 Cases Per 1M Population','Date','Number of Cases Per 1M'), \
                gen_figure(traces2,'New Daily Confirmed COVID-19 Cases Per 1M Population','Date','Number of Cases Per 1M'), \
                gen_figure(traces3,'Cumulative COVID-19 Deaths Per 1M Population','Date','Number of Deaths Per 1M'), \
                gen_figure(traces4,'New Daily COVID-19 Deaths Per 1M Population','Date','Number of Deaths Per 1M'), \
                gen_figure(traces5,'Cumulative Recovered COVID-19 Cases Per 1M Population','Date','Number of Deaths Per 1M'), \
                gen_figure(traces6,'New Daily Recovered COVID-19 Cases Per 1M Population','Date','Number of Deaths Per 1M'), \
                gen_map(df_covid19_confirmed_country_filter,df_covid19_deaths_country_filter,df_covid19_recovered_country_filter,start,end,'country'), \
                gen_table_data(df_all), \
                gen_table_columns(df_all)


@app.callback(
    [Output('state-scatter','figure'),
     Output('state-bar-daily','figure'),
     Output('state-scatter-deaths','figure'),
     Output('state-bar-deaths-daily','figure'),
     Output('state-scatter-recovered','figure'),
     Output('state-bar-recovered-daily','figure'),
     Output('state-map','figure'),
     Output('state-table','data'),
     Output('state-table','columns')],
    [Input('state-dropdown','value'),
     Input('state-radio','value'),
     Input('state-date-picker','start_date'),
     Input('state-date-picker','end_date')]
)

def update_state(states,radio,start,end):
    start = dt.strptime(start,'%Y-%m-%d')
    start = dt.strftime(start,"%-m/%-d/%y")
    end = dt.strptime(end,'%Y-%m-%d')
    end = dt.strftime(end,"%-m/%-d/%y")

    df_covid19_confirmed_state_filter, df_covid19_confirmed_state_daily_filter = filter_df(df_covid19_confirmed_state_merged,states,start,end,radio,'state')
    df_covid19_deaths_state_filter, df_covid19_deaths_state_daily_filter = filter_df(df_covid19_deaths_state_merged,states,start,end,radio,'state')
    df_covid19_recovered_state_filter, df_covid19_recovered_state_daily_filter = filter_df(df_covid19_recovered_state_merged,states,start,end,radio,'state')

    df_all = combine_data(df_covid19_confirmed_state_filter,df_covid19_deaths_state_filter,df_covid19_recovered_state_filter,start,end,'state')

    traces1 = []
    traces2 = []
    traces3 = []
    traces4 = []
    traces5 = []
    traces6 = []

    for state in df_covid19_confirmed_state_filter.index:
        traces1.append(gen_trace(df_covid19_confirmed_state_filter,state,'scatter'))
        traces2.append(gen_trace(df_covid19_confirmed_state_daily_filter,state,'bar'))
        traces3.append(gen_trace(df_covid19_deaths_state_filter,state,'scatter'))
        traces4.append(gen_trace(df_covid19_deaths_state_daily_filter,state,'bar'))
        try:
            traces5.append(gen_trace(df_covid19_recovered_state_filter,state,'scatter'))
            traces6.append(gen_trace(df_covid19_recovered_state_daily_filter,state,'bar'))
        except:
            pass

    if radio == 'Raw':
        return  gen_figure(traces1,'Cumulative Daily Confirmed COVID-19 Cases','Date','Number of Cases'), \
                gen_figure(traces2,'New Daily Confirmed COVID-19 Cases','Date','Number of Cases'), \
                gen_figure(traces3,'Cumulative COVID-19 Deaths','Date','Number of Deaths'), \
                gen_figure(traces4,'New Daily COVID-19 Deaths','Date','Number of Deaths'), \
                gen_figure(traces5,'Cumulative Recovered COVID-19 Cases','Date','Number of Deaths'), \
                gen_figure(traces6,'New Daily Recovered COVID-19 Cases','Date','Number of Deaths'), \
                gen_map(df_covid19_confirmed_state_filter,df_covid19_deaths_state_filter,df_covid19_recovered_state_filter,start,end,'state'), \
                gen_table_data(df_all), \
                gen_table_columns(df_all)
    
    else:
        return  gen_figure(traces1,'Cumulative Daily Confirmed COVID-19 Cases Per 1M Population','Date','Number of Cases Per 1M'), \
                gen_figure(traces2,'New Daily Confirmed COVID-19 Cases Per 1M Population','Date','Number of Cases Per 1M'), \
                gen_figure(traces3,'Cumulative COVID-19 Deaths Per 1M Population','Date','Number of Deaths Per 1M'), \
                gen_figure(traces4,'New Daily COVID-19 Deaths Per 1M Population','Date','Number of Deaths Per 1M'), \
                gen_figure(traces5,'Cumulative Recovered COVID-19 Cases Per 1M Population','Date','Number of Deaths Per 1M'), \
                gen_figure(traces6,'New Daily Recovered COVID-19 Cases Per 1M Population','Date','Number of Deaths Per 1M'), \
                gen_map(df_covid19_confirmed_state_filter,df_covid19_deaths_state_filter,df_covid19_recovered_state_filter,start,end,'state'), \
                gen_table_data(df_all), \
                gen_table_columns(df_all) 


@app.callback(
    [Output('county-scatter','figure'),
     Output('county-bar-daily','figure'),
     Output('county-scatter-deaths','figure'),
     Output('county-bar-deaths-daily','figure'),
     Output('county-scatter-recovered','figure'),
     Output('county-bar-recovered-daily','figure'),
     Output('county-map','figure'),
     Output('county-table','data'),
     Output('county-table','columns')],
    [Input('county-dropdown','value'),
     Input('county-radio','value'),
     Input('county-date-picker','start_date'),
     Input('county-date-picker','end_date')]
)
def update_county(counties,radio,start,end):
    start = dt.strptime(start,'%Y-%m-%d')
    start = dt.strftime(start,"%-m/%-d/%y")
    end = dt.strptime(end,'%Y-%m-%d')
    end = dt.strftime(end,"%-m/%-d/%y")

    df_covid19_confirmed_county_filter, df_covid19_confirmed_county_daily_filter = filter_df(df_covid19_confirmed_county_merged,counties,start,end,radio,'county')
    df_covid19_deaths_county_filter, df_covid19_deaths_county_daily_filter = filter_df(df_covid19_deaths_county_merged,counties,start,end,radio,'county')
    df_covid19_recovered_county_filter, df_covid19_recovered_county_daily_filter = filter_df(df_covid19_recovered_county_merged,counties,start,end,radio,'county')

    df_all = combine_data(df_covid19_confirmed_county_filter,df_covid19_deaths_county_filter,df_covid19_recovered_county_filter,start,end,'county')

    traces1 = []
    traces2 = []
    traces3 = []
    traces4 = []
    traces5 = []
    traces6 = []

    for county in df_covid19_confirmed_county_filter.index:
        traces1.append(gen_trace(df_covid19_confirmed_county_filter,county,'scatter'))
        traces2.append(gen_trace(df_covid19_confirmed_county_daily_filter,county,'bar'))
        traces3.append(gen_trace(df_covid19_deaths_county_filter,county,'scatter'))
        traces4.append(gen_trace(df_covid19_deaths_county_daily_filter,county,'bar'))
        try:
            traces5.append(gen_trace(df_covid19_recovered_county_filter,county,'scatter'))
            traces6.append(gen_trace(df_covid19_recovered_county_daily_filter,county,'bar'))
        except:
            pass

    if radio == 'Raw':
        return  gen_figure(traces1,'Cumulative Daily Confirmed COVID-19 Cases','Date','Number of Cases'), \
                gen_figure(traces2,'New Daily Confirmed COVID-19 Cases','Date','Number of Cases'), \
                gen_figure(traces3,'Cumulative COVID-19 Deaths','Date','Number of Deaths'), \
                gen_figure(traces4,'New Daily COVID-19 Deaths','Date','Number of Deaths'), \
                gen_figure(traces5,'Cumulative Recovered COVID-19 Cases','Date','Number of Deaths'), \
                gen_figure(traces6,'New Daily Recovered COVID-19 Cases','Date','Number of Deaths'), \
                gen_map(df_covid19_confirmed_county_filter,df_covid19_deaths_county_filter,df_covid19_recovered_county_filter,start,end,'county'), \
                gen_table_data(df_all), \
                gen_table_columns(df_all)
    
    else:
        return  gen_figure(traces1,'Cumulative Daily Confirmed COVID-19 Cases Per 1M Population','Date','Number of Cases Per 1M'), \
                gen_figure(traces2,'New Daily Confirmed COVID-19 Cases Per 1M Population','Date','Number of Cases Per 1M'), \
                gen_figure(traces3,'Cumulative COVID-19 Deaths Per 1M Population','Date','Number of Deaths Per 1M'), \
                gen_figure(traces4,'New Daily COVID-19 Deaths Per 1M Population','Date','Number of Deaths Per 1M'), \
                gen_figure(traces5,'Cumulative Recovered COVID-19 Cases Per 1M Population','Date','Number of Deaths Per 1M'), \
                gen_figure(traces6,'New Daily Recovered COVID-19 Cases Per 1M Population','Date','Number of Deaths Per 1M'), \
                gen_map(df_covid19_confirmed_county_filter,df_covid19_deaths_county_filter,df_covid19_recovered_county_filter,start,end,'county'), \
                gen_table_data(df_all), \
                gen_table_columns(df_all) 

def gen_trace(data,filt,chart_type):
    return dict(
            x = data.columns,
            y = data.loc[filt],
            name=filt,
            type=chart_type
        )


def gen_figure(trace,fig_title,x_title,y_title):
    return {
            'data':trace,
            'layout': dict(
                title=fig_title,
                xaxis={
                    'title':x_title,
                    'showgrid':False
                },
                yaxis={
                    'title':y_title,
                    'showgrid':True,
                    'gridcolor':'gray'
                },
                plot_bgcolor="#1F2833",
                paper_bgcolor="#1F2833",
                font=dict(color="#C5C6C7")
            )
        }

def gen_map(df_confirmed,df_deaths,df_recovered,start,end,level):
    if level=='country':
        df_confirmed = df_confirmed[[start,end]].diff(axis=1).merge(df_countries,how='inner',left_on=df_confirmed.index, right_on='Combined_Key')
        df_deaths = df_deaths[[start,end]].diff(axis=1).merge(df_countries,how='inner',left_on=df_deaths.index, right_on='Combined_Key')
        df_recovered = df_recovered[[start,end]].diff(axis=1).merge(df_countries,how='inner',left_on=df_recovered.index, right_on='Combined_Key')

    if level =='state':
        df_confirmed = df_confirmed[[start,end]].diff(axis=1).merge(df_states,how='inner',left_on=df_confirmed.index, right_on='Combined_Key')
        df_deaths = df_deaths[[start,end]].diff(axis=1).merge(df_states,how='inner',left_on=df_deaths.index, right_on='Combined_Key')
        df_recovered = df_recovered[[start,end]].diff(axis=1).merge(df_states,how='inner',left_on=df_recovered.index, right_on='Combined_Key')

    if level =='county':
        df_confirmed = df_confirmed[[start,end]].diff(axis=1).merge(df_counties,how='inner',left_on=df_confirmed.index, right_on='Combined_Key')
        df_deaths = df_deaths[[start,end]].diff(axis=1).merge(df_counties,how='inner',left_on=df_deaths.index, right_on='Combined_Key')
        df_recovered = df_recovered[[start,end]].diff(axis=1).merge(df_counties,how='inner',left_on=df_recovered.index, right_on='Combined_Key')

    confirmed_max = df_confirmed[end].max()
    confirmed_min = df_confirmed[end].min()
    deaths_max = df_deaths[end].max()
    deaths_min = df_deaths[end].min()
    recovered_max = df_recovered[end].max()
    recovered_min = df_recovered[end].min()
    min_lat = df_confirmed['Lat'].min()
    max_lat = df_confirmed['Lat'].max()
    min_lng = df_confirmed['Long_'].min()
    max_lng = df_confirmed['Long_'].max()

    zoom_level = calc_zoom(min_lat,max_lat,min_lng,max_lng,len(df_confirmed.index))
    cen_lat, cen_lon = calc_center(min_lat,max_lat,min_lng,max_lng,len(df_confirmed.index))
    

    if confirmed_max==confirmed_min:
        confirmed_min=0
    if deaths_max==deaths_min:
        deaths_min=0
    if recovered_max==recovered_min:
        recovered_min=0

    data = [
        go.Scattermapbox(
            lat=df_confirmed['Lat'],
            lon=df_confirmed['Long_'],
            mode='markers',
            marker=dict(
                size=np.nan_to_num(df_confirmed[end].apply(lambda x: (x-confirmed_min)/(confirmed_max-confirmed_min)*50+10).to_numpy())
            ),
            text=df_confirmed[end],
            visible=True,
            name='COVID-19 Confirmed Cases'
        ),
        go.Scattermapbox(
            lat=df_deaths['Lat'],
            lon=df_deaths['Long_'],
            mode='markers',
            marker=dict(
                size=np.nan_to_num(df_deaths[end].apply(lambda x: (x-deaths_min)/(deaths_max-deaths_min)*50+10).to_numpy())
            ),
            hovertext=df_deaths[end],
            hovertemplate='<extra></extra>',
            visible='legendonly',
            name='COVID-19 Deaths'
        ),
        go.Scattermapbox(
            lat=df_recovered['Lat'],
            lon=df_recovered['Long_'],
            mode='markers',
            marker=dict(
                size=np.nan_to_num(df_recovered[end].apply(lambda x: (x-recovered_min)/(recovered_max-recovered_min)*50+10).to_numpy())
            ),
            hovertext=df_recovered[end],
            hovertemplate='<extra></extra>',
            visible='legendonly',
            name='COVID-19 Recoveries'
        )
    ]

    layout = go.Layout(
        mapbox=dict(
            accesstoken=token,
            center=dict(
                lat = cen_lat,
                lon = cen_lon
            ),
            zoom = zoom_level
        ),
        mapbox_style='dark',
        margin={"r":0,"t":0,"l":0,"b":0},
        font = dict(
            color='#E1E1E1'
        ),
        autosize = True,
        legend = dict(
            orientation= "v",
            x=0,
            y=1,
            traceorder="normal",
            bgcolor='#0B0C10'
        ),
    )

    return {
        'data':data,
        'layout':layout
    }

def calc_zoom(min_lat,max_lat,min_lng,max_lng,length):

    if(length>1):
        width_y = max_lat - min_lat
        width_x = max_lng - min_lng
        zoom_y = -1.446*math.log(width_y) + 7.2753
        zoom_x = -1.415*math.log(width_x) + 8.7068
        return min(zoom_y,zoom_x)
    
    else:
        return 2

def calc_center(min_lat,max_lat,min_lng,max_lng,length):

    if(length>1):
        return (min_lat+max_lat)/2,(min_lng+max_lng)/2
    else:
        return min_lat, min_lng

def combine_data(df_confirmed,df_deaths,df_recovered,start,end,level):
    if level=='country':
        df_all = df_confirmed[[start,end]].diff(axis=1).merge(df_countries,how='inner',left_on=df_confirmed.index, right_on='Combined_Key').rename(columns={end:'confirmed'})
        df_all = df_deaths[[start,end]].diff(axis=1).merge(df_all,how='inner',left_on=df_deaths.index, right_on='Combined_Key').rename(columns={end:'deaths'})
        df_all = df_recovered[[start,end]].diff(axis=1).merge(df_all,how='right',left_on=df_recovered.index, right_on='Combined_Key').rename(columns={end:'recovered'})
        
    if level=='state':
        df_all = df_confirmed[[start,end]].diff(axis=1).merge(df_states,how='inner',left_on=df_confirmed.index, right_on='Combined_Key').rename(columns={end:'confirmed'})
        df_all = df_deaths[[start,end]].diff(axis=1).merge(df_all,how='inner',left_on=df_deaths.index, right_on='Combined_Key').rename(columns={end:'deaths'})
        df_all = df_recovered[[start,end]].diff(axis=1).merge(df_all,how='right',left_on=df_recovered.index, right_on='Combined_Key').rename(columns={end:'recovered'})
    
    if level=='county':
        df_all = df_confirmed[[start,end]].diff(axis=1).merge(df_counties,how='inner',left_on=df_confirmed.index, right_on='Combined_Key').rename(columns={end:'confirmed'})
        df_all = df_deaths[[start,end]].diff(axis=1).merge(df_all,how='inner',left_on=df_deaths.index, right_on='Combined_Key').rename(columns={end:'deaths'})
        df_all = df_recovered[[start,end]].diff(axis=1).merge(df_all,how='right',left_on=df_recovered.index, right_on='Combined_Key').rename(columns={end:'recovered'})

    return df_all

def gen_table_data(df_all):
    return df_all[['Combined_Key','Population','confirmed','deaths','recovered']].to_dict('records')

def gen_table_columns(df_all):
    columns = [{"name": i, "id": i} for i in df_all[['Combined_Key','Population','confirmed','deaths','recovered']].columns]
    return columns

def filter_df(df,filt,start,end,scale,level):
    try:
        df_filt = df[df['Combined_Key'].isin(filt)].set_index('Combined_Key').loc[:,start:end]
        df_filt_diff = df_filt.diff(axis=1)

        if (scale == 'Norm') & (level=='country'):
            df_filt = df_filt.divide(df_country_population.loc[filt]/1000000,axis=0).round(2)
            df_filt_diff = df_filt_diff.divide(df_country_population.loc[filt]/1000000,axis=0).round(2)

        if (scale == 'Norm') & (level=='state'):
            df_filt = df_filt.divide(df_state_population.loc[filt]/1000000,axis=0).round(2)
            df_filt_diff = df_filt_diff.divide(df_state_population.loc[filt]/1000000,axis=0).round(2)

        if (scale == 'Norm') & (level=='county'):
            df_filt = df_filt.divide(df_county_population.loc[filt]/1000000,axis=0).round(2)
            df_filt_diff = df_filt_diff.divide(df_county_population.loc[filt]/1000000,axis=0).round(2)
    
    except:
        df_filt = pd.DataFrame()
        df_filt_diff = pd.DataFrame()
       
    return df_filt, df_filt_diff



if __name__ == '__main__':
    app.run_server(host='0.0.0.0')