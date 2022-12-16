import os
import requests
import geopy
from flask import Flask, jsonify, session, g, request, url_for, flash, redirect,abort,render_template
from geopy.geocoders import Nominatim
import json
from Elena.abstraction.abstraction import Graph_Abstraction
from Elena.control.algorithms import Algorithms
from Elena.control.settings import *


app = Flask(__name__, static_url_path = '', static_folder = "../home/static", template_folder = "../home/templates")
app.config.from_object(__name__)

app.config.from_envvar('APP_CONFIG_FILE', silent=True)

MAPBOX_ACCESS_KEY = MAPBOX_KEY

init = False
G, M, algo = None, None, None


def get_location(pt):

    locator = Nominatim(user_agent="myGeocoder")
    loc = locator.reverse(pt)
    locate = loc.address.split(',')
    len_location = len(locate)
    point = locate[0] + ',' + locate[1] + ',' + locate[2] + ',' + locate[len_location-5] + ',' + locate[len_location-3] + ', USA - ' + locate[len_location-2] 

    return point

def get_geojson_coor(coordinates):
    geojson_coor = {}
    geojson_coor["properties"] = {}
    geojson_coor["type"] = "Feature"
    geojson_coor["geometry"] = {}
    geojson_coor["geometry"]["type"] = "LineString"
    geojson_coor["geometry"]["coordinates"] = coordinates

    return geojson_coor

def get_data_points(spt, ept, x,min_max, log=True):
    # Generates data points for computing the routes.
    global init, G, M, algo

    start = get_location(spt)
    if log:
        print("Start location: ",start)
    
    
    end = get_location(ept)
    if log:
        print("End location: ",end)
    
    if log:
        print("Total path percentage: ",x)
        print("Elevation type: ",min_max)
    if not init:
        abstract = Graph_Abstraction()
        G = abstract.graph_getter(ept)
        algo = Algorithms(G, x = x,elev_type = min_max)
        init = True
    
    shortestPath, elevatedPath = algo.get_shortest_path(spt, ept, x,elev_type = min_max, log = log)   
    
    if shortestPath is None and elevatedPath is None:
        data = {"elevation_route" : [] , "shortest_route" : []}        
        data["shortDist"] = 0
        data["gainShort"] = 0
        data["dropShort"] = 0
        data["elenavDist"]  = 0
        data["gainElenav"] = 0
        data["dropElenav"] = 0
        data["popup_flag"] = 0 
        return data
    data = {"elevation_route" : get_geojson_coor(elevatedPath[0]), "shortest_route" : get_geojson_coor(shortestPath[0])}
    data["shortDist"] = shortestPath[1]
    data["gainShort"] = shortestPath[2]
    data["dropShort"] = shortestPath[3]
    data["start"] = start
    data["end"] = end
    data["elenavDist"] = elevatedPath[1]
    data["gainElenav"] = elevatedPath[2]
    data["dropElenav"] = elevatedPath[3] 
    if len(elevatedPath[0])==0:
        data["popup_flag"] = 1
    else: 
        data["popup_flag"] = 2    
    return data
    
@app.route('/home')
def home():    

    return render_template(
        'home.html', 
        ACCESS_KEY=MAPBOX_ACCESS_KEY
    )

@app.route('/route',methods=['POST'])
def get_route():  
    data=request.get_json(force=True)
    route_data = get_data_points((data['start_location']['lat'],data['start_location']['lng']),(data['end_location']['lat'],data['end_location']['lng']),data['x'],data['min_max'])
    return json.dumps(route_data)
