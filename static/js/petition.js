$(document).ready(function() {
    $('#sign_button').click(function() {
        var petitionId = $(this).attr('data-petition-id');

        $.ajax({
            url: '/wildthoughts/sign_petition/',
            type: 'GET',
            data: {
                'petition_id': petitionId
            },
            success: function(response) {
                if(response.status === 'success') {
                    var count = parseInt($('#signatures_count').text()) + 1;
                    var goal = parseInt($('#goal').text());
                    var progressWidth = Math.floor(count / goal * 100);

                    $('#signatures_count').text(count);    
                    $('.progress-bar').text(progressWidth+ '%').css('width', progressWidth + '%');    
                    
                    if (goal === count) {
                        $('#sign_button').attr('value', 'Goal Reached!');
                        $('#sign_button').prop('disabled', true);
                        $('#sign_button').removeClass('btn btn-primary');
                        $('#sign_button').addClass('btn btn-success');
                    } else {
                        $('#sign_button').attr('value', 'Signed');
                        $('#sign_button').prop('disabled', true);
                    }
            
                } 
                else if (response.status === 'login') {
                    window.location.href = response.login_url;
                }
            },
        })
    });
});
