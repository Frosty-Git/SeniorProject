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

function input_answer() {
    var selected = document.getElementById("submit_the_question")
    selected.onclick = function() {
        this.questionIndex = this.questionIndex + 1
    }


}

var questions = [
    new Question("Which of the following genres do you prefer?",["Rock", "Country", "Pop","Sea-Shanties","Tibetan Throat Singing"]),
    new Question("Which of the following artists do you prefer?",["The Beatles", "Metallica", "The Grateful Dead","Electric Lights Orchestra","Simon and Garfunkel"]),
    new Question("Which of the following artists do you prefer?",["Carrie Underwood", "Dan + Shay", "Morgan Wallen","Luke Combs","Kane Brown"]),
    new Question("Which of the following artists do you prefer?",["Justin Beiber", "Nikki Minaj", "Katy Perry","Billy Eilish", "Ariana Grande"]),
    new Question("Which of the following artists do you prefer?",["The Irish Sailors", "", "Pop","Sea-Shanties","Tibetan Throat Singing"]),
    new Question("Which of the following artists do you prefer?",["Deva Premal", "Tibetan Monks", "The Gyuto Monks of Tibet","Tradidional","Shu-de"]),
 

];
function Get_Question(){

    var element = document.getElementById("question");
    element.innerHTML = quiz.return_value_of_question().question;
    var options  = quiz.return_value_of_question().choices;
    for(var i = 0; i < options.length; i++){
        var element  = document.getElementById("option"+i); 
       element.innerHTML = options[i];
    }

};


var quiz = new Quiz(questions);
<<<<<<< HEAD:django/static/js/question.js
Create_Quiz();
Get_Question();
while(true){
input_answer()


}
>>>>>>> 2cf8e08651991d9ca984fef8b0b241eb72a11a75:django/static/question.js
