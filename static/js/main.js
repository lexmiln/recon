
function setUpUniqueIDs() {
    var id_counter = 1;
    Object.defineProperty(Object.prototype, "__uniqueId", {
        writable: true
    });
    Object.defineProperty(Object.prototype, "uniqueId", {
        get: function() {
            if (this.__uniqueId === undefined)
                this.__uniqueId = id_counter++;
            return this.__uniqueId;
        }
    });
}

function testSpeech() {
    var msg = new SpeechSynthesisUtterance('Everything looks good, I am able to speak just fine.');
    window.speechSynthesis.speak(msg);
}

$(function(){
    setUpUniqueIDs();

    $("#test-tts").click(testSpeech);    

    ENGINE.setup($("#begin-conversation"));
});