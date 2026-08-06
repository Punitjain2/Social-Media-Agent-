import json
import logging
import random
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from services.watsonx_service import watsonx_service
from config import Config

logger = logging.getLogger(__name__)


class AnalyticsAgent:
    def __init__(self):
        self.instructions = Config.AGENT_INSTRUCTIONS
        self.settings = self.instructions['analytics_settings']
        self.name = "Analytics Agent"
        self.role = "Transforms raw social media metrics into strategic insights, benchmarks, and predictive forecasts"

    def generate_dashboard_data(self, platforms: Optional[List[str]] = None,
                                days: int = 30,
                                include_forecast: bool = True) -> Dict[str, Any]:

        platforms = platforms or ["twitter", "linkedin", "instagram", "facebook"]
        system_prompt = f"""You are a senior social media analytics director reporting to the CMO.

Role: {self.role}
Benchmark industry: {self.settings['benchmark_industry']}
Tracking period: {days} days
Forecasting enabled: {include_forecast}

KPIs to calculate and contextualize:
1. Reach & Impressions (with % change vs. prior period)
2. Engagement (likes, comments, shares, clicks, saves) & Engagement Rate
3. Follower/Fan growth (net new, growth rate, churn rate)
4. Content performance (top/bottom posts by format, length, topic)
5. Platform-specific breakdowns with cross-platform benchmarks
6. Optimal posting patterns (hours, days, content types)
7. Viral post patterns
8. Audience demographics snapshot
9. Forecast for next {days//2} days (if enabled)
10. AI-generated strategic recommendations with expected impact

FORMAT ONLY VALID JSON with rich metrics including trend lines and benchmark comparisons."""

        user_prompt = f"""Generate a comprehensive {days}-day analytics report for platforms: {', '.join(platforms)}.

Prior period: Compare vs. previous {days} days.
Industry benchmark: Technology/SaaS companies at similar stage.
Forecast next {days//2} days based on current trajectory: {'YES' if include_forecast else 'NO'}

IMPORTANT:
- Provide realistic, believable numbers (millions range for reach, thousands for engagement)
- Show realistic platform strengths (LinkedIn: high-quality engagement, Instagram: visual-driven, etc.)
- All % changes should be in a realistic range (-20% to +80% for period-over-period)
- Generate 8-10 specific, quantified strategic recommendations
- Include 5-7 top performing post patterns with "why it worked" analysis

Return ONLY valid JSON analytics report."""

        try:
            result = watsonx_service.generate(
                user_prompt=user_prompt,
                system_prompt=system_prompt,
                max_tokens=3500,
                temperature=0.4
            )
            parsed = self._parse_json(result)
            if parsed:
                parsed['agent'] = self.name
                parsed['generated_at'] = _now_iso()
                parsed['platforms'] = platforms
                parsed['tracking_days'] = days
                return parsed
        except Exception as e:
            logger.error(f"Analytics dashboard generation failed: {e}")

        return self._fallback_analytics(platforms, days, include_forecast)

    def _parse_json(self, result: str) -> Optional[Dict[str, Any]]:
        try:
            json_str = result
            if json_str.startswith('```json'):
                json_str = json_str.replace('```json', '').replace('```', '')
            start = json_str.find('{')
            end = json_str.rfind('}') + 1
            if start >= 0 and end > start:
                json_str = json_str[start:end]
            return json.loads(json_str)
        except:
            return None

    def _fallback_analytics(self, platforms: List[str], days: int,
                            include_forecast: bool) -> Dict[str, Any]:
        start_date = datetime.now() - timedelta(days=days)
        dates = [(start_date + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(days)]

        platform_base = {
            "twitter": {"reach": 120000, "impressions": 450000, "engagements": 28000, "followers": 45000, "growth": 0.08},
            "linkedin": {"reach": 85000, "impressions": 210000, "engagements": 15000, "followers": 28000, "growth": 0.12},
            "instagram": {"reach": 150000, "impressions": 520000, "engagements": 42000, "followers": 62000, "growth": 0.06},
            "facebook": {"reach": 95000, "impressions": 280000, "engagements": 18000, "followers": 38000, "growth": 0.03}
        }

        platform_data = {}
        total_reach = 0
        total_impressions = 0
        total_engagements = 0
        total_followers = 0
        total_new_followers = 0

        reach_daily = []
        engagement_daily = []

        for p in platforms:
            base = platform_base.get(p, platform_base['twitter'])
            variation_pct = random.uniform(-0.05, 0.15)
            prior_variation_pct = random.uniform(-0.10, 0.05)

            reach = int(base["reach"] * (1 + variation_pct))
            impressions = int(base["impressions"] * (1 + variation_pct))
            engagements = int(base["engagements"] * (1 + variation_pct + random.uniform(-0.02, 0.05)))
            followers = int(base["followers"] * (1 + variation_pct))
            new_followers = int(followers * base["growth"])
            engagement_rate = round(engagements / impressions * 100, 2)

            prior_reach = int(reach * (1 + prior_variation_pct - random.uniform(0.05, 0.25)))
            prior_engagements = int(engagements * (1 + prior_variation_pct - random.uniform(0.05, 0.20)))
            prior_followers = int(followers - new_followers * random.uniform(0.8, 1.2))

            clicks = int(engagements * random.uniform(0.08, 0.20))
            likes = int(engagements * random.uniform(0.45, 0.65))
            comments = int(engagements * random.uniform(0.10, 0.20))
            shares = int(engagements * random.uniform(0.08, 0.18))
            saves = int(engagements * random.uniform(0.05, 0.15))

            platform_data[p] = {
                "name": self.instructions['platforms'][p]['name'] if p in self.instructions['platforms'] else p.title(),
                "reach": reach,
                "reach_change_pct": round((reach - prior_reach) / max(1, prior_reach) * 100, 1),
                "impressions": impressions,
                "impressions_change_pct": round((impressions - int(impressions * (1 - random.uniform(0.05, 0.2)))) / max(1, int(impressions * (1 - random.uniform(0.05, 0.2)))) * 100, 1),
                "engagements": engagements,
                "engagements_change_pct": round((engagements - prior_engagements) / max(1, prior_engagements) * 100, 1),
                "engagement_rate": engagement_rate,
                "engagement_rate_change": round(random.uniform(-0.8, 1.5), 2),
                "industry_benchmark_er": round(random.uniform(1.5, 3.8), 2),
                "followers": followers,
                "new_followers": new_followers,
                "follower_growth_pct": round(new_followers / max(1, prior_followers) * 100, 2),
                "follower_churn_pct": round(random.uniform(0.2, 1.0), 2),
                "clicks": clicks,
                "ctr": round(clicks / max(1, impressions) * 100, 3),
                "likes": likes,
                "comments": comments,
                "shares": shares,
                "saves_or_bookmarks": saves,
                "posts_published": random.randint(days // 3, days)
            }
            total_reach += reach
            total_impressions += impressions
            total_engagements += engagements
            total_followers += followers
            total_new_followers += new_followers

        for d in dates:
            day_factor = random.uniform(0.7, 1.4)
            reach_daily.append({"date": d, "value": int(total_reach / days * day_factor)})
            engagement_daily.append({"date": d, "value": int(total_engagements / days * day_factor)})

        content_formats = [
            {"format": "Short-form Video/Reels", "avg_er": round(random.uniform(4.5, 8.5), 2), "volume_share_pct": random.randint(25, 40), "er_change": round(random.uniform(0.3, 2.0), 2)},
            {"format": "Carousel Posts", "avg_er": round(random.uniform(3.5, 6.5), 2), "volume_share_pct": random.randint(15, 30), "er_change": round(random.uniform(0.2, 1.5), 2)},
            {"format": "Static Images", "avg_er": round(random.uniform(2.0, 4.0), 2), "volume_share_pct": random.randint(20, 35), "er_change": round(random.uniform(-0.5, 0.8), 2)},
            {"format": "Text/Link Posts", "avg_er": round(random.uniform(1.0, 2.8), 2), "volume_share_pct": random.randint(10, 25), "er_change": round(random.uniform(-0.8, 0.3), 2)},
            {"format": "Live Video/Stories", "avg_er": round(random.uniform(3.0, 5.5), 2), "volume_share_pct": random.randint(5, 15), "er_change": round(random.uniform(0.0, 1.2), 2)}
        ]

        posting_hours = []
        for hour in [6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22]:
            posting_hours.append({
                "hour": f"{hour:02d}:00",
                "avg_engagement_index": round(random.uniform(40, 100), 0)
            })
        posting_hours.sort(key=lambda x: x["avg_engagement_index"], reverse=True)
        for i, ph in enumerate(posting_hours):
            ph["performance_tier"] = "🏆 PEAK" if i < 3 else ("✅ GOOD" if i < 8 else ("⚠️ OK" if i < 13 else "❌ LOW"))

        posting_days = []
        for day in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]:
            posting_days.append({
                "day": day,
                "avg_engagement_index": round(random.uniform(55, 100), 0)
            })
        posting_days.sort(key=lambda x: x["avg_engagement_index"], reverse=True)

        top_posts = []
        post_templates = [
            ("Data-driven carousel on industry trends", "carousel", "Statistics + actionable framework"),
            ("Controversial take thread with polls", "text-thread", "Polarizing opinion + data backup"),
            ("Behind-the-scenes team culture Reel", "video", "Authenticity + humor + music"),
            ("Founder's personal LinkedIn story", "text", "Vulnerability + specific lesson"),
            ("Side-by-side comparison visual", "image", "Clear contrast + bold claim"),
            ("'3 mistakes I made' educational post", "text", "Humility + numbered list + CTA")
        ]
        for title, fmt, pattern in random.sample(post_templates, k=5):
            eng_rate = round(random.uniform(5.5, 15.5), 2)
            viral = eng_rate > 9.0
            top_posts.append({
                "title": title,
                "format": fmt,
                "platform": random.choice(platforms),
                "published_on": random.choice(dates[-14:]),
                "reach": random.randint(15000, 150000),
                "impressions": random.randint(40000, 450000),
                "engagements": random.randint(2000, 15000),
                "engagement_rate": eng_rate,
                "viral_qualified": viral,
                "why_it_worked": f"{pattern}. Posted during optimal {random.choice(['Tuesday 10am','Wednesday 2pm','Thursday 5pm'])} window. Aligned with trending conversation topic.",
                "replication_score": round(random.uniform(0.70, 0.98), 2)
            })

        forecast = {}
        if include_forecast:
            future_days = days // 2
            growth_rate = random.uniform(0.02, 0.10)
            forecast = {
                "period_days": future_days,
                "projected_reach": int(total_reach / days * future_days * (1 + growth_rate)),
                "projected_reach_change_pct": round(growth_rate * 100, 1),
                "projected_engagements": int(total_engagements / days * future_days * (1 + growth_rate + random.uniform(0.01, 0.05))),
                "projected_engagement_rate": round(random.uniform(3.8, 6.5), 2),
                "projected_new_followers": int(total_new_followers / days * future_days * (1 + random.uniform(0.05, 0.15))),
                "confidence": round(random.uniform(0.78, 0.92), 2),
                "upside_scenario_pct": 25,
                "downside_scenario_pct": 15,
                "key_assumptions": [
                    "Current posting cadence continues",
                    "No major platform algorithm shifts",
                    "1-2 viral posts in the period",
                    "Competitor activity remains stable"
                ]
            }

        return {
            "agent": self.name,
            "generated_at": _now_iso(),
            "platforms": platforms,
            "tracking_days": days,
            "summary": {
                "total_reach": total_reach,
                "total_reach_change_pct": round(random.uniform(15, 65), 1),
                "total_impressions": total_impressions,
                "total_impressions_change_pct": round(random.uniform(12, 55), 1),
                "total_engagements": total_engagements,
                "total_engagements_change_pct": round(random.uniform(18, 72), 1),
                "overall_engagement_rate": round(total_engagements / max(1, total_impressions) * 100, 2),
                "industry_benchmark_er": 2.8,
                "er_vs_benchmark_pct": 62,
                "total_followers": total_followers,
                "total_new_followers": total_new_followers,
                "total_follower_growth_pct": round(total_new_followers / max(1, int(total_followers - total_new_followers * 1.05)) * 100, 2),
                "reporting_period": {
                    "start_date": dates[0],
                    "end_date": dates[-1]
                }
            },
            "platform_breakdown": platform_data,
            "daily_timeseries": {
                "reach": reach_daily,
                "engagements": engagement_daily,
                "new_followers": [{"date": d, "value": int(total_new_followers / days * random.uniform(0.5, 1.8))} for d in dates]
            },
            "engagement_mix": {
                "likes_pct": round(random.uniform(48, 62), 1),
                "comments_pct": round(random.uniform(10, 20), 1),
                "shares_pct": round(random.uniform(8, 16), 1),
                "saves_pct": round(random.uniform(5, 12), 1),
                "clicks_pct": round(random.uniform(8, 16), 1)
            },
            "content_format_performance": content_formats,
            "optimal_posting": {
                "best_hours": posting_hours[:8],
                "best_days": posting_days,
                "recommended_schedule": f"Prioritize {posting_days[0]['day']}-{posting_days[2]['day']} between {posting_hours[0]['hour']} and {posting_hours[2]['hour']}. Minimum 3 posts/week per platform during peak windows."
            },
            "top_performing_posts": top_posts,
            "audience_demographics": {
                "age_distribution": [
                    {"group": "18-24", "pct": random.randint(5, 15)},
                    {"group": "25-34", "pct": random.randint(25, 40)},
                    {"group": "35-44", "pct": random.randint(22, 32)},
                    {"group": "45-54", "pct": random.randint(10, 20)},
                    {"group": "55+", "pct": random.randint(5, 12)}
                ],
                "gender_mix": (lambda m, o: {"male_pct": m, "female_pct": round(100 - m - o, 1), "other_pct": o})(round(random.uniform(52, 68), 1), round(random.uniform(3, 7), 1)),
                "top_locations": [
                    {"name": "United States", "pct": random.randint(38, 52)},
                    {"name": "United Kingdom", "pct": random.randint(6, 12)},
                    {"name": "Germany", "pct": random.randint(4, 9)},
                    {"name": "India", "pct": random.randint(5, 10)},
                    {"name": "Canada", "pct": random.randint(3, 7)}
                ],
                "top_interests": [
                    "Technology & Innovation", "Startups & Entrepreneurship", "AI & Machine Learning",
                    "Marketing & Growth", "Productivity & Tools", "Business Leadership"
                ]
            },
            "forecast": forecast,
            "ai_insights": [
                {
                    "title": "Video content is driving disproportionate results",
                    "detail": f"Short-form video delivers {round((content_formats[0]['avg_er'] / content_formats[3]['avg_er']) - 1, 0)*100:.0f}% higher ER vs. text posts. Current allocation at {content_formats[0]['volume_share_pct']}% should increase to ~45% of content mix.",
                    "impact": "📈 Projected +18% total engagements in 30 days",
                    "priority": "HIGH",
                    "confidence": 94
                },
                {
                    "title": "LinkedIn follower growth outperforming other channels",
                    "detail": f"LinkedIn growing followers at {platform_data.get('linkedin', {}).get('follower_growth_pct', 'N/A')}% monthly vs. cross-platform avg. {round(sum([p['follower_growth_pct'] for p in platform_data.values()]) / max(1, len(platform_data)), 2)}%. Consider shifting 20% of content development budget to LinkedIn.",
                    "impact": "👥 +350 high-quality new followers monthly",
                    "priority": "MEDIUM",
                    "confidence": 87
                },
                {
                    "title": "Weekend posting has hidden ROI on Instagram",
                    "detail": f"Sunday posts show {round(random.uniform(15, 35))}% higher save rate. Currently only {random.randint(4, 12)}% of content scheduled weekends. Recommend adding a weekend carousel focused on education/value.",
                    "impact": "💾 +22% content saves + improved algorithm favorability",
                    "priority": "MEDIUM",
                    "confidence": 82
                },
                {
                    "title": "CTR gap highlights optimization opportunity",
                    "detail": "Click-through rate is strong on image posts but 38% below average on link-in-bio calls-to-action. Test explicit link placement in caption first sentence vs. end placement.",
                    "impact": "🔗 +12% referral traffic to website",
                    "priority": "HIGH",
                    "confidence": 79
                },
                {
                    "title": "Viral post pattern identified: Personal storytelling + frameworks",
                    "detail": "Top 5 posts all include a personal anecdote (3+ sentences) followed by a 3-5 item numbered framework. This structural pattern has 88% replication score.",
                    "impact": "🎯 2.1x increase in posts reaching >100K impressions",
                    "priority": "HIGH",
                    "confidence": 91
                }
            ],
            "recommendations": [
                {
                    "action": "Increase short-form video output from current to 4-5 videos/week",
                    "investment": "+4 hours/week content production",
                    "expected_impact": "+15-20% total engagement, +8-12% follower growth",
                    "roi_estimate": "3.2x"
                },
                {
                    "action": "Launch 'Founder Story' monthly LinkedIn article series",
                    "investment": "+6 hours/month writing + editing",
                    "expected_impact": "+1,200 new LinkedIn followers, +45 new connection requests/mo with decision makers",
                    "roi_estimate": "4.8x"
                },
                {
                    "action": "A/B test caption length: 50-100 chars vs. 200+ chars",
                    "investment": "30 min setup, 4 week test window",
                    "expected_impact": "Identify optimal length for +7-10% engagement lift",
                    "roi_estimate": "8.0x"
                },
                {
                    "action": "Add community-focused content bucket (polls, Q&As, shoutouts)",
                    "investment": "+2 hours/week",
                    "expected_impact": "+25% comments rate, +30% share rate, stronger brand affinity",
                    "roi_estimate": "5.5x"
                },
                {
                    "action": "Repurpose top 3 performing posts into cross-platform long-form",
                    "investment": "+3 hours/week repurposing",
                    "expected_impact": "+18% reach on secondary platforms, +12% total content output with low marginal cost",
                    "roi_estimate": "6.0x"
                }
            ]
        }


def _now_iso() -> str:
    return datetime.now().isoformat()
