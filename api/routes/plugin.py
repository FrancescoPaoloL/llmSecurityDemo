import sqlite3
import os
from flask import Blueprint, request, jsonify

plugin_bp = Blueprint('plugin', __name__)

DB_PATH = os.path.join(os.path.dirname(__file__), '../../data/northwind.db')

BLOCKED_KEYWORDS = ['drop', 'delete', 'insert', 'update', 'alter', 'create', 'truncate']

def is_safe_query(query: str) -> bool:
    # Naive keyword-based protection.
    # Intentionally incomplete to demonstrate LLM07 vulnerability.
    lower = query.lower()
    for keyword in BLOCKED_KEYWORDS:
        if keyword in lower:
            return False
    return True

def execute_query(query: str) -> list:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute(query)
    rows = [dict(row) for row in cursor.fetchmany(20)]
    conn.close()
    return rows

@plugin_bp.route('/api/plugin/query', methods=['POST'])
def query():
    data = request.get_json()
    sql = data.get('query', '').strip()
    mode = data.get('mode', 'unsafe')

    if not sql:
        return jsonify({'error': 'No query provided'}), 400

    if mode == 'safe':
        if not is_safe_query(sql):
            return jsonify({
                'query_executed': sql,
                'results': [],
                'safe_mode': True,
                'warning': 'Query blocked: contains dangerous keywords'
            }), 200

    try:
        results = execute_query(sql)
        return jsonify({
            'query_executed': sql,
            'results': results,
            'safe_mode': mode == 'safe',
            'warning': None
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


