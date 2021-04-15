let profile_token = $('#access_token').val();
let device;
window.onSpotifyWebPlaybackSDKReady = () => {
    const token = profile_token;
    const player = new Spotify.Player({
        name: 'PengBeats Player',
        getOAuthToken: cb => { cb(token); },
        volume: 0.5
    });
    

    // Error handling
    player.addListener('initialization_error', ({ message }) => { console.error(message); });
    player.addListener('authentication_error', ({ message }) => { console.error(message); });
    player.addListener('account_error', ({ message }) => { console.error(message); });
    player.addListener('playback_error', ({ message }) => { console.error(message); });

    // Playback status updates
    player.addListener('player_state_changed', state => { 
        console.log(state); 
        $('#songtitle').html(state['track_window']['current_track']['name']);
        $('#albumpic').attr('src', state['track_window']['current_track']['album']['images'][0]['url']);
        $('#artistname').html(state['track_window']['current_track']['artists'][0]['name']);
        if(state['paused'] == true) {
            $('#playpauseBtn').html('<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="currentColor" class="bi bi-play-circle" viewBox="0 0 16 16">'                
                        + '<path d="M8 15A7 7 0 1 1 8 1a7 7 0 0 1 0 14zm0 1A8 8 0 1 0 8 0a8 8 0 0 0 0 16z"/>'
                        + '<path d="M6.271 5.055a.5.5 0 0 1 .52.038l3.5 2.5a.5.5 0 0 1 0 .814l-3.5 2.5A.5.5 0 0 1 6 10.5v-5a.5.5 0 0 1 .271-.445z"/>'
                        + '</svg>');
        }
        else {
            $('#playpauseBtn').html('<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="currentColor" class="bi bi-pause-circle" viewBox="0 0 16 16">'
                        + '<path d="M8 15A7 7 0 1 1 8 1a7 7 0 0 1 0 14zm0 1A8 8 0 1 0 8 0a8 8 0 0 0 0 16z"/>'
                        + '<path d="M5 6.25a1.25 1.25 0 1 1 2.5 0v3.5a1.25 1.25 0 1 1-2.5 0v-3.5zm3.5 0a1.25 1.25 0 1 1 2.5 0v3.5a1.25 1.25 0 1 1-2.5 0v-3.5z"/>'
                        + '</svg>');
        }
        $('#songprogress').attr('max', state['duration']);
        $('#totalTime').text(millisToMinutesAndSeconds(state['duration']));
    });

    setInterval(function() {
        player.getCurrentState().then(state => {
            if(state != null) {
                $('#songprogress').attr('value', state['position']);
                $('#currentTime').text(millisToMinutesAndSeconds(state['position']));
                // $('#songprogress').text(state['position']);
            }
        })
    }, 500);

    // Ready
    player.addListener('ready', ({ device_id }) => {
        console.log('Ready with Device ID', device_id);
        device = device_id;
        console.log('GOD I HOPE THIS WORKS' + device);
    
    });


    

    // Not Ready
    player.addListener('not_ready', ({ device_id }) => {
        console.log('Device ID has gone offline', device_id);
    });

    // Connect to the player!
    player.connect().then(success => {
        if (success) {
        console.log('The Web Playback SDK successfully connected to Spotify!');
        }
    });

    // Button Functionality
    $('#playpauseBtn').click(function() {
        player.togglePlay();
    });

    $('#nextTrack').click(function() {
        player.nextTrack();
    });

    $('#prevTrack').click(function() {
        player.previousTrack();
    });

    $('#shuffle').click(function() {
        player.getCurrentState().then(state => {
            let is_shuffle_true = state['shuffle'];
            $.ajax({
                url: "https://api.spotify.com/v1/me/player/shuffle?state=" + !is_shuffle_true + "&device_id=" + device,
                type: "PUT",
                beforeSend: function(xhr){xhr.setRequestHeader('Authorization', 'Bearer ' + profile_token );},
                success: function(data) { 
                    console.log('is this the data ' + data)
                    if(is_shuffle_true) {
                        $('#shuffle').html('<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-shuffle" viewBox="0 0 16 16">'
                                    + '<path fill-rule="evenodd" d="M0 3.5A.5.5 0 0 1 .5 3H1c2.202 0 3.827 1.24 4.874 2.418.49.552.865 1.102 1.126 1.532.26-.43.636-.98 1.126-1.532C9.173 4.24 10.798 3 13 3v1c-1.798 0-3.173 1.01-4.126 2.082A9.624 9.624 0 0 0 7.556 8a9.624 9.624 0 0 0 1.317 1.918C9.828 10.99 11.204 12 13 12v1c-2.202 0-3.827-1.24-4.874-2.418A10.595 10.595 0 0 1 7 9.05c-.26.43-.636.98-1.126 1.532C4.827 11.76 3.202 13 1 13H.5a.5.5 0 0 1 0-1H1c1.798 0 3.173-1.01 4.126-2.082A9.624 9.624 0 0 0 6.444 8a9.624 9.624 0 0 0-1.317-1.918C4.172 5.01 2.796 4 1 4H.5a.5.5 0 0 1-.5-.5z"/>'
                                    + '<path d="M13 5.466V1.534a.25.25 0 0 1 .41-.192l2.36 1.966c.12.1.12.284 0 .384l-2.36 1.966a.25.25 0 0 1-.41-.192zm0 9v-3.932a.25.25 0 0 1 .41-.192l2.36 1.966c.12.1.12.284 0 .384l-2.36 1.966a.25.25 0 0 1-.41-.192z"/>'
                                    + '</svg>');
                    }
                    else {
                        $('#shuffle').html('<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="#f99108" class="bi bi-shuffle" viewBox="0 0 16 16">'
                                    + '<path fill-rule="evenodd" d="M0 3.5A.5.5 0 0 1 .5 3H1c2.202 0 3.827 1.24 4.874 2.418.49.552.865 1.102 1.126 1.532.26-.43.636-.98 1.126-1.532C9.173 4.24 10.798 3 13 3v1c-1.798 0-3.173 1.01-4.126 2.082A9.624 9.624 0 0 0 7.556 8a9.624 9.624 0 0 0 1.317 1.918C9.828 10.99 11.204 12 13 12v1c-2.202 0-3.827-1.24-4.874-2.418A10.595 10.595 0 0 1 7 9.05c-.26.43-.636.98-1.126 1.532C4.827 11.76 3.202 13 1 13H.5a.5.5 0 0 1 0-1H1c1.798 0 3.173-1.01 4.126-2.082A9.624 9.624 0 0 0 6.444 8a9.624 9.624 0 0 0-1.317-1.918C4.172 5.01 2.796 4 1 4H.5a.5.5 0 0 1-.5-.5z"/>'
                                    + '<path d="M13 5.466V1.534a.25.25 0 0 1 .41-.192l2.36 1.966c.12.1.12.284 0 .384l-2.36 1.966a.25.25 0 0 1-.41-.192zm0 9v-3.932a.25.25 0 0 1 .41-.192l2.36 1.966c.12.1.12.284 0 .384l-2.36 1.966a.25.25 0 0 1-.41-.192z"/>'
                                    + '</svg>');
                    } 
                }
            });
        });
    });

    $('#repeat').click(function() {
        player.getCurrentState().then(state => {
            let which_repeat = state['repeat_mode'];
            let final_repeat;
            if (which_repeat == 0) { // None
                final_repeat = 'context';
            }
            else if (which_repeat == 1) { // Context
                final_repeat = 'track';
            }
            else { // Track
                final_repeat = 'off';
            }
            $.ajax({
                url: "https://api.spotify.com/v1/me/player/repeat?state=" + final_repeat + "&device_id=" + device,
                type: "PUT",
                beforeSend: function(xhr){xhr.setRequestHeader('Authorization', 'Bearer ' + profile_token );},
                success: function(data) { 
                    console.log('is this the data ' + data)
                    if(final_repeat == 'off') {
                        $('#repeat').html('<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-arrow-repeat" viewBox="0 0 16 16">'
                                            + '<path d="M11.534 7h3.932a.25.25 0 0 1 .192.41l-1.966 2.36a.25.25 0 0 1-.384 0l-1.966-2.36a.25.25 0 0 1 .192-.41zm-11 2h3.932a.25.25 0 0 0 .192-.41L2.692 6.23a.25.25 0 0 0-.384 0L.342 8.59A.25.25 0 0 0 .534 9z"/>'
                                            + '<path fill-rule="evenodd" d="M8 3c-1.552 0-2.94.707-3.857 1.818a.5.5 0 1 1-.771-.636A6.002 6.002 0 0 1 13.917 7H12.9A5.002 5.002 0 0 0 8 3zM3.1 9a5.002 5.002 0 0 0 8.757 2.182.5.5 0 1 1 .771.636A6.002 6.002 0 0 1 2.083 9H3.1z"/>'
                                            + '</svg>');
                    }
                    else if (final_repeat == 'context') {
                        $('#repeat').html('<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="#f99108" class="bi bi-arrow-repeat" viewBox="0 0 16 16">'
                                            + '<path d="M11.534 7h3.932a.25.25 0 0 1 .192.41l-1.966 2.36a.25.25 0 0 1-.384 0l-1.966-2.36a.25.25 0 0 1 .192-.41zm-11 2h3.932a.25.25 0 0 0 .192-.41L2.692 6.23a.25.25 0 0 0-.384 0L.342 8.59A.25.25 0 0 0 .534 9z"/>'
                                            + '<path fill-rule="evenodd" d="M8 3c-1.552 0-2.94.707-3.857 1.818a.5.5 0 1 1-.771-.636A6.002 6.002 0 0 1 13.917 7H12.9A5.002 5.002 0 0 0 8 3zM3.1 9a5.002 5.002 0 0 0 8.757 2.182.5.5 0 1 1 .771.636A6.002 6.002 0 0 1 2.083 9H3.1z"/>'
                                            + '</svg> <small>All</small>');
                    } 
                    else if (final_repeat == 'track') {
                        $('#repeat').html('<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="#f99108" class="bi bi-arrow-repeat" viewBox="0 0 16 16">'
                                            + '<path d="M11.534 7h3.932a.25.25 0 0 1 .192.41l-1.966 2.36a.25.25 0 0 1-.384 0l-1.966-2.36a.25.25 0 0 1 .192-.41zm-11 2h3.932a.25.25 0 0 0 .192-.41L2.692 6.23a.25.25 0 0 0-.384 0L.342 8.59A.25.25 0 0 0 .534 9z"/>'
                                            + '<path fill-rule="evenodd" d="M8 3c-1.552 0-2.94.707-3.857 1.818a.5.5 0 1 1-.771-.636A6.002 6.002 0 0 1 13.917 7H12.9A5.002 5.002 0 0 0 8 3zM3.1 9a5.002 5.002 0 0 0 8.757 2.182.5.5 0 1 1 .771.636A6.002 6.002 0 0 1 2.083 9H3.1z"/>'
                                            + '</svg> <small>One</small>');
                    } 
                }
            });
        });
    });

};

function millisToMinutesAndSeconds(millis) {
    var minutes = Math.floor(millis / 60000);
    var seconds = ((millis % 60000) / 1000).toFixed(0);
    return minutes + ":" + (seconds < 10 ? '0' : '') + seconds;
}