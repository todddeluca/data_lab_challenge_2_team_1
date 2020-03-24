

import argparse
import geopandas
import gzip
import io
import json
import pandas as pd
import plotly
import plotly.express as px
from pprint import pprint
import requests


def load_all_paper_data(download=False):
    if download:
        # download and gunzip the spreadsheet
        url = "https://github.com/todddeluca/data_lab_challenge_2_team_1/raw/master/data/all_paper_data.xlsx.gz"
        content = gzip.decompress(requests.get(url).content)
    else:
        with open('../data/all_paper_data.xlsx', 'rb') as fh:
            content = fh.read()
    # load each sheet into a dataframe
    trigger_na = pd.read_excel(io.BytesIO(content), sheet_name="Trigger_NA")
    trigger_ave = pd.read_excel(io.BytesIO(content), sheet_name="Trigger_Ave")
    trigger_other = pd.read_excel(io.BytesIO(content), sheet_name="Trigger Other")
    follow_up = pd.read_excel(io.BytesIO(content), sheet_name="Follow Up")
    follow_up_other = pd.read_excel(io.BytesIO(content), sheet_name="Follow Up Other")
    codebook = pd.read_excel(io.BytesIO(content), sheet_name="Codebook")
    return trigger_na, trigger_ave, trigger_other, follow_up, follow_up_other, codebook


def load_cases_confirmed():
    return pd.read_csv('../data/ChiefdomCasesData-lab-confirmed-database.csv')


def load_cases_suspected():
    return pd.read_csv('../data/ChiefdomCasesData-suspected-database.csv')


def load_digital_data(download=False):
    # content = gzip.decompress(requests.get("https://github.com/todddeluca/data_lab_challenge_2_team_1/raw/master/data/digita.csv.gz").content)
    if download:
        url = "https://github.com/todddeluca/data_lab_challenge_2_team_1/raw/master/data/digital.csv.gz"
    else:
        url = '../data/digital.csv.gz'

    digital = pd.read_csv(url, low_memory=False)
    # the digital codebook is not structured as a table.
    # See https://github.com/todddeluca/data_lab_challenge_2_team_1/raw/master/data/digital_codebook.xls
    return digital


def load_chiefdom_adjacency_data(download=False):
    if download:
        url = 'https://raw.githubusercontent.com/todddeluca/data_lab_challenge_2_team_1/master/data/sierra_leone_chiefdom_adjacency.csv'
    else:
        url = '../data/sierra_leone_chiefdom_adjacency.csv'

    adj = pd.read_csv(url, low_memory=False)
    return adj


def load_chiefdom_geojson(download=False):
    '''return chiefdom geojson data as text'''
    if download:
        url = 'https://github.com/todddeluca/data_lab_challenge_2_team_1/raw/master/data/chiefdom.geojson'
        data = requests.get(url).json
    else:
        with open('../data/chiefdom.geojson') as fh:
            data = json.load(fh)

    return data


def load_chiefdom_geopandas(download=False):
    '''return chiefdom geojson as geopandas'''
    if download:
        url = 'https://github.com/todddeluca/data_lab_challenge_2_team_1/raw/master/data/chiefdom.geojson'
    else:
        url = '../data/chiefdom.geojson'

    return geopandas.read_file(url)


def load_all(download=False):
    adj = load_chiefdom_adjacency_data()
    print('adj', adj)
    trigger_na, trigger_ave, trigger_other, follow_up, follow_up_other, codebook = load_all_paper_data()
    print('all_paper', trigger_na, trigger_ave, trigger_other, follow_up, follow_up_other, codebook)
    digital = load_digital_data()
    print('digital', digital)

    chief = load_chiefdom_geopandas()
    print('chief', chief)
    chief_geojson = load_chiefdom_geojson()
    print('chief_geojson', chief_geojson)
    # chiefdom_geojson_filename = "chiefdom.geojson"
    # chief.to_file(chiefdom_geojson_filename, driver = "GeoJSON")
    # with open(chiefdom_geojson_filename) as fh:
    #     chief_geojson = json.load(fh)
    # print('chief_geojson', chief_geojson)


    # with pd.option_context('display.max_rows', None, 'display.max_columns', None):  # more options can be specified also
    with pd.option_context('display.max_rows', 20, 'display.max_columns', 10):  # more options can be specified also
        print('num unique chiefdom:', trigger_ave['Chiefdom'].unique().shape[0])
        print('how many observations per chiefdom in trigger_ave table?')
        pprint(trigger_ave['Chiefdom'].value_counts())

"""## Plot Chiefdoms in Plotly

Converting geopandas/shapefile to geojson, which plotly uses
https://community.plot.ly/t/create-your-own-choropleth-map-with-custom-shapefiles/2567/7

Plotly Choropleth maps
https://plot.ly/python/choropleth-maps/
"""

def animate_map(chief, chief_geojson):

    # If your shapefile has coordinates in UTM format,
    # and you want to transform them into WGS84 (Lat / Lon format), you can do this:
    # geodf = geodf.to_crs({'init': 'epsg:4326'})
    print(chief.crs)

    print(plotly.__version__)
    # Plot Chiefdoms, colored by district
    fig = px.choropleth(
        chief,
        geojson=chief_geojson,
    #     color='Shape_Area',
        color='admin2Name',
        locations="OBJECTID",
        featureidkey="properties.OBJECTID",
        )
    # go.Figure()
    fig.update_geos(fitbounds="locations", visible=False)
    # fig.update_geos(lataxis_showgrid=True, lonaxis_showgrid=True)
    fig.update_layout(mapbox_style="white-bg")
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    fig.show()


def main():
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('task', help='a task to run.')
    parser.add_argument('--download', action='store_true', default=False, help='download data from github')
    args = parser.parse_args()

    if args.task == 'animate_map':
        chief = load_chiefdom_geopandas()
        chief_geojson = load_chiefdom_geojson()
        globals()[args.task](chief, chief_geojson)
    elif args.task == 'load_all':
        load_all(args.download)


if __name__ == '__main__':
    main()
