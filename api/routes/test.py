from flask import Blueprint, request, jsonify
from llama_service import LlamaService

test_bp = Blueprint('test', __name__)
llama_service = LlamaService()

@test_bp.route('/api/test', methods=['POST'])
def test_prompt():
    try:
        data = request.get_json()

        if not data or 'prompt' not in data:
            return jsonify({'error': 'Missing prompt field'}), 400

        prompt = data['prompt']
        max_tokens = data.get('max_tokens', 50)

        if len(prompt) > 5000:
            return jsonify({'error': 'Prompt too long (max 5000 characters)'}), 400

        result = llama_service.process_prompt(prompt, max_tokens)

        return jsonify(result), 200

    except RuntimeError as e:
        return jsonify({'error': str(e)}), 500
    except Exception as e:
        return jsonify({'error': f'Unexpected error: {str(e)}'}), 500

