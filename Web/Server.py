from flask import Flask, request, render_template, jsonify
app = Flask(__name__)


@app.route('/')
def index():
	return render_template('index.html')


@app.route('/query')
def query():
	steam_id = request.args.get('x', 0, type=int)
	return jsonify(result=1)





