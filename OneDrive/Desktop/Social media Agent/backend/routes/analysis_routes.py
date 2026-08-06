from flask import Blueprint, request, jsonify
from agents.sentiment_agent import SentimentAnalysisAgent
from agents.analytics_agent import AnalyticsAgent
from agents.trend_agent import TrendAnalysisAgent
from config import Config
import logging
from datetime import datetime
import random

logger = logging.getLogger(__name__)

analysis_bp = Blueprint('analysis', __name__)

sentiment_agent = SentimentAnalysisAgent()
analytics_agent = AnalyticsAgent()
trend_agent = TrendAnalysisAgent()


@analysis_bp.route('/trends', methods=['GET', 'POST'])
def get_trends():
    try:
        if request.method == 'GET':
            niche = request.args.get('niche')
            platforms = request.args.get('platforms')
            limit = int(request.args.get('limit', 10))
            include_ideas = request.args.get('include_ideas', 'true').lower() == 'true'
            platforms_list = platforms.split(',') if platforms else None
        else:
            data = request.get_json() or {}
            niche = data.get('niche')
            platforms_list = data.get('platforms')
            limit = int(data.get('limit', 10))
            include_ideas = data.get('include_ideas', True)

        result = trend_agent.analyze_trends(
            niche=niche,
            platforms=platforms_list,
            limit=limit,
            include_ideas=include_ideas
        )

        return jsonify({
            "success": True,
            "data": result,
            "timestamp": datetime.now().isoformat()
        })

    except Exception as e:
        logger.exception(f"Trends analysis error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@analysis_bp.route('/sentiment', methods=['POST'])
def analyze_sentiment():
    try:
        data = request.get_json() or {}
        texts = data.get('texts')
        if not texts or not isinstance(texts, list):
            sample_comments = [
                "This product is absolutely amazing! Game changer for our team 🔥",
                "Pretty good overall but the onboarding was confusing at first.",
                "Customer support helped me within 10 minutes. Incredible service!",
                "Meh. Not sure if it's worth the price yet. Still evaluating.",
                "The new update broke everything. Frustrating! 😡",
                "I recommended this to 3 colleagues already. Total game changer.",
                "Documentation is lacking. Took me 3 days to figure out basic setup.",
                "Absolutely love the community. Everyone is so helpful 💙",
                "Feature request: dark mode for the dashboard please!",
                "ROI in 2 weeks. Enough said. Worth every penny 💯",
                "Compared to competitor X, this is night and day better.",
                "Wish the mobile app was smoother. Desktop version is great though.",
                "Honest 10/10. Been using it daily for 6 months now.",
                "Not a fan of the recent pricing changes. Disappointing update.",
                "Saved me 5 hours a week. That adds up fast ⏰"
            ]
            texts = data.get('comments', sample_comments)

        detail_level = data.get('detail_level', 'standard')
        include_emotions = data.get('include_emotions', True)
        include_topics = data.get('include_topics', True)

        result = sentiment_agent.analyze_sentiment(
            texts=texts,
            detail_level=detail_level,
            include_emotions=include_emotions,
            include_topics=include_topics
        )

        return jsonify({
            "success": True,
            "data": result,
            "timestamp": datetime.now().isoformat()
        })

    except Exception as e:
        logger.exception(f"Sentiment analysis error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@analysis_bp.route('/analytics', methods=['GET', 'POST'])
def get_analytics():
    try:
        if request.method == 'GET':
            platforms = request.args.get('platforms')
            days = int(request.args.get('days', 30))
            include_forecast = request.args.get('include_forecast', 'true').lower() == 'true'
            platforms_list = platforms.split(',') if platforms else None
        else:
            data = request.get_json() or {}
            platforms_list = data.get('platforms')
            days = int(data.get('days', 30))
            include_forecast = data.get('include_forecast', True)

        result = analytics_agent.generate_dashboard_data(
            platforms=platforms_list,
            days=days,
            include_forecast=include_forecast
        )

        return jsonify({
            "success": True,
            "data": result,
            "timestamp": datetime.now().isoformat()
        })

    except Exception as e:
        logger.exception(f"Analytics error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@analysis_bp.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        "success": True,
        "service": "Social Media Agent API",
        "status": "healthy",
        "version": "1.0.0",
        "agents_available": [
            "Content Creation Agent",
            "Trend Analysis Agent",
            "Hashtag Recommendation Agent",
            "Sentiment Analysis Agent",
            "Analytics Agent",
            "Content Optimization Agent"
        ],
        "platforms_supported": list(Config.AGENT_INSTRUCTIONS['platforms'].keys()),
        "timestamp": datetime.now().isoformat()
    })
