$(document).ready(function() { 
    var theme = $('html').attr('data-bs-theme');
    if (theme == 'dark') {
        $("#theme-switch").prop("checked", true);
    };

    $('#theme-switch').change(function() {
        if ($(this).is(":checked")) {
            var newTheme = 'dark';  
        }
        else {
            var newTheme = 'light';
        }

        $.get('/wildthoughts/theme/',
        {'theme': newTheme})
        $('html').attr('data-bs-theme', newTheme); 
    });
});
