"""
AgriVision AI — Gemini AI Service

Responsibilities:
  - Send structured prompts to Google Gemini 2.5 Flash.
  - Provide domain-specific helpers:
      • Crop advisory (soil, climate, market).
      • Disease analysis and treatment recommendation.
      • Weather-to-agriculture insight translation.
      • General agricultural Q&A chatbot.

Google AI Python SDK docs: https://ai.google.dev/gemini-api/docs
"""

from google import genai
from google.genai import types
from app.core.exceptions import ExternalAPIError

_MODEL_NAME = "gemini-2.5-flash"

_SYSTEM_PROMPT = (
    "You are AgriVision AI, an expert agricultural advisor. "
    "Your goal is to help farmers, agronomists, and gardeners make data-driven decisions. "
    "Always give practical, science-backed advice tailored to the specific crop, region, "
    "and season. Format your answers clearly with headings and bullet points where helpful."
)


class GeminiService:
    def __init__(self, api_key: str) -> None:
        self._client = genai.Client(api_key=api_key)
        self._model_name = _MODEL_NAME

    # ── Public methods ────────────────────────────────────────────────────────

    async def ask(self, prompt: str) -> str:
        """
        Send an arbitrary prompt and return the text response.

        Args:
            prompt: User or system-constructed prompt.
        """
        try:
            response = self._client.models.generate_content(
                model=self._model_name,
                contents=prompt,
                config=types.GenerateContentConfig(system_instruction=_SYSTEM_PROMPT),
            )
            return response.text
        except Exception as exc:
            raise ExternalAPIError("Gemini", str(exc)) from exc

    async def get_crop_advisory(
        self,
        crop: str,
        location: str,
        soil_type: str = "",
        season: str = "",
        issue: str = "",
    ) -> str:
        """
        Generate a comprehensive crop management advisory.

        Args:
            crop: Crop name (e.g. "tomato", "wheat").
            location: Geographic location (city, country).
            soil_type: Optional soil description (e.g. "sandy loam").
            season: Optional growing season (e.g. "kharif", "rabi", "summer").
            issue: Optional specific problem the farmer is facing.
        """
        parts = [f"Crop: {crop}", f"Location: {location}"]
        if soil_type:
            parts.append(f"Soil type: {soil_type}")
        if season:
            parts.append(f"Season: {season}")
        if issue:
            parts.append(f"Specific concern: {issue}")

        prompt = (
            "Provide a detailed crop management advisory for the following context:\n"
            + "\n".join(parts)
            + "\n\nInclude: planting schedule, irrigation needs, fertilisation, "
            "pest & disease management, and expected yield optimisation tips."
        )
        return await self.ask(prompt)

    async def analyse_disease(
        self,
        plant_name: str,
        symptoms: str,
        image_description: str = "",
    ) -> str:
        """
        Analyse plant disease symptoms and recommend treatment.

        Args:
            plant_name: Name of the affected plant.
            symptoms: Description of observed symptoms.
            image_description: Optional textual description of image findings.
        """
        prompt = (
            f"A farmer reports the following problem with their {plant_name}:\n"
            f"Symptoms: {symptoms}\n"
        )
        if image_description:
            prompt += f"Visual observation: {image_description}\n"
        prompt += (
            "\nDiagnose the likely disease(s) or pest(s) and provide:\n"
            "1. Most probable cause\n"
            "2. Confirmation steps\n"
            "3. Organic treatment options\n"
            "4. Chemical treatment options (if necessary)\n"
            "5. Preventive measures for the future"
        )
        return await self.ask(prompt)

    async def weather_to_farm_insight(
        self,
        weather_summary: str,
        crop: str = "",
        region: str = "",
    ) -> str:
        """
        Translate a weather summary into actionable farming advice.

        Args:
            weather_summary: Plain-text description of current / forecast weather.
            crop: Optional primary crop being grown.
            region: Optional region name for context.
        """
        context = f"Region: {region}\n" if region else ""
        context += f"Primary crop: {crop}\n" if crop else ""
        prompt = (
            f"{context}"
            f"Current/forecast weather conditions:\n{weather_summary}\n\n"
            "Based on these conditions, advise on:\n"
            "- Irrigation scheduling\n"
            "- Pest and disease risk\n"
            "- Harvesting / planting windows\n"
            "- Any urgent protective actions needed"
        )
        return await self.ask(prompt)

    async def chat(self, conversation: list[dict]) -> str:
        """
        Continue a multi-turn conversation with the AI advisor.

        Args:
            conversation: List of {"role": "user"|"model", "parts": ["text"]} dicts.
        """
        try:
            # Build contents list from conversation history
            contents = [
                types.Content(
                    role=msg["role"],
                    parts=[types.Part(text=msg["parts"][0]) if isinstance(msg["parts"][0], str) else msg["parts"][0]],
                )
                for msg in conversation
            ]
            response = self._client.models.generate_content(
                model=self._model_name,
                contents=contents,
                config=types.GenerateContentConfig(system_instruction=_SYSTEM_PROMPT),
            )
            return response.text
        except Exception as exc:
            raise ExternalAPIError("Gemini", str(exc)) from exc
