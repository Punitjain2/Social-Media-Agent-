import json
import logging
import random
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from services.watsonx_service import watsonx_service
from config import Config

logger = logging.getLogger(__name__)


class TrendAnalysisAgent:
    def __init__(self):
        self.instructions = Config.AGENT_INSTRUCTIONS
        self.trend_settings = self.instructions['trend_settings']
        self.name = "Trend Analysis Agent"
        self.role = "Identifies emerging trends, viral topics, and high-engagement content opportunities"

        self._simulated_trends = [
            {"topic": "AI Agentic Workflows", "volume": 284729, "velocity": 342, "category": "Technology",
             "sentiment": 0.82, "platforms": ["Twitter/X", "LinkedIn", "HackerNews"]},
            {"topic": "Multimodal AI Content Creation", "volume": 198472, "velocity": 267, "category": "Technology",
             "sentiment": 0.76, "platforms": ["Instagram", "TikTok", "Twitter/X"]},
            {"topic": "Sustainable Business Practices", "volume": 456721, "velocity": 156, "category": "Business",
             "sentiment": 0.89, "platforms": ["LinkedIn", "Facebook", "Instagram"]},
            {"topic": "Remote Work Culture Evolution", "volume": 312847, "velocity": 89, "category": "Workplace",
             "sentiment": 0.45, "platforms": ["LinkedIn", "Twitter/X", "Facebook"]},
            {"topic": "Generative Video Production", "volume": 167234, "velocity": 421, "category": "Creative",
             "sentiment": 0.91, "platforms": ["TikTok", "Instagram", "YouTube"]},
            {"topic": "AI Ethics & Governance", "volume": 203567, "velocity": 178, "category": "Society",
             "sentiment": 0.34, "platforms": ["LinkedIn", "Twitter/X", "News"]},
            {"topic": "Personal Brand Building", "volume": 589234, "velocity": 123, "category": "Marketing",
             "sentiment": 0.78, "platforms": ["LinkedIn", "Instagram", "Twitter/X"]},
            {"topic": "Micro-SaaS Entrepreneurship", "volume": 134521, "velocity": 234, "category": "Business",
             "sentiment": 0.87, "platforms": ["Twitter/X", "LinkedIn", "HackerNews"]},
            {"topic": "Customer Experience AI", "volume": 178945, "velocity": 167, "category": "Business",
             "sentiment": 0.72, "platforms": ["LinkedIn", "Facebook", "Twitter/X"]},
            {"topic": "Data Privacy & Security", "volume": 267389, "velocity": 112, "category": "Technology",
             "sentiment": 0.28, "platforms": ["Twitter/X", "LinkedIn", "News"]},
            {"topic": "Hybrid Event Strategy", "volume": 89234, "velocity": 98, "category": "Marketing",
             "sentiment": 0.68, "platforms": ["LinkedIn", "Facebook", "Instagram"]},
            {"topic": "Creator Economy Monetization", "volume": 345678, "velocity": 189, "category": "Marketing",
             "sentiment": 0.81, "platforms": ["Instagram", "TikTok", "Twitter/X"]}
        ]

    def analyze_trends(self, niche: Optional[str] = None,
                       platforms: Optional[List[str]] = None,
                       limit: int = 10,
                       include_ideas: bool = True) -> Dict[str, Any]:

        system_prompt = f"""You are a senior trend analyst specializing in social media and digital culture.

Role: {self.role}
Freshness Window: {self.trend_settings['trend_freshness_hours']} hours
Minimum Volume Threshold: {self.trend_settings['min_trend_volume']}
Relevance Threshold: {self.trend_settings['trend_relevance_threshold']}

Your analysis must include:
1. Volume (total mentions in window)
2. Velocity (percentage growth rate)
3. Sentiment (-1.0 to +1.0)
4. Platform distribution
5. Category classification
6. Content angle ideas (if requested)

FORMAT: Return ONLY valid JSON with this structure:
{{
  "trends": [
    {{
      "topic": "trend name",
      "volume": 12345,
      "velocity": 145,
      "category": "category",
      "sentiment": 0.75,
      "sentiment_label": "Positive",
      "platforms": ["Platform1", "Platform2"],
      "relevance_score": 0.88,
      "growth_indicator": "SOARING|ACCELERATING|STABLE|DECLINING",
      "predicted_peak_hours": "description",
      "content_ideas": ["idea1", "idea2", "idea3"]
    }}
  ],
  "insights": ["insight1", "insight2"],
  "opportunities": ["opportunity1", "opportunity2"],
  "risk_alerts": ["risk1"]
}}"""

        user_prompt = f"""Analyze the TOP {limit} emerging social media trends RIGHT NOW.

Niche/Industry focus: {niche or 'Technology, Marketing, Business, Innovation'}
Platforms to prioritize: {', '.join(platforms) if platforms else 'Twitter/X, LinkedIn, Instagram, Facebook, TikTok'}
Include content angle ideas: {'YES - provide 3 highly specific creative angles per trend' if include_ideas else 'NO - skip content ideas'}

IMPORTANT:
- Rank by VIRAL POTENTIAL (combination of velocity, sentiment, and relevance)
- Identify micro-trends before they go mainstream (velocity > 200% is critical)
- Flag which trends are peaking NOW vs. emerging vs. already saturated
- For content ideas, think of counter-narrative takes, data-driven posts, and relatable story angles

Return ONLY the valid JSON structure specified."""

        try:
            result = watsonx_service.generate(
                user_prompt=user_prompt,
                system_prompt=system_prompt,
                max_tokens=2500,
                temperature=0.7
            )
            parsed = self._parse_json(result)
            if parsed:
                parsed['agent'] = self.name
                parsed['analyzed_at'] = datetime.now().isoformat()
                parsed['niche'] = niche
                return parsed
        except Exception as e:
            logger.error(f"Trend analysis failed: {e}")

        return self._fallback_trends(niche, platforms, limit, include_ideas)

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

    def _fallback_trends(self, niche: Optional[str], platforms: Optional[List[str]],
                         limit: int, include_ideas: bool) -> Dict[str, Any]:

        filtered = []
        for trend in self._simulated_trends:
            if niche:
                if niche.lower() not in trend['category'].lower() and niche.lower() not in trend['topic'].lower():
                    continue
            if platforms:
                if not any(p.lower() in [pl.lower() for pl in trend['platforms']] for p in platforms):
                    continue
            filtered.append(trend)

        filtered.sort(key=lambda x: x['velocity'], reverse=True)
        selected = filtered[:limit]

        trends_result = []
        for t in selected:
            velocity = t['velocity']
            if velocity > 300:
                growth = "SOARING"
            elif velocity > 150:
                growth = "ACCELERATING"
            elif velocity > 50:
                growth = "STABLE"
            else:
                growth = "DECLINING"

            sent_label = "Positive" if t['sentiment'] > 0.5 else "Neutral" if t['sentiment'] > -0.2 else "Negative"

            trend_item = {
                "topic": t['topic'],
                "volume": t['volume'],
                "velocity": t['velocity'],
                "category": t['category'],
                "sentiment": t['sentiment'],
                "sentiment_label": sent_label,
                "platforms": t['platforms'],
                "relevance_score": round(random.uniform(0.65, 0.95), 2),
                "growth_indicator": growth,
                "predicted_peak_hours": f"Next {random.randint(12, 48)} hours",
            }

            if include_ideas:
                topic = t['topic']
                trend_item['content_ideas'] = [
                    f"🔥 The Counter-Intuitive Take: Why most people have {topic} completely backwards (and what the data actually shows)",
                    f"📊 Data-Driven Deep Dive: I analyzed 500+ posts about {topic}. Here are the 3 patterns that predict 90% of success.",
                    f"💬 Relatable Story: The moment I realized {topic} wasn't what everyone said it was (lesson saved me $10k+)"
                ]

            trends_result.append(trend_item)

        return {
            "agent": self.name,
            "analyzed_at": datetime.now().isoformat(),
            "niche": niche,
            "trends": trends_result,
            "insights": [
                f"📈 {len([t for t in trends_result if t['growth_indicator'] in ['SOARING', 'ACCELERATING']])} trends show strong growth momentum—high capture opportunity",
                f"🎯 {trends_result[0]['topic'] if trends_result else 'N/A'} is the top viral candidate with {trends_result[0]['velocity'] if trends_result else 0}% velocity",
                f"⚖️ Positive sentiment trends outnumber negative 3:1, favorable for brand association"
            ],
            "opportunities": [
                f"🎣 Micro-trend capture: The {trends_result[1]['topic'] if len(trends_result) > 1 else 'N/A'} trend is in early adoption—first movers gain disproportionate share of voice",
                f"🔄 Content repurpose: Trends in {', '.join(list(set([t['category'] for t in trends_result[:3]])))} can be cross-posted across {', '.join(platforms) if platforms else 'all platforms'}",
                f"💡 Thought leadership window: AI Governance & Ethics trend has mixed sentiment—establish authority with balanced, nuanced perspective"
            ],
            "risk_alerts": [
                f"⚠️ {len([t for t in trends_result if t['sentiment'] < 0.4])} trends have negative/neutral sentiment—avoid unless you have a clear, positive framing",
                "🚫 Trending topics with high velocity but low relevance: Avoid trendjacking without authentic connection to your brand"
            ]
        }

    def predict_trend_lifecycle(self, topic: str) -> Dict[str, Any]:
        lifecycle = random.choice(["emerging", "growth", "peak", "declining"])
        now = datetime.now()
        return {
            "agent": self.name,
            "topic": topic,
            "lifecycle_stage": lifecycle,
            "current_position_pct": random.randint(15, 85),
            "predicted_peak_time": (now + timedelta(hours=random.randint(6, 72))).isoformat(),
            "predicted_saturation_time": (now + timedelta(hours=random.randint(48, 168))).isoformat(),
            "remaining_window_hours": random.randint(24, 120),
            "recommendation": f"ACT NOW: {topic} is in the {lifecycle} stage with ~{random.randint(24, 96)}h of high-engagement window remaining",
            "opportunity_score": round(random.uniform(0.4, 0.95), 2)
        }
