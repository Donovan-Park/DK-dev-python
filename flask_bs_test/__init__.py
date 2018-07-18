import os

from flask import (
	Flask, render_template
)

app = Flask(__name__)

@app.route('/')
def bootstrap_home():
	return render_template("bs_home.html")

if __name__=='__main__':
	app.run(debug=True)