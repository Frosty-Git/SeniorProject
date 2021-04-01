// code by Kevin Magill
function Quiz(questions) {
    this.questions = questions;
    this.questionIndex = 0;
}

Quiz.prototype.change_question_index = function (value) {
    this.questionIndex = value
}


Quiz.prototype.return_value_of_question = function () {
    return this.questions[this.questionIndex];

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
        true
    ),
    new Question("Which of the following artists do you prefer?", ["Justin Bieber", "Nikki Minaj", "Katy Perry", "Billy Eilish", "Ariana Grande"],
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
        }
        else{
            quiz.increment_question_index(increment_value);
        }
    }
    else if (value == "2") {
        increment_value = 2;
        if(quiz.return_value_of_question().is_dynamic == true){
            quiz.change_question_index( quiz.return_question_index() * 5 + increment_value );
        }else{
            quiz.increment_question_index(increment_value);
        }
    }
    else if (value == "3") {
        increment_value = 3;
        if(quiz.return_value_of_question().is_dynamic == true){
            quiz.change_question_index( quiz.return_question_index() * 5 + increment_value );
    }else{
        quiz.increment_question_index(increment_value);
    } 
    }
    else if (value == "4") {
        increment_value = 4;
        if(quiz.return_value_of_question().is_dynamic == true){
            quiz.change_question_index( quiz.return_question_index() * 5 + increment_value );
    }else{
        quiz.increment_question_index(increment_value);
    }
    }
    else if (value == "5") {
        if(quiz.return_value_of_question().is_dynamic == true){
        increment_value = 5;
        quiz.change_question_index( quiz.return_question_index() * 5 + increment_value );
    }else{
        quiz.increment_question_index(increment_value);
    }  
    }
Get_Question();


    



}
