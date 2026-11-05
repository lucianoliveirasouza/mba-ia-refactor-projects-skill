from datetime import datetime

from flask import Blueprint, jsonify

API_VERSION = '1.0'


def create_main_blueprint():
    bp = Blueprint('main', __name__)

    @bp.get('/health')
    def health():
        return jsonify({'status': 'ok', 'timestamp': str(datetime.now())})

    @bp.get('/')
    def index():
        return jsonify({'message': 'Task Manager API', 'version': API_VERSION})

    return bp
