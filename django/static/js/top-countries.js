function setCountry() {
    let selectBox = document.getElementById("country");
    let select = selectBox.options[selectBox.selectedIndex].value;
    
    switch(select){
        case "USA": setPlaylistURI("37i9dQZEVXbLRQDuF5jeBp"); break;
        case "Vietnam": setPlaylistURI("37i9dQZEVXbLdGSmz6xilI"); break;
        // case "USA": ; break;
        // case "USA": ; break;
        // case "USA": ; break;
        // case "USA": ; break;
        // case "USA": ; break;
        // case "USA": ; break;
        // case "USA": ; break;
        // case "USA": ; break;
        // case "USA": ; break;
        // case "USA": ; break;
        // case "USA": ; break;
        // case "USA": ; break;
        // case "USA": ; break;
        // case "USA": ; break;
        // case "USA": ; break;
        // case "USA": ; break;
        // case "USA": ; break;
        // case "USA": ; break;
        default: setPlaylistURI("37i9dQZEVXbLRQDuF5jeBp");
    }
}

function setPlaylistURI(id) {
    const uri = "https://open.spotify.com/embed/playlist/" + id;
    document.getElementById("country-playlist").src = uri;
}