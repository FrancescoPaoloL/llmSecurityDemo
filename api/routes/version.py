from flask import Blueprint, jsonify
from __version__ import __version__

version_bp = Blueprint('version', __name__)

@version_bp.route('/api/version', methods=['GET'])
def get_version():
    return jsonify({
        'api_version': __version__,
        'detection_coverage': '4/10',
        'detection_accuracy': '84%'
    }), 200
