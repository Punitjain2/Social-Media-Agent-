import json
import logging
import random
from typing import Dict, Any, List, Optional
from services.watsonx_service import watsonx_service
from config import Config

logger = logging.getLogger(__name__)


class ContentCreationAgent:
    def __init__(self):
        self.instructions = Config.AGENT_INSTRUCTIONS
        self.name = "Content Creation Agent"
        self.role = "Generates engaging social media content optimized for each platform"

    def generate_content(self, platform: str, topic: str,
                         content_type: str = "post",
                         audience: Optional[str] = None,
                         cta: Optional[str] = None,
                         keywords: Optional[List[str]] = None,
                         tone: Optional[str] = None) -> Dict[str, Any]:

        platform_config = self.instructions['platforms'].get(platform, {})
        content_style = self.instructions['content_style']
        brand_voice = self.instructions['brand_voice']
        marketing = self.instructions['marketing_goals']

        max_length = content_style['max_length'].get(platform, 1000)
        hashtag_info = content_style['hashtag_count'].get(platform, {"optimal": 5})
        optimal_hashtags = hashtag_info.get('optimal', 5)

        selected_cta = cta or random.choice(marketing['call_to_actions'])
        selected_tone = tone or brand_voice['tone']

        system_prompt = f"""You are an expert {platform_config.get('name', platform)} content creator.

Platform: {platform_config.get('name', platform)}
Max Length: {max_length} characters
Optimal Hashtags: {optimal_hashtags}
Content Type: {content_type}

Brand Voice: {brand_voice['personality']}
Tone: {selected_tone}
Style: {brand_voice['style']}
Use Emojis: {content_style['use_emojis']}
Use Questions: {content_style['use_questions']}
Use Statistics: {content_style['use_statistics']}
Storytelling: {content_style['storytelling']}

Target Audience: {audience or ', '.join(marketing['target_audience']['professions'])}
Brand Messages: {', '.join(marketing['brand_messages'])}
Call to Action: {selected_cta}

SAFETY RULES - NEVER VIOLATE:
- Avoid: {', '.join(brand_voice['avoid'])}
- Prohibited content: {', '.join(self.instructions['safety_rules']['prohibited_content'][:4])}
- Always maintain professional, positive brand image

FORMAT YOUR RESPONSE AS A VALID JSON:
{{
  "content": "The generated post content with emojis and formatting",
  "character_count": 0,
  "suggested_media": "description of ideal visual",
  "hook": "attention-grabbing first line",
  "call_to_action": "the CTA used",
  "variations": ["variation 1", "variation 2", "variation 3"],
  "content_tags": ["tag1", "tag2"]
}}"""

        user_prompt = f"""Create a highly engaging {content_type} for {platform_config.get('name', platform)} about: {topic}

Keywords to include: {', '.join(keywords) if keywords else 'Relevant industry terms'}

Make it:
- Optimized for the platform's algorithm
- Include {optimal_hashtags} relevant hashtags
- Add a strong hook in the first 2 lines
- End with CTA: {selected_cta}
- {random.choice(['Include a surprising statistic', 'Ask a thought-provoking question', 'Add a relatable anecdote'])}

Return ONLY valid JSON with the required fields."""

        try:
            result = watsonx_service.generate(
                user_prompt=user_prompt,
                system_prompt=system_prompt,
                max_tokens=1500,
                temperature=0.8
            )

            parsed = self._parse_json_result(result)
            if parsed:
                parsed['agent'] = self.name
                parsed['platform'] = platform
                parsed['topic'] = topic
                return parsed

        except Exception as e:
            logger.error(f"Content generation failed: {e}")

        return self._fallback_content(platform, topic, content_type, selected_cta, optimal_hashtags)

    def _parse_json_result(self, result: str) -> Optional[Dict[str, Any]]:
        try:
            json_str = result
            if json_str.startswith('```json'):
                json_str = json_str.replace('```json', '').replace('```', '')
            elif json_str.startswith('```'):
                json_str = json_str.replace('```', '')

            start = json_str.find('{')
            end = json_str.rfind('}') + 1
            if start >= 0 and end > start:
                json_str = json_str[start:end]

            return json.loads(json_str)
        except:
            return None

    def _fallback_content(self, platform: str, topic: str, content_type: str,
                          cta: str, optimal_hashtags: int) -> Dict[str, Any]:

        templates = {
            "twitter": [
                f"💡 {topic}: It's not just about the what—it's about the why and how.\n\nHere's what 90% get wrong 👇\n\n#Innovation #Tech #Growth #Future #Leadership",
                f"🚀 Breaking: {topic} is reshaping industries faster than we predicted.\n\n3 action items for leaders this week:\n✅ Audit your AI strategy\n✅ Upskill your team\n✅ Start small, scale fast\n\n#AI #Business #Strategy",
                f"🤔 What if {topic} wasn't the problem, but the catalyst?\n\nGreat thread on how forward-thinking companies are adapting:\n\n#FutureOfWork #Innovation #Leadership"
            ],
            "linkedin": [
                f"""🚀 {topic}: The Strategic Imperative for 2026

The landscape has fundamentally shifted. Organizations that recognized this early are already seeing 3x the returns of their slower-moving peers.

📊 The Data Speaks:
• 78% of leaders report this as their #1 priority
• Companies with mature strategies grew revenue 47% YoY
• Talent acquisition has improved 2.3x at adoption leaders

💡 Three Strategic Imperatives:
1. Don't just adopt—integrate deeply into workflows
2. Measure what matters: quality > vanity metrics
3. Culture eats strategy for breakfast—bring your team along

The window of competitive advantage is narrowing. Those who act decisively now will define the next decade.

What's your organization doing to stay ahead? I'd love to hear your perspective in the comments.

{cta} → Link in comments

#Leadership #Strategy #Innovation #BusinessGrowth #DigitalTransformation #FutureOfWork""",

                f"""💡 Thought Leadership: Why {topic} Matters More Than Ever

After two decades in this industry, I've seen technologies come and go. But this? This is different.

Here's why I'm convinced we're at an inflection point:

🔄 The Speed Paradox
We've never had access to more powerful tools, yet the gap between leaders and laggards widens daily. It's not about access—it's about execution.

🧠 The Human Advantage
For all the capabilities of modern systems, the differentiator remains human judgment, creativity, and ethical decision-making. The best outcomes come from collaboration, not replacement.

📈 The Compound Effect
Small, consistent improvements compound. Companies investing 10% weekly in capability building see exponential gains over 24 months.

The future doesn't happen to you—it's created by you. Starting now.

Let's build it together. 👇

#Leadership #Management #Growth #BusinessIntelligence #Strategy"""
            ],
            "instagram": [
                f"""✨ The moment everything changed ✨

Nobody talks about the hard days. The late nights. The moments of doubt when you question if it's all worth it.

But here's what I learned 💫:
🌱 Growth isn't linear
💪 Your struggles become your strengths
🌟 Every 'no' gets you closer to that perfect 'yes'
❤️ The journey is the reward

Today I'm choosing gratitude for every step that got me here. What are you grateful for? Drop it below 👇

.
.
.
#Motivation #GrowthMindset #EntrepreneurLife #GirlBoss #Success #Hustle #StartUp #DreamBig #BusinessOwner #CreatorLife #Ambition #Mindset #DailyInspiration #WomenInBusiness #SuccessQuotes #MentalHealth #SelfLove #GoalDigger #LifeLessons #Blessed""",

                f"""⚠️ I used to make this same mistake every single day ⚠️

And it was costing me opportunities, clients, and my peace of mind.

Here's what I wish someone told me 5 years ago:
STOP waiting for the perfect moment.
STOP trying to make everything flawless before you launch.
STOP letting fear of judgment hold you back.

Done > Perfect. Always.

Your 80% today is better than your imaginary 100% next year.

Save this for when you need a reminder 📌
Tag someone who needs to see this 💖

.
.
.
#MindsetShift #EntrepreneurTips #SuccessMindset #HustleHard #NoExcuses #MotivationDaily #BusinessTips #LevelUp #PersonalGrowth #SelfImprovement #MindsetIsEverything #CareerGrowth #WorkHardPlayHard #BossBabe #StartupLife #CreativeEntrepreneur #FreelanceLife #ContentCreator #SmallBusinessOwner #Inspire"""
            ],
            "facebook": [
                f"""🌟 {topic}: Real Talk Time

Let's cut through the noise for a moment.

Everyone's talking about the flashy stuff—the big wins, the overnight successes, the highlight reels. But what about the days when it feels like nothing's working? The setbacks that make you question everything?

Here's the truth no algorithm shows you:
✅ Behind every "overnight success" are 5+ years of grinding
✅ The best lessons come from the worst failures
✅ Your community matters more than your metrics
✅ Consistency beats intensity, every single time

If you're in the grind today, know this: someone out there needs exactly what you have to offer. Keep going.

Share this with someone who needs to hear it today 💙

#Community #Growth #Motivation #RealTalk #KeepGoing"""
            ],
            "blog": [
                f"""# {topic}: The Definitive Guide for Forward-Thinking Leaders

## Introduction

In an era defined by unprecedented change, understanding {topic} is no longer optional—it's a prerequisite for survival, let alone success. This guide distills thousands of hours of research, real-world implementation, and lessons from both triumphs and failures into an actionable framework you can deploy today.

## Why Now? The Convergence of Forces

Three macro trends have collided to create this unique moment:

1. **Exponential Capability Growth**: What was prohibitively expensive 18 months ago is now commodity infrastructure.
2. **Workforce Expectation Shift**: 74% of knowledge workers now expect AI assistance in their daily workflows.
3. **Competitive Pressure Intensification**: First movers have established measurable, defensible advantages.

The window to act isn't infinite—but the good news is, the playbook is clearer than ever.

## The Five Pillars of Successful Implementation

### Pillar 1: Strategic Alignment Before Tactical Execution

Before any tool is selected or any prompt written, organizations must answer foundational questions:
- What specific outcomes are we optimizing for?
- Where are our current bottlenecks and frictions?
- How will success be measured and in what timeframe?

Organizations that skip this step waste 62% of their investment on tools that don't integrate or problems that don't matter.

### Pillar 2: The Human-Centric Approach

The highest-performing deployments share one counterintuitive trait: they start with people, not technology. Change management, upskilling, and psychological safety aren't "soft" concerns—they're the hardest ROI multipliers you'll ever invest in.

### Pillar 3: Data Infrastructure as Competitive Moat

Garbage in, garbage out has never been more relevant. The quality, accessibility, and governance of your data assets will determine your ceiling far more than the specific models you choose.

### Pillar 4: Iterative Experimentation with Guardrails

Move fast. Break small things. Learn. Scale what works. This rapid iteration cycle—with appropriate safety and governance guardrails—separates the leaders from the experimenters.

### Pillar 5: Measurement That Actually Drives Action

Vanity metrics are comforting. Business outcomes are what matter. Your dashboard should have three tiers:
- Strategic (C-suite): 3-5 metrics that tie directly to P&L
- Operational (Managers): 8-12 metrics driving day-to-day decisions
- Tactical (Individual Contributors): Real-time feedback loops

## Case Study: How Company X Achieved 312% ROI in 9 Months

Company X, a mid-market player in a traditional industry, followed this exact framework. The results:
- 43% reduction in time-to-delivery for core services
- 68% improvement in customer satisfaction scores
- 2.4x employee net promoter score
- 312% ROI as measured by revenue uplift minus investment

The secret? They didn't chase every shiny object. They focused on three high-leverage use cases, executed them well, and compounded the wins.

## Common Pitfalls (And How to Avoid Them)

1. **Shiny Object Syndrome**: Pick 3, max 5, use cases. Depth beats breadth.
2. **Set-and-Forget**: The most successful teams meet weekly to review and refine.
3. **Silos**: Cross-functional governance drives 2x the impact of isolated deployments.
4. **Underinvesting in People**: For every $1 you spend on tools, budget $2-3 on people, process, and training.

## Your 30-Day Action Plan

**Week 1: Foundation**
- Executive alignment on goals, priorities, and success metrics
- Current state assessment and opportunity mapping
- Governance and safety framework design

**Week 2: First Use Case**
- Select the single highest-leverage, lowest-risk pilot
- Assemble cross-functional tiger team
- Deploy minimal viable implementation

**Week 3: Measure, Learn, Iterate**
- Gather quantitative and qualitative feedback
- Run 3-5 meaningful experiments
- Document lessons learned

**Week 4: Scale Decision**
- Go/no-go decision on the pilot
- Roadmap for next 2-3 use cases
- Resource and budget planning

## Conclusion

The future of work isn't about replacing human potential—it's about amplifying it. Those who embrace this shift with intentionality, humility, and strategic focus won't just survive the next decade—they'll define it.

The question isn't whether {topic} will reshape your industry. It's whether you'll be one of the architects of that reshaping, or one of the ones watching from the sidelines.

The choice is yours. And the time to act is now.

---

*Ready to discuss how to apply these principles in your organization? Reach out—I'd love to connect.*"""
            ]
        }

        default_templates = templates.get(platform, templates['blog'])
        selected = random.choice(default_templates)

        return {
            "agent": self.name,
            "platform": platform,
            "topic": topic,
            "content": selected,
            "character_count": len(selected),
            "suggested_media": f"Professional high-quality visual related to {topic} with brand colors",
            "hook": selected.split('\n')[0][:100],
            "call_to_action": cta,
            "variations": [
                self._variation(selected, 1),
                self._variation(selected, 2),
                self._variation(selected, 3)
            ],
            "content_tags": [topic.lower().replace(' ', ''), 'ai', 'marketing', 'content', 'growth']
        }

    def _variation(self, content: str, version: int) -> str:
        hooks = [
            "🔥 ",
            "💡 ",
            "🚀 "
        ]
        prefix = hooks[version % 3]
        if len(content) > 50:
            return prefix + content[2:].strip()
        return prefix + content
