import React, { Component } from 'react';

import ControlPanel from './components/ControlPanel'; 
import { GeoSearchControl, OpenStreetMapProvider } from 'leaflet-geosearch'; 
import L from 'leaflet'; 
import Locate from 'leaflet.locatecontrol';
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
		this.addLocateControl(); 
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

	addLocateControl = () => {
		const options = {
		  position: 'topright',
		  strings: {
		    title: ''
		  }
		}
		const locate = new Locate(options);
	    this.map.on('locationfound', this.handleLocationFound); 
	    locate.addTo(this.map);
	    locate.start()
	}

	handleLocationFound = e => {
		const currLoc = `${e.latlng.lat} ${e.latlng.lng}`; 
		this.addToCache('Your Location'); 
		if(this.state.matches_cache_start.length === 0 && this.state.matches_cache_end.length === 0) {
			this.setState({ currLoc: currLoc, matches_cache_start: ['Your Location'], matches_cache_end: ['Your Location'] }); 
		} else {
			this.setState({ currLoc: currLoc }); 
		}
	}

	addSearchControl = () => {
		const searchControl = new GeoSearchControl({ provider: provider }); 
		searchControl.addTo(this.map); 
	}

	addRoutingControl = async (e) => {
		e.preventDefault(); 
		if(!this.validateInput()) return; 

		let start = this.fromInput.current.value.trim().replace(/\s+/g,' '); 
		let end = this.toInput.current.value.trim().replace(/\s+/g,' '); 
		let currLoc = this.state.currLoc; 

		this.addToCache(start); 
		this.addToCache(end); 

		if(start === 'Your Location') start = currLoc; 
		if(end === 'Your Location') end = currLoc; 
		
		const from = start; 
		const to = end; 
		const ratio = this.state.steep; 
		const prev_from = this.from; 
		const prev_to = this.to; 
		const prev_ratio = this.ratio; 
		if(!this.isDifferent(prev_from, prev_to, from, to, prev_ratio, ratio)) return; 
		this.from = from; 
		this.to = to; 
		this.ratio = ratio; 

		this.setState({progress: true, error: false}); 
	 	let res = {}; 
	 	try {
	 		let response = await fetch('https://still-caverns-05146.herokuapp.com/search', {
				method: 'POST', 
				headers: { 'Content-Type': 'application/json' }, 
				body: JSON.stringify({origin: start, destination: end, ratio: this.state.steep})
			}); 
			res = await response.json(); 
	 	} catch(e) {
	 		this.setState({progress: false, error: true}); 
	 		console.error(e); 
	 		return; 
	 	}; 

	    let waypoints = res['waypoints']; 
	    this.clearMap(); 
		let latlngs = []; 
		for(let i in waypoints) {
			let waypoint = [waypoints[i].y, waypoints[i].x]
			if(i == 0) {
				this.marker_from = new L.Marker(waypoint).bindPopup(`<b>${this.fromInput.current.value}</b>`); 
		        this.map.addLayer(this.marker_from);
			} else if(i == waypoints.length-1) {
				this.marker_to = new L.Marker(waypoint).bindPopup(`<b>${this.toInput.current.value}</b>`); 
				this.map.addLayer(this.marker_to); 
			} else {
				L.circle(waypoint, {
					color: 'red',
				    fillColor: '#f03',
				    fillOpacity: 0.5,
				    radius: 20
				}).addTo(this.map); 
			}
			latlngs.push(L.latLng(waypoint[0], waypoint[1])); 
		}
		L.polyline(latlngs, {color: 'red'}).addTo(this.map); 
		this.map.setView(this.marker_to.getLatLng(), this.map.getZoom()); 
		this.setState({route_distance: res['route_distance'], route_elevation: res['route_elevation'], progress: false}); 
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
					<ControlPanel 
						state={this.state} 
						getPath={this.addRoutingControl} 
						fromInput={this.fromInput} 
						toInput={this.toInput} 
						steepChangeHandler={this.steepChangeHandler} 
					/>
				</div>
			</AppContext.Provider>
		);
	}
}

export default App;
