// https://stackoverflow.com/questions/13604144/bootstrap-popover-image-as-content
$(document).ready(function () {
    $('[data-toggle="popover-hover"]').each(function() {
        var imgSrc = $(this).data('img');
        $(this).popover({
            html: true,
            trigger: 'hover',
            placement: 'bottom',
            content: function () { return '<img src="' + imgSrc + '"  class="img-fluid"/>'; }
        });
    });
})