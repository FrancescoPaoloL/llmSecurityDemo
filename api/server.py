from flask import Flask
from flask_cors import CORS
from config import Config
from routes import health_bp, test_bp, version_bp
from routes.plugin import plugin_bp
from routes.llm10 import llm10_bp          # added
from error import register_error_handlers
from __version__ import __version__

app = Flask(__name__)
CORS(app)

try:
    Config.validate()
except (ValueError, FileNotFoundError) as e:
    print(f"Configuration error: {e}")
    exit(1)

app.register_blueprint(health_bp)
app.register_blueprint(test_bp)
app.register_blueprint(version_bp)
app.register_blueprint(plugin_bp)
app.register_blueprint(llm10_bp)

register_error_handlers(app)

if __name__ == '__main__':
    print(f"Starting OWASP LLM API Server v{__version__}")
    print(f"\tEnvironment: {Config.FLASK_ENV}")
    print(f"\tPort: {Config.FLASK_PORT}")
    print(f"\tDebug: {Config.FLASK_DEBUG}\n")
    app.run(
        host='0.0.0.0',
        port=Config.FLASK_PORT,
        debug=Config.FLASK_DEBUG
    )

