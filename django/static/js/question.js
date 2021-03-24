// code by Kevin Magill
function Quiz(questions){
    this.questions = questions;
    this.questionIndex = 0;
    this.danceability = 0;
    this.accousticness = 0;
    this.danceability = 0;
    this.energy = 0;
    this.instrumentalness = 0;
    this.speechiness = 0;
    this.loudness = 0;
    this.tempo = 0;
    this.valence = 0;
}

Quiz.prototype.increment_question_index = function(value) {
    this.questionIndex = this.questionIndex + value;
}


Quiz.prototype.return_value_of_question = function() {
    return this.questions[this.questionIndex];
    
}

Quiz.prototype.return_question_index = function() {
    return this.questionIndex;
}

function Question(question, choices) {
    this.question = question;
    this.choices = choices;
};


let questions = [
    new Question("Which of the following genres do you prefer?",["Rock", "Country", "Pop","Sea-Shanties","Tibetan Throat Singing"]),
    new Question("Which of the following artists do you prefer?",["The Beatles", "Metallica", "The Grateful Dead","Electric Lights Orchestra","Simon and Garfunkel"]),
    new Question("Which of the following artists do you prefer?",["Carrie Underwood", "Dan + Shay", "Morgan Wallen","Luke Combs","Kane Brown"]),
    new Question("Which of the following artists do you prefer?",["Justin Beiber", "Nikki Minaj", "Katy Perry","Billy Eilish", "Ariana Grande"]),
    new Question("Which of the following artists do you prefer?",["The Irish Sailors", "The Largest Johns", "The Irish Rovers","The Fisherman's Friends","High Tide"]),
    new Question("Which of the following artists do you prefer?",["Deva Premal", "Tibetan Monks", "The Gyuto Monks of Tibet","Tradidional","Shu-de"]),
   // new Question("Which of the following songs do you listen to the most?", [""])
 

];
function Get_Question(){

    let element = document.getElementById("question");
    element.innerHTML = quiz.return_value_of_question().question;
    let options  = quiz.return_value_of_question().choices;
    for(let i = 0; i < options.length; i++){
        let element  = document.getElementById("option" + i); 
       element.innerHTML = options[i];
    }

};


let quiz = new Quiz(questions);
Get_Question();
function increment_and_reload(value){
    console.log(value)
    if (value == "1"){
    quiz.increment_question_index(1);
    }
    else if (value == "2"){
    quiz.increment_question_index(2);
    }
    else if (value == "3"){
    quiz.increment_question_index(3);
    }
    else if (value == "4"){
    quiz.increment_question_index(4);
    }
    else if (value == "5"){
    quiz.increment_question_index(5);
    }
    Get_Question();
 

}

