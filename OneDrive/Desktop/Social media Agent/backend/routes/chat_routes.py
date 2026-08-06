from flask import Blueprint, request, jsonify
from services.watsonx_service import watsonx_service
from agents.content_agent import ContentCreationAgent
from agents.hashtag_agent import HashtagAgent
from agents.optimization_agent import ContentOptimizationAgent
from agents.trend_agent import TrendAnalysisAgent
from agents.sentiment_agent import SentimentAnalysisAgent
import logging
from datetime import datetime
import re
import json

logger = logging.getLogger(__name__)

chat_bp = Blueprint('chat', __name__)

content_agent = ContentCreationAgent()
hashtag_agent = HashtagAgent()
optimization_agent = ContentOptimizationAgent()
trend_agent = TrendAnalysisAgent()
sentiment_agent = SentimentAnalysisAgent()


def _detect_intent(message: str) -> dict:
    msg_lower = message.lower()

    intents = {
        "linkedin_post": {
            "keywords": ["linkedin", "b2b", "professional post", "thought leadership"],
            "platform": "linkedin",
            "action": "generate_content",
            "content_type": "post"
        },
        "tweet_thread": {
            "keywords": ["tweet", "twitter", "thread", "x post", "280"],
            "platform": "twitter",
            "action": "generate_content",
            "content_type": "thread"
        },
        "instagram_caption": {
            "keywords": ["instagram", "caption", "reels", "ig post", "insta"],
            "platform": "instagram",
            "action": "generate_content",
            "content_type": "caption"
        },
        "facebook_post": {
            "keywords": ["facebook", "fb post", "community post"],
            "platform": "facebook",
            "action": "generate_content",
            "content_type": "post"
        },
        "blog_article": {
            "keywords": ["blog", "article", "long-form", "post for blog", "write a blog"],
            "platform": "blog",
            "action": "generate_content",
            "content_type": "article"
        },
        "hashtags": {
            "keywords": ["hashtag", "tags", "keywords for", "seo tags"],
            "action": "generate_hashtags"
        },
        "viral_score": {
            "keywords": ["viral", "score", "rate my", "how will this perform", "engagement potential", "predict"],
            "action": "viral_score"
        },
        "trends": {
            "keywords": ["trend", "viral topic", "what's trending", "hot topic", "popular right now"],
            "action": "analyze_trends"
        },
        "sentiment": {
            "keywords": ["sentiment", "how do people feel", "analyze comments", "opinion", "audience reaction"],
            "action": "analyze_sentiment"
        },
        "analytics": {
            "keywords": ["analytics", "dashboard", "metrics", "report", "how are we doing", "performance"],
            "action": "analytics"
        }
    }

    detected = None
    for intent_id, intent_data in intents.items():
        for kw in intent_data["keywords"]:
            if kw in msg_lower:
                detected = {"intent_id": intent_id, **intent_data}
                break
        if detected:
            break

    if not detected:
        if any(p in msg_lower for p in ["create", "generate", "write", "draft", "make me"]) and \
           any(t in msg_lower for t in ["post", "content", "caption", "article", "copy"]):
            detected = {"intent_id": "content_generic", "action": "generate_content",
                        "platform": "linkedin", "content_type": "post"}
        else:
            detected = {"intent_id": "general_assist", "action": "chat"}

    return detected


def _extract_topic(message: str) -> str:
    remove_patterns = [
        r'(?i)^(create|generate|write|draft|make|suggest|can you|please|i need|help me|want)\s+(a|an|the|some|me)?\s*',
        r'(?i)\s+(for\s+(my|our|a|an|the)\s+)?(post|content|caption|article|blog|tweet|thread|linkedin|twitter|instagram|facebook|copy)\s*.*$',
        r'(?i)\s+about\s+',
        r'(?i)[?.!]+$'
    ]
    topic = message
    for pattern in remove_patterns:
        topic = re.sub(pattern, '', topic).strip()
    if len(topic) < 3:
        return "AI and Business Transformation"
    if len(topic) > 120:
        return topic[:120].rsplit(' ', 1)[0]
    return topic.title() if topic.islower() else topic


@chat_bp.route('/message', methods=['POST'])
def chat_message():
    try:
        data = request.get_json() or {}
        messages = data.get('messages', [])
        if not messages:
            user_message = data.get('message', '')
            messages = [{"role": "user", "content": user_message}]
        elif isinstance(messages, list) and len(messages) > 0 and isinstance(messages[-1], dict):
            user_message = messages[-1].get('content', '')
        else:
            user_message = ''

        if not user_message:
            return jsonify({"error": "message is required"}), 400

        intent = _detect_intent(user_message)
        topic = _extract_topic(user_message)
        platform = intent.get('platform', 'linkedin')
        action = intent.get('action', 'chat')

        tool_result = None
        tool_name = None

        if action == "generate_content":
            result = content_agent.generate_content(
                platform=platform,
                topic=topic,
                content_type=intent.get('content_type', 'post')
            )
            tool_name = "Content Creation Agent"
            tool_result = {
                "type": "content_generated",
                "platform": platform,
                "topic": topic,
                "content": result.get("content", ""),
                "variations": result.get("variations", []),
                "cta": result.get("call_to_action"),
                "suggested_media": result.get("suggested_media")
            }

        elif action == "generate_hashtags":
            result = hashtag_agent.generate_hashtags(
                content=user_message,
                topic=topic,
                platform=platform
            )
            tool_name = "Hashtag Recommendation Agent"
            tags = [h["tag"] for h in result.get("hashtags", [])]
            tool_result = {
                "type": "hashtags_generated",
                "count": len(tags),
                "hashtags": tags,
                "strategy": result.get("strategy", "")
            }

        elif action == "viral_score":
            sample = user_message + "\n\nThis is a sample content placeholder to demonstrate viral scoring. In a real use case, you would provide the actual content text you want analyzed."
            result = optimization_agent.calculate_viral_score(
                content=sample,
                platform=platform,
                topic=topic
            )
            tool_name = "Content Optimization Agent"
            tool_result = {
                "type": "viral_score",
                "score": result.get("viral_score"),
                "label": result.get("viral_likelihood_label"),
                "strengths": result.get("strengths", []),
                "improvements": result.get("improvements", [])[:3]
            }

        elif action == "analyze_trends":
            result = trend_agent.analyze_trends(niche=topic, limit=8)
            tool_name = "Trend Analysis Agent"
            trends_summary = [{"topic": t["topic"], "velocity": t["velocity"],
                                "growth": t["growth_indicator"]} for t in result.get("trends", [])[:5]]
            tool_result = {
                "type": "trends_analysis",
                "top_trends": trends_summary,
                "insights": result.get("insights", [])[:3],
                "opportunities": result.get("opportunities", [])[:2]
            }

        elif action == "analyze_sentiment":
            sample_comments = [
                "Absolutely love this product! 10/10 would recommend 💯",
                "Great customer support and amazing features.",
                "The new update is a game changer for our team.",
                "Had some issues at first but support resolved quickly.",
                "This saved us 20 hours a week. Total ROI in 1 month!",
                "Wish the pricing was a bit more flexible though.",
                "Easy to use, intuitive interface, team adopted instantly.",
                "Document could be better. Otherwise 5 stars."
            ]
            result = sentiment_agent.analyze_sentiment(sample_comments)
            tool_name = "Sentiment Analysis Agent"
            overall = result.get("overall", {})
            tool_result = {
                "type": "sentiment_analysis",
                "overall_score": overall.get("sentiment_score"),
                "label": overall.get("sentiment_label"),
                "distribution": overall.get("distribution", {}),
                "insights": result.get("actionable_insights", [])[:3]
            }

        assistant_message = watsonx_service.chat(messages)
        if not assistant_message or len(assistant_message.strip()) < 10:
            if tool_result:
                tool_type = tool_result.get("type")
                if tool_type == "content_generated":
                    assistant_message = f"""✨ Here's what the **Content Creation Agent** prepared for you:

**Platform**: {tool_result['platform'].title()}
**Topic**: {tool_result['topic']}

📝 Generated Content:
{tool_result['content'][:1500]}

---
💡 Variations available: {len(tool_result['variations'])} alternatives
🎯 Suggested CTA: {tool_result['cta'] or 'Standard'}
🖼️ Suggested Media: {tool_result['suggested_media'] or 'Brand-aligned visual'}

**What would you like to do next?**
• Optimize for viral potential
• Generate custom hashtags
• Create a different variation
• Schedule this on the content calendar"""

                elif tool_type == "hashtags_generated":
                    tags_display = " ".join(tool_result["hashtags"][:20])
                    assistant_message = f"""🏷️ **Hashtag Strategy Ready**

The Hashtag Recommendation Agent generated {tool_result['count']} optimized tags:

{tags_display}

📊 Strategy Notes:
{tool_result['strategy'][:500]}

Tip: Use Set A vs. Set B (saved in full results) to A/B test which hashtag mix drives better discovery!

Need anything adjusted — more niche, more broad, specific location, or different platform?"""

                elif tool_type == "viral_score":
                    improvements = "\n".join([
                        f"  • **{imp['priority']}**: +{imp['expected_lift_pct']}% lift — {imp['suggested'][:80]}"
                        for imp in tool_result["improvements"]
                    ])
                    assistant_message = f"""🔬 **Viral Potential Analysis Complete**

**Score**: {tool_result['score']}/100 — **{tool_result['label']}**

⭐ Key Strengths:
{chr(10).join('  • ' + s[:100] for s in (tool_result['strengths'] or [])[:3])}

🛠️ Top Optimization Opportunities:
{improvements}

Next steps: Apply these improvements, re-score, and if score >85, schedule during peak windows! Want me to rewrite the content with all improvements applied?"""

                elif tool_type == "trends_analysis":
                    trends_list = "\n".join([
                        f"  • {t['topic']} — {t['growth']} ({t['velocity']}% velocity)"
                        for t in tool_result["top_trends"]
                    ])
                    insights_list = "\n".join([
                        f"  💡 {i[:120]}" for i in tool_result.get("insights", [])
                    ])
                    assistant_message = f"""📈 **Trend Report: Top Opportunities Right Now**

{trends_list}

**Key Insights from Trend Analysis Agent:**
{insights_list}

💡 Recommendation: Start creating content around the fastest-growing micro-trend before it saturates. Want me to draft a content calendar with these trends woven in?"""

                elif tool_type == "sentiment_analysis":
                    d = tool_result["distribution"]
                    assistant_message = f"""💬 **Audience Sentiment Analysis Complete**

**Overall**: {tool_result['label']} ({tool_result['overall_score']:+.2f})

📊 Sentiment Distribution:
  • 😃 Very Positive: {d.get('very_positive_pct', 0)}%
  • 🙂 Positive: {d.get('positive_pct', 0)}%
  • 😐 Neutral: {d.get('neutral_pct', 0)}%
  • ☹️ Negative: {d.get('negative_pct', 0)}%
  • 😠 Very Negative: {d.get('very_negative_pct', 0)}%

**Top Actionable Insights:**
{chr(10).join('  • ' + s[:120] for s in (tool_result['insights'] or []))}

Want me to deep-dive into the negative comments, identify root causes, and draft response templates?"""

            else:
                assistant_message = f"""👋 Hi there! I'm your **AI Social Media Agent**, powered by IBM Granite models on watsonx.ai.

I can help you with:

**✍️ Content Creation**
- "Create a LinkedIn post about AI for Engineers"
- "Generate viral Instagram captions for my startup"
- "Write a Twitter thread on productivity"
- "Draft a Facebook community post"
- "Blog article about digital marketing trends"

**🔍 Analysis & Optimization**
- "Score this post for viral potential"
- "What's trending in SaaS marketing right now?"
- "Generate 20 hashtags for a Reel about AI"
- "Analyze audience sentiment from these comments"
- "Show me the 30-day analytics dashboard"
- "Compare my brand to 4 competitors"

**🗓️ Strategy**
- "Build me a 2-week content calendar"
- "Best posting times for LinkedIn thought leadership"
- "Competitor analysis for the top 3 brands in AI"

Try one of the examples above, or tell me exactly what you need! 💬"""

        return jsonify({
            "success": True,
            "data": {
                "intent_detected": intent.get("intent_id", "general_assist"),
                "action": action,
                "tool_used": tool_name,
                "tool_result": tool_result,
                "assistant_message": assistant_message
            },
            "timestamp": datetime.now().isoformat()
        })

    except Exception as e:
        logger.exception(f"Chat error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500
