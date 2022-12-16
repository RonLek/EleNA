import osmnx as ox
import networkx as nx
import os
import numpy as np
import pickle as p
from Elena.abstraction.config import API

class Graph_Abstraction:
    def __init__(self):
        print("Initializing the model")        
        self.GOOGLEAPIKEY=API["googleapikey"]        
        if os.path.exists("./graph.p"):
            self.G = p.load( open( "graph.p", "rb" ) )
            self.init = True
            print("Graph is now ready to be used")
        else:
            self.init = False

    def elev_graph(self, G):
        # Networkx graph, elevation data and rise/fall grade is returned.
        G = ox.add_node_elevations(G, api_key=self.GOOGLEAPIKEY)        
        return G

    def dist_bw_nodes(self,latitude1,longitude1,latitude2,longitude2):
        # Computes distance between given latitude and longitudes
        radius=6371008.8 # Earth radius
        
        latitude1, longitude1 = np.radians(latitude1), np.radians(longitude1)
        latitude2, longitude2 = np.radians(latitude2),np.radians(longitude2)

        distlong,distlat = longitude2 - longitude1,latitude2 - latitude1

        temp = np.sin(distlat / 2)**2 + np.cos(latitude1) * np.cos(latitude2) * np.sin(distlong / 2)**2
        final = 2 * np.arctan2(np.sqrt(temp), np.sqrt(1 - temp))
        return radius * final

    def compDist(self, G,edge_node):

        for node,data in G.nodes(data=True):
            latitude2=G.nodes[node]['y']
            longitude2=G.nodes[node]['x']
            distance=self.dist_bw_nodes(edge_node["y"],edge_node["x"],latitude2,longitude2)            
            data['dist_from_dest'] = distance
        return G

    def add_dist_frm_ept(self,G,ept):
        # Adding dist between final destination and all nodes
        edge_node=G.nodes[ox.get_nearest_node(G, point=ept)]            
        return self.compDist(G,edge_node)

    def graph_getter(self, endpt):    
        # Generates graph and elevation data
   
        start = [42.384803, -72.529262]
        if not self.init:
            print("Graph is now loading")
            self.G = ox.graph_from_point(start, distance=20000, network_type='walk')
            self.G = self.elev_graph(self.G)                         
            p.dump( self.G, open( "graph.p", "wb" ) )
            self.init = True
            print("Saved Graph")
        self.G = self.add_dist_frm_ept(self.G,endpt)
        return self.G

    
    
