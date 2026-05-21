"""Cumbre AI — asistente interno powered by Claude API."""
import os
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

router = APIRouter()

SYSTEM_PROMPT = """Sos Cumbre AI, el asistente interno de la plataforma Cumbre IDP para equipos de ingeniería en LATAM.

Tu rol es ayudar a los desarrolladores a:
- Configurar servicios correctamente (upstream_host, upstream_port, public_path)
- Elegir rate limits apropiados (rate_limit_rpm) según el tipo de servicio
- Diagnosticar por qué un servicio está en estado FAILED o PROVISIONING
- Entender qué hace cada campo del API del OSB
- Seguir mejores prácticas de seguridad en la plataforma

Respondé en español. Sé conciso y directo. Si no sabés algo específico del contexto del usuario, pedí más información."""


class AIRequest(BaseModel):
    question: str = Field(..., min_length=5, max_length=2000, description="Pregunta o problema del developer")
    context: dict = Field(default_factory=dict, description="Contexto opcional: servicio, logs, etc.")


class AIResponse(BaseModel):
    answer: str
    model: str


@router.post("/ai/suggest", response_model=AIResponse, summary="Preguntale a Cumbre AI")
async def ai_suggest(payload: AIRequest):
    api_key = os.getenv("ANTHROPIC_API_KEY", "")
    if not api_key:
        raise HTTPException(status_code=503, detail="Cumbre AI no está configurado (falta ANTHROPIC_API_KEY)")

    try:
        import anthropic
        client = anthropic.Anthropic(api_key=api_key)

        user_message = payload.question
        if payload.context:
            import json
            user_message += f"\n\nContexto adicional:\n```json\n{json.dumps(payload.context, indent=2, ensure_ascii=False)}\n```"

        message = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_message}],
        )

        return AIResponse(
            answer=message.content[0].text,
            model=message.model,
        )
    except anthropic.AuthenticationError:
        raise HTTPException(status_code=503, detail="API key de Anthropic inválida")
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Error del servicio AI: {type(e).__name__}")
