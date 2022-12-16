import osmnx as ox
import networkx as nx
from collections import deque, defaultdict
from heapq import *
import time

class Algorithms:
    def __init__(self, G, x = 0.0, elev_type = "maximize"):

        self.G = G
        self.elev_type = elev_type
        self.x = x
        self.best = [[], 0.0, float('-inf'), 0.0]
        self.start_node= None
        self.end_node =None

    def reload(self, G):
        # Reloading with modified G
        self.G = G


    def get_cost(self, node1, node2, cost_type = "normal"):
        
        # The cost between two nodes is compared according to the cost_type and returned 
        G = self.G
        if node1 is None or node2 is None : 
            return 
        if cost_type == "normal":
            try : 
                return G.edges[node1, node2 ,0]["length"]
            except : 
                return G.edges[node1, node2]["weight"]
        elif cost_type == "elevation_difference":
            return G.nodes[node2]["elevation"] - G.nodes[node1]["elevation"]
        elif cost_type == "elevation_gain":
            return max(0.0, G.nodes[node2]["elevation"] - G.nodes[node1]["elevation"])
        elif cost_type == "elevation_drop":
            return max(0.0, G.nodes[node1]["elevation"] - G.nodes[node2]["elevation"])
        else:
            return abs(G.nodes[node1]["elevation"] - G.nodes[node2]["elevation"])
        


    def get_Elevation(self, route, cost_type = "both", isPiecewise = False):
        # For a particular route, the function returrns the total or piecewise cost.
        total = 0
        if isPiecewise : 
            piece_elevation = []
        for i in range(len(route)-1):
            if cost_type == "both":
                diff = self.get_cost(route[i],route[i+1],"elevation_difference")	
            elif cost_type == "elevation_gain":
                diff = self.get_cost(route[i],route[i+1],"elevation_gain")
            elif cost_type == "elevation_drop":
                diff = self.get_cost(route[i],route[i+1],"elevation_drop")
            elif cost_type == "normal":
                diff = self.get_cost(route[i],route[i+1],"normal")
            total += diff
            if isPiecewise : 
                piece_elevation.append(diff)
        if isPiecewise:
            return total, piece_elevation
        else:
            return total

    

    def get_route(self, parent_node, dest):
        # Given parent and destination, returns the path
        path = [dest]
        curr = parent_node[dest]
        while curr!=-1:
            path.append(curr)
            curr = parent_node[curr]
        return path[::-1]


    def check_nodes(self):
        # Checks for null values in start or end node.
        if self.start_node is None or self.end_node is None:
            return False
        return True

    
    def bfs(self):

        G, x, shortest, elev_type = self.G, self.x, self.shortest_dist, self.elev_type
        start_node, end_node = self.start_node, self.end_node

        temp = [(0.0, 0.0, start_node)]
        seen = set()
        prior_info = {start_node: 0}
        parent_node = defaultdict(int)
        parent_node[start_node] = -1

        while temp:
            curr_prior, curr_dist, curr_n = heappop(temp)
            
            if curr_n not in seen:
                seen.add(curr_n)
                if curr_n == end_node:
                    break

                for n in G.neighbors(curr_n):
                    if n in seen: 
                        continue
                    
                    p = prior_info.get(n, None) 
                    e_length = self.get_cost(curr_n, n, "normal")
                    
                    # Dist between nodes is updated depending on maximize or minimize condition
                    if elev_type == "maximize":
                        if x <= 0.5:
                            next_node = e_length*0.1 + self.get_cost(curr_n, n, "elevation_drop")
                            next_node += curr_prior
                        else:
                            next_node = (e_length*0.1 - self.get_cost(curr_n, n, "elevation_difference"))* e_length*0.1
                    else:
                        next_node = e_length*0.1 + self.get_cost(curr_n, n, "elevation_gain")
                        next_node += curr_prior
                    
                    next_dist = curr_dist + e_length
                    
                    if next_dist <= shortest*(1.0+x) and (p is None or next_node < p):
                        parent_node[n] = curr_n
                        prior_info[n] = next_node
                        heappush(temp, (next_node, next_dist, n))   
        if not curr_dist : 
            return
        
        return parent_node,end_node,curr_dist
        




    # Computes the Dijkstra path
    def dijkstra_path(self):
        #Implements Dijkstra's Algorithm
        
        if not self.check_nodes() : 
            return
        parent_node,end_node,curr_dist=self.bfs()
        route = self.get_route(parent_node, end_node)
        elevation_dist, dropDist = self.get_Elevation(route, "elevation_gain"), self.get_Elevation(route, "elevation_drop")
        self.best = [route[:], curr_dist, elevation_dist, dropDist]

        return


    