// code by Kevin Magill, James Cino
function Quiz(questions) {
    this.questions = questions;
    this.questionIndex = 0;
    this.previous_value_boolean = false;
}

Quiz.prototype.change_question_index = function (value) {
    this.questionIndex = value;
}


Quiz.prototype.return_value_of_question = function () {
    return this.questions[this.questionIndex];

}

Quiz.prototype.return_previous_value_boolean = function () {
    return this.previous_value_boolean;

}

Quiz.prototype.set_previous_value_boolean = function (value) {
    this.previous_value_boolean = value;

}

Quiz.prototype.return_question_index = function () {
    return this.questionIndex;
}

function Question(question, choices, danceability, accousticness, energy, instrumentalness, speechiness, loudness, tempo, valence, is_dynamic) {
    this.question = question;
    this.choices = choices;
    this.danceability = danceability;
    this.accousticness = accousticness;
    this.energy = energy;
    this.instrumentalness = instrumentalness;
    this.speechiness = speechiness;
    this.loudness = loudness;
    this.tempo = tempo;
    this.valence = valence;
    this.is_dynamic = is_dynamic;

};


let questions = [
    new Question("Which of the following genres do you prefer?", ["Rock", "Country", "Pop", "Sea-Shanties", "Tibetan Throat Singing"],
        //danceability
        [null, null, null, null, null],
        //acousticness
        [null, null, null, null, null],
        //energy
        [null, null, null, null, null],
        //instrumentalness
        [null, null, null, null, null],
        //speechiness
        [null, null, null, null, null],
        //loudness
        [null, null, null, null, null],
        //tempo
        [null, null, null, null, null],
        //valence
        [null, null, null, null, null],
        true
    ),
    new Question("Which of the following artists do you prefer?", ["The Beatles", "Metallica", "The Grateful Dead", "Electric Lights Orchestra", "Simon and Garfunkel"],
        //danceability
        [null, null, null, null, null],
        //acousticness
        [null, null, null, null, null],
        //energy
        [null, null, null, null, null],
        //instrumentalness
        [null, null, null, null, null],
        //speechiness
        [null, null, null, null, null],
        //loudness
        [null, null, null, null, null],
        //tempo
        [null, null, null, null, null],
        //valence
        [null, null, null, null, null],
        true
    ),
    new Question("Which of the following artists do you prefer?", ["Carrie Underwood", "Dan + Shay", "Morgan Wallen", "Luke Combs", "Kane Brown"],
        //danceability
        [null, null, null, null, null],
        //acousticness
        [null, null, null, null, null],
        //energy
        [null, null, null, null, null],
        //instrumentalness
        [null, null, null, null, null],
        //speechiness
        [null, null, null, null, null],
        //loudness
        [null, null, null, null, null],
        //tempo
        [null, null, null, null, null],
        //valence
        [null, null, null, null, null],
        false
    ),
    new Question("Which of the following artists do you prefer?", ["Justin Bieber", "Nicki Minaj", "Katy Perry", "Billy Eilish", "Ariana Grande"],
      //danceability
      [null, null, null, null, null],
      //acousticness
      [null, null, null, null, null],
      //energy
      [null, null, null, null, null],
      //instrumentalness
      [null, null, null, null, null],
      //speechiness
      [null, null, null, null, null],
      //loudness
      [null, null, null, null, null],
      //tempo
      [null, null, null, null, null],
      //valence
      [null, null, null, null, null],
      true
      ),
      
    new Question("Which of the following artists do you prefer?", ["The Irish Sailors", "The Largest Johns", "The Irish Rovers", "The Fisherman's Friends", "High Tide"],
      //danceability
      [null, null, null, null, null],
      //acousticness
      [null, null, null, null, null],
      //energy
      [null, null, null, null, null],
      //instrumentalness
      [null, null, null, null, null],
      //speechiness
      [null, null, null, null, null],
      //loudness
      [null, null, null, null, null],
      //tempo
      [null, null, null, null, null],
      //valence
      [null, null, null, null, null],
      true
      ),
    new Question("Which of the following artists do you prefer?", ["Deva Premal", "Tibetan Monks", "The Gyuto Monks of Tibet", "Tradidional", "Shu-de"],
      //danceability
      [null, null, null, null, null],
      //acousticness
      [null, null, null, null, null],
      //energy
      [null, null, null, null, null],
      //instrumentalness
      [null, null, null, null, null],
      //speechiness
      [null, null, null, null, null],
      //loudness
      [null, null, null, null, null],
      //tempo
      [null, null, null, null, null],
      //valence
      [null, null, null, null, null],
      true
      ),
    new Question("Which of the following songs do you listen to the most?", ["In My Life", "Yesterday", "Twist and Shout", "Come Together", "Strawberry Fields Forever"],
    //danceability
    [0.688, 0.332, 0.482, 0.533, 0.39],
    //acousticness
    [0.449, 0.879, 0.641, 0.0302, 0.336],
    //energy
    [0.435, 0.179, 0.849, 0.376, 0.502],
    //instrumentalness
    [0, 0, 0.00000774, 0.248, 0.000138],
    //speechiness
    [0.0323, 0.0326, 0.0452, 0.0393, 0.178],
    //loudness
    [-11.359, -11.83, -9.198, -11.913, -12.277],
    //tempo
    [103.239, 96.529, 124.631, 165.007, 97.871],
    //valence
    [0.435, 0.315, 0.937, 0.187, 0.289],
    true
    ),
    
    new Question("Which of the following songs do you listen to the most?", ["Sad But True", "Nothing Else Matters", "Enter Sandman", "Master of Puppets", "Fade To Black"],
    //danceability
    [0.632, 0.558, 0.579, 0.539, 0.256],
    //acousticness
    [0.000773, 0.0505, 0.00206, 0.00067, 0.00311],
    //energy
    [0.845, 0.364, 0.824, 0.828, 0.929],
    //instrumentalness
    [0.00152, 0.00000502, 0.421, 0.248, 0.201],
    //speechiness
    [0.0333, 0.0265, 0.03, 0.035, 0.113],
    //loudness
    [-6.336, -11.258, -8.71, -9.108, -6.667],
    //tempo
    [89.232, 142.171, 123.331, 105.25, 113.47],
    //valence
    [0.433, 0.17, 0.635, 0.562, 0.278],
    true
    ),
    new Question("Which of the following songs do you listen to the most?", ["Shakedown Street", "Althea", "Touch of Grey", "Truckin'", "Casey Jones"],
    //danceability
    [0.809, 0.783, 0.612, 0.644, 0.671],
    //acousticness
    [0.156, 0.679, 0.0785, 0.389, 0.385],
    //energy
    [0.575, 0.284, 0.696, 0.623, 0.405],
    //instrumentalness
    [0.00000165, 0.282, 0.0000094, 0.0202, 0],
    //speechiness
    [0.0298, 0.0365, 0.0353, 0.059, 0.0392],
    //loudness
    [-12.176, -14.307, -11.34, -13.862, -10.052],
    //tempo
    [109.447, 82.676, 159.829, 126.553, 99.678],
    //valence
    [0.85, 0.584, 0.849, 0.676, 0.828],
    true
    ),
    new Question("Which of the following songs do you listen to the most?", ["Mr. Blue Sky", "Last Train to London", "Don't Bring Me Down", "Turn to Stone", "Evil Woman"],
    //danceability
    [0.388, 0.727, 0.638, 0.548, 0.677],
    //acousticness
    [0.652, 0.396, 0.144, 0.0686, 0.457],
    //energy
    [0.338, 0.537, 0.867, 0.72, 0.619],
    //instrumentalness
    [0.00000372, 0.000789, 0.000733, 0.000232, 0.000149],
    //speechiness
    [0.0328, 0.0295, 0.0331, 0.0409, 0.0334],
    //loudness
    [-10.054, -9.785, -6.469, -9.777, -7.446],
    //tempo
    [177.784, 121.493, 115.692, 140.966, 119.624],
    //valence
    [0.477, 0.954, 0.805, 0.458, 0.74],
    true
    ),
    new Question("Which of the following songs do you listen to the most?", ["Cecilia", "Bridge Over Troubled Water", "The Only Living Boy in New York", "The Boxer", "America"],
    //danceability
    [0.755, 0.727, 0.411, 0.439, 0.259],
    //acousticness
    [0.357, 0.396, 0.13, 0.702, 0.554],
    //energy
    [0.876, 0.537, 0.381, 0.488, 0.241],
    //instrumentalness
    [0.00000517, 0.000649, 0.257, 0.000339, 0.00000662],
    //speechiness
    [0.0362, 0.0323, 0.0286, 0.0615, 0.042],
    //loudness
    [-8.867, -13.888, -12.361, -14.464, -15.955],
    //tempo
    [102.762, 79.764, 76.963, 93.017, 178.453],
    //valence
    [0.954, 0.264, 0.524, 0.629, 0.275],
    true
    ),
    new Question("Which of the following songs do you listen to the most?", ["The Champion", "Jesus, Take the Wheel", "Before He Cheats", "All-American Girl", "How Great Thou Art"],
    //danceability
    [0.663, 0.359, 0.519, 0.624, 0.318],
    //acousticness
    [0.0821, 0.665, 0.271, 0.0466, 0.436],
    //energy
    [0.875, 0.511, 0.749, 0.805, 0.427],
    //instrumentalness
    [0, 0, 0.257, 0, 0],
    //speechiness
    [0.183, 0.0302, 0.0405, 0.029, 0.0288],
    //loudness
    [-3.301, -3.537, -3.318, -2.632, -6.912],
    //tempo
    [91.056, 76.572, 147.905, 123.991, 92.535],
    //valence
    [0.51, 0.135, 0.29, 0.77, 0.282],
    true
    ),
    new Question("Which of the following songs do you listen to the most?", ["Glad You Exist", "I Should Probably Go To Bed", "10,000 Hours (with Justin Bieber)", "How Not To", "From the Ground Up"],
    //danceability
    [0.748, 0.721, 0.654, 0.501, 0.281],
    //acousticness
    [0.235, 0.634, 0.153, 0.208, 0.333],
    //energy
    [0.551, 0.277, 0.63, 0.836, 0.58],
    //instrumentalness
    [0, 0, 0.257, 0, 0],
    //speechiness
    [0.0349, 0.0365, 0.0259, 0.0491, 0.0323],
    //loudness
    [-6.12, -7.128, -4.644, -3.587, -5.967],
    //tempo
    [103.953, 131.935, 89.991, 159.863, 151.568],
    //valence
    [0.66, 0.309, 0.43, 0.618, 0.282],
    true
    ),
    new Question("Which of the following songs do you listen to the most?", ["Somebody's Problem", "865", "Whiskey Glasses", "Sand In My Boots", "Dangerous"],
    //danceability
    [0.657, 0.532, 0.614, 0.403, 0.635],
    //acousticness
    [0.662, 0.723, 0.369, 0.59, 0.216],
    //energy
    [0.54, 0.584, 0.68, 0.537, 0.772],
    //instrumentalness
    [0, 0, 0.00000184, 0, 0],
    //speechiness
    [0.0287, 0.0248, 0.0289, 0.031, 0.0279],
    //loudness
    [-7.675, -5.254, -4.58, -6.628, -4.825],
    //tempo
    [136.97, 88.003, 149.959, 69.877, 119.017],
    //valence
    [0.625, 0.367, 0.707, 0.414, 0.948],
    true
    ),
    new Question("Which of the following songs do you listen to the most?", ["Lovin' On You", "Better Together", "Hurricane", "She Got the Best of Me", "Forever After All"],
    //danceability
    [0.572, 0.552, 0.464, 0.533, 0.487],
    //acousticness
    [0.00165, 0.827, 0.0153, 0.0292, 0.191],
    //energy
    [0.949, 0.225, 0.813, 0.907, 0.65],
    //instrumentalness
    [0, 0, 0, 0, 0],
    //speechiness
    [0.06, 0.0477, 0.0416, 0.0406, 0.0253],
    //loudness
    [-4.865, -11.501, -6.185, -3.793, -5.195],
    //tempo
    [118.974, 138.002, 75.977, 150.99, 151.964],
    //valence
    [0.53, 0.67, 0.515, 0.7, 0.456],
    true
    ),
    new Question("Which of the following songs do you listen to the most?", ["Be Like That", "Like a Rodeo", "Lose It", "For My Daughter", "What Ifs"],
    //danceability
    [0.727, 0.67, 0.544, 0.537, 0.612],
    //acousticness
    [0.0469, 0.704, 0.00245, 0.275, 0.00898],
    //energy
    [0.626, 0.661, 0.854, 0.561, 0.799],
    //instrumentalness
    [0.0000258, 0, 0, 0, 0],
    //speechiness
    [0.0726, 0.0466, 0.0289, 0.0287, 0.0275],
    //loudness
    [-8.415, -6.798, -4.968, -8.09, -4.603],
    //tempo
    [86.97, 119.985, 91.966, 139.939, 125.976],
    //valence
    [0.322, 0.425, 0.436, 0.35, 0.687],
    true
    ),
    new Question("Which of the following songs do you listen to the most?", ["As I Am", "Anyone", "Hold On", "Ghost", "2 Much"],
    //danceability
    [0.595, 0.686, 0.658, 0.601, 0.583],
    //acousticness
    [0.127, 0.181, 0.0106, 0.185, 0.593],
    //energy
    [0.543, 0.538, 0.634, 0.741, 0.444],
    //instrumentalness
    [0, 0, 0,  0.0000291, 0],
    //speechiness
    [0.038, 0.0345, 0.0413, 0.0478, 0.0456],
    //loudness
    [-8.149, -8.026, -5.797, -5.569, -8.601],
    //tempo
    [99.928, 115.884, 139.98, 153.96, 119.59],
    //valence
    [0.109, 0.584, 0.29, 0.441, 0.167],
    true
    ),
    new Question("Which of the following songs do you listen to the most?", ["Anaconda", "Feeling Myself", "The Night is Still Young", "Yikes", "I'm Legit"],
    //danceability
    [0.964, 0.564, 0.656, 0.911, 0.859],
    //acousticness
    [0.0668, 0.437, 0.00212, 0.0409, 0.0301],
    //energy
    [0.605, 0.703, 0.692, 0.637, 0.746],
    //instrumentalness
    [0.00000778, 0.00927, 0.00305,  0.0000368, 0.000877],
    //speechiness
    [0.179, 0.269, 0.0563, 0.447, 0.0663],
    //loudness
    [-6.223, -5.459, -6.145, -8.381, -3.014],
    //tempo
    [129.99, 139.045, 128.016, 149.996, 75.002],
    //valence
    [0.646, 0.477, 0.693, 0.66, 0.543],
    true
    )



];


Quiz.prototype.get_currently_selected_answer = function () {
    let value = document.querySelector('input[name="Form1"]:checked').value
    if (value == "1") {
        return this.questions[this.questionIndex].choices[0];
    }
    else if (value == "2") {
        return this.questions[this.questionIndex].choices[1];
    }
    else if (value == "3") {
        return this.questions[this.questionIndex].choices[2];
    }
    else if (value == "4") {
        return this.questions[this.questionIndex].choices[3];
    }
    else if (value == "5") {
        return this.questions[this.questionIndex].choices[4];
    }
}


function Get_Question() {

    let element = document.getElementById("question");
    element.innerHTML = quiz.return_value_of_question().question;
    let options = quiz.return_value_of_question().choices;
    for (let i = 0; i < options.length; i++) {
        let element = document.getElementById("option" + i);
        element.innerHTML = options[i];
    }

};


let quiz = new Quiz(questions);
Get_Question();

function increment_and_reload(value) {
    let increment_value = 0;
    if (value == "1") {
        increment_value = 1;
        if(quiz.return_value_of_question().is_dynamic == true){
    
            quiz.change_question_index( quiz.return_question_index() * 5 + increment_value );
            quiz.set_previous_value_boolean(true);
        }
        else{
            if(quiz.return_previous_value_boolean() == true){
                console.log((quiz.return_question_index() - (quiz.return_question_index() % 5)) * 5 + 6);
                quiz.change_question_index( (quiz.return_question_index() - (quiz.return_question_index() % 5)) * 5 + 6);
                quiz.set_previous_value_boolean(false);
            }else{
                quiz.set_previous_value_boolean(false);
                quiz.change_question_index(quiz.return_question_index() + 1);
            }
        }
    }
    else if (value == "2") {
        increment_value = 2;
        if(quiz.return_value_of_question().is_dynamic == true){
            quiz.change_question_index( quiz.return_question_index() * 5 + increment_value );
            quiz.set_previous_value_boolean(true);
        }else{
            if(quiz.return_previous_value_boolean() == true){
                quiz.change_question_index( (quiz.return_question_index() - (quiz.return_question_index() % 5)) * 5 + 6);
                quiz.set_previous_value_boolean(false);
            }else{
                    quiz.set_previous_value_boolean(false);
                    quiz.change_question_index(quiz.return_question_index() + 1);
                }
        }
    }
    else if (value == "3") {
        increment_value = 3;
        if(quiz.return_value_of_question().is_dynamic == true){
            quiz.change_question_index( quiz.return_question_index() * 5 + increment_value );
            quiz.set_previous_value_boolean(true);
    }else{
        if(quiz.return_previous_value_boolean() == true){
            quiz.change_question_index( (quiz.return_question_index() - (quiz.return_question_index() % 5)) * 5 + 6);
            quiz.set_previous_value_boolean(false);
        }else{
                quiz.change_question_index(quiz.return_question_index() + 1);
                quiz.set_previous_value_boolean(false);
            }
    } 
    }
    else if (value == "4") {
        increment_value = 4;
        if(quiz.return_value_of_question().is_dynamic == true){
            quiz.change_question_index( quiz.return_question_index() * 5 + increment_value );
            quiz.set_previous_value_boolean(true);
    }else{
        if(quiz.return_previous_value_boolean() == true){
            quiz.change_question_index( (quiz.return_question_index() - (quiz.return_question_index() % 5)) * 5 + 6);
            quiz.set_previous_value_boolean(false);   
        }else{
                quiz.change_question_index(quiz.return_question_index() + 1);
                quiz.set_previous_value_boolean(false);
            }
    }
    }
    else if (value == "5") {
        if(quiz.return_value_of_question().is_dynamic == true){
        increment_value = 5;
        quiz.change_question_index( quiz.return_question_index() * 5 + increment_value );
        quiz.set_previous_value_boolean(true);
    }else{
        if(quiz.return_previous_value_boolean() == true){
            quiz.change_question_index( (quiz.return_question_index() - (quiz.return_question_index() % 5)) * 5 + 6);
            quiz.set_previous_value_boolean(false);
        }else{
            quiz.set_previous_value_boolean(false);
                quiz.change_question_index(quiz.return_question_index() + 1);
            }
    }  
    }
Get_Question();


    



}
