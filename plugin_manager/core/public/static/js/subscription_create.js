$(function(){

    $( document ).ready(function() {
        var urlajax = $('#ajaxUrl').val();
        var projid = $('#id_project').val();
        var newurlajax = urlajax + projid;
        $('#id_tasks').empty();

        $.get(newurlajax, function(data){

            }).success(function(data) {
                $('#id_tasks').empty();
                $.each(data, function(i, item){
                    $('#id_tasks').append($("<option></option>")
                        .attr("value", item.id).text("Task:  "+item.name+"  Stage: "+item.stage));
                });
            });
    });

    $('#id_fullprojectsub').change(function(){
        var checked = $('#id_fullprojectsub').prop('checked');
        if(checked)
            {
                $('#id_tasks option').prop('selected', 'selected');
                $('#id_tasks').prop('disabled','true')
            }
        else
            {
                $('#id_tasks').prop('disabled','false')
                $('#id_tasks').removeProp('disabled')

            }


    });

    $('#id_project').change(function(){
        var urlajax = $('#ajaxUrl').val()
        var projid = $('#id_project').val()
        var newurlajax = urlajax + projid

        $.get(newurlajax, function(data){

            }).success(function(data) {
                $('#id_tasks').empty();
                $.each(data, function(i, item){
                    $('#id_tasks').append($("<option></option>")
                        .attr("value", item.id).text("Task:  "+item.name+"  Stage: "+item.stage));
                });
            });
    });

    $('form').bind('submit', function() {
        $(this).find(':input').removeAttr('disabled');
    });



});
