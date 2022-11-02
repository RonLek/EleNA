import React, { Component } from 'react';

import { GeoSearchControl, OpenStreetMapProvider } from 'leaflet-geosearch'; 
import L from 'leaflet'; 
import 'leaflet-routing-machine'; 

import './App.css';
import './leaflet-geosearch.css'; 
import './leaflet-routing-machine.css'; 

const provider = new OpenStreetMapProvider(); 

export const AppContext = React.createContext({}); 

class App extends Component {
	constructor(props) {
		super(props); 
		this.state = {
			currLoc: '', 
			matches_start: [], 
			matches_end: [], 
			matches_cache_start: [], 
			matches_cache_end: [], 
			steep: 0, 
			route_distance: 0, 
			route_elevation: 0, 
			progress: false, 
			error: false
		}

		this.from = ''; 
		this.to = ''; 
		this.ratio = undefined; 
		this.cache = []; 

		this.marker_from = undefined; 
		this.marker_to = undefined; 

		this.fromInput = React.createRef(); 
		this.toInput = React.createRef(); 
	}

	componentDidMount() {
		this.map = this.initializeMap(); 
		this.addBaseMap(); 
		this.addSearchControl(); 
	}

	initializeMap = () => {
		let map = L.map('map', {
			zoom: 15, 
	        maxZoom: 15, 
	        attributionControl: true, 
	        zoomControl: true, 
	        doubleClickZoom: true,
	        scrollWheelZoom: true,
	        dragging: true,
	        animate: true,
	        easeLinearity: 0.35
		}); 
		return map; 
	}

	addBaseMap = () => {
		L.tileLayer('http://{s}.tile.osm.org/{z}/{x}/{y}.png').addTo(this.map); 
	}

	addSearchControl = () => {
		const searchControl = new GeoSearchControl({ provider: provider }); 
		searchControl.addTo(this.map); 
	}

	addToCache = (addr) => {
		if(this.cache.length > 10) this.cache.splice(10, this.cache.length); // keep top 10 cache results
		let idx = -1; 
		for(let i in this.cache) {
			if(addr.toLowerCase() === this.cache[i].toLowerCase()) {
				idx = i; 
				break; 
			}
		}
		if(idx >= 0) {
			this.cache.splice(idx, 1); 
		}
		this.cache.unshift(addr); 
	}

	validateInput = () => {
		if(this.fromInput.current.value === '') {
			this.fromInput.current.focus(); 
			return false; 
		}
		if(this.toInput.current.value === '') {
			this.toInput.current.focus(); 
			return false; 
		}
		return true; 
	}

	isDifferent = (prev_from, prev_to, from, to, prev_steep, steep) => {
		return prev_from !== from || prev_to !== to || prev_steep !== steep; 
	}

	steepChangeHandler = (e, value) => {
		this.setState({ steep: Math.floor(value/10)/10 })
	}

	clearMap = () => {
		if(this.marker_from !== undefined && this.marker_to !== undefined) {
	    	this.map.removeLayer(this.marker_from); 
	    	this.map.removeLayer(this.marker_to); 
	    }
	    for(let i in this.map._layers) {
	        if(this.map._layers[i]._path !== undefined) {
	            try {
	                this.map.removeLayer(this.map._layers[i]);
	            }
	            catch(e) {
	                console.log("problem with " + e + this.map._layers[i]);
	            }
	        }
	    }
    }

	render() {
		return (
			<AppContext.Provider value={{ cache: this.cache }}>
				<div className="App">
					<div id='map' style={{height: "100vh"}}></div>
				</div>
			</AppContext.Provider>
		);
	}
}

export default App;
