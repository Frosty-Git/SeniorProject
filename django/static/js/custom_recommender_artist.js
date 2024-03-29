const user_input = $('#artistterm');
const search_div = $('#search_artists');
const endpoint = '/custom_recommender/';
const delay_by_in_ms = 300;
let scheduled_function = false;

window.onload = function() {
    document.getElementById('artistterm').value = '';
}

let ajax_call = function (endpoint, request_parameters) {
    $.getJSON(endpoint, request_parameters)
        .done(response => {
            // fade out the search_div, then:
            search_div.fadeTo('fast', 0).promise().then(() => {
                // replace the HTML contents
                search_div.html(response['artist_h'])
                // fade-in the div with new contents
                search_div.fadeTo('fast', 1)    
            })

        })
}
user_input.on('keyup', function () {

    const request_parameters = {
        q: $(this).val(), // value of user_input: the HTML element with ID user-input
        action: 'artist',
    }

    // if scheduled_function is NOT false, cancel the execution of the function
    if (scheduled_function) {
        clearTimeout(scheduled_function)
    }

    // setTimeout returns the ID of the function to be executed
    scheduled_function = setTimeout(ajax_call, delay_by_in_ms, endpoint, request_parameters)
})
