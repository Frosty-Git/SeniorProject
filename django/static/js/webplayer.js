let profile_token = $('#access_token').val();
let device;
window.onSpotifyWebPlaybackSDKReady = () => {
    const token = profile_token;
    const player = new Spotify.Player({
        name: 'PengBeats Player',
        getOAuthToken: cb => { cb(token); },
        volume: 0.1
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
        let next_tracks = state['track_window']['next_tracks']['length'];
        if(next_tracks != 0) {
            $('#emptyqueue').hide();
            $('#divider').show();
            $('#showqueue').show();
            $('#song1').show().html(state['track_window']['next_tracks'][0]['name'] + '<small style="font-size:x-small"> ' + state['track_window']['next_tracks'][0]['artists'][0]['name'] + '</small>');
            if(next_tracks == 2) {
                $('#song2').show().html(state['track_window']['next_tracks'][1]['name'] + '<small style="font-size:x-small"> ' + state['track_window']['next_tracks'][1]['artists'][0]['name'] + '</small>');
            }
        }
        else {
            $('#emptyqueue').show();
            $('#divider').hide();
            $('#showqueue').hide();
            $('#song1').hide();
            $('#song2').hide();
        }
        
    });

    setInterval(function() {
        player.getCurrentState().then(state => {
            if(state != null) {
                $('#songprogress').attr('value', state['position']);
                $('#currentTime').text(millisToMinutesAndSeconds(state['position']));
                $('#songprogress').text(state['position']);
                $('#songprogress').attr('max', state['duration']);
                $('#totalTime').text(millisToMinutesAndSeconds(state['duration']));
                document.getElementById('dummysong').reset();
            }
        })
    }, 500);

    // Ready
    player.addListener('ready', ({ device_id }) => {
        console.log('Ready with Device ID', device_id);
        device = device_id;
        console.log('GOD I HOPE THIS WORKS' + device);

        player.getVolume().then(volume => {
            let volume_percentage = volume * 100;
            $('#volume').val(volume_percentage);
            console.log(`The volume of the player is ${volume_percentage}%`);
        });
    
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

    $('#volume').mouseup(function() {
        let volume_value = $(this).val();
        if (volume_value == 0) {
            player.setVolume(0.00001);
            $('#volumeBtn').html('<svg xmlns="http://www.w3.org/2000/svg" width="25" height="25" fill="currentColor" class="bi bi-volume-mute-fill" viewBox="0 0 16 16">'
                            + '<path d="M6.717 3.55A.5.5 0 0 1 7 4v8a.5.5 0 0 1-.812.39L3.825 10.5H1.5A.5.5 0 0 1 1 10V6a.5.5 0 0 1 .5-.5h2.325l2.363-1.89a.5.5 0 0 1 .529-.06zm7.137 2.096a.5.5 0 0 1 0 .708L12.207 8l1.647 1.646a.5.5 0 0 1-.708.708L11.5 8.707l-1.646 1.647a.5.5 0 0 1-.708-.708L10.793 8 9.146 6.354a.5.5 0 1 1 .708-.708L11.5 7.293l1.646-1.647a.5.5 0 0 1 .708 0z"/>'
                            + '</svg>')
        }
        else {
            player.setVolume(volume_value/100);
            $('#volumeBtn').html('<svg xmlns="http://www.w3.org/2000/svg" width="25" height="25" fill="currentColor" class="bi bi-volume-down-fill" viewBox="0 0 16 16">'
                            + '<path d="M9 4a.5.5 0 0 0-.812-.39L5.825 5.5H3.5A.5.5 0 0 0 3 6v4a.5.5 0 0 0 .5.5h2.325l2.363 1.89A.5.5 0 0 0 9 12V4zm3.025 4a4.486 4.486 0 0 1-1.318 3.182L10 10.475A3.489 3.489 0 0 0 11.025 8 3.49 3.49 0 0 0 10 5.525l.707-.707A4.486 4.486 0 0 1 12.025 8z"/>'
                            + '</svg>');
        }
       
        console.log(`The volume of the player is ${volume_value}%`);
    });

    $('#songprogress').mouseup(function() {
        let seek_value = $(this).val();
        player.seek(seek_value);
        console.log(`The player is now at ${seek_value} seconds`);
        document.getElementById('dummysong').reset();
    });

    let prev_volume;
    $('#volumeBtn').click(function() {
        player.getVolume().then(volume => {
            if (volume != 0.00001) {
                prev_volume = volume;
                player.setVolume(0.00001);
                $('#volume').val(0);
                $(this).html('<svg xmlns="http://www.w3.org/2000/svg" width="25" height="25" fill="currentColor" class="bi bi-volume-mute-fill" viewBox="0 0 16 16">'
                            + '<path d="M6.717 3.55A.5.5 0 0 1 7 4v8a.5.5 0 0 1-.812.39L3.825 10.5H1.5A.5.5 0 0 1 1 10V6a.5.5 0 0 1 .5-.5h2.325l2.363-1.89a.5.5 0 0 1 .529-.06zm7.137 2.096a.5.5 0 0 1 0 .708L12.207 8l1.647 1.646a.5.5 0 0 1-.708.708L11.5 8.707l-1.646 1.647a.5.5 0 0 1-.708-.708L10.793 8 9.146 6.354a.5.5 0 1 1 .708-.708L11.5 7.293l1.646-1.647a.5.5 0 0 1 .708 0z"/>'
                            + '</svg>');
                console.log('Muted');
            }
            else {
                player.setVolume(prev_volume);
                $('#volume').val(prev_volume*100);
                $(this).html('<svg xmlns="http://www.w3.org/2000/svg" width="25" height="25" fill="currentColor" class="bi bi-volume-down-fill" viewBox="0 0 16 16">'
                            + '<path d="M9 4a.5.5 0 0 0-.812-.39L5.825 5.5H3.5A.5.5 0 0 0 3 6v4a.5.5 0 0 0 .5.5h2.325l2.363 1.89A.5.5 0 0 0 9 12V4zm3.025 4a4.486 4.486 0 0 1-1.318 3.182L10 10.475A3.489 3.489 0 0 0 11.025 8 3.49 3.49 0 0 0 10 5.525l.707-.707A4.486 4.486 0 0 1 12.025 8z"/>'
                            + '</svg>');
                console.log('Sound on');
                console.log(`The volume of the player is ${prev_volume}%`);
            }
        })
    });

    $('#song1').click(function() {
        player.nextTrack();
    });
    $('#song2').click(function() {
        player.nextTrack();
        player.nextTrack();
    });


};

function millisToMinutesAndSeconds(millis) {
    var minutes = Math.floor(millis / 60000);
    var seconds = ((millis % 60000) / 1000).toFixed(0);
    return minutes + ":" + (seconds < 10 ? '0' : '') + seconds;
}