$(function(){
    $("a[id^='add_']").click(function(){
        var urladd = $('#addUrl').val()
        var userid = ($(this).attr('id')).split('_')[1]
        var adiv = $(this)
        $.get(urladd, {projid: project_id, userid: userid}, function(data){
            adiv.html("<i class='glyphicon glyphicon-ok'></i>")
            adiv.removeClass("btn btn-primary btn-xs btn-default")
           });
        });
});
