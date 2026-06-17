import json

from providers.local_provider import OllamaProvider

with open("config/settings.json", "r", encoding="utf-8") as f:
    settings = json.load(f)

provider = OllamaProvider(settings)

texto = "Armor Explosion def"

print("Original:")
print(texto)

print("\nTraducido:")
print(provider.translate(texto))