var ENABLE_RECOGNITION = true;

var recognition;
var recognizing = false;
var final_transcript = "";
var $beginConversationButton;

var exchange = new IVY.Exchange();
var transcript;
var ui;

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

function setUpRecognition() {
    recognition = new webkitSpeechRecognition();
    recognition.continuous = true;
    recognition.interim = true;
    recognition.interimResults = true; // Not W3C-compliant.
    resetRecognition();
    recognition.onend = resetRecognition;
    recognition.onresult = function(event) {
        var partial_transcript = "";
        
        for (var i = event.resultIndex; i < event.results.length; ++i) {
            var text = event.results[i][0].transcript;
            if (event.results[i].isFinal) {
                final_transcript += text;
            } else {
                partial_transcript += text;
            }
        }

        $("#final-results").html(final_transcript);
        $("#partial-results").html(partial_transcript);
        
        exchange.updateWithTranscripts(final_transcript, partial_transcript);
        ui.forceUpdate();
    };
}

function toggleRecognition() {
    if (recognizing) {
        resetRecognition();
    } else {
        beginRecognition();
    }    
}

function beginRecognition() {
    transcript = React.createElement(Transcript, {
        "exchanges": [exchange]
    });
    
    ui = React.render(transcript, document.getElementById('transcript-container'));
    
    if (ENABLE_RECOGNITION) {
        recognition.start();
    }
    recognizing = true;
    $beginConversationButton.html("Stop");
    $beginConversationButton.removeClass("btn-primary").addClass("btn-danger");
}

// Called whether the user stopped the recognition, or the user agent did.
function resetRecognition() {
    recognition.stop();
    recognizing = false;
    $beginConversationButton.html("Start Conversation");
    $beginConversationButton.removeClass("btn-danger").addClass("btn-primary");
}

function testSpeech() {
    var msg = new SpeechSynthesisUtterance('Everything looks good, I am able to speak just fine.');
    window.speechSynthesis.speak(msg);
}

function setUpUI() {
    $beginConversationButton = $("#begin-conversation");
    
    $("#test-tts").click(testSpeech);    
    $beginConversationButton.click(toggleRecognition);
}

$(function(){
    setUpUniqueIDs();
    setUpUI();
    setUpRecognition();
});