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
Quiz.prototype.return_index = function() {
    return this.questions[this.questionIndex];
    
}
function Question(question, choices) {
    this.question = question;
    this.choices = choices;
};

var questions = [
    new Question("Which of the following genres do you prefer?",["Rock", "Country", "Pop","Sea-Shanties","Tibetan Throat Singing"])


];
function Create_Quiz(){

    var element = document.getElementById("question");
    element.innerHTML = quiz.return_index().question;
    var options  = quiz.return_index().choices;
    for(var i = 0; i < options.length; i++){
        var element  = document.getElementById("option"+i); 
       element.innerHTML = options[i];
    }

};


var quiz = new Quiz(questions);
Create_Quiz();
