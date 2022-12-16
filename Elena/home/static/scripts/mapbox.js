function reset()
{
    document.getElementById('start').innerHTML ="Start Location: ";
    document.getElementById('end').innerHTML ="End Location: ";
    document.getElementById('calc_route').innerHTML ="Calculate"
    document.getElementById("calc_route").disabled = true;
    document.getElementById('x').value = 0;
    document.getElementById('info').style.height = "135px";
    document.getElementById('end').style.top = "185px";
    document.getElementById('start').style.top = "155px";
    start_loc="";
    start_flag=false;
    end_loc="";
    m1.remove();
    m2.remove();
    end_flag=false;
    points = turf.featureCollection([]);
    map.getSource('circleData').setData(points);
    if (map.getLayer("shortest_route")){
        map.removeLayer("shortest_route");
    }

    if (map.getSource("shortest_route")){
        map.removeSource("shortest_route");
    }

    if (map.getLayer("ele_route")){
        map.removeLayer("ele_route");
    }

    if (map.getSource("ele_route")){
        map.removeSource("ele_route");
    }

    document.getElementById('gain_1').innerHTML="";
    document.getElementById('gain_2').innerHTML="";
    document.getElementById('drop_1').innerHTML="";
    document.getElementById('drop_2').innerHTML="";
    document.getElementById('dist_1').innerHTML="";
    document.getElementById('dist_2').innerHTML="";

}
function calc_route_reset()
{
    
    if (map.getLayer("shortest_route")){
        map.removeLayer("shortest_route");
    }

    if (map.getSource("shortest_route")){
        map.removeSource("shortest_route");
    }

    if (map.getLayer("ele_route")){
        map.removeLayer("ele_route");
    }

    if (map.getSource("ele_route")){
        map.removeSource("ele_route");
    }

    document.getElementById('gain_1').innerHTML="";
    document.getElementById('gain_2').innerHTML="";
    document.getElementById('drop_1').innerHTML="";
    document.getElementById('drop_2').innerHTML="";
    document.getElementById('dist_1').innerHTML="";
    document.getElementById('dist_2').innerHTML="";

}
document.getElementById('reset').onclick=reset;
function handleData(data)
{   
    if (data["popup_flag"]==0)  
    {
        var temp=confirm("Selected locations do not have neighboring nodes in underlying graph.Please select different points.");
        return; print(elevation_profile_elenav)
    }  
    console.log(data["popup_flag"])
    
    if (data["popup_flag"]==1)  
    {
        var temp=confirm("Could not find a path optimizing elevation for the given threshold (Plotting just the shortest path.).");
        
    }
    
    map.addSource("ele_route", {
        "type": "geojson",
        "data": data["elevation_route"]
    });

    map.addLayer({
        "id": "ele_route",
        "type": "line",
        "source": "ele_route",
        "layout": {
            "line-join": "round",
            "line-cap": "round"
        },
        "paint": {
            "line-color": "green",
            "line-width": 2,
            "line-dasharray": [3, 3]
        }
    });

    map.addSource("shortest_route", {
        "type": "geojson",
        "data": data["shortest_route"]
    });

    map.addLayer({
        "id": "shortest_route",
        "type": "line",
        "source": "shortest_route",
        "layout": {
            "line-join": "round",
            "line-cap": "round"
        },
        "paint": {
            "line-color": "Blue",
            "line-width": 2
        }
    });
    console.log("Routes Drawn");
    document.getElementById('info').style.height = "260px";
    document.getElementById('start').innerHTML = "Start Location: " + data["start"];
    document.getElementById('end').innerHTML = "End Location: " + data["end"];
    document.getElementById('end').style.top = "245px";
    document.getElementById('start').style.top = "150px";
    document.getElementById('calc_route').innerHTML ="Re-Calculate";
    document.getElementById('gain_1').innerHTML= data["gainElenav"].toFixed(2) + 'm';
    document.getElementById('drop_1').innerHTML= data["dropElenav"].toFixed(2) + 'm';
    document.getElementById('dist_1').innerHTML= data["elenavDist"].toFixed(2) + 'm';
    document.getElementById('gain_2').innerHTML= data["gainShort"].toFixed(2) + 'm';
    document.getElementById('drop_2').innerHTML= data["dropShort"].toFixed(2) + 'm';
    document.getElementById('dist_2').innerHTML= data["shortDist"].toFixed(2) + 'm';

}

document.getElementById('calc_route').onclick=function(){                
    var checkedValue = $('.check:checked').val();  
    console.log(document.getElementById('x').value) ;             
    var input_data='{"start_location":'+start_loc+',"x":'+document.getElementById('x').value+',"end_location":'+end_loc+',"min_max":"'+checkedValue.toString()+'"}';                
    
    $('#loading').show();
    calc_route_reset();
    $.ajax({
        type: "POST",
        url: '/route',
        data: input_data,
        success: function(data){
            $('#loading').hide();
            console.log("POST SUCCESS");                         
            handleData(data);                        
        },
        dataType: "json"
    });
};