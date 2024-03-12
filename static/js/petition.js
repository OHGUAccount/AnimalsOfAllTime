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
                    
                    var signButton = $('#sign_button');
                    if (goal === count) {
                        signButton.attr('value', 'Goal Reached!');
                        signButton.removeClass('btn btn-primary');
                        signButton.addClass('btn btn-success').
                        signButton.prop('disabled', true);
                    } else {
                        signButton.attr('value', 'Signed');
                        signButton.prop('disabled', true);
                    }
            
                }
            },
        })
    });
});
