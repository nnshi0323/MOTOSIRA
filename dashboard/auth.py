import os
from functools import wraps
from flask import session, redirect, url_for, request, jsonify
from dotenv import load_dotenv

load_dotenv()

VALID_USER = os.getenv('MOTOSIRA_USER', 'admin')
VALID_PASS = os.getenv('MOTOSIRA_PASS', 'motosira123')

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('logged_in'):
            if request.is_json or request.path.startswith('/api/'):
                return jsonify({"error": "Unauthorized"}), 401
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

def check_credentials(username, password):
    return username == VALID_USER and password == VALID_PASS