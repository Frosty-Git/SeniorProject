const filter_button = $('.filterBtn');
let user_id = $('#user_id').val();
const feed_table = $('#feed_table');
const endpoint = '/feed/';
const delay_by_in_ms = 300;
let scheduled_function = false;

let ajax_call = function (endpoint, request_parameters) {
    $.getJSON(endpoint, request_parameters)
        .done(response => {
            // fade out the table, then:
            feed_table.fadeTo('fast', 0).promise().then(() => {
                // replace the HTML contents
                feed_table.html(response['feed_h'])
                // fade-in the div with new contents
                feed_table.fadeTo('fast', 1)
            })
        })
}
filter_button.on('click', function () {
    let query;
    let buttons = [$('#socialFilter'), $('#songFilter'), $('#playlistFilter'), $('#popFilter')];
    let button_id = $(this).attr('id');
    let curr_button = $('#' + button_id);
    let other_active_button = null;
    for (i = 0; i < buttons.length; i++) {
        if (buttons[i] != curr_button) {
            if (buttons[i].hasClass('active')) {
                other_active_button = buttons[i];
                break;
            }
        }
    }

    if (curr_button.hasClass('active')) {
        curr_button.removeClass('active');
        query = "";
    }
    else {
        if (other_active_button != null) {
            other_active_button.removeClass('active');
        }
        curr_button.addClass('active');
        query = button_id;
    }

    const request_parameters = {
        q: query // id of button
    }

    // if scheduled_function is NOT false, cancel the execution of the function
    if (scheduled_function) {
        clearTimeout(scheduled_function)
    }

    // setTimeout returns the ID of the function to be executed
    scheduled_function = setTimeout(ajax_call, delay_by_in_ms, endpoint, request_parameters)
})