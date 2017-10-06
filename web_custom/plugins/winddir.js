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
        var speedElement = $('<div class="tw-value">---</div>');
        var directionElement = $('<div class="tw-value">---</div>');

        var data = {
            "type": "gauge",
            "faceBorderColor": "#FFFFFF",
            "color": "#FFFFFF",
            "arrows": [
                {
                    "color": "#FFFFFF",
                    "id": "GaugeArrow-1",
                    "innerRadius": 0,
                    "nailRadius": 0,
                    "radius": "50%",
                    "startWidth": 7,
                    "value": 0
                }
            ],
            "axes": [
                {
                    "axisColor": "#FFFFFF",
                    "bandOutlineColor": "#FFFFFF",
                    "bottomText": "0 kt",
                    "bottomTextYOffset": -20,
                    "bottomTextFontSize":15,
                    "endAngle": 360,
                    "endValue": 360,
                    "id": "GaugeAxis-1",
                    "showFirstLabel": false,
                    "startAngle": 0,
                    "tickColor": "#FFFFFF",
                    "unit": "°",
                    "valueInterval": 45,
                    "bands": []
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
			// Remember we defined "the_text" up above in our settings.
			if(settingName == "direction")
			{
				// Here we do the actual update of the value that's displayed in on the screen.
				//$(myTextElement).html(newValue);
                directionElement.text(newValue);//newValue;
                data.arrows[0].setValue(newValue)
			}
						// Remember we defined "the_text" up above in our settings.
			if(settingName == "speed")
			{
				// Here we do the actual update of the value that's displayed in on the screen.
				//$(myTextElement).html('<strong>'+newValue+'</strong>');
                //speedElement.text(newValue);//newValue;
                //data.axes.bottomText = newValue+" kt"
			    data.axes[0].bottomText = newValue+" kt"; //.setValue(newValue+" kt")
			}
			AmCharts.update();
		}

		// **onDispose()** (required) : Same as with datasource plugins.
		self.onDispose = function()
		{
		}
	}
}());