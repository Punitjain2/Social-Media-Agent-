import os
from dotenv import load_dotenv

load_dotenv()


AGENT_INSTRUCTIONS = {
    "brand_voice": {
        "personality": "Professional yet approachable, innovative, and forward-thinking",
        "tone": "Confident, inspiring, knowledgeable, and friendly",
        "style": "Modern, concise, impactful with strategic use of emojis",
        "language": "English (US)",
        "avoid": ["Jargon overload", "Overly casual slang", "Controversial topics", "Misleading claims"]
    },

    "content_style": {
        "max_length": {
            "twitter": 280,
            "linkedin": 3000,
            "instagram": 2200,
            "facebook": 5000,
            "blog": 2000,
            "caption": 500
        },
        "paragraph_length": "2-4 sentences per paragraph",
        "use_emojis": True,
        "use_hashtags": True,
        "hashtag_count": {
            "twitter": {"min": 2, "max": 4, "optimal": 3},
            "linkedin": {"min": 3, "max": 7, "optimal": 5},
            "instagram": {"min": 10, "max": 30, "optimal": 20},
            "facebook": {"min": 2, "max": 5, "optimal": 3}
        },
        "cta_position": "end",
        "storytelling": True,
        "use_questions": True,
        "use_statistics": True
    },

    "platforms": {
        "twitter": {
            "name": "Twitter/X",
            "enabled": True,
            "best_times": ["09:00", "12:00", "15:00", "18:00", "21:00"],
            "best_days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
            "content_types": ["Updates", "Threads", "Polls", "Retweets with comments", "Short insights"],
            "character_limit": 280,
            "thread_optimization": True
        },
        "linkedin": {
            "name": "LinkedIn",
            "enabled": True,
            "best_times": ["08:00", "10:00", "12:00", "14:00", "17:00"],
            "best_days": ["Tuesday", "Wednesday", "Thursday"],
            "content_types": ["Thought leadership", "Case studies", "Industry insights", "Career advice", "Company updates"],
            "character_limit": 3000,
            "professional_tone": True
        },
        "instagram": {
            "name": "Instagram",
            "enabled": True,
            "best_times": ["11:00", "13:00", "17:00", "19:00", "21:00"],
            "best_days": ["Monday", "Tuesday", "Friday", "Saturday", "Sunday"],
            "content_types": ["Reels", "Carousels", "Stories", "Posts", "Guides"],
            "character_limit": 2200,
            "visual_focus": True
        },
        "facebook": {
            "name": "Facebook",
            "enabled": True,
            "best_times": ["09:00", "13:00", "15:00", "19:00"],
            "best_days": ["Thursday", "Friday", "Saturday", "Sunday"],
            "content_types": ["Updates", "Events", "Videos", "Polls", "Community posts"],
            "character_limit": 5000,
            "community_focus": True
        }
    },

    "posting_strategy": {
        "posts_per_week": {
            "twitter": 14,
            "linkedin": 5,
            "instagram": 5,
            "facebook": 4
        },
        "content_mix": {
            "educational": 30,
            "promotional": 20,
            "engaging": 25,
            "community": 15,
            "behind_the_scenes": 10
        },
        "a_b_testing": True,
        "recycling_enabled": True,
        "recycle_after_days": 30,
        "peak_hours_only": True,
        "frequency_cap": True
    },

    "safety_rules": {
        "content_moderation": True,
        "prohibited_content": [
            "Hate speech or discrimination",
            "Violence or threats",
            "Adult/explicit content",
            "False or misleading information",
            "Spam or excessive self-promotion",
            "Copyrighted material without permission",
            "Personal information without consent",
            "Illegal activities"
        ],
        "disclosure_requirements": {
            "sponsored_content": True,
            "ai_generated": False,
            "affiliate_links": True
        },
        "brand_safety_filters": True,
        "sentiment_threshold": -0.3,
        "human_review_required": False,
        "auto_approve_threshold": 0.8
    },

    "marketing_goals": {
        "primary_goal": "Increase brand awareness and engagement",
        "kpis": {
            "engagement_rate": "5%+",
            "follower_growth_monthly": "10%+",
            "click_through_rate": "3%+",
            "conversion_rate": "2%+",
            "reach_growth": "25%+ monthly"
        },
        "target_audience": {
            "age_range": "25-45",
            "professions": ["Tech professionals", "Entrepreneurs", "Marketing specialists", "Business leaders"],
            "interests": ["AI", "Technology", "Innovation", "Startups", "Digital transformation", "Marketing"],
            "locations": ["United States", "Europe", "Asia Pacific"]
        },
        "brand_messages": [
            "Innovation meets practicality",
            "Empowering businesses through AI",
            "Transforming social media strategy",
            "Data-driven decisions for growth"
        ],
        "call_to_actions": [
            "Learn more",
            "Try for free",
            "Book a demo",
            "Sign up today",
            "Get started",
            "Discover how"
        ]
    },

    "trend_settings": {
        "trend_sources": ["Twitter/X", "LinkedIn", "Google Trends", "News APIs", "Industry reports"],
        "trend_freshness_hours": 24,
        "min_trend_volume": 1000,
        "trend_relevance_threshold": 0.7,
        "max_trends_per_request": 10,
        "include_hashtag_trends": True,
        "include_topic_clusters": True
    },

    "hashtag_settings": {
        "mix_types": True,
        "types_mix": {"broad": 0.20, "niche": 0.50, "branded": 0.15, "trending": 0.15},
        "location_based": True,
        "industry_specific": True,
        "avoid_banned_hashtags": True,
        "research_competitor_hashtags": True
    },

    "analytics_settings": {
        "tracking_period_days": 30,
        "competitor_count": 5,
        "benchmark_industry": "technology",
        "sentiment_analysis_enabled": True,
        "viral_prediction_enabled": True,
        "realtime_monitoring": True,
        "ai_insights_frequency": "daily"
    }
}


class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'

    IBM_CLOUD_API_KEY = os.getenv('IBM_CLOUD_API_KEY', '')
    IBM_WATSONX_URL = os.getenv('IBM_WATSONX_URL', 'https://us-south.ml.cloud.ibm.com')
    IBM_WATSONX_PROJECT_ID = os.getenv('IBM_WATSONX_PROJECT_ID', '')

    IBM_MODEL_ID = os.getenv('IBM_MODEL_ID', 'meta-llama/llama-3-1-8b')
    IBM_EMBEDDING_MODEL_ID = os.getenv('IBM_EMBEDDING_MODEL_ID', 'ibm/slate-30m-english-rtrvr-v2')
    IBM_GENERATION_MODEL_ID = os.getenv('IBM_GENERATION_MODEL_ID', 'meta-llama/llama-3-1-8b')
    IBM_REASONING_MODEL_ID = os.getenv('IBM_REASONING_MODEL_ID', 'meta-llama/llama-3-3-70b-instruct')

    CORS_ORIGINS = os.getenv('CORS_ORIGINS', 'http://localhost:5000,http://localhost:3000').split(',')

    MAX_CONTENT_LENGTH = 16 * 1024 * 1024

    AGENT_INSTRUCTIONS = AGENT_INSTRUCTIONS
