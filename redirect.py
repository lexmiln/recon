from flask import Flask, jsonify, redirect

app = Flask(__name__, static_folder=None)

@app.route("/", defaults={'path': ''})
@app.route("/<path:path>")
def send_to_https_site(path):
    return redirect("https://ivy.x13n.com/")

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=80)
