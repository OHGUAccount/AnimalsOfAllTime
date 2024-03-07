$(function () {
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