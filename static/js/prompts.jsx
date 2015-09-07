var Prompts = React.createClass({
    render: function() {
        var exchange = this.props.exchange;

        if (exchange === null) {
            return <div className="prompts">
                <p>Waiting for server...</p>
            </div>
        } else if (exchange.userOptions.length) {
            var optionElements = _.map(exchange.userOptions, function(option) {
                return <Prompt 
                    key={option.uniqueId} 
                    option={option} 
                    isWinner={exchange.winner === option}
                    />
            });
            
            return <div className="prompts">
                <p>{exchange.agentSpeech}</p>
                <ul>{optionElements}</ul>
            </div>
        } else {
            return <div className="prompts">
                <p>{exchange.agentSpeech}</p>
                <ul><li>The conversation has finished. You can start it again if you like.</li></ul>
            </div>
        }
    }
});

var Prompt = React.createClass({
    render: function() {
        var option = this.props.option;
        var status = "ineligible";
        
        if (this.props.isWinner) {
            status = "winner";
        } else if (option.isEligibleToWin()) {
            status = "eligible";
        }

        return <li className={"option " + status}>
            <i className="glyphicon glyphicon-chevron-right"></i> {option.sentence}
        </li>;
    }
});