// # Building a Freeboard Plugin
//
// A freeboard plugin is simply a javascript file that is loaded into a web page after the main freeboard.js file is loaded.
//
// Let's get started with an example of a datasource plugin and a widget plugin.
//
// -------------------

// Best to encapsulate your plugin in a closure, although not required.
(function()
{
	// ## A Datasource Plugin
	//
	// -------------------
	// ### Datasource Definition
	//
	// -------------------
	// **freeboard.loadDatasourcePlugin(definition)** tells freeboard that we are giving it a datasource plugin. It expects an object with the following:


	// ## A Widget Plugin
	//
	// -------------------
	// ### Widget Definition
	//
	// -------------------
	// **freeboard.loadWidgetPlugin(definition)** tells freeboard that we are giving it a widget plugin. It expects an object with the following:
	freeboard.loadWidgetPlugin({
		// Same stuff here as with datasource plugin.
		"type_name"   : "winddir_plugin",
		"display_name": "Widget for Winddirection",
        "description" : "Show Wind direction and strength",
		// **external_scripts** : Any external scripts that should be loaded before the plugin instance is created.
		"external_scripts": [
			"https://www.amcharts.com/lib/3/amcharts.js",
            "https://www.amcharts.com/lib/3/gauge.js"
		],
		// **fill_size** : If this is set to true, the widget will fill be allowed to fill the entire space given it, otherwise it will contain an automatic padding of around 10 pixels around it.
		"fill_size" : false,
		"settings"    : [
			{
				"name"        : "direction",
				"display_name": "Wind Direction in Degree",
				// We'll use a calculated setting because we want what's displayed in this widget to be dynamic based on something changing (like a datasource).
				"type"        : "calculated"
			},
						{
				"name"        : "speed",
				"display_name": "Wind Speed in kt",
				"type"        : "calculated"
			},
			{
				"name"        : "direction_high",
				"display_name": "Wind Direction in Degree",
				// We'll use a calculated setting because we want what's displayed in this widget to be dynamic based on something changing (like a datasource).
				"type"        : "calculated"
			},
						{
				"name"        : "speed_high",
				"display_name": "Wind Speed in kt",
				"type"        : "calculated"
			},
			{
				"name"        : "runway",
				"display_name": "First Runway indicator",
				"type"        : "calculated"
			}
		],
		// Same as with datasource plugin, but there is no updateCallback parameter in this case.
		newInstance   : function(settings, newInstanceCallback)
		{
			newInstanceCallback(new WinddirPlugin(settings));
		}
	});

	// ### Widget Implementation
	//
	// -------------------
	// Here we implement the actual widget plugin. We pass in the settings;
	var WinddirPlugin = function(settings)
	{
		var self = this;
		var currentSettings = settings;

        var displayElement = $('<div id="chartdiv" style="width: 100%; height: 100%;" ></div>');
        //var speedElement = $('<div class="tw-value">---</div>');
        //var directionElement = $('<div class="tw-value">---</div>');

        var data = {
            "type": "gauge",
            "faceBorderColor": "#FFFFFF",
            "color": "#FFFFFF",
			"creditsPosition": "bottom-right",
			"marginBottom": 2,
			"marginLeft": 2,
			"marginRight": 2,
			"marginTop": 2,
            "arrows": [
            	{
                    "alpha": 0.49,
					"color": "#FF0000",
                    "id": "GaugeArrow-2",
                    "innerRadius": 0,
                    "nailRadius": 0,
                    "radius": "40%",
                    "startWidth": 9,
                    "value": 180
                },
                {
                    "color": "#FFFFFF",
                    "id": "GaugeArrow-1",
                    "innerRadius": 0,
                    "nailRadius": 6,
                    "radius": "50%",
                    "startWidth": 7,
                    "value": 0
                }
            ],
            "axes": [
                {
                    "axisColor": "#FFFFFF",
                    "bandOutlineColor": "#FFFFFF",
                    "bottomText": "- kt",
                    "bottomTextYOffset": -20,
                    "bottomTextFontSize":15,
                    "topText": "- kt high",
                    "topTextColor": "#FF0000",
                    "topTextFontSize": 10,
					"topTextYOffset": 20,
                    "endAngle": 360,
                    "endValue": 360,
                    "id": "GaugeAxis-1",
                    "showFirstLabel": false,
                    "startAngle": 0,
                    "tickColor": "#FFFFFF",
                    "unit": "°",
                    "valueInterval": 45,
                    "bands": [
						{
							"alpha": 0.7,
							"balloonText": "RWY 07",
							"color": "#00A2FF",
							"endValue": 5,
							"id": "GaugeBand-1",
							"innerRadius": "90%",
							"radius": "106%",
							"startValue": -5
						},
						{
							"alpha": 0.7,
							"balloonText": "RWY 25",
							"color": "#00A2FF",
							"endValue": 185,
							"id": "GaugeBand-1",
							"innerRadius": "90%",
							"radius": "106%",
							"startValue": 175
						}
					]
                }
            ],
            "allLabels": [],
            "balloon": {},
            "titles": []
        }
		// Here we create an element to hold the text we're going to display. We're going to set the value displayed in it below.


		// **render(containerElement)** (required) : A public function we must implement that will be called when freeboard wants us to render the contents of our widget. The container element is the DIV that will surround the widget.
		self.render = function(containerElement)
		{
			/*$(containerElement).empty();

			$(displayElement)
				.append($('<div class="tw-tr"></div>').append(speedElement))
				.append($('<div class="tw-tr"></div>').append(directionElement)
                );

			$(containerElement).append(displayElement);
            */
			$(containerElement).empty();
            $(containerElement).append(displayElement);

            //$(displayElement).append(AmCharts.makeChart("chartdiv",
            AmCharts.makeChart("chartdiv",data);


		    // Here we append our text element to the widget container element.
            //var myTextElement = $("<span>"+self.speed+"<strong>"+self.direction+"</strong></span>");
			//$(containerElement).append("<span>"+speed.toString()+"<strong>"+direction.toString()+"</strong></span>");
		}

		// **getHeight()** (required) : A public function we must implement that will be called when freeboard wants to know how big we expect to be when we render, and returns a height. This function will be called any time a user updates their settings (including the first time they create the widget).
		//
		// Note here that the height is not in pixels, but in blocks. A block in freeboard is currently defined as a rectangle that is fixed at 300 pixels wide and around 45 pixels multiplied by the value you return here.
		//
		// Blocks of different sizes may be supported in the future.
		self.getHeight = function()
		{
			return 4;
		}

		// **onSettingsChanged(newSettings)** (required) : A public function we must implement that will be called when a user makes a change to the settings.
		self.onSettingsChanged = function(newSettings)
		{
			// Normally we'd update our text element with the value we defined in the user settings above (the_text), but there is a special case for settings that are of type **"calculated"** -- see below.
			currentSettings = newSettings;
		}

		// **onCalculatedValueChanged(settingName, newValue)** (required) : A public function we must implement that will be called when a calculated value changes. Since calculated values can change at any time (like when a datasource is updated) we handle them in a special callback function here.
		self.onCalculatedValueChanged = function(settingName, newValue)
		{
			if(settingName == "direction")
			{
                data.arrows[1].setValue(newValue)
			}
			if(settingName == "speed")
			{
			    data.axes[0].setBottomText(newValue + " kt");
			}
			if(settingName == "direction_high")
			{
                data.arrows[0].setValue(newValue)
			}
			if(settingName == "speed_high")
			{
			    data.axes[0].setTopText(newValue + " kt high");
			}
			if(settingName == "runway")
			{
			    var size = 10 / 2;
			    var rwy = parseInt(newValue);
				data.axes[0].bands[0].setStartValue(rwy-size);
			    data.axes[0].bands[0].setEndValue(rwy+size);
				data.axes[0].bands[1].setStartValue(rwy+180-size);
			    data.axes[0].bands[1].setEndValue(rwy+180+size);
			}
			//AmCharts.update();
		}

		// **onDispose()** (required) : Same as with datasource plugins.
		self.onDispose = function()
		{
		}
	}
}());