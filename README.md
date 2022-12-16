# Elevation Based Navigation System (EleNa)
Elevation Based Navigation System (EleNa) is a web application that aims to provide users hiking/trekking routes between any two points on a map. The routes can be tuned to either maximize or minimize elevation and the user can specify the percentage of elevation. EleNa provides a traditional shortest path route as well. 

# Installation and set up

### Requirements
The application has the following requirements -
1. osmnx (0.11.4)
2. networkx (2.4)
3. Flask (1.1.1)
4. numpy (1.18.1)
5. geopy (1.21.0)

The requirements can be installed with pip

pip install -r requirements.txt


# Running and testing the application

### Using the application
- Clone the git repository from `GIT LINKKKKKKKKKKKKKK`
- Make `start` an executable by running `chmod +x start`
- ./start To start up the application. 
- Head over to `http://127.0.0.1:5000/home` on preferably Google Chrome to use the web interface.

HOME PAGE PICTURE
![EleNa Interface](home-page.png)

### Interacting with the UI
- The start and end points can be set by clicking on the map.
- The percentage (x%) of shortest distance that the user wants to go extra can be entered in the entry field.
- The corresponding radio buttons for the minimization or maximization of elevation can be selected. 
- Once all the inputs are given, clicking the "Calculate" button will display the computed shortest path in blue and the path with elevation in red.
- Statistics about the path will also be shown on the UI. 
- Clicking the "Reset" button will clear the UI of all inputs and paths. 
- To make any change to inputs such as source, destination or x% the user should "Reset" the UI then enter the updated values and click on "Calculate" button to recompute the paths.

### Back-end Logic

- The backend computes the paths using two algorithms - Dijkstra and A* algorithm. The final path returned is the best of the two for the given elevation data. 


### Testing 
- To run the tests run `python test/test.py` from the home directory.

# Exterminators_520

- `Rohan Lekhwani`
- `Arunima Sundar`
- `Kalyani Patle`
- `Anirudh Lakkaraju`