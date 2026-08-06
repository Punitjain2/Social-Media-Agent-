import os
import sys
import logging

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from config import Config

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = create_app()

if __name__ == '__main__':
    from waitress import serve
    port = int(os.getenv('PORT', 5000))
    logger.info(f"🚀 Starting Social Media Agent (Waitress) on port {port}")
    logger.info(f"🔧 IBM Model: {app.config.get('IBM_GENERATION_MODEL_ID')}")
    logger.info(f"🌐 Access at: http://127.0.0.1:{port}")
    serve(app, host='0.0.0.0', port=port, threads=8)
