function Redirect (url) {
    var ua        = navigator.userAgent.toLowerCase(),
        isIE      = ua.indexOf('msie') !== -1,
        version   = parseInt(ua.substr(4, 2), 10);

    // Internet Explorer 8 and lower
    if (isIE && version < 9) {
        var link = document.createElement('a');
        link.href = url;
        document.body.appendChild(link);
        link.click();
    }

    // All other browsers
    else { window.location.href = url; }
}


$(function(){
    if(deployment_pending){

        var scroll_iframe_ticker = setInterval(function(){
            var $contents = $('#deployment_output').contents();

            $contents.scrollTop($contents.height());
            if($contents.find('#finished').length > 0){
                status = $contents.find('#finished').html();
                if(status == 'failed'){
                    clearInterval(scroll_iframe_ticker);
                    $('#status_section legend').html('Status: Failed!');
                    $('#status_section .glyphicon').attr('class', '').addClass('glyphicon').addClass('glyphicon-warning-sign').addClass('text-danger');
                }else if(status == 'success') {
                    $('#status_section legend').html('Status: Success!');
                    $('#status_section .glyphicon').attr('class', '').addClass('glyphicon').addClass('glyphicon-ok').addClass('text-success');
                    var regexToken = /(((ftp|https?):\/\/)[\-\w@:%_\+.~#?,&\/\/=]+)|((mailto:)?[_.\w-]+@([\w][\w\-]+\.)+[a-zA-Z]{2,3})/g;

                    matches = regexToken.exec($("#deployment_output").contents().find("body").html())

                    if(matches!=null) window.location.href = matches[0]

                    clearInterval(scroll_iframe_ticker);

                    $contents.scrollTop(0);

                }

                clearInterval(scroll_iframe_ticker);
            }
        }, 100);


    }else{
        var regexToken = /(((ftp|https?):\/\/)[\-\w@:%_\+.~#?,&\/\/=]+)|((mailto:)?[_.\w-]+@([\w][\w\-]+\.)+[a-zA-Z]{2,3})/g;

        matches = regexToken.exec($("#deployment_output pre").html())
        $("#status_section").append("<br><br><p><a class='btn btn-success' href='" + matches[0] + "'><i class='glyphicon glyphicon-download' style='font-size:20px;'></i>  <b>Download File</b></a></p>")
        $('#deployment_output pre').scrollTop($('#deployment_output pre')[0].scrollHeight);
    }
});
