$(function () {
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
    loadExampleData()
    $(".samplernnbutton").click(function () {
        loadRNNSampleData()
    });

    function loadRNNSampleData() {
        showLoading(".rnnsampleloader")
        var samplesize = ($("input#sampleinput").val())*1 || 500
        var prime = ($("input#prime").val()) || "{"
        console.log(" ======= ",samplesize)
        // Load vlSpec from Server
        $.ajax({
            url: "/samplernn",
            data: {
                samplesize: samplesize,
                prime: prime
            }
        }).done(function (samplernndata) {
            hideLoading(".rnnsampleloader")
            console.log(samplernndata)
            $(".rnnsamplecontent").text(samplernndata)
        });
    }

    function loadExampleData() {
        // Load example vlSpec from Server
        $.ajax({
            url: "/vldata",
        }).done(function (vldata) {
            if (!firstLoad) {
                hideLoading("#graph_loading_overlay")
            }
            firstLoad = true;
            console.log(vldata);
            vldata.width = graphWidth
            vldata.height = graphHeight
            vldata.autosize = {
                "type": "fit",
                "contains": "padding"
            }
            $(".vizbox").fadeOut("slow", function () {
                loadVisualization(vldata)
            })
        });
    }

    function loadVisualization(vlSpec) {
        // optional argument passed to Vega-Embed to specify vega-lite spec. More info at https://github.com/vega/vega-embed
        var opt = {
            "mode": "vega-lite"
        };

        // Embed the visualization in the container with id `vis`
        vegaEmbed("#vis", vlSpec, opt).then(function (result) {
            // Callback receiving the View instance and parsed Vega spec
            // result.view is the View, which resides under the '#vis' element
            $(".vizbox").fadeIn("slow", function () {
                setTimeout(function () {
                    loadExampleData()
                }, 2000)
            })
        }).catch(console.warn);
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