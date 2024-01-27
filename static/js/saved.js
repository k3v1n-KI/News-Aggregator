$(document).ready(function() {
    $('form').on('submit', function(event) {
        $.ajax({
            data : {
                news : $('#save').val()
            },
            type : 'POST',
            url : '/saves/'
        })
        .done(function(data) {
            $('#polarity_heading').show();
            // $('#polarity').show();
            $('#polarity').text(data.polarity).show();
            $('#bias_heading').show();
            // $('#bias').show();
            $('#bias').text(data.bias).show();
            $('#predict_heading').show();
            if (data.fake_news_detect == "Verified Credibility") {
                $('#real').show();
                $('#fake').hide();
            }
            else {
                $('#fake').show();
                $('#real').hide();
            }
        });
        event.preventDefault();
    });
});