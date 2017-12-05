from flask import Flask, request, render_template
app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def index():
	if request.method == 'POST':
		if request.form.get('steamid'):
			print "hello\n"
			print request.form['steamid']
	return render_template('index.html')




