ckan.module('ngsipreviewmap',function(jQuery,_){
    return{
	options:{
		i18n:{error:_('An error occurred: %(text)s %(error)s')},
		parameters:{contentType:'application/json',
                    dataType:'json',
			        dataConverter:function(data){return JSON.stringify(data,null,2);},
			        language:'json',type:'GET'}},
    initialize:function(){
        var self=this;
        var p;
        p=this.options.parameters;
        jQuery.ajax(preload_resource['url'],{
	        type:p.type,
	        contentType:p.contentType,
	        dataType:p.dataType,
	        success:function(data,textStatus,jqXHR){
	            var i;
	            var pos_list = new Array();
	            var listlat = new Array();
                var listlon = new Array();

	            if(typeof(data.contextResponses) != 'undefined'){
	                for(i=0;i<data.contextResponses.length;i++){
		                var attributes = data.contextResponses[i]['contextElement']['attributes'];
		                var lat = '';
		                var lon = '';
		                var e;
		                var info = new String();
		                for(e=0;e<attributes.length;e++){
			                if(attributes[e].name == 'position'){
				                var cd = attributes[e].value.split(",");
				                var dat = {}
                        	    dat.pos = [parseFloat(cd[1]),parseFloat(cd[0])];
                        	    dat.name = data.contextResponses[i]['contextElement']['id'];
	                            var x;
				                info += "<table style='font-size:85%;line-height:90%;'>";
        	                    for(x=0;x<attributes.length;x++){
                                    if (attributes[x].value.length < 35){
                                        info += "<tr><td><div><strong>"+attributes[x].name+" : </strong></div></td><td><div>"+attributes[x].value+"</div></td></tr>";
                                    }
                	            }
				                info += "</table>";
			        	        dat.attrib = info;
				                pos_list[pos_list.length] = dat;
				                listlat[listlat.length] = parseFloat(cd[0]);
				                listlon[listlon.length] = parseFloat(cd[1]);
			                }
                            if(attributes[e].type == 'urn:x-ogc:def:phenomenon:IDAS:1.0:latitude'){
                                lat = parseFloat(attributes[e].value);
                            }
                            if(attributes[e].type == 'urn:x-ogc:def:phenomenon:IDAS:1.0:longitude'){
                                lon = parseFloat(attributes[e].value);
                            }
		                }
		                if(lat.length != 0 && lon.length !=0){
			                var dat = {}
			                dat.pos = [lon,lat];
			                dat.name = data.contextResponses[i]['contextElement']['id'];
                            var x;
                            for(x=0;x<attributes.length;x++){
                                if (attributes[x].value.length < 35){
                                    info += "<div><strong>"+attributes[x].name+"</strong> : "+attributes[x].value+"</div>";
                                }
                            }
                            dat.attrib = info;
			                pos_list[pos_list.length] = dat;
			                listlat[listlat.length] = lat;
                            listlon[listlon.length] = lon;
		                }
	                }
	            }

                if (pos_list.length == 0){
                    document.getElementById('map').style.height = '0px';
	                document.getElementById('map').style.border = '0px';
                }

	            var iconStyle = new ol.style.Style({
		            image: new ol.style.Icon(/** @type {olx.style.IconOptions} */ ({
    			        anchor: [0.5, 46],
    			        anchorXUnits: 'fraction',
    			        anchorYUnits: 'pixels',
    			        opacity: 0.75,
    			        src: '/images/marker-icon.png'
  		            }))
	            });
	    
	            var z;
	            var feats = new Array();
    	        for(z=0;z<pos_list.length;z++){
	    	        var iconFeature = new ol.Feature({
  			            geometry: new ol.geom.Point(ol.proj.transform(pos_list[z].pos, 'EPSG:4326', 'EPSG:3857')),
  			            name: pos_list[z].name,
			            attrib: pos_list[z].attrib,
	    	        });
	    	        iconFeature.setStyle(iconStyle);
		            feats[feats.length] = iconFeature;
	            }

	            var vectorSource = new ol.source.Vector({features: feats});
	            var vectorLayer = new ol.layer.Vector({source: vectorSource});

	            var view = new ol.View({
                    center:ol.proj.transform([4.3753899,50.854975], 'EPSG:4326', 'EPSG:3857'),
                    zoom: 3,
                    minZoom:2,
	            });

	            var map = new ol.Map({
        	        view: view,
        	        layers: [
                	    new ol.layer.Tile({source: new ol.source.MapQuest({layer: 'osm'})}),
        		        vectorLayer
		            ],
        	        target: 'map'}
        	    );

	            var element = document.getElementById('popup');
	            var popup = new ol.Overlay({
  		            element: element,
  		                positioning: 'bottom-center',
  		                stopEvent: false
	            });
	            map.addOverlay(popup);

	            var feature;
	            // display popup on click
	            map.on('click', function(evt) {
		            feature = map.forEachFeatureAtPixel(evt.pixel,
      		        function(feature, layer){return feature;});
  		            if (feature) {
			            $(element).popover('destroy');
    			        $(element).popover({
				            'title':'<center><strong>'+feature.get('name')+'</strong></center>',
				            'delay': { show: 500, hide: 50 },
				            'html': true,
      				        'content': feature.get('attrib'),
    			        });
                        var geometry = feature.getGeometry();
                        var coord = geometry.getCoordinates();
			            popup.setPosition(coord);
    			        $(element).popover('show');
  		            }
  		            else {$(element).popover('destroy');}
	            });

                var maxlat = Math.max.apply(null, listlat);
                var minlat = Math.min.apply(null, listlat);
                var maxlon = Math.max.apply(null, listlon);
                var minlon = Math.min.apply(null, listlon);

                //centerzoom
                centerlat = (maxlat + minlat)/2;
                centerlon = (maxlon + minlon)/2;
                var autofocus = ol.proj.transform([centerlon, centerlat], 'EPSG:4326', 'EPSG:3857');

                //autozoom range 180 = zoom 0; range 0 = zoom 28
                rangelat = maxlat - minlat;
                rangelon = maxlon -  minlon;
                autozoomlat = (28)*(1-(1/180)*rangelat);
                autozoomlon = (28)*(1-(1/180)*rangelon);
                autozoom =  Math.min.apply(null,[Math.round(autozoomlat),Math.round(autozoomlon)]);
                if(autozoom >= 12){autozoom = 12;}

                function mapZoom(){
                    var pan = ol.animation.pan({
                        duration: 2000,
                        source: /** @type {ol.Coordinate} */ (view.getCenter())
                    });
                    map.beforeRender(pan);
                    view.setCenter(autofocus);

                    var zoom = ol.animation.zoom({
                        duration: 2000,
                        resolution: map.getView().getResolution()
                    });
                    map.beforeRender(zoom);
                    map.getView().setZoom(autozoom);
                }
                setTimeout(mapZoom, 2000);

        	    // change mouse cursor when over marker
	            map.on('pointermove', function(e) {
  	   	            if (e.dragging) {
  	   	                $(element).popover('destroy');
    			        return;
  		            }
  		            var pixel = map.getEventPixel(e.originalEvent);
  		            var hit = map.hasFeatureAtPixel(pixel);
  		            map.getTarget().style.cursor = hit ? 'pointer' : '';
	            });

	        },
            error:function(jqXHR,textStatus,errorThrown){
	            if(textStatus=='error'&&jqXHR.responseText.length){
		            document.getElementById('map').style.height = '0px';
                    document.getElementById('map').style.border = '0px';
                }
	            else{document.getElementById('map').style.height = '0px';;}}});}};});
