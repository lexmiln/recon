import recon

from flask import Flask, jsonify

app = Flask(__name__)

player = recon.get_player("test.recon")

@app.route('/')
def root():
    return app.send_static_file('index.html')
        
@app.route('/dialog/test/')
def dialog():
    return jsonify(
        **player.play(continuous=False)
    )
    
@app.route('/dialog/test/<int:cursor>/<int:choice>')
def choice(cursor, choice):
    return jsonify(
        **player.play(continuous=False, cursor=cursor, choice=choice)
    )
        
if __name__ == '__main__':
    app.debug = True
    app.run()