var ENGINE = (function(){
    var my = {};
    
    // pseudo-constants
    var ENABLE_RECOGNITION = true;

    // recogniser state
    var recognition;
    var recognizing = false;
    var finalized_speech = "";

    // conversation state
    var exchanges;
    var exchange;
    var cursor;
    var choice;

    // jquery objects 
    var $controlButton; 

    // react objects
    var ui;

    var reset = function() {
        recognition.abort();
        recognizing = false;
        $controlButton.html("Start Conversation");
        $controlButton.removeClass("btn-danger").addClass("btn-primary");
    };

    var begin = function() {
        // Reset the conversation.
        exchanges = [];
        exchange = null;
        cursor = 0;
        choice = null;

        // Ask the server for the first exchange.
        $.getJSON("/dialog/test/").done(handle);

        var transcript = React.createElement(Transcript, {
            "exchanges": exchanges
        });
        ui = React.render(transcript, document.getElementById('transcript-container'));
    };
    
    var listen = function() {
        finalized_speech = "";

        if (ENABLE_RECOGNITION) {
            recognition.start();
        }
        recognizing = true;
        $controlButton.html("Stop");
        $controlButton.removeClass("btn-primary").addClass("btn-danger");
    };

    // New conversation responses from the server are handled here. They
    // may continue the conversation, or signal that the conversation is
    // over.
    var handle = function(json) {
        exchange = new IVY.Exchange(json, winner);
        exchanges.push(exchange);
        var msg = new SpeechSynthesisUtterance(exchange.agentSpeech);
        window.speechSynthesis.speak(msg);
        ui.forceUpdate();

        if (json.action === "input") {
            listen();
        }
    };
    
    // Called by exchanges when a winner has been chosen.
    var winner = function(option) {
        // Stop recognition, in order to discard unfinalized results.
        reset();
        
        // Get the index of the winner.
        var index = _.indexOf(exchange.userOptions, option);
        
        // Ask the server for the next part of the conversation.
        $.getJSON("/dialog/test/" + exchange.cursor + "/" + index).done(handle);
    };


    var control = function () {
        if (recognizing) {
            reset();
        } else {
            begin();
        }    
    };

    my.setup = function (controlButton) {
        $controlButton = controlButton;
        $controlButton.click(control);
        
        recognition = new webkitSpeechRecognition();
        recognition.continuous = true;
        recognition.interim = true;        // W3C-compliant.
        recognition.interimResults = true; // Not W3C-compliant, for Chrome
        recognition.lang = "en-GB";
        reset();
        recognition.onend = reset;
        recognition.onresult = function(event) {
            var provisional_speech = "";
            
            for (var i = event.resultIndex; i < event.results.length; ++i) {
                var text = event.results[i][0].transcript;
                if (event.results[i].isFinal) {
                    finalized_speech += text;
                } else {
                    provisional_speech += text;
                }
            }

            exchange.updateWithTranscripts(finalized_speech, provisional_speech);
            ui.forceUpdate();
        };
    };


    return my;
}());