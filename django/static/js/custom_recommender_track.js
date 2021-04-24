const track_user_input = $('#trackterm');
const track_search_div = $('#search_tracks');
const track_endpoint = '/custom_recommender/';
const track_delay_by_in_ms = 300;
let track_scheduled_function = false;

window.onload = function() {
    document.getElementById('trackterm').value = '';
}

let track_ajax_call = function (track_endpoint, request_parameters) {
    $.getJSON(track_endpoint, request_parameters)
        .done(response => {
            // fade out the search_div, then:
            track_search_div.fadeTo('fast', 0).promise().then(() => {
                // replace the HTML contents
                track_search_div.html(response['track_h'])
                // fade-in the div with new contents
                track_search_div.fadeTo('fast', 1)    
            })

        })
}
track_user_input.on('keyup', function () {

    const request_parameters = {
        q: $(this).val(), // value of user_input: the HTML element with ID user-input
        action: 'track',
    }

    // if scheduled_function is NOT false, cancel the execution of the function
    if (track_scheduled_function) {
        clearTimeout(track_scheduled_function)
    }

    // setTimeout returns the ID of the function to be executed
    track_scheduled_function = setTimeout(track_ajax_call, track_delay_by_in_ms, track_endpoint, request_parameters)
})
