import os
import sys
import logging
from flask import Flask, render_template, send_from_directory
from flask_cors import CORS

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import Config
from routes.content_routes import content_bp
from routes.analysis_routes import analysis_bp
from routes.chat_routes import chat_bp

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def create_app():
    app = Flask(__name__,
                template_folder=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates'),
                static_folder=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static'))
    app.config.from_object(Config)

    CORS(app, resources={
        r"/api/*": {
            "origins": Config.CORS_ORIGINS,
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization", "X-Requested-With"]
        }
    })

    app.register_blueprint(content_bp, url_prefix='/api/content')
    app.register_blueprint(analysis_bp, url_prefix='/api/analysis')
    app.register_blueprint(chat_bp, url_prefix='/api/chat')

    @app.route('/')
    def index():
        return render_template('index.html',
                               platforms=list(Config.AGENT_INSTRUCTIONS['platforms'].keys()),
                               brand_voice=Config.AGENT_INSTRUCTIONS['brand_voice'])

    @app.route('/api/health')
    def api_health():
        from datetime import datetime
        return {
            "success": True,
            "service": "Social Media Agent API",
            "status": "healthy",
            "version": "1.0.0",
            "model": app.config.get('IBM_GENERATION_MODEL_ID'),
            "timestamp": datetime.now().isoformat()
        }

    @app.route('/@vite/client')
    def vite_client_stub():
        return "", 200

    @app.errorhandler(404)
    def not_found(e):
        return {"success": False, "error": "Route not found"}, 404

    @app.errorhandler(500)
    def server_error(e):
        logger.exception("Internal server error")
        return {"success": False, "error": "Internal server error"}, 500

    return app


app = create_app()


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = app.config.get('DEBUG', True)
    logger.info(f"🚀 Starting Social Media Agent on port {port} (debug={debug})")
    logger.info(f"🔧 IBM Model: {app.config.get('IBM_GENERATION_MODEL_ID')}")
    app.run(host='0.0.0.0', port=port, debug=debug, use_reloader=False, threaded=True)
