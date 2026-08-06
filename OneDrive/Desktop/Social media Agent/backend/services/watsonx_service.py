import json
import re
import logging
from typing import List, Dict, Any, Optional
from config import Config

logger = logging.getLogger(__name__)


class WatsonXService:
    _instance = None
    _client = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self._initialized = True
            self.api_key = Config.IBM_CLOUD_API_KEY
            self.url = Config.IBM_WATSONX_URL
            self.project_id = Config.IBM_WATSONX_PROJECT_ID
            self.model_id = Config.IBM_MODEL_ID
            self.generation_model_id = Config.IBM_GENERATION_MODEL_ID
            self.reasoning_model_id = Config.IBM_REASONING_MODEL_ID
            self._init_client()

    def _init_client(self):
        try:
            from ibm_watsonx_ai import Credentials
            from ibm_watsonx_ai.foundation_models import Model

            if not self.api_key or not self.project_id:
                logger.warning("IBM Cloud credentials not configured. Using fallback mode.")
                self._client = None
                return

            credentials = Credentials(
                url=self.url,
                api_key=self.api_key
            )

            self._client = Model(
                model_id=self.generation_model_id,
                credentials=credentials,
                project_id=self.project_id
            )

            logger.info("IBM watsonx.ai client initialized successfully")
        except ImportError as e:
            logger.warning(f"ibm-watsonx-ai package not installed: {e}. Using fallback mode.")
            self._client = None
        except Exception as e:
            logger.warning(f"Failed to initialize IBM watsonx.ai client: {e}. Using fallback mode.")
            self._client = None

    def _build_prompt(self, system_prompt: str, user_prompt: str) -> str:
        return f"""<|begin_of_solution|>
<|start_of_role|>system<|end_of_role|>
{system_prompt}
<|start_of_role|>user<|end_of_role|>
{user_prompt}
<|start_of_role|>assistant<|end_of_role|>"""

    def generate(self, user_prompt: str, system_prompt: str = "",
                 max_tokens: int = 1024, temperature: float = 0.7,
                 top_p: float = 0.9, model_override: Optional[str] = None) -> str:
        instructions = Config.AGENT_INSTRUCTIONS

        default_system = f"""You are an expert AI Social Media Marketing Agent powered by IBM Granite models.

Brand Voice: {instructions['brand_voice']['personality']}
Tone: {instructions['brand_voice']['tone']}
Style: {instructions['brand_voice']['style']}
Language: {instructions['brand_voice']['language']}

Primary Goal: {instructions['marketing_goals']['primary_goal']}
Target Audience: Age {instructions['marketing_goals']['target_audience']['age_range']}, 
Professions: {', '.join(instructions['marketing_goals']['target_audience']['professions'])}
Interests: {', '.join(instructions['marketing_goals']['target_audience']['interests'])}
Locations: {', '.join(instructions['marketing_goals']['target_audience']['locations'])}

Content Guidelines:
- Paragraph length: {instructions['content_style']['paragraph_length']}
- Use emojis: {instructions['content_style']['use_emojis']}
- Use storytelling: {instructions['content_style']['storytelling']}
- Use questions: {instructions['content_style']['use_questions']}
- Use statistics: {instructions['content_style']['use_statistics']}

Safety Rules:
- Prohibited: {', '.join(instructions['safety_rules']['prohibited_content'][:5])}
- Always maintain positive, professional brand image

Brand Messages to weave in:
{chr(10).join([f"- {msg}" for msg in instructions['marketing_goals']['brand_messages']])}
"""
        system = system_prompt if system_prompt else default_system

        if self._client is not None:
            try:
                model_to_use = model_override or self.generation_model_id
                params = {
                    "max_new_tokens": max_tokens,
                    "temperature": temperature,
                    "top_p": top_p
                }
                prompt = self._build_prompt(system, user_prompt)
                response = self._client.generate_text(prompt=prompt, params=params)
                return response.strip() if response else self._fallback_generate(user_prompt, system)
            except Exception as e:
                logger.error(f"IBM watsonx.ai API call failed: {e}")
                return self._fallback_generate(user_prompt, system)
        else:
            return self._fallback_generate(user_prompt, system)

    def _fallback_generate(self, user_prompt: str, system_prompt: str) -> str:
        prompt_lower = user_prompt.lower()

        if any(kw in prompt_lower for kw in ["linkedin", "professional", "business", "b2b"]):
            return """🚀 Transforming Business with AI: The Future is Now

The business landscape is evolving at unprecedented speed. Companies that embrace AI today aren't just gaining a competitive edge—they're redefining entire industries.

💡 Key Insight: 87% of early AI adopters report significant ROI within the first year.

Here's what separates the leaders from the rest:
✅ Strategic AI integration, not isolated tools
✅ Data-driven decision-making culture
✅ Continuous innovation and adaptation
✅ Human-AI collaboration models

The question isn't whether AI will transform your business—it's how quickly you can harness its power.

Ready to future-proof your organization? Let's connect and explore how AI can accelerate your growth journey.

#AI #ArtificialIntelligence #BusinessTransformation #Innovation #Leadership #TechStrategy #FutureOfWork #DigitalTransformation"""

        if any(kw in prompt_lower for kw in ["instagram", "viral", "trendy", "reels", "caption"]):
            return """✨ Stop scrolling. Start dreaming. ✨

They say the best time to plant a tree was 20 years ago. The second best time? RIGHT NOW. 🌱

Here's your Monday motivation to chase that thing you've been putting off:
💫 Every expert was once a beginner
💫 Progress > perfection
💫 Small steps = big results
💫 You're capable of more than you think

Drop a 🔥 in the comments if you're committing to your dreams this week!
.
.
.
#MotivationMonday #DreamBig #HustleCulture #SuccessMindset #GirlBoss #EntrepreneurLife #StartUpVibes #GoGetter #NoExcuses #MindsetMatters #Ambition #DailyMotivation #SuccessTips #BusinessOwner #CreatorEconomy"""

        if any(kw in prompt_lower for kw in ["tweet", "twitter", "thread", "short", "280"]):
            return """🧵 5 AI Trends That Will Define 2026 (and beyond) [THREAD]

1/6 The AI landscape is shifting. Here's what every leader needs to know 👇

2/6 🤖 Agentic AI goes mainstream
Autonomous agents will handle 40% of routine business tasks by Q4.
The shift from "AI tools" to "AI co-workers" is here.

3/6 🔒 Trust & Safety layer becomes critical
AI governance moves from nice-to-have to board-level priority.
Companies with robust AI ethics frameworks will outperform.

4/6 ⚡ Multimodal intelligence unlocks new use cases
Text + image + video + audio = unified AI experiences.
Content creation transformed forever.

5/6 🌍 AI democratization reaches SMB market
Enterprise-grade AI capabilities at startup price points.
Level playing field for innovation.

6/6 The future belongs to those who prepare today.
What's your AI strategy? Let's chat 📩

#AI #TechTrends #FutureOfAI #MachineLearning #Innovation
"""

        return """🚀 Introducing Your AI-Powered Social Media Advantage

Imagine never staring at a blank post again. Imagine every caption, every hashtag, every post perfectly optimized for maximum engagement.

That's not science fiction—it's what our AI Social Media Agent delivers every single day.

✨ Features:
✓ AI Content Creator for every platform
✓ Viral Score predictions & optimization tips
✓ Smart hashtag research
✓ Trend analysis & content ideas
✓ Optimal posting schedule
✓ Competitor intelligence
✓ Sentiment analysis & insights

Join hundreds of brands already saving 10+ hours weekly while boosting engagement by 250%.

Ready to transform your social media presence?
Try it free → Link in bio

#AIMarketing #SocialMediaMarketing #ContentCreation #MarketingAI #SaaS #GrowthHacking"""

    def generate_with_reasoning(self, user_prompt: str, system_prompt: str = "",
                                max_tokens: int = 2000, temperature: float = 0.5) -> Dict[str, Any]:
        result = self.generate(
            user_prompt=user_prompt,
            system_prompt=system_prompt,
            max_tokens=max_tokens,
            temperature=temperature,
            model_override=self.reasoning_model_id
        )
        return {
            "reasoning": result,
            "tokens_used": len(result.split()) * 1.3,
            "model": self.reasoning_model_id
        }

    def chat(self, messages: List[Dict[str, str]], max_tokens: int = 1024,
             temperature: float = 0.7) -> str:
        system_prompt = "You are a helpful AI Social Media Assistant. Help users create content, analyze trends, and optimize their social media strategy."
        user_parts = []
        for msg in messages:
            role = msg.get('role', 'user')
            content = msg.get('content', '')
            prefix = "User" if role == 'user' else "Assistant" if role == 'assistant' else "System"
            user_parts.append(f"{prefix}: {content}")

        user_prompt = "\n\n".join(user_parts[-10:])
        return self.generate(user_prompt, system_prompt, max_tokens=max_tokens, temperature=temperature)


watsonx_service = WatsonXService()
