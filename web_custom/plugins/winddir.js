(function () {
    freeboard.loadWidgetPlugin({
        "type_name": "winddir_plugin",
        "display_name": "Widget for Winddirection",
        "description": "Show Wind direction and strength",
        "external_scripts": [
            "https://www.amcharts.com/lib/3/amcharts.js",
            "https://www.amcharts.com/lib/3/gauge.js"
        ],
        "fill_size": true,
        "settings": [
            {
                "name": "size",
                "display_name": "Size of Gauge",
                "type": "option",
                "options": [
                    {"name": "Small", "value":"small" },
                    {"name": "Big", "value":"big" }
                ]
            },
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
                "display_name": "High Wind Direction in Degree",
                "type": "calculated"
            },
            {
                "name": "speed_high",
                "display_name": "High Wind Speed in kt",
                "type": "calculated"
            },
            {
                "name": "gusts",
                "display_name": "Gusts",
                "type": "calculated"
            },
            {
                "name": "runway",
                "display_name": "First Runway indicator",
                "type": "calculated"
            },
            {
                "name": "error",
                "display_name": "If set to true, error gets displayed",
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
        var size = currentSettings.size;

        var values = {'dir':0, 'dir_high':0, 'wind':0, 'wind_high':0, 'error':false, 'gusts':false}

        var displayElement_small = $('<div id="chartdiv" style="width: 100%; height: 100%;" ></div>');
        var displayElement_big = $('<div id="chartdiv" style="width: 100%; height: 550px;" ></div>');
        var chart = null;

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
                    "color": "#ff0000",
                    "id": "RedArrow",
                    "innerRadius": "75%",
                    "nailRadius": 0,
                    "radius": "-50%",
                    "startWidth": 2,
                    "value": 180
                },
                {
                    "color": "#ff8000",
                    "id": "GaugeArrow-1",
                    "innerRadius": "70%",
                    "nailRadius": 0,
                    "radius": "-50%",
                    "startWidth": 16,
                    "value": 0
                },
                {
                    "color": "#ffffff",
                    "id": "GaugeArrow-1",
                    "innerRadius": "46%",
                    "nailRadius": 0,
                    "radius": "-50%",
                    "startWidth": 13,
                    "value": 0
                },
                {
                    "color": "#ff8000",
                    "id": "GaugeArrow-1",
                    "innerRadius": "22%",
                    "nailRadius": 0,
                    "radius": "-50%",
                    "startWidth": 10,
                    "value": 0
                },
                {
                    "color": "#ffffff",
                    "id": "GaugeArrow-1",
                    "innerRadius": "-2%",
                    "nailRadius": 0,
                    "radius": "-50%",
                    "startWidth": 7,
                    "value": 0
                },
                {
                    "color": "#ff8000",
                    "id": "GaugeArrow-1",
                    "innerRadius": "-26%",
                    "nailRadius": 0,
                    "radius": "-50%",
                    "startWidth": 4,
                    "value": 0
                }

            ],
            "axes": [
                {
                    "axisColor": "#FFFFFF",
                    "bandOutlineColor": "#FFFFFF",

                    "bottomText": "- kt hi",
                    "bottomTextColor": "#FF0000",
                    "bottomTextYOffset": -20,
                    "bottomTextFontSize": 17,
                    "topText": "- kt act",
                    "topTextFontSize": 22,
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
                            "balloonText": "RWY A",
                            "color": "#00A2FF",
                            "endValue": 5,
                            "id": "GaugeBand-1",
                            "innerRadius": "90%",
                            "radius": "106%",
                            "startValue": -5
                        },
                        {
                            "alpha": 0.7,
                            "balloonText": "RWY B",
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
            if(size == 'small') {
                $(containerElement).append(displayElement_small);
            } else {
                $(containerElement).append(displayElement_big);
                data.axes[0].bottomTextFontSize = data.axes[0].bottomTextFontSize * 2;
                data.axes[0].topTextFontSize = data.axes[0].topTextFontSize * 2;
                data.arrows[0].startWidth = data.arrows[0].startWidth * 2;

                for (var i = 1; i <= data.arrows.length-1; i++) {
                    data.arrows[i].startWidth = data.arrows[i].startWidth * 2;
                }
            }
            chart = AmCharts.makeChart("chartdiv", data);
        }
        self.getHeight = function () {
             if(size == 'small') {
                return 4;
            } else {
                return 9;
            }
        }

        self.onSettingsChanged = function (newSettings) {
            currentSettings = newSettings;
            size = newSettings.size;
        }

        self.onCalculatedValueChanged = function (settingName, newValue) {
            if (settingName == "direction") {
                values.dir = newValue;
                for (var i = 1; i <= data.arrows.length-1; i++) {
                    data.arrows[i].setValue(newValue);
                }
            }
            if (settingName == "speed") {
                values.wind = newValue;
            }
            if (settingName == "direction_high") {
                values.dir_high = newValue;
                data.arrows[0].setValue(newValue)
            }
            if (settingName == "speed_high") {
                values.wind_high = newValue
            }
            if (settingName == "gusts") {
                values.gusts = newValue
                if(size == 'small') {
                    data.arrows[0].startWidth = Math.round(newValue * 1.3, 0);
                } else {
                    data.arrows[0].startWidth = Math.round(newValue * 1.3, 0) * 2;
                }
            }
            if (settingName == "runway") {
                size = 10 / 2;
                var rwy = parseInt(newValue);
                data.axes[0].bands[0].setStartValue(rwy - size);
                data.axes[0].bands[0].setEndValue(rwy + size);
                data.axes[0].bands[0].balloonText = "RWY " + Math.round((rwy + 180) / 10);

                data.axes[0].bands[1].setStartValue(rwy + 180 - size);
                data.axes[0].bands[1].setEndValue(rwy + 180 + size);
                data.axes[0].bands[1].balloonText = "RWY " + Math.round(rwy / 10);

            }
            if (settingName == 'size') {
                size = newValue;
            }
            if (settingName == "error") {
                if(newValue) {
                    values.error = true;
                } else {
                    values.error = false;
                }
            }

            if (values.error) {
                chart.addLabel("50%", "122%", "! INOP !", "center", 60, "#FF0000", 5.4, 0.8, true, null);
            } else {
                chart.clearLabels();
            }

            data.axes[0].setBottomText(Math.round(values.wind_high,0) + " / " + Math.round(values.gusts, 0) + " kt hi" + "\n" + values.dir_high + '°');
            data.axes[0].setTopText(values.wind + " kt act" + "\n" + values.dir + '°');

        }

        self.onDispose = function () {
        }
    }
}());