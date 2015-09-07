import recon
import ssl

from flask import Flask, jsonify

app = Flask(__name__)

player = recon.get_player("recon/steve.recon")

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
    context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
    context.load_cert_chain('cert/server.crt', 'cert/server.key')
    
    app.debug = True
    app.run(host="127.0.0.1", ssl_context=context)