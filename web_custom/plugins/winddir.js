(function () {
    freeboard.loadWidgetPlugin({
        "type_name": "winddir_plugin",
        "display_name": "Widget for Winddirection",
        "description": "Show Wind direction and strength",
        "external_scripts": [
            "https://www.amcharts.com/lib/3/amcharts.js",
            "https://www.amcharts.com/lib/3/gauge.js"
        ],
        "fill_size": false,
        "settings": [
            {
                "name": "direction",
                "display_name": "Wind Direction in Degree",
                "type": "calculated"
            },
            {
                "name": "speed",
                "display_name": "Wind Speed in kt",
                "type": "calculated"
            },
            {
                "name": "direction_high",
                "display_name": "Wind Direction in Degree",
                "type": "calculated"
            },
            {
                "name": "speed_high",
                "display_name": "Wind Speed in kt",
                "type": "calculated"
            },
            {
                "name": "runway",
                "display_name": "First Runway indicator",
                "type": "calculated"
            }
        ],
        // Same as with datasource plugin, but there is no updateCallback parameter in this case.
        newInstance: function (settings, newInstanceCallback) {
            newInstanceCallback(new WinddirPlugin(settings));
        }
    });

    // ### Widget Implementation
    //
    // -------------------
    var WinddirPlugin = function (settings) {
        var self = this;
        var currentSettings = settings;

        var displayElement = $('<div id="chartdiv" style="width: 100%; height: 100%;" ></div>');

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
                    "bottomTextFontSize": 15,
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


        self.render = function (containerElement) {
            $(containerElement).empty();
            $(containerElement).append(displayElement);
            AmCharts.makeChart("chartdiv", data);
        }
        self.getHeight = function () {
            return 4;
        }

        self.onSettingsChanged = function (newSettings) {
            currentSettings = newSettings;
        }

        self.onCalculatedValueChanged = function (settingName, newValue) {
            if (settingName == "direction") {
                data.arrows[1].setValue(newValue)
            }
            if (settingName == "speed") {
                data.axes[0].setBottomText(newValue + " kt");
            }
            if (settingName == "direction_high") {
                data.arrows[0].setValue(newValue)
            }
            if (settingName == "speed_high") {
                data.axes[0].setTopText(newValue + " kt high");
            }
            if (settingName == "runway") {
                var size = 10 / 2;
                var rwy = parseInt(newValue);
                data.axes[0].bands[0].setStartValue(rwy - size);
                data.axes[0].bands[0].setEndValue(rwy + size);
                data.axes[0].bands[1].setStartValue(rwy + 180 - size);
                data.axes[0].bands[1].setEndValue(rwy + 180 + size);
            }
        }

        self.onDispose = function () {
        }
    }
}());