$(document).ready(function() {
    $('#sign_button').click(function() {
    var petitionIdVar = $(this).attr('data-petition-id');
    $.get('/wildthoughts/sign_petition/',
    {'petition_id': petitionIdVar},
    function(data) {
    $('#signatures_count').html(data);
    $('#sign_button').attr('value', 'Signed').prop('disabled', true);
    var goal = parseInt($('#goal').text());
    var progressWidth = Math.floor(parseInt(data) / goal * 100);
    $('.progress-bar').text(progressWidth+ '%').css('width', progressWidth + '%');    
    })
    });
});