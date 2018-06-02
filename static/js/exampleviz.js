/**
 * JS Script to load up random Vegalite data from server and display charts
 * 
 */
$(function () {
    var exampleProgressBarColor = "#152934"
    // Assign the specification to a local variable vlSpec.
    var exampleGraphWidth = ($(".examplebox").width()) / 6;
    var exampleGraphHeight = 250;

    var loadDuration = 5000;
    var firstLoad = false
    var loadeddivcount = 1;
    var numGraphs = 10;

    var generatedDataHolder;

    hideLoading(".rnnsampleloader")

    loadExamplesData()

    $(".generateexamplesbutton").click(function () {
        numInputExamples = $(".numexamplesinput").val()
        if (numInputExamples != "" && numInputExamples < 50) {
            numGraphs = numInputExamples * 1
        }
        $(".examplebox").empty()
        loadeddivcount = 1;
        $(".exampleprogressbarinner").width(0);
        $(".exampleprogressbarinner").css('background-color', exampleProgressBarColor)
        showLoading(".rnnsampleloader")
        loadExamplesData()

    });



    function loadExamplesData() {
        $.ajax({
            url: "/examplesdata"
        }).done(function (result) {
            // alert(JSON.stringify(result))
            loadExampleVisualization(result.vegaspec)
        }).fail(function (xhr, status, error) {
            // error handling
            console.log("Eroor fetchng data!!")
        });;
    }



    function loadExampleVisualization(vlSpec) {
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

        vegaEmbed("#" + divid, vlSpec, opt).then(function (result) {
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

});