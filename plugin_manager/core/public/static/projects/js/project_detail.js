$(function(){
    $('#Subscribe').click(function(){
        var urlgetsubscribe = $('#subUrl').val()
        var unsubscribeManagementUrl = $('#unsubUrl').val()
            if ($('#Subscribe').data('action') == 'Subscribe')
            {
               $.get(urlgetsubscribe, {pk: project_id}, function(data){

               $('#Subscribe').removeClass('btn-success');
               $('#Subscribe').addClass('btn-danger');
               $('#Subscribe').html('Unsubscribe from Project');
               $('#Subscribe').data('action','Unsubscribe');
               });

             }
             else
             {
               $.get(unsubscribeManagementUrl, {pk: project_id}, function(data){
               $('#Subscribe').removeClass('btn-danger');
               $('#Subscribe').addClass('btn-success');
               $('#Subscribe').html('Subscribe to Project');
               $('#Subscribe').data('action','Subscribe')
               });
             }
        });
});

