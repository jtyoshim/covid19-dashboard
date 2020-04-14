import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import pandas as pd
import numpy as np
import folium
pd.set_option('display.max_columns',50)

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__,external_stylesheets=external_stylesheets)
colors = {
    'background': '#111111',
    'text': '#7FDBFF'
}

# Read in JHU Data from Github
df_covid19_confirmed_US = pd.read_csv('https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_US.csv')
df_covid19_confirmed_global = pd.read_csv('https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv')
df_covid19_deaths_US = pd.read_csv('https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_US.csv')
df_covid19_deaths_global = pd.read_csv('https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv')
df_covid19_recovered_global = pd.read_csv('https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_recovered_global.csv')
df_fips_lookup = pd.read_csv('https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/UID_ISO_FIPS_LookUp_Table.csv')

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
# print(list_counties)

df_covid19_confirmed_global_merged = df_covid19_confirmed_global.merge(df_countries,how='inner',left_on=['Province/State','Country/Region'],right_on=['Province_State','Country_Region']).drop(columns=['Lat_x','Long','Province/State','Country/Region'])
# print(df_covid19_confirmed_global_merged.head())
df_country_population = df_covid19_confirmed_global_merged.set_index('Combined_Key')['Population']
print(df_country_population.head())

app.layout = html.Div(
    [
        html.Div(
            className='row div-row div-card',
            children = [
                html.Div([
                    html.Label('Countries'),
                    dcc.Dropdown(
                        id='country-dropdown',
                        options=list_countries,
                        multi=True,
                        value=['US']
                    )
                ],
                className='three columns'),
                html.Div([
                    html.Label('States'),
                    dcc.Dropdown(
                        options=list_states,
                        multi=True
                    )
                ],
                className='three columns'),
                html.Div([
                    html.Label('Counties'),
                    dcc.Dropdown(
                        options=list_counties,
                        multi=True
                    )
                ],
                className='three columns')
            ]
        ), 
        html.Div(
            className='row div-row div-card',
            children = [
                html.Div(
                    children=[
                        html.H3(
                            children='Confirmed COVID-19 Cases By Country',
                            style={
                                'textAlign': 'center',
                                'color': colors['text']
                            }
                        ),
                        dcc.Graph(id='global-scatter')
                    ],
                    className='six columns'
                ),
                html.Div(
                    children=[
                        html.H3(
                            children='Confirmed COVID-19 Cases By Country per 10000000 Population',
                            style={
                                'textAlign': 'center',
                                'color': colors['text']
                            }
                        ),
                        dcc.Graph(id='global-scatter-population')
                    ],
                    className='six columns'
                )
            ]
        )
    ] 
)

@app.callback(
    Output('global-scatter','figure'),
    [Input('country-dropdown','value')]
)

def update_global(countries):
    # print(countries)
    df_covid19_confirmed_global_filter = df_covid19_confirmed_global_merged[df_covid19_confirmed_global_merged['Combined_Key'].isin(countries)]
    print(df_covid19_confirmed_global_filter.head())
    df_covid19_confirmed_global_filter.drop(columns=['UID','iso2','iso3','code3','FIPS','Admin2','Province_State','Country_Region','Lat_y','Long_','Population','value','label'],inplace=True)
    df_covid19_confirmed_global_filter.set_index('Combined_Key',inplace=True)
    traces = []
    for country in df_covid19_confirmed_global_filter.index:
        traces.append(dict(
            x = df_covid19_confirmed_global_filter.columns,
            y = df_covid19_confirmed_global_filter.loc[country],
            name=country
        ))
    return {
        'data':traces,
        'layout': dict(
            xaxis={'title':'Date'},
            yaxis={'title':'Number of Cases'}
        )
    }

@app.callback(
    Output('global-scatter-population','figure'),
    [Input('country-dropdown','value')]
)

def update_global_pop(countries):
    # print(countries)
    df_covid19_confirmed_global_pop_filter = df_covid19_confirmed_global_merged[df_covid19_confirmed_global_merged['Combined_Key'].isin(countries)]
    df_covid19_confirmed_global_pop_filter.drop(columns=['UID','iso2','iso3','code3','FIPS','Admin2','Province_State','Country_Region','Lat_y','Long_','Population','value','label'],inplace=True)
    df_covid19_confirmed_global_pop_filter.set_index('Combined_Key',inplace=True)
    df_covid19_confirmed_global_pop_filter = df_covid19_confirmed_global_pop_filter.divide(df_country_population.loc[countries]/1000000,axis=0)
    traces = []
    for country in df_covid19_confirmed_global_pop_filter.index:
        traces.append(dict(
            x = df_covid19_confirmed_global_pop_filter.columns,
            y = df_covid19_confirmed_global_pop_filter.loc[country],
            name=country
        ))
    return {
        'data':traces,
        'layout': dict(
            xaxis={'title':'Date'},
            yaxis={'title':'Number of Cases'}
        )
    }
    


if __name__ == '__main__':
    app.run_server(debug=True,host='0.0.0.0')