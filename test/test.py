import sys
import osmnx as ox
import networkx as nx
sys.path.insert(1, sys.path[0][:-5])
import pickle as p
import geopy
from geopy.geocoders import Nominatim

from Elena.abstraction.abstraction import *
from Elena.control.algorithms import *
from Elena.control.control import get_geojson_coor, get_data_points
from Elena.control.settings import *

def Test(value = ""):
    def test_f(func):
        def c(*args, **kwargs):
            try:
                func(*args,**kwargs)
                print("Condition passed" ) # Passed
                print()
            except Exception as error:
                print(error)
                print("Condition failed") # Failed
                print()
        return c
    return test_f

@Test("")
def test_graph_getter(end):
    print("# Test graph_getter method in abstraction.py")

    abst = Graph_Abstraction()
    G = abst.graph_getter(end)
    assert isinstance(G, nx.classes.multidigraph.MultiDiGraph)

@Test("")
def test_get_route(A):
    print("# Test get_route method in algorithms.py.")

    c = A.get_route({0 : 2, 1 : -1, 2 : 1}, 0)
    assert isinstance(c, list)
    assert c == [1,2,0]


@Test("")
def test_get_shortest_path():

    print("# Test get_shortest_path method in algorithms.py") 
    x = 100.0 
    
    startpt=(42.3762, -72.5148)
    endpt =(42.3948, -72.5266)

    abstract = Graph_Abstraction()
    G = abstract.graph_getter(endpt)

    A = Algorithms(G, x = 100.0)

    shortest_path, best_path = A.get_shortest_path(startpt, endpt, x, elev_type = "maximize", log = False)
    assert best_path[1] <= (1 + x/100.0)*shortest_path[1]
    assert best_path[2] >= shortest_path[2]

    startpt= (42.3762, -72.5148)
    endpt= (42.3948, -72.5266)
    shortest_path, best_path = A.get_shortest_path(startpt, endpt, x, elev_type = "minimize", log = False)
    assert best_path[1] <= (1 + x/100.0)*shortest_path[1]
    assert best_path[2] <= shortest_path[2]

@Test("")
def test_get_Elevation(A):
    print("# Test get_Elevation method in algorithms.py")

    route = [0, 3, 4, 2]
    c, p = A.get_Elevation(route, cost_type = "both", isPiecewise = True)
    assert isinstance(c, float)
    assert isinstance(p, list)
    assert c == 0.0
    assert p == [1.0, 0.0, -1.0]

    c = A.get_Elevation(route, cost_type = "both")
    assert isinstance(c, float)
    assert c == 0.0

    c, p = A.get_Elevation(route, cost_type = "elevation_gain", isPiecewise = True)
    assert isinstance(c, float)
    assert isinstance(p, list)
    assert c == 1.0
    assert p == [1.0, 0.0, 0.0]

    c, p = A.get_Elevation(route, cost_type = "elevation_drop", isPiecewise = True)
    assert isinstance(c, float)
    assert isinstance(p, list)
    assert c == 1.0
    assert p == [0.0, 0.0, 1.0]

    c, p = A.get_Elevation(route, cost_type = "normal", isPiecewise = True)
    assert isinstance(c, float)
    assert isinstance(p, list)
    assert c == 6.726999999999999
    assert p == [1.414, 4.0, 1.313]


@Test("")
def test_get_cost(A, n1 = 0, n2 = 1):
    print("# Test get_cost method in algorithms.py")

    c = A.get_cost(0, 1, cost_type = "normal")
    assert isinstance(c, float)
    assert c == 3.0
    
    c = A.get_cost(0, 3, cost_type = "elevation_difference")
    assert isinstance(c, float)
    assert c == 1.0

    c = A.get_cost(5, 4, cost_type = "elevation_difference")
    assert isinstance(c, float)
    assert c == -2.0
    
    c = A.get_cost(1, 4, cost_type= "elevation_gain")
    assert isinstance(c, float)
    assert c == 1.0

    c = A.get_cost(4, 1, cost_type = "elevation_gain")
    assert isinstance(c, float)
    assert c == 0.0
    
    c = A.get_cost(6, 2, cost_type = "elevation_drop")
    assert isinstance(c, float)
    assert c == 4.0
    
    c = A.get_cost(2, 6, cost_type = "elevation_drop")
    assert isinstance(c, float)
    assert c == 0.0

    c = A.get_cost(2, 6, cost_type = "abs")
    assert isinstance(c, float)
    assert c == 4.0

    c = A.get_cost(6, 2, cost_type = "abs")
    assert isinstance(c, float)
    assert c == 4.0

@Test("")
def test_get_geojson_coor(location):
    print("# Test get_geojson_coor method in control.py")

    json = get_geojson_coor(location)
    assert isinstance(json, dict)
    assert all(k in ["properties", "type", "geometry"] for k in json.keys())

@Test("")
def test_get_data_points(start, end, x = 100, min_max = "maximize"):
    print("# Test get_data_points method in control.py")

    d = get_data_points(start, end, x, min_max, log=False)
    locator = Nominatim(user_agent="myGeocoder")
    location = locator.reverse(start)
    locate = location.address.split(',')

    len_location = len(locate)

    start_loc = locate[0] + ',' + locate[1] + ',' + locate[2] + ',' + locate[len_location-5] + ',' + locate[len_location-3] + ', USA - ' + locate[len_location-2]

    location = locator.reverse(end)
    locate = location.address.split(',')
    len_location = len(locate)

    end_loc = locate[0] + ',' + locate[1] + ',' + locate[2] + ',' + locate[len_location-5] + ',' + locate[len_location-3] + ', USA - ' + locate[len_location-2]

    assert isinstance(d, dict)
    assert start_loc == d["start"]
    assert end_loc == d["end"]


if __name__ == "__main__":
    start, end = (42.373222, -72.519852), (42.375544, -72.524210)
    
    G = nx.Graph()
    # Create toy graph with nodes 0-7
    [G.add_node(i, elevation = 0.0) for i in range(7)]
    edgeList = [(0,1,3.0), (1,2,3.0), (0,3,1.414), (3,4,4.0), (4,2,1.313), (0,5,4.24), (5,2,4.24), (0,6,5.0), (6,2,5.0)]
    G.add_weighted_edges_from(edgeList)
    elev = [0.0, 0.0, 0.0, 1.0, 1.0, 3.0, 4.0]

    for i, e in enumerate(elev):
        G.nodes[i]["elevation"] = e
    
    A = Algorithms(G, x = 0.0)
    # Tests #####
    test_graph_getter(end)
    test_get_route(A)
    test_get_shortest_path()
    test_get_Elevation(A)
    test_get_cost(A)
    test_get_geojson_coor(start)
    test_get_data_points(start, end)


