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


    def backtrack(self, f_node, c_node):
        # Plots and reconnects the path
        if not f_node or not c_node : 
            return
        all_n = [c_node]
        while c_node in f_node:
            c_node = f_node[c_node]
            all_n.append(c_node)
        
        self.best = [all_n[:], self.get_Elevation(all_n, "normal"), self.get_Elevation(all_n, "elevation_gain"), self.get_Elevation(all_n, "elevation_drop")]
        return


    def costInitialization(self, G):
        
        cost = {}

        for node in G.nodes():
            cost[node] = float("inf")
        
        cost[self.start_node] = 0 

        return cost


    def a_star_path(self):
        # Computes the A* path.  
        eval_node = set()      
        not_evaluated = set() 
        least_cost_node = {} 
        weighted_edge = {} 


        if not self.check_nodes() : 
            return
        G, minimum_dist= self.G, self.shortest_dist
        x, elev_type = self.x, self.elev_type
        start_node= self.start_node
        end_node = self.end_node
        
        costToStart = self.costInitialization(G) 

        not_evaluated.add(start_node)
                
        costToStart1 = self.costInitialization(G)

        weighted_edge[start_node] = G.nodes[start_node]['dist_from_dest']*0.1
        
        while len(not_evaluated):
            curr_node = min([(node,weighted_edge[node]) for node in not_evaluated], key=lambda t: t[1])[0]            
            if curr_node == end_node:
                self.backtrack(least_cost_node, curr_node)
                return
            
            not_evaluated.remove(curr_node)
            eval_node.add(curr_node)
            for n in G.neighbors(curr_node):
                if n in eval_node: 
                    continue 
                if elev_type == "minimize":
                    pred_costToStart = costToStart[curr_node] + self.get_cost(curr_node, n, "elevation_gain")
                elif elev_type == "maximize":
                    pred_costToStart = costToStart[curr_node] + self.get_cost(curr_node, n, "elevation_drop")

                pred_costToStart1 = costToStart1[curr_node] + self.get_cost(curr_node, n, "normal")

                if n not in not_evaluated and pred_costToStart1<=(1+x)*minimum_dist:# Discover a new node
                    not_evaluated.add(n)
                else: 
                    if (pred_costToStart >= costToStart[n]) or (pred_costToStart1>=(1+x)*minimum_dist):
                        continue 

                least_cost_node[n] = curr_node
                costToStart[n] = pred_costToStart
                costToStart1[n] = pred_costToStart1
                weighted_edge[n] = costToStart[n] + G.nodes[n]['dist_from_dest']*0.1


    def compare(self, G, shortestPathStats):

        if (self.elev_type == "maximize" and self.best[2] == float('-inf')) or (self.elev_type == "minimize" and self.best[3] == float('-inf')):            
            return shortestPathStats, [[], 0.0, 0, 0]
        
        self.best[0] = [[G.nodes[route_node]['x'],G.nodes[route_node]['y']] for route_node in self.best[0]]

        # If computed path does not match the requirements
        if((self.elev_type == "maximize" and self.best[2] < shortestPathStats[2]) or (self.elev_type == "minimize" and self.best[2] > shortestPathStats[2])):
            self.best = shortestPathStats
        
        return shortestPathStats, self.best


    def get_shortest_path(self, spt, ept, x, elev_type = "maximize", log=True):
        
        # Computes Shortest Path
        G = self.G
        self.x = x/100.0
        self.elev_type = elev_type
        self.start_node, self.end_node = None, None

        if elev_type == "maximize": 
            self.best = [[], 0.0, float('-inf'), float('-inf')]
        else:
            self.best = [[], 0.0, float('inf'), float('-inf')]

        # Obtains shortest path
        self.start_node, d1 = ox.get_nearest_node(G, point=spt, return_dist = True)
        self.end_node, d2   = ox.get_nearest_node(G, point=ept, return_dist = True)

        # returns distance based shortest path
        self.shortest_route = nx.shortest_path(G, source=self.start_node, target=self.end_node, weight='length')
        
        self.shortest_dist  = sum(ox.get_route_edge_attributes(G, self.shortest_route, 'length'))
        
        shortest_route_latlong = [[G.nodes[route_node]['x'],G.nodes[route_node]['y']] for route_node in self.shortest_route] 
        
        shortestPathStats = [shortest_route_latlong, self.shortest_dist, \
                            self.get_Elevation(self.shortest_route, "elevation_gain"), self.get_Elevation(self.shortest_route, "elevation_drop")]

        
        if(x == 0):
            return shortestPathStats, shortestPathStats

        start_time = time.time()
        self.dijkstra_path()
        end_time = time.time()
        dijkstra_way = self.best
        if log:
            print()
            print("Statics - Dijkstra's route")
            print(dijkstra_way[1])
            print(dijkstra_way[2])
            print(dijkstra_way[3])
            print("--- Time taken = %s seconds ---" % (end_time - start_time))

        if elev_type == "maximize": 
            self.best = [[], 0.0, float('-inf'), float('-inf')]
        else:
            self.best = [[], 0.0, float('inf'), float('-inf')]

        start_time = time.time()
        self.a_star_path()
        end_time = time.time()
        a_star_way = self.best
        if log:
            print()
            print("Statics - A star route")
            print(a_star_way[1])
            print(a_star_way[2])
            print(a_star_way[3])
            print("--- Time taken = %s seconds ---" % (end_time - start_time))

            print()

        if self.elev_type == "maximize":
            if (dijkstra_way[2] > a_star_way[2]) or (dijkstra_way[2] == a_star_way[2] and dijkstra_way[1] < a_star_way[1]):
                self.best = dijkstra_way
                if log:
                    print("The Dijkstra algorithm computes the best possible route")
                    print()
            else:
                self.best = a_star_way
                if log:
                    print("The A star algorithm computes the best possible route")
                    print()
        else:
            if (dijkstra_way[2] < a_star_way[2]) or (dijkstra_way[2] == a_star_way[2] and dijkstra_way[1] < a_star_way[1]):
                self.best = dijkstra_way
                if log:
                    print("The Dijkstra algorithm computes the best possible route")
                    print()
            else:
                self.best = a_star_way
                if log:
                    print("The A star algorithm computes the best possible route")
                    print()

        return self.compare(G, shortestPathStats)
