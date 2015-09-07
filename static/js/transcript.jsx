var Transcript = React.createClass({
    render: function() {
        var exchange_elements = _.map(this.props.exchanges, function(exchange) {
            return <Exchange key={exchange.uniqueId} data={exchange}/>
        }, this);
        
        return <div className="transcript">
            <h2>Transcript</h2>
            {exchange_elements}
        </div>;
    }
});

var Exchange = React.createClass({
    render: function() {
        var data = this.props.data;
        
        var option_elements = _.map(data.userOptions, function(option) {
            return <UserOption 
                key={option.uniqueId} 
                data={option} 
                isWinner={data.winner === option}
                />
        });
        
        return <div className="exchange">
            <h3>{data.agentSpeech}</h3>
            <p className="speech">
                <span className="prompt">&gt; </span>
                <span className="final">{data.finalSpeech}</span>
                <span className="provisional"> {data.provisionalSpeech}</span>
            </p>
            <ul>{option_elements}</ul>
        </div>;
    }
});

var UserOption = React.createClass({
    render: function() {
        var data = this.props.data;
        var status = "ineligible";
        
        if (this.props.isWinner) {
            status = "winner";
        } else if (data.isEligibleToWin()) {
            status = "eligible";
        }

        return <li className={"option " + status}>
            <span className="score">
                {data.getScorePercent()}
            </span>
            <span className="checkmark">
                <i className="glyphicon glyphicon-ok"></i>
            </span>
            {data.sentence}
        </li>;
    }
});