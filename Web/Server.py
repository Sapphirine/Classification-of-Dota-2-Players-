from flask import Flask, request, render_template, jsonify
import os
import json

app = Flask(__name__)


@app.route('/')
def index():
	return render_template('index.html')


@app.route('/query')
def query():
	steam_id = request.args.get('x', 0, type=int)
	return jsonify(result=1)

@app.route('/json')
def graph_json():
	SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
	json_url = os.path.join(SITE_ROOT, "json", "graph.json")
	json_data = json.load(open(json_url))
	print json_data
	return jsonify(json_data)






