import requests


class MockProvider:
    def translate(self, text):
        dictionary = {
            "Blood Decal Large": "Calcomanía de sangre grande",
            "Blood Decal Small": "Calcomanía de sangre pequeña",
            "Slow Time": "Ralentizar tiempo",
            "Gore Pile": "Montón de vísceras",
            "Dust Pile": "Montón de polvo",
            "Death Effects Dragon": "Efectos de muerte de dragón",
            "Bleed Head": "Sangrado de cabeza",
            "Bleed Eye": "Sangrado de ojo",
            "Bleed Mouth": "Sangrado de boca",
            "Blood Head": "Sangre de cabeza",
            "Blood Mouth": "Sangre de boca",
            "Blood Eye": "Sangre de ojo"
        }

        return dictionary.get(text, f"ES: {text}")


class OllamaProvider:
    def __init__(self, settings):
        self.model = settings.get("model", "qwen2.5:3b")
        self.url = settings.get(
            "ollama_url",
            "http://localhost:11434/api/generate"
        )

    def translate(self, text):
        prompt = f"""
Traduce este texto de un mod de Skyrim al español neutro.

Reglas:
- Devuelve solo la traducción.
- No expliques nada.
- Mantén nombres propios de fantasía si corresponde.
- No traduzcas IDs técnicos.
- Usa un español natural para videojuegos.
- Si el texto es muy técnico, tradúcelo de forma corta y clara.

Texto:
{text}
"""

        response = requests.post(
            self.url,
            json={
                "model": self.model,
                "prompt": prompt,
                "stream": False
            },
            timeout=180
        )

        response.raise_for_status()

        data = response.json()

        return data.get("response", "").strip()