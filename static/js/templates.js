/*
Load template for page layout
Author: Victor Dibia <victor.dibia@gmail.com>
*/

$(function () {
    // $("#sidebar").load("sidebar.html", function(){
    var selectedtab = "modifyviz"
    selectedtab = getHash() || selectedtab
    // alert (  selectedtab + $("a.sidelink").html())
    $(".sidebarlinks").removeClass("sidebarselected")
    $("a.sidelink#" + selectedtab).parent().addClass("sidebarselected")

    // });

    // $("#header").load("header.html");
    // $("#footer").load("footer.html");

    // $("#disqusbox").load("disqus.html");


    // $("#modifyviz").load("modifyviz.html");
    // $("#examples").load("examples.html");
    // $("#documentation").load("documentation.html");


    // Sidebar clicks to show/hide page sections
    // $(".pagesection").hide()


    $.getScript("static/js/seqviz.js", function (data, textStatus, jqxhr) {
        $(".pagesection").hide()
        selectedtab = "documentation"

        selectedtab = getHash() || selectedtab
        $(".pagesection#" + selectedtab).show()

        $(".sidelink").click(function (e) {
            e.preventDefault();
            $(".sidebarlinks").removeClass("sidebarselected")
            $("a#" + $(this).attr("id")).parent().addClass("sidebarselected")
            clickedSection = $(".pagesection#" + $(this).attr("id"))
            window.location.hash = '#' + $(this).attr("id");
            $(".pagesection").hide()
            clickedSection.show()

        })
    });

    function getHash() {
        var hash = null;
        if (window.location.hash) {
            hash = window.location.hash.substring(1); //Puts hash in variable, and removes the # character
        }
        return hash
    }
})