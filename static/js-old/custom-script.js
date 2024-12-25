
function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

$(document).ready(function() {
    $('.like').click(function() {
        var val = $(this).val();
        var likeUrl = $(this).data('like-url');
        
        if (val == "like") {
            $(this).val("dislike");
            $('.Outline').attr('style', 'fill:red');
        } else {
            $(this).val("like");
            $('.Outline').attr('style', 'fill:#3270FC');
        }
        
        var csrfToken = getCookie('csrftoken'); // Get the CSRF token
        
        $.ajax({
            type: "POST",
            url: likeUrl,
            data: {
                'key': val,
                'pk': $(this).attr('name'),
                'csrfmiddlewaretoken': csrfToken // Include the CSRF token in the request data
            },
            success: function(response) {
                $('.num_likes_count').html('').append(response.num_likes_count);
                document.getElementById('num_likes_count').innerHTML = response.num_likes_count;
            },
            beforeSend: function(xhr) {
                xhr.setRequestHeader('X-CSRFToken', csrfToken); // Set the CSRF token in the request header
            },
        });
    });
});

