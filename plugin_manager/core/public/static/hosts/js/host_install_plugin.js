$(function(){

    $( document ).ready(function() {
        var urlajax = $('#ajaxUrl').val()
        var projid = $('#id_plugins').val()
        var newurlajax = urlajax + projid

        $.get(newurlajax, function(data){

            }).success(function(data) {
                $('#id_versions').empty();
                $.each(data, function(i, item){
                    $('#id_versions').append($("<option></option>")
                        .attr("value", item.version).text(item.version));
                });
            });
    });


    $('#id_plugins').change(function(){
        var urlajax = $('#ajaxUrl').val()
        var projid = $('#id_plugins').val()
        var newurlajax = urlajax + projid

        $.get(newurlajax, function(data){

            }).success(function(data) {
                $('#id_versions').empty();
                $.each(data, function(i, item){
                    $('#id_versions').append($("<option></option>")
                        .attr("value", item.version).text(item.version));
                });
            });
    });




});
