import asyncio
import json
from typing import AsyncGenerator
from app.services.llm_service import LLMService
from app.services.ticker_extractor import get_all_tickers, get_primary_ticker
from app.services.chart_service import get_chart_image
from app.models.schemas import (
    TransformResponse,
    LinkedInOutput,
    NewsletterOutput,
    WhatsAppOutput,
    StockChartOutput,
)
from app.prompts import (
    LINKEDIN_SYSTEM_PROMPT,
    LINKEDIN_USER_PROMPT,
    WHATSAPP_SYSTEM_PROMPT,
    WHATSAPP_USER_PROMPT,
)
from app.prompts.streaming import (
    LINKEDIN_STREAM_SYSTEM,
    LINKEDIN_STREAM_USER,
    WHATSAPP_STREAM_SYSTEM,
    WHATSAPP_STREAM_USER,
    HASHTAG_SYSTEM,
    HASHTAG_USER,
    get_variant_modifier,
)
from app.prompts.tones import Tone, get_tone_modifier


class TransformerService:
    def __init__(self, llm_service: LLMService):
        self.llm = llm_service

    async def _generate_linkedin(self, report_text: str) -> LinkedInOutput:
        """Generate LinkedIn post from report."""
        result = await self.llm.generate(
            system_prompt=LINKEDIN_SYSTEM_PROMPT,
            user_prompt=LINKEDIN_USER_PROMPT.format(report_text=report_text),
        )
        return LinkedInOutput(**result)

    async def _generate_whatsapp(self, report_text: str) -> WhatsAppOutput:
        """Generate WhatsApp message from report."""
        result = await self.llm.generate(
            system_prompt=WHATSAPP_SYSTEM_PROMPT,
            user_prompt=WHATSAPP_USER_PROMPT.format(report_text=report_text),
        )
        return WhatsAppOutput(**result)

    async def transform(self, report_text: str) -> TransformResponse:
        """Transform report into LinkedIn and WhatsApp formats concurrently."""
        linkedin, whatsapp = await asyncio.gather(
            self._generate_linkedin(report_text),
            self._generate_whatsapp(report_text),
        )

        # Newsletter is deprecated - return empty placeholder
        newsletter = NewsletterOutput(
            headline="",
            thesis="",
            key_points=[],
            call_to_action="",
        )

        return TransformResponse(
            linkedin=linkedin,
            newsletter=newsletter,
            whatsapp=whatsapp,
        )

    async def transform_stream(
        self, report_text: str, tone: Tone = Tone.PROFESSIONAL, variant: str = "A"
    ) -> AsyncGenerator[str, None]:
        """
        Stream the transformation of a report into LinkedIn and WhatsApp formats.
        Yields SSE-formatted events with the streaming content.
        """
        linkedin_content = ""
        whatsapp_content = ""
        tone_modifier = get_tone_modifier(tone)
        variant_modifier = get_variant_modifier(variant)

        # Stream LinkedIn content first
        yield f"data: {json.dumps({'type': 'linkedin_start', 'variant': variant})}\n\n"

        linkedin_system = LINKEDIN_STREAM_SYSTEM.format(
            tone_modifier=tone_modifier,
            variant_modifier=variant_modifier
        )
        async for chunk in self.llm.generate_stream(
            system_prompt=linkedin_system,
            user_prompt=LINKEDIN_STREAM_USER.format(report_text=report_text),
        ):
            linkedin_content += chunk
            yield f"data: {json.dumps({'type': 'linkedin_chunk', 'content': chunk})}\n\n"

        # Generate hashtags (non-streaming, quick)
        try:
            hashtag_response = await self.llm.generate(
                system_prompt=HASHTAG_SYSTEM,
                user_prompt=HASHTAG_USER.format(content=linkedin_content),
                temperature=0.5,
            )
            # Parse hashtags from response - handle both dict and string formats
            if isinstance(hashtag_response, dict):
                hashtags_str = hashtag_response.get("hashtags", "")
            else:
                hashtags_str = str(hashtag_response)
            hashtags = [h.strip() for h in hashtags_str.split(",") if h.strip()]
        except Exception:
            hashtags = ["MonarchNetworth", "StockMarket", "IndianStocks"]

        yield f"data: {json.dumps({'type': 'linkedin_complete', 'content': linkedin_content, 'hashtags': hashtags, 'character_count': len(linkedin_content), 'variant': variant})}\n\n"

        # Stream WhatsApp content
        yield f"data: {json.dumps({'type': 'whatsapp_start', 'variant': variant})}\n\n"

        whatsapp_system = WHATSAPP_STREAM_SYSTEM.format(
            tone_modifier=tone_modifier,
            variant_modifier=variant_modifier
        )
        async for chunk in self.llm.generate_stream(
            system_prompt=whatsapp_system,
            user_prompt=WHATSAPP_STREAM_USER.format(report_text=report_text),
        ):
            whatsapp_content += chunk
            yield f"data: {json.dumps({'type': 'whatsapp_chunk', 'content': chunk})}\n\n"

        yield f"data: {json.dumps({'type': 'whatsapp_complete', 'content': whatsapp_content, 'variant': variant})}\n\n"

        # Signal end of stream (chart is fetched separately via user input)
        yield f"data: {json.dumps({'type': 'done', 'variant': variant})}\n\n"
