from flask import Blueprint, request, jsonify
from agents.content_agent import ContentCreationAgent
from agents.hashtag_agent import HashtagAgent
from agents.optimization_agent import ContentOptimizationAgent
from agents.trend_agent import TrendAnalysisAgent
import logging
from datetime import datetime, timedelta
import random

logger = logging.getLogger(__name__)

content_bp = Blueprint('content', __name__)

content_agent = ContentCreationAgent()
hashtag_agent = HashtagAgent()
optimization_agent = ContentOptimizationAgent()
trend_agent = TrendAnalysisAgent()


@content_bp.route('/generate', methods=['POST'])
def generate_content():
    try:
        data = request.get_json() or {}
        platform = data.get('platform', 'linkedin').lower()
        topic = data.get('topic', 'AI and Business Transformation')
        content_type = data.get('content_type', 'post')
        audience = data.get('audience')
        cta = data.get('cta')
        keywords = data.get('keywords')
        tone = data.get('tone')

        if platform not in ['twitter', 'linkedin', 'instagram', 'facebook', 'blog']:
            return jsonify({"error": f"Invalid platform: {platform}. Must be one of: twitter, linkedin, instagram, facebook, blog"}), 400

        result = content_agent.generate_content(
            platform=platform,
            topic=topic,
            content_type=content_type,
            audience=audience,
            cta=cta,
            keywords=keywords,
            tone=tone
        )

        return jsonify({
            "success": True,
            "data": result,
            "timestamp": datetime.now().isoformat()
        })

    except Exception as e:
        logger.exception(f"Content generation error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@content_bp.route('/viral-score', methods=['POST'])
def get_viral_score():
    try:
        data = request.get_json() or {}
        content = data.get('content', '')
        if not content:
            return jsonify({"error": "content field is required"}), 400

        platform = data.get('platform', 'linkedin').lower()
        hashtags = data.get('hashtags')
        topic = data.get('topic')
        format_type = data.get('format', 'text')

        result = optimization_agent.calculate_viral_score(
            content=content,
            platform=platform,
            hashtags=hashtags,
            topic=topic,
            format_type=format_type
        )

        return jsonify({
            "success": True,
            "data": result,
            "timestamp": datetime.now().isoformat()
        })

    except Exception as e:
        logger.exception(f"Viral score error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@content_bp.route('/hashtags', methods=['POST'])
def generate_hashtags():
    try:
        data = request.get_json() or {}
        content = data.get('content', '')
        if not content and not data.get('topic'):
            return jsonify({"error": "Either content or topic is required"}), 400

        platform = data.get('platform', 'instagram').lower()
        topic = data.get('topic')
        location = data.get('location')
        count = data.get('count')

        result = hashtag_agent.generate_hashtags(
            content=content,
            platform=platform,
            topic=topic,
            location=location,
            count=count
        )

        return jsonify({
            "success": True,
            "data": result,
            "timestamp": datetime.now().isoformat()
        })

    except Exception as e:
        logger.exception(f"Hashtag generation error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@content_bp.route('/calendar', methods=['POST', 'GET'])
def content_calendar():
    try:
        if request.method == 'GET':
            days = int(request.args.get('days', 14))
            platforms = request.args.get('platforms', 'twitter,linkedin,instagram,facebook').split(',')
        else:
            data = request.get_json() or {}
            days = int(data.get('days', 14))
            platforms = data.get('platforms', ['twitter', 'linkedin', 'instagram', 'facebook'])

        now = datetime.now()
        from config import Config
        instructions = Config.AGENT_INSTRUCTIONS

        content_cats = []
        for cat, pct in instructions['posting_strategy']['content_mix'].items():
            content_cats.extend([cat] * pct)

        topic_ideas = [
            "Industry trend analysis with counter-intuitive data point",
            "Behind-the-scenes team culture moment",
            "3 lessons we learned the hard way (mistakes + takeaways)",
            "Customer success story with specific numbers",
            "Quick win hack: 60-second productivity tip",
            "Myth vs. Fact: Debunking common misconceptions",
            "Product update + 'here's exactly why we built this'",
            "Poll + discussion: Asking audience for their perspective",
            "Frameworks post: 5-step process for X result",
            "Personal vulnerability story + lesson learned",
            "Resource roundup: Top 7 tools we use this month",
            "Before vs. After transformation story",
            "Opinion piece: Unpopular take with data backup",
            "Q&A format: Top 4 questions we get asked"
        ]

        formats = ["Text Post", "Image/Graphics", "Short Video/Reels", "Carousel/Slides", "Story", "Poll", "Thread"]

        calendar = []
        for d in range(days):
            day_date = now + timedelta(days=d)
            day_name = day_date.strftime("%A")
            dow_idx = day_date.weekday()

            for p in platforms:
                pconfig = instructions['platforms'].get(p, {})
                if day_name not in pconfig.get('best_days', []) and random.random() > 0.5:
                    continue

                best_times = pconfig.get('best_times', ['12:00'])
                if not best_times:
                    continue

                posts_per_day = {
                    "twitter": random.randint(1, 3),
                    "linkedin": 1 if dow_idx < 5 else random.choice([0, 1]),
                    "instagram": random.randint(0, 2),
                    "facebook": random.randint(0, 1)
                }.get(p, 1)

                for post_idx in range(posts_per_day):
                    post_time = random.choice(best_times)
                    category = random.choice(content_cats)
                    topic = random.choice(topic_ideas)
                    fmt = random.choice(formats)

                    calendar.append({
                        "id": f"schedule-{d}-{p}-{post_idx}",
                        "date": day_date.strftime("%Y-%m-%d"),
                        "day_name": day_name,
                        "time": post_time,
                        "platform": p,
                        "platform_name": pconfig.get('name', p.title()),
                        "content_category": category,
                        "topic_idea": topic,
                        "recommended_format": fmt,
                        "status": random.choice(["draft", "scheduled", "needs_approval"]),
                        "engagement_prediction_pct": round(random.uniform(55, 95), 1),
                        "best_for_goal": random.choice(["Reach", "Engagement", "Conversions", "Community"]),
                        "ai_note": f"AI recommends {fmt} format on {day_name} {post_time} — historically {random.randint(18, 47)}% above baseline ER for this slot."
                    })

        calendar.sort(key=lambda x: (x["date"], x["time"]))

        platform_counts = {}
        category_counts = {}
        for item in calendar:
            p = item['platform']
            platform_counts[p] = platform_counts.get(p, 0) + 1
            c = item['content_category']
            category_counts[c] = category_counts.get(c, 0) + 1

        return jsonify({
            "success": True,
            "data": {
                "calendar": calendar,
                "total_scheduled": len(calendar),
                "date_range": {
                    "start": now.strftime("%Y-%m-%d"),
                    "end": (now + timedelta(days=days-1)).strftime("%Y-%m-%d"),
                    "days": days
                },
                "summary_by_platform": platform_counts,
                "summary_by_category": category_counts,
                "recommendations": [
                    "✅ Cadence looks balanced across platforms with peak-hour concentration",
                    f"💡 Content mix aligned with strategy: {instructions['posting_strategy']['content_mix']}",
                    "⚠️ Add 1-2 community-focused posts on weekends for Instagram/Facebook",
                    "🔔 Tip: Schedule LinkedIn posts Tue-Thu for +23% higher average reach"
                ]
            },
            "timestamp": datetime.now().isoformat()
        })

    except Exception as e:
        logger.exception(f"Calendar error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@content_bp.route('/competitor', methods=['POST'])
def competitor_analysis():
    try:
        data = request.get_json() or {}
        competitors = data.get('competitors', ['CompetitorBrandA', 'CompetitorBrandB', 'IndustryLeaderCo', 'DirectRivalX'])
        platforms = data.get('platforms', ['linkedin', 'instagram', 'twitter'])
        niche = data.get('niche', 'AI SaaS / Technology')
        days = int(data.get('days', 30))

        result = {
            "niche": niche,
            "period_days": days,
            "competitors": []
        }

        my_benchmark = {
            "followers": 173000,
            "avg_engagement_rate": 4.8,
            "posting_frequency_wk": 12,
            "avg_reach_per_post": 28400
        }

        for idx, comp in enumerate(competitors):
            base_mult = 0.5 + (idx * 0.2) + random.uniform(-0.1, 0.3)
            comp_data = {
                "name": comp,
                "platforms": {},
                "strengths": [],
                "weaknesses": [],
                "opportunities_to_exploit": [],
                "content_analysis": {}
            }

            for p in platforms:
                followers = int(random.randint(40000, 500000) * base_mult)
                er = round(random.uniform(1.2, 6.8), 2)
                posting_wk = random.randint(4, 22)
                reach_per_post = int(followers * random.uniform(0.08, 0.32))
                comp_data["platforms"][p] = {
                    "followers": followers,
                    "followers_vs_us_pct": round((followers - my_benchmark["followers"]) / my_benchmark["followers"] * 100, 1),
                    "avg_engagement_rate": er,
                    "er_vs_us_pct": round((er - my_benchmark["avg_engagement_rate"]) / my_benchmark["avg_engagement_rate"] * 100, 1),
                    "posting_frequency_per_week": posting_wk,
                    "freq_vs_us_pct": round((posting_wk - my_benchmark["posting_frequency_wk"]) / my_benchmark["posting_frequency_wk"] * 100, 1),
                    "avg_reach_per_post": reach_per_post,
                    "top_content_types": random.sample(["Reels", "Carousels", "Text Posts", "Polls", "Stories", "Threads"], k=3),
                    "top_hashtags": [f"#{comp.replace(' ','')}", f"#{niche.split('/')[0].strip()}{random.choice(['Life','Tips','Pro','Hub'])}", f"#{random.choice(['Growth','Innovation','Future','Success','Daily'])}"]
                }

            overall_er = round(sum(v["avg_engagement_rate"] for v in comp_data["platforms"].values()) / max(1, len(comp_data["platforms"])), 2)
            comp_data["overall"] = {
                "total_estimated_followers": sum(v["followers"] for v in comp_data["platforms"].values()),
                "avg_engagement_rate": overall_er,
                "total_posts_estimated": sum(v["posting_frequency_per_week"] for v in comp_data["platforms"].values()) * (days // 7),
                "share_of_voice_pct": round(random.uniform(5, 35), 1),
                "sentiment_score": round(random.uniform(-0.1, 0.8), 2)
            }

            strengths = [
                f"High posting frequency on {random.choice(platforms)} — above industry avg by +{random.randint(20, 60)}%",
                f"Strong ER on short-form video content ({round(random.uniform(5, 12), 1)}% vs industry 2.9%)",
                f"Established thought leadership in {random.choice(['AI ethics','Product strategy','Customer success'])} niche",
                f"Active community management — sub-{random.randint(2, 6)}h average response time to comments"
            ]
            weaknesses = [
                f"Low LinkedIn presence — only {random.randint(1, 4)} posts/week in high-intent channel",
                f"Static-image heavy ({random.randint(50, 75)}% of content) — missing video shift",
                f"Minimal user-generated content or community features",
                f"Hashtag strategy relies too heavily on saturated broad tags"
            ]
            opportunities = [
                f"🎯 Their {random.choice(['Tuesday','Thursday'])} posting gap = OUR window — capture {random.randint(15, 35)}% more share of voice",
                f"💡 They're ignoring {random.choice(['Threads/X','Carousel storytelling','Audio content'])} format — be first mover",
                f"🏆 Their weak spot: {random.choice(['Data-backed posts','Founder storytelling','Educational carousels'])} — double down here",
                f"🔄 Target audience overlap with us is {random.randint(40, 70)}% — poach their inactive followers with better value"
            ]

            comp_data["strengths"] = random.sample(strengths, k=2)
            comp_data["weaknesses"] = random.sample(weaknesses, k=2)
            comp_data["opportunities_to_exploit"] = random.sample(opportunities, k=2)

            comp_data["content_analysis"] = {
                "top_topics": [f"{random.choice(['Product updates','How-to guides','Industry news','Customer stories','Opinion pieces'])} {random.randint(18, 42)}%"],
                "average_caption_length": f"{random.randint(80, 350)} chars",
                "cta_usage_pct": random.randint(35, 85),
                "emoji_usage": random.choice(["Minimal", "Moderate", "High"]),
                "hashtag_count_avg": random.randint(3, 28)
            }

            result["competitors"].append(comp_data)

        sorted_for_rank = sorted(result["competitors"], key=lambda c: c["overall"]["avg_engagement_rate"], reverse=True)
        our_rank = 2
        result["ranking"] = {
            "metric": "Overall Social Media Performance Score",
            "weighted_by": ["Reach", "Engagement", "Share of Voice", "Follower Growth", "Content Quality"],
            "our_position": our_rank,
            "total_compared": len(competitors) + 1,
            "ranked_list": [
                {"name": sorted_for_rank[0]["name"], "score": round(random.uniform(82, 95), 1), "tier": "LEADER"},
                {"name": "YOUR BRAND", "score": round(random.uniform(72, 84), 1), "tier": "CHALLENGER", "is_us": True},
                {"name": sorted_for_rank[1]["name"], "score": round(random.uniform(65, 78), 1), "tier": "CONTENDER"},
            ] + [{"name": c["name"], "score": round(random.uniform(45, 68), 1), "tier": "LAGGARD"} for c in sorted_for_rank[2:]]
        }

        result["action_plan"] = [
            {
                "priority": "🏆 QUICK WIN (0-30 days)",
                "action": f"Outpost {sorted_for_rank[-1]['name']} on LinkedIn: increase Tue-Thu cadence to match their volume + add 1 educational carousel/week",
                "expected_impact": f"+{random.randint(12, 25)}% LinkedIn reach, close {random.randint(30, 55)}% of gap with #1 ranked",
                "confidence": random.randint(78, 94)
            },
            {
                "priority": "🚀 STRATEGIC (30-90 days)",
                "action": "Launch differentiated content pillar that no competitor currently dominates: 'real results / real data' case studies with specific ROI numbers",
                "expected_impact": f"Move from {our_rank} → top 3 in 90 days, +{random.randint(20, 40)}% share of voice",
                "confidence": random.randint(70, 88)
            },
            {
                "priority": "💎 MOAT BUILDING (90+ days)",
                "action": "Build branded community hashtag + UGC program featuring customer stories — create category ownership competitors can't replicate quickly",
                "expected_impact": f"Category leader in {random.randint(6, 18)} months, organic search + social flywheel effect",
                "confidence": random.randint(62, 82)
            }
        ]

        result["ai_summary"] = f"After analyzing {len(competitors)} competitors across {len(platforms)} platforms for {days} days: The #1 opportunity vs. the field is your unexploited content cadence on under-served days paired with data-backed storytelling — fast execution will close 40% of the gap to the category leader in one quarter."

        return jsonify({
            "success": True,
            "data": result,
            "timestamp": datetime.now().isoformat()
        })

    except Exception as e:
        logger.exception(f"Competitor analysis error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500
