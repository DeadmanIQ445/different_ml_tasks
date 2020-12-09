
from flask import Flask
from flask import render_template
from flask import request

import process_dataset
app = Flask(__name__)

@app.route('/query', methods=['GET'])
def query():
    if request.method == 'GET':
        n = request.args.get("n")
        if n is None:
            docs = engine_obj.query(request.args.get('query'))
        else:
            docs = engine_obj.query(request.args.get('query'), int(request.args.get('n')))
        return render_template('results.html', docs=docs)
    return 0


@app.route('/')
def hello_world(name=None):
    return render_template('main.html', name=name)


engine_obj = process_dataset.Engine()
if __name__ == '__main__':
    app.run()
