var generatedVegaSpec = {}
var visualizationData = []
var generatedVegaSpecEncoding = {};
var serverUrl = ""

$(function () {
    var toastNotificationSelector
    var toastNotification
    CarbonComponents.settings.disableAutoInit = true;
    toastNotificationSelector = document.querySelector('[data-notification]');
    toastNotification = CarbonComponents.Notification.create(toastNotificationSelector);


    var exampleProgressBarColor = "#152934"
    var numExampleGraphsPerRow = 10
    // Assign the specification to a local variable vlSpec.
    var exampleGraphWidth = 150
    var exampleGraphHeight = 100;

    var loadDuration = 5000;
    var firstLoad = false
    var loadeddivcount = 1;
    var numGraphs = 10;

    var generatedDataHolder;

    // loadExamplesData() 

    var testResultHolder = []
    var modelName = ""
    var testIndex = 0;
    var validJsonCount = 0;
    var validJsonArray = []
    var validVegaspecCount = 0;
    var validVegaspecArray = [];
    var beamWidth = 0;
    var phantomVariableCount = 0;
    var phantomVariableArray = [];
    var maxTestDataCount = 100;


    /**
     * JS Script to load up random Vegalite data from server and display charts
     * 
     */

    // Assign the specification to a local variable vlSpec.
    var graphWidth = $(".vizbox").width();
    var graphHeight = 300;
    var loadDuration = 5000;
    var firstLoad = false


    hideLoading(".rnnsampleloader")
    hideLoading("#graph_loading_overlay")

    // generate set of examples
    $(".generateexamplesbutton").click(function () {
        numInputExamples = $(".numexamplesinput").val()
        if (numInputExamples != "" && numInputExamples <= 50) {
            numGraphs = numInputExamples * 1
        }
        $(".examplebox").empty()
        $(".vizbox").empty()
        loadeddivcount = 1;
        $(".exampleprogressbarinner").width(0);
        $(".exampleprogressbarinner").css('background-color', exampleProgressBarColor)
        showLoading(".rnnsampleloader")
        loadExamplesData()
        sendGAEvent("button", "click", "generate examples set " + numInputExamples)

    });

    // run test suite
    $(".runtestbutton").click(function () {
        loadTestSuiteData()
    });


    function resetTestCounters() {
        validJsonCount = 0;
        validVegaspecCount = 0;
        beamWidth = 0;
        phantomVariableCount = 0;

        validJsonArray = []
        validVegaspecArray = [];
        phantomVariableArray = [];
    }

    // send test results for a model and beam to server
    function sendTestResults() {
        showLoading("#graph_loading_overlay")
        $.ajax({
            url: serverUrl + "/savetest",
            type: "POST",
            contentType: "application/json",
            data: JSON.stringify({
                "index": testIndex,
                "model": modelName,
                "beamwidth": beamWidth,
                "data": testResultHolder
            })
        }).done(function (result) {
            console.log("Test Results save: ", result)
            hideLoading("#graph_loading_overlay")

        }).fail(function (xhr, status, error) {
            $(".vizbox").fadeOut("slow")
            hideLoading("#graph_loading_overlay")
            showNotification("Error Reaching Model Server", status, error + ".Might have to try again later.")
        });;
    }

    // Fetch test100 dataset
    function loadTestSuiteData() {
        resetTestCounters()

        showLoading("#graph_loading_overlay")
        $.ajax({
            url: serverUrl + "/testhundred",
            type: "POST",
            contentType: "application/json",
            data: JSON.stringify({
                "index": testIndex
            })
        }).done(function (result) {
            if (result.status) {
                $(".sourcedata").val(JSON.stringify(result.data))
                modelName = result.model
                visualizationData = result;
                testIndex++;
                loadGeneratedData(true)
            } else {
                result = JSON.parse(JSON.stringify(result))
                showNotification("An Error Occurred", result.reason, error + ".")
            }

        }).fail(function (xhr, status, error) {
            $(".vizbox").fadeOut("slow")
            hideLoading("#graph_loading_overlay")
            showNotification("Error Reaching Model Server", status, error + ".Might have to try again later.")
        });;
    }


    // generate single updateable example
    $(".generateseqbutton").click(function () {
        loadGeneratedData()
        sendGAEvent("button", "click", "generate button dataset")
    });

    // loadExamplesData()
    $(".laodsampledataset").click(function () {
        loadSampleData()
        sendGAEvent("button", "click", "load sample dataset")
    });

    $(".documentationdemolink").click(function () {
        $(".sidelink#modifyviz").click()
        sendGAEvent("link", "click", "view demo")
    });

    $(".documentationexamplelink").click(function () {
        sendGAEvent("link", "click", "view documentation")
    });
    // Enable/disable Generate button if data is in input box
    jQuery('.sourcedata').on('input propertychange paste', function () {
        sendGAEvent("input", "paste", "paste or update input data")
        if ($(this).val() == "") {
            $(".generateseqbutton").attr("disabled", "disabled");
        } else {
            $(".generateseqbutton").removeAttr("disabled")
        }
    });

    $('body').on('mouseover', '.beambox', function (event) {
        theid = $(this).attr("id")
        $(".vizbeambox").removeClass("border")
        $(".vizbeambox#" + "divbox" + theid).addClass("border");
    });

    // Enable/disable update visualization button if data is in input box
    jQuery('.vegaoutput').on('input propertychange paste', function () {
        sendGAEvent("input", "paste", "paste or update output visualization spec")
        if ($(this).val() == "") {
            $(".updatevizbutton").attr("disabled", "disabled");
        } else {
            $(".updatevizbutton").removeAttr("disabled")
        }
    });

    // Update the visualization using the vegaspec in the vegabox
    $(".updatevizbutton").click(function () {
        currentVegaspec = JSON.parse($(".vegaoutput").val())
        currentVegaspec.data = visualizationData
        // console.log(currentVegaspec)
        loadVisualization(currentVegaspec)
    });

    function loadSampleData() {
        showLoading("#graph_loading_overlay")
        $.ajax({
            url: serverUrl + "/testdata",
            data: {}
        }).done(function (result) {
            $(".sourcedata").val(JSON.stringify(result))
            visualizationData = result;
            loadGeneratedData(false)
        }).fail(function (xhr, status, error) {
            $(".vizbox").fadeOut("slow")
            hideLoading("#graph_loading_overlay")
            showNotification("Error Reaching Model Server", status, error + ".Might have to try again later.")
        });;
    }

    function loadGeneratedData(isTestSuite) {
        showLoading("#graph_loading_overlay")
        $(".beamboxdiv").fadeOut()
        $(".beamthing").fadeOut()
        var sourcedata = ($("textarea#sourcedata").val())
        if (!isValidJSON(sourcedata)) {
            showNotification("BAD Input Data Format", " Bad Input", "Please enter a valid JSON array without nesting.")
            hideLoading("#graph_loading_overlay");
            return
        }

        beamindex = 0;

        var payload = {
            sourcedata: sourcedata
        }
        // Load vlSpec from Server
        $.ajax({
            url: serverUrl + "/inference",
            type: "POST",
            contentType: "application/json",
            data: JSON.stringify(payload)
        }).done(function (result) {
            hideLoading("#graph_loading_overlay")
            // result = JSON.parse(result)
            $(".beamboxdiv").fadeIn();
            validJsonCount = 0;

            if (result.status) {
                $(".vizbox").empty();
                $(".beamboxdiv").empty();

                $(".vizbox").show();
                var specholder
                try {
                    vegavals = JSON.parse(result.vegaspec);
                } catch (e) {
                    console.log("JSON parse error parsing array")
                }

                beamWidth = vegavals.length;

                vegavals.forEach(function (vegaspec) {
                    var $beamboxsub = $("<div id='" + beamindex + "' class='beambox'> </div>")
                    try {
                        var spec = JSON.parse(vegaspec);
                        specholder = Object.assign({}, spec);
                        spec["data"] = {
                            "values": result.data
                        };
                        // console.log(typeof (spec), "======", spec);
                        loadBeam(spec, beamindex, specholder);
                        $beamboxsub.addClass("bottomgreen").attr("tooltip", "Valid JSON Generated.")
                        validJsonCount++
                        validJsonArray.push(true)
                    } catch (e) {
                        validJsonArray.push(false)
                        // console.log("JSON parse error .. parsing spec", beamindex)
                        $beamboxsub.addClass("bottomred").attr("tooltip", "InValid JSON .. Oops")
                    }

                    $beamboxsub.text(vegaspec);
                    beamindex++


                    $(".beamboxdiv").append($beamboxsub);

                });

                headertext = "<strong> [ " + validJsonCount + " / " + vegavals.length + " ]</strong>  generated visualization specifications are valid JSON. Specifications are generated using <a href='https://machinelearningmastery.com/beam-search-decoder-natural-language-processing/'>Beam Search</a>  (width = " + vegavals.length + "). "
                $(".generatedvizheader").text("Generated Visualization Grammar ")
                $(".resultupdate").html(headertext)
                $(".beamthing").fadeIn()

                // if we are running a test suite, we continue for iterations.
                if (isTestSuite) {
                    setTimeout(function () {
                        testResult = {
                            "beamwidth": beamWidth,
                            "validjsoncount": validJsonCount,
                            "validjsonarray": validJsonArray,
                            "validvegacount": validVegaspecCount,
                            "validvegaarray": validVegaspecArray,
                            "phantomcount": phantomVariableCount,
                            "phantomarray": phantomVariableArray
                        }
                        testResultHolder.push(testResult)
                        console.log(testIndex, " of ", maxTestDataCount, " Loading next test data", testResult)
                        if (testIndex < maxTestDataCount) {
                            loadTestSuiteData()
                        } else {
                            sendTestResults()
                        }
                    }, 800)
                }



            } else {
                result = JSON.parse(JSON.stringify(result))
                showNotification("An Error Occurred", result.reason, error + ".")
            }


        }).fail(function (xhr, status, error) {
            $(".vizbox").fadeOut("slow")
            hideLoading("#graph_loading_overlay")
            showNotification("Error Reaching Model Server", status, error + ".Might have to try again later.")

        });;
    }

    function loadBeam(vlSpec, beamindex, specholder) {

        specString = JSON.stringify(specholder)
        containsPhantom = specString.includes("str") && !isNaN(specString.charAt(specString.indexOf("str") + 3)) || specString.includes("num") && !isNaN(specString.charAt(specString.indexOf("num") + 3))
        phantomContent = containsPhantom ? " Model generated a phantom field." : "No phantom field generated."
        phantomClass = containsPhantom ? "bottomred" : "bottomgreen"
        tooltip = containsPhantom ? "Phantom field generated." : "No Phantom field."

        if (containsPhantom) {
            phantomVariableCount++
            phantomVariableArray.push(true)
        } else {
            phantomVariableArray.push(false)
        }

        exampleGraphWidth = 150
        vlSpec.width = exampleGraphWidth
        vlSpec.height = exampleGraphHeight
        var opt = {
            "mode": "vega-lite",
            "actions": true,
            "width": exampleGraphWidth,
            "height": exampleGraphHeight
        };

        divid = "divbox" + beamindex
        var $vizsubbox = $("<div id='" + divid + "' class=' " + phantomClass + " vizbeambox beamgraphbox iblock'></div>")
        $vizsubbox.attr("tooltip", tooltip)

        $(".vizbox").append($vizsubbox)
        // $vizsubbox.hide()

        vegaEmbed(".vizbeambox#" + divid, vlSpec, opt).then(function (result) {
            validVegaspecCount++
            validVegaspecArray.push(true)
        }).catch(function (err) {
            // reloadData()
            validVegaspecArray.push(false)
        });

    }

    function loadVisualization(vlSpec) {

        // check if we likely have a phantomfield
        specString = $(".vegaoutput").val()
        containsPhantom = specString.includes("str") && !isNaN(specString.charAt(specString.indexOf("str") + 3)) || specString.includes("num") && !isNaN(specString.charAt(specString.indexOf("num") + 3))
        phantomContent = containsPhantom ? " Model generated a phantom field." : "No phantom field generated."
        phantomClass = containsPhantom ? "outputeval phantomred" : "outputeval phantomgreen"
        $(".outputeval").text(phantomContent);
        $(".outputeval").attr("class", phantomClass);

        graphWidth = $(".vizbox").width();
        vlSpec.width = graphWidth
        vlSpec.height = graphHeight
        vlSpec.autosize = {
            "type": "fit",
            "contains": "padding"
        }
        // optional argument passed to Vega-Embed to specify vega-lite spec. More info at https://github.com/vega/vega-embed
        var opt = {
            "mode": "vega-lite"
        };

        $(".vizbox").fadeOut("slow", function () {
            // Embed the visualization in the container with id `vis`
            vegaEmbed("#vis", vlSpec, opt).then(function (result) {
                // Callback receiving the View instance and parsed Vega spec
                // result.view is the View, which resides under the '#vis' element
                $(".vizbox").fadeIn("slow")
            }).catch(console.warn);

        })
    }

    function loadExamplesData() {
        $.ajax({
            url: serverUrl + "/examplesdata"
        }).done(function (result) {
            // alert(JSON.stringify(result))
            loadExampleVisualization(result.vegaspec)
        }).fail(function (xhr, status, error) {
            // error handling
            console.log("Eroor fetchng data!!")
        });;
    }



    function loadExampleVisualization(vlSpec) {
        exampleGraphWidth = ($(".examplebox").width()) / numExampleGraphsPerRow;
        loadStatus = loadeddivcount + " / " + numGraphs
        progressBarWidth = (loadeddivcount / numGraphs) * $(".exampleprogresbarouter").width()
        $(".exampleprogressbarinner").width(progressBarWidth)
        $(".examplesStatus").text(loadStatus)
        vlSpec.width = exampleGraphWidth
        vlSpec.height = exampleGraphHeight
        var opt = {
            "mode": "vega-lite",
            "actions": false,
            "width": exampleGraphWidth,
            "height": exampleGraphHeight
        };

        divid = "divbox" + loadeddivcount
        $vizsubbox = $("<div id='" + divid + "' class='vizsubbox'></div>")

        $(".examplebox").append($vizsubbox)
        $vizsubbox.hide()

        vegaEmbed(".vizsubbox#" + divid, vlSpec, opt).then(function (result) {
            // Callback receiving the View instance and parsed Vega spec
            // result.view is the View, which resides under the '#vis' element
            $vizsubbox.fadeIn("slow")
            reloadData()

        }).catch(function (err) {
            reloadData()
        });

    }

    function reloadData() {
        if (loadeddivcount < numGraphs) {
            loadExamplesData()
            loadeddivcount++;
        } else {
            hideLoading(".rnnsampleloader")
            $(".exampleprogressbarinner").css('background-color', '#3BD804');
        }
    }

    // Show Loading Spinner
    function showLoading(element) {
        $(element).fadeIn("slow")
    }
    // Hide Loading Spinner
    function hideLoading(element) {
        $(element).fadeOut("slow")
    }

    // Check if valid JSON
    function isValidJSON(text) {
        if (typeof text !== "string") {
            return false;
        }
        try {
            JSON.parse(text);
            return true;
        } catch (error) {
            return false;
        }
    }


    // show Notification
    function showNotification(title, subtitle, caption) {

        $(".toasttemplate").find(".bx--toast-notification__title").text(title)
        $(".toasttemplate").find(".bx--toast-notification__subtitle").text(subtitle)
        $(".toasttemplate").find(".bx--toast-notification__caption").text(caption)

        toastInstance = $(".toasttemplate").clone()
        toastInstance.removeClass("toasttemplate")

        toastInstance.hide().appendTo(".toastDivBox")
        toastInstance.fadeIn("slow")
        toastInstance.find(".bx--toast-notification__close-button").click(function () {
            $(this).parent().fadeOut("slow", function () {
                $(this).remove()
            })

        });
    }

    function sendGAEvent(eCategory, eAction, eLabel) {
        console.log("logging", eCategory, eAction, eLabel)
        ga('send', {
            hitType: 'event',
            eventCategory: eCategory,
            eventAction: eAction,
            eventLabel: eLabel
        });
    }

});