import requests
import json
import os
import re

# Diccionario completo para MockProvider con términos de Skyrim y mods populares
MOCK_DICTIONARIES = {
    "Spanish": {
        # ====== TÉRMINOS BASE DE SKYRIM ======
        # Sangre y efectos de muerte
        "Blood Decal Large": "Mancha de sangre grande",
        "Blood Decal Small": "Mancha de sangre pequeña",
        "Blood Spray": "Salpicadura de sangre",
        "Blood Splatter": "Salpicadura de sangre",
        "Blood Effect": "Efecto de sangre",
        "Blood Impact": "Impacto de sangre",
        "Gore Pile": "Montón de vísceras",
        "Gore Effect": "Efecto de vísceras",
        "Dust Pile": "Montón de polvo",
        "Dust Effect": "Efecto de polvo",
        "Death Effects Dragon": "Efectos de muerte de dragón",
        "Death Effects Giant": "Efectos de muerte de gigante",
        "Death Effects Troll": "Efectos de muerte de trol",
        
        # Heridas y sangrado
        "Bleed Head": "Sangrado de cabeza",
        "Bleed Eye": "Sangrado de ojo",
        "Bleed Mouth": "Sangrado de boca",
        "Bleed left arm": "Sangrado del brazo izquierdo",
        "Bleed right arm": "Sangrado del brazo derecho",
        "Bleed left leg": "Sangrado de pierna izquierda",
        "Bleed right leg": "Sangrado de pierna derecha",
        "Bleed Torso": "Sangrado de torso",
        "Blood Head": "Sangre de cabeza",
        "Blood Mouth": "Sangre de boca",
        "Blood Eye": "Sangre de ojo",
        "Blood Torso": "Sangre de torso",
        "Blood Arm": "Sangre de brazo",
        "Blood Leg": "Sangre de pierna",
        
        # ====== TÉRMINOS DE MODS POPULARES ======
        # Maximum Carnage (mod de gore)
        "Armor Explosion def": "Explosión de armadura",
        "Explosion Effect": "Efecto de explosión",
        "Gore Explosion": "Explosión de vísceras",
        "Brain Explosion": "Explosión de cerebro",
        "Heart Explosion": "Explosión de corazón",
        "Lung Explosion": "Explosión de pulmón",
        "Stomach Explosion": "Explosión de estómago",
        "Spine Explosion": "Explosión de columna",
        "Skull Explosion": "Explosión de cráneo",
        "Rib Explosion": "Explosión de costilla",
        "Pelvis Explosion": "Explosión de pelvis",
        "Leg Explosion": "Explosión de pierna",
        "Arm Explosion": "Explosión de brazo",
        "Hand Explosion": "Explosión de mano",
        "Foot Explosion": "Explosión de pie",
        "Ragdoll Explosion": "Explosión de ragdoll",
        "Blood Explosion": "Explosión de sangre",
        
        # Vigor / Wildcat (combate)
        "Injury Head": "Lesión en cabeza",
        "Injury Torso": "Lesión en torso",
        "Injury Arm": "Lesión en brazo",
        "Injury Leg": "Lesión en pierna",
        "Injury Fatigue": "Fatiga por lesión",
        "Injury Health": "Salud por lesión",
        "Injury Stamina": "Resistencia por lesión",
        "Injury Magicka": "Magicka por lesión",
        
        # ====== MAGIA Y HECHIZOS ======
        "Slow Time": "Ralentizar tiempo",
        "Slow Time Effect": "Efecto de ralentizar tiempo",
        "Paralysis Effect": "Efecto de parálisis",
        "Fear Effect": "Efecto de miedo",
        "Frenzy Effect": "Efecto de frenesí",
        "Calm Effect": "Efecto de calma",
        "Invisibility Effect": "Efecto de invisibilidad",
        "Ethereal Effect": "Efecto de etéreo",
        "Fire Effect": "Efecto de fuego",
        "Frost Effect": "Efecto de escarcha",
        "Shock Effect": "Efecto de descarga",
        "Poison Effect": "Efecto de veneno",
        "Drain Health": "Drenar salud",
        "Drain Stamina": "Drenar resistencia",
        "Drain Magicka": "Drenar magicka",
        
        # ====== MECÁNICAS DE JUEGO ======
        "Stagger Effect": "Efecto de aturdimiento",
        "Knockdown Effect": "Efecto de derribo",
        "Pushback Effect": "Efecto de retroceso",
        "Stun Effect": "Efecto de aturdimiento",
        "Critical Hit": "Golpe crítico",
        "Sneak Attack": "Ataque sigiloso",
        "Power Attack": "Ataque poderoso",
        "Block Effect": "Efecto de bloqueo",
        "Shield Bash": "Golpe de escudo",
        
        # ====== EQUIPAMIENTO Y ARMADURA ======
        "Armor Rating": "Clasificación de armadura",
        "Armor Bonus": "Bonificación de armadura",
        "Weapon Damage": "Daño de arma",
        "Weapon Speed": "Velocidad de arma",
        "Reach": "Alcance",
        "Weight": "Peso",
        "Value": "Valor",
        "Temper": "Templar",
        "Refine": "Refinar",
        "Enchantment Effect": "Efecto de encantamiento",
        "Enchantment Charge": "Carga de encantamiento",
        "Enchantment Use": "Uso de encantamiento",
        
        # ====== CREATURAS Y ENEMIGOS ======
        "Dragon Effect": "Efecto de dragón",
        "Troll Effect": "Efecto de trol",
        "Giant Effect": "Efecto de gigante",
        "Werewolf Effect": "Efecto de hombre lobo",
        "Vampire Effect": "Efecto de vampiro",
        "Daedra Effect": "Efecto de daedra",
        "Undead Effect": "Efecto de no-muerto",
        "Dwarven Effect": "Efecto enano",
        "Falmer Effect": "Efecto de falmer",
        "Spriggan Effect": "Efecto de Spriggan",
        "Atronach Effect": "Efecto de atronach",
        
        # ====== MODS POPULARES DE SKYRIM ======
        # Ordinator (perks)
        "Perk Effect": "Efecto de ventaja",
        "Perk Tree": "Árbol de ventajas",
        "Perk Point": "Punto de ventaja",
        "Perk Rank": "Rango de ventaja",
        "Perk Description": "Descripción de ventaja",
        
        # SkyUI
        "Inventory Filter": "Filtro de inventario",
        "Sort By": "Ordenar por",
        "Group": "Grupo",
        "Favorites": "Favoritos",
        "Item Card": "Tarjeta de objeto",
        "Stat Display": "Pantalla de estadísticas",
        
        # Summermyst (encantamientos)
        "Enchantment Affix": "Afixo de encantamiento",
        "Enchantment Prefix": "Prefijo de encantamiento",
        "Enchantment Suffix": "Sufijo de encantamiento",
        "Enchantment Effect Name": "Nombre de efecto de encantamiento",
        "Enchantment Description": "Descripción de encantamiento",
        
        # Wintersun (religión)
        "Deity Favor": "Favor de deidad",
        "Deity Quest": "Misión de deidad",
        "Prayer Effect": "Efecto de oración",
        "Meditation Effect": "Efecto de meditación",
        "Sacrifice Effect": "Efecto de sacrificio",
        
        # Imperious (razas)
        "Racial Ability": "Habilidad racial",
        "Racial Power": "Poder racial",
        "Racial Skill": "Habilidad racial",
        "Racial Bonus": "Bonificación racial",
        "Racial Effect": "Efecto racial",
        
        # Andromeda (standing stones)
        "Standing Stone": "Piedra de los guardianes",
        "Stone Effect": "Efecto de piedra",
        "Stone Power": "Poder de piedra",
        "Stone Blessing": "Bendición de piedra",
        
        # ====== TÉRMINOS DE CONSTRUCCIÓN (Hearthfire) ======
        "Building Material": "Material de construcción",
        "Furniture Craft": "Artesanía de muebles",
        "House Upgrade": "Mejora de casa",
        "Wing Addition": "Adición de ala",
        "Plot Foundation": "Cimientos de parcela",
        "Building Scheme": "Plano de construcción",
        
        # ====== TÉRMINOS DE CRAFTING ======
        "Smelting": "Fundición",
        "Tanning": "Curtido",
        "Cooking": "Cocina",
        "Alchemy": "Alquimia",
        "Enchanting": "Encantamiento",
        "Smithing": "Herrería",
        "Mining": "Minería",
        "Woodcutting": "Tala de madera",
        "Harvesting": "Cosecha",
        "Refining": "Refinado",
        
        # ====== TÉRMINOS COMUNES DE SKYRIM ======
        "FUS RO DAH": "FUS RO DAH",
        "Unrelenting Force": "Fuerza implacable",
        "Dragon Shout": "Grito de dragón",
        "Word of Power": "Palabra de poder",
        "Dragon Soul": "Alma de dragón",
        "Dragonborn": "Sangre de dragón",
        "Thu'um": "Thu'um",
        "Greybeards": "Barbas grises",
        "Blades": "Cuchillas",
        "Dark Brotherhood": "Hermandad oscura",
        "Thieves Guild": "Gremio de ladrones",
        "Companions": "Compañeros",
        "College of Winterhold": "Colegio de Winterhold",
        
        # ====== CIUDADES Y UBICACIONES ======
        "Whiterun": "Carrera blanca",
        "Windhelm": "Vientohelado",
        "Solitude": "Soledad",
        "Markarth": "Markarth",
        "Riften": "Riften",
        "Winterhold": "Winterhold",
        "Dawnstar": "Estrella del amanecer",
        "Morthal": "Morthal",
        "Falkreath": "Falkreath",
        "Riverwood": "Riverwood",
        "Rorikstead": "Rorikstead",
        "Ivarstead": "Ivarstead",
        "Helgen": "Helgen",
        
        # ====== TÉRMINOS DE MODS ESPECÍFICOS ======
        # Apocalypse / Odin (magia)
        "Spell Mastery": "Maestría de hechizo",
        "Spell Scaling": "Escalado de hechizo",
        "Spell Tier": "Nivel de hechizo",
        "Novice Spell": "Hechizo de novicio",
        "Apprentice Spell": "Hechizo de aprendiz",
        "Adept Spell": "Hechizo de experto",
        "Expert Spell": "Hechizo de experto",
        "Master Spell": "Hechizo de maestro",
        
        # Thunderchild (shouts)
        "Shout Cooldown": "Enfriamiento de grito",
        "Shout Strength": "Potencia de grito",
        "Shout Mastery": "Maestría de grito",
        "Shout Recharge": "Recarga de grito",
        
        # Sacrosanct (vampiros)
        "Vampire Lord": "Señor vampiro",
        "Blood Magic": "Magia de sangre",
        "Blood Potion": "Poción de sangre",
        "Vampire Stage": "Etapa de vampiro",
        "Vampire Weakness": "Debilidad de vampiro",
        
        # Growl (hombres lobo)
        "Werewolf Form": "Forma de hombre lobo",
        "Beast Form": "Forma de bestia",
        "Lunar Affinity": "Afinidad lunar",
        "Wolf Howl": "Aullido de lobo",
        "Feral Power": "Poder feral",
        
        # Términos generales de combate
        "Combat Style": "Estilo de combate",
        "Aggression Level": "Nivel de agresión",
        "Confidence Level": "Nivel de confianza",
        "Morality Level": "Nivel de moralidad",
        "Combat Radius": "Radio de combate",
        "Sight Distance": "Distancia de visión",
        "Hearing Distance": "Distancia de audición",
    },
    
    # ====== VERSIONES EN INGLÉS ======
    "English": {
        "Blood Decal Large": "Blood Decal Large",
        "Blood Decal Small": "Blood Decal Small",
        "Slow Time": "Slow Time",
        "Gore Pile": "Gore Pile",
        "Dust Pile": "Dust Pile",
        "Death Effects Dragon": "Death Effects Dragon",
        "Bleed Head": "Bleed Head",
        "Bleed Eye": "Bleed Eye",
        "Bleed Mouth": "Bleed Mouth",
        "Blood Head": "Blood Head",
        "Blood Mouth": "Blood Mouth",
        "Blood Eye": "Blood Eye",
        "Armor Explosion def": "Armor Explosion def",
        "FUS RO DAH": "FUS RO DAH",
        "Unrelenting Force": "Unrelenting Force",
        "Dragonborn": "Dragonborn",
        "Thu'um": "Thu'um",
        "Greybeards": "Greybeards",
        "Blades": "Blades",
        "Dark Brotherhood": "Dark Brotherhood",
        "Thieves Guild": "Thieves Guild",
        "Companions": "Companions",
        "College of Winterhold": "College of Winterhold",
        "Whiterun": "Whiterun",
        "Windhelm": "Windhelm",
        "Solitude": "Solitude",
        "Markarth": "Markarth",
        "Riften": "Riften",
        "Winterhold": "Winterhold",
        "Dawnstar": "Dawnstar",
        "Morthal": "Morthal",
        "Falkreath": "Falkreath",
    },
    
    # ====== VERSIONES EN FRANCÉS ======
    "French": {
        "Blood Decal Large": "Grand décalque de sang",
        "Blood Decal Small": "Petit décalque de sang",
        "Slow Time": "Ralentissement du temps",
        "Gore Pile": "Tas de chair",
        "Dust Pile": "Tas de poussière",
        "Death Effects Dragon": "Effets de mort de dragon",
        "Bleed Head": "Saignement de tête",
        "Bleed Eye": "Saignement d'œil",
        "Bleed Mouth": "Saignement de bouche",
        "Blood Head": "Sang de tête",
        "Blood Mouth": "Sang de bouche",
        "Blood Eye": "Sang d'œil",
        "Armor Explosion def": "Explosion d'armure",
        "FUS RO DAH": "FUS RO DAH",
        "Unrelenting Force": "Force implacable",
        "Dragonborn": "Dragonborn",
        "Whiterun": "Blancherive",
        "Windhelm": "Vendeaume",
        "Solitude": "Solitude",
        "Riften": "Riften",
    },
    
    # ====== VERSIONES EN ALEMÁN ======
    "German": {
        "Blood Decal Large": "Großer Blutaufkleber",
        "Blood Decal Small": "Kleiner Blutaufkleber",
        "Slow Time": "Zeit verlangsamen",
        "Gore Pile": "Bluthaufen",
        "Dust Pile": "Staubhaufen",
        "Death Effects Dragon": "Todeseffekte Drachen",
        "Bleed Head": "Kopfblutung",
        "Bleed Eye": "Augenblutung",
        "Bleed Mouth": "Mundblutung",
        "Blood Head": "Blut Kopf",
        "Blood Mouth": "Blut Mund",
        "Blood Eye": "Blut Auge",
        "Armor Explosion def": "Rüstungsexplosion",
        "FUS RO DAH": "FUS RO DAH",
        "Unrelenting Force": "Unnachgiebige Kraft",
        "Dragonborn": "Drachenblut",
        "Whiterun": "Weißlauf",
        "Windhelm": "Windhelm",
        "Solitude": "Einsamkeit",
        "Riften": "Riften",
    },
    
    # ====== VERSIONES EN ITALIANO ======
    "Italian": {
        "Blood Decal Large": "Grande decalcomania di sangue",
        "Blood Decal Small": "Piccola decalcomania di sangue",
        "Slow Time": "Tempo rallentato",
        "Gore Pile": "Mucchio di viscere",
        "Dust Pile": "Mucchio di polvere",
        "Death Effects Dragon": "Effetti di morte del drago",
        "Bleed Head": "Sanguinamento della testa",
        "Bleed Eye": "Sanguinamento dell'occhio",
        "Bleed Mouth": "Sanguinamento della bocca",
        "Blood Head": "Sangue della testa",
        "Blood Mouth": "Sangue della bocca",
        "Blood Eye": "Sangue dell'occhio",
        "Armor Explosion def": "Esplosione dell'armatura",
        "FUS RO DAH": "FUS RO DAH",
        "Whiterun": "Corsa bianca",
        "Windhelm": "Elmo del vento",
        "Solitude": "Solitudine",
    },
    
    # ====== VERSIONES EN PORTUGUÉS ======
    "Portuguese": {
        "Blood Decal Large": "Grande decalque de sangue",
        "Blood Decal Small": "Pequeno decalque de sangue",
        "Slow Time": "Tempo desacelerado",
        "Gore Pile": "Monte de vísceras",
        "Dust Pile": "Monte de poeira",
        "Death Effects Dragon": "Efeitos de morte do dragão",
        "Bleed Head": "Sangramento na cabeça",
        "Bleed Eye": "Sangramento no olho",
        "Bleed Mouth": "Sangramento na boca",
        "Blood Head": "Sangue da cabeça",
        "Blood Mouth": "Sangue da boca",
        "Blood Eye": "Sangue do olho",
        "Armor Explosion def": "Explosão de armadura",
        "FUS RO DAH": "FUS RO DAH",
        "Whiterun": "Corrida Branca",
        "Windhelm": "Elmo do Vento",
        "Solitude": "Solidão",
    },
    
    # ====== VERSIONES EN RUSO ======
    "Russian": {
        "Blood Decal Large": "Большая кровавая нашивка",
        "Blood Decal Small": "Маленькая кровавая нашивка",
        "Slow Time": "Замедление времени",
        "Gore Pile": "Куча мяса",
        "Dust Pile": "Куча пыли",
        "Death Effects Dragon": "Эффекты смерти дракона",
        "Bleed Head": "Кровотечение головы",
        "Bleed Eye": "Кровотечение глаза",
        "Bleed Mouth": "Кровотечение рта",
        "Blood Head": "Кровь головы",
        "Blood Mouth": "Кровь рта",
        "Blood Eye": "Кровь глаза",
        "Armor Explosion def": "Взрыв брони",
        "FUS RO DAH": "ФУС РО ДАХ",
        "Whiterun": "Вайтран",
        "Windhelm": "Виндхельм",
        "Solitude": "Солитьюд",
    },
    
    # ====== VERSIONES EN JAPONÉS ======
    "Japanese": {
        "Blood Decal Large": "血のデカール大",
        "Blood Decal Small": "血のデカール小",
        "Slow Time": "時間停止",
        "Gore Pile": "内臓の山",
        "Dust Pile": "塵の山",
        "Death Effects Dragon": "ドラゴンの死のエフェクト",
        "Bleed Head": "頭部出血",
        "Bleed Eye": "眼部出血",
        "Bleed Mouth": "口部出血",
        "Blood Head": "頭部の血",
        "Blood Mouth": "口の血",
        "Blood Eye": "目の血",
        "Armor Explosion def": "防具爆発",
        "FUS RO DAH": "FUS RO DAH",
        "Unrelenting Force": "不屈の力",
        "Dragonborn": "ドラゴンボーン",
        "Thu'um": "トゥーム",
        "Greybeards": "灰色の髭",
        "Blades": "ブレイド",
        "Dark Brotherhood": "ダークブラザーフッド",
        "Thieves Guild": "盗賊ギルド",
        "Companions": "コンパニオン",
        "College of Winterhold": "ウィンターホールド大学",
        "Whiterun": "ホワイトラン",
        "Windhelm": "ウィンドヘルム",
        "Solitude": "ソリチュード",
        "Markarth": "マーカス",
        "Riften": "リフテン",
        "Winterhold": "ウィンターホールド",
        "Dawnstar": "ドーンスター",
        "Morthal": "モーサル",
        "Falkreath": "フォークリス",
        "Riverwood": "リバーウッド",
        "Bleed left arm": "左腕の出血",
        "Bleed right arm": "右腕の出血",
        "Bleed left leg": "左脚の出血",
        "Bleed right leg": "右脚の出血",
        "Bleed Torso": "胴体の出血",
        "Blood Torso": "胴体の血",
        "Blood Arm": "腕の血",
        "Blood Leg": "脚の血",
        "Dragon Shout": "ドラゴンの雄叫び",
        "Word of Power": "力の言葉",
        "Dragon Soul": "ドラゴンの魂",
    }
}


class MockProvider:
    def __init__(self, settings=None):
        self.settings = settings or {}
        self.target_language = self.settings.get("target_language", "Spanish")

    def translate(self, text):
        lang_dict = MOCK_DICTIONARIES.get(self.target_language, {})
        
        if text in lang_dict:
            return lang_dict[text]
        
        return f"[{self.target_language}] {text}"


class OllamaProvider:
    def __init__(self, settings):
        self.model = settings.get("model", "qwen2.5:1.5b")
        self.url = settings.get(
            "ollama_url",
            "http://localhost:11434/api/generate"
        )
        self.target_language = settings.get("target_language", "Spanish")
        
        self.prompt_template = self.load_prompt_template()
    
    def load_prompt_template(self):
        """Carga el prompt personalizado desde archivo de configuración"""
        prompt_path = os.path.join("config", "prompt_template.txt")
        
        # Prompt mejorado con instrucciones para escritura nativa
        default_prompt = """You are a translator for Skyrim game mods. Translate from English to {language}.

CRITICAL RULES - FOLLOW STRICTLY:
1. Output ONLY the translation in {language}. Return NOTHING else.
2. Use the CORRECT NATIVE WRITING SYSTEM for the target language:
   - Japanese (Japanese): Use Japanese characters (Kanji, Hiragana, Katakana). 
     ABSOLUTELY NO romaji (Latin alphabet) for Japanese translations.
   - Chinese (Chinese): Use Chinese characters.
   - Korean (Korean): Use Hangul characters.
   - Russian (Russian): Use Cyrillic characters.
   - Spanish/French/German/Italian/Portuguese: Use Latin alphabet with accents.
3. Keep proper names (like Whiterun, FUS RO DAH) unchanged.
4. Keep codes and abbreviations (like def, FX, DLC) unchanged.
5. Translate literally, not creatively.

LANGUAGE-SPECIFIC WRITING SYSTEM EXAMPLES:
English: "Blood Decal Large"
- Japanese: 血のデカール大 (NOT "Chi no dekāru dai" - this is romaji, WRONG!)
- Chinese: 血贴花大
- Korean: 혈액 데칼 대
- Russian: Большая кровавая нашивка

English: "Bleed left arm"
- Japanese: 左腕の出血 (NOT "Hidari ude no shukketsu" - this is romaji, WRONG!)
- Chinese: 左臂出血
- Korean: 왼쪽 팔 출혈
- Russian: Кровотечение левой руки

English: "Slow Time"
- Japanese: 時間停止 (NOT "Jikan teishi" - this is romaji, WRONG!)
- Chinese: 时间停止
- Korean: 시간 정지
- Russian: Замедление времени

Text to translate (ONLY translate this exact text):
{text}

Translation ({language}) in correct native writing system:"""
        
        try:
            if os.path.exists(prompt_path):
                with open(prompt_path, "r", encoding="utf-8") as f:
                    custom_prompt = f.read().strip()
                    if custom_prompt:
                        return custom_prompt
        except Exception:
            pass
        
        return default_prompt

    def translate(self, text):
        prompt = self.prompt_template.format(
            language=self.target_language,
            text=text
        )

        try:
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
            result = data.get("response", "").strip()

            # Limpiar prefijos comunes
            prefixes = [
                "Translation:", "Traducción:", "Resultado:", 
                "Result:", "Output:", "Salida:", "Response:", 
                "Respuesta:", f"Translation ({self.target_language}):",
                "Translation", "Traducción"
            ]
            
            for prefix in prefixes:
                if result.startswith(prefix):
                    result = result[len(prefix):].strip()
            
            # Para japonés, NO eliminar caracteres nativos
            # Solo eliminar caracteres de control
            if self.target_language == "Japanese":
                # Mantener caracteres japoneses, solo limpiar espacios extra
                result = re.sub(r'\s+', ' ', result).strip()
            else:
                # Para otros idiomas, limpiar caracteres extraños
                clean_pattern = re.compile(r'[^\w\s.,;:!?¿¡()\-\'"]+', re.UNICODE)
                result = clean_pattern.sub('', result)
            
            if not result:
                return text

            return result

        except Exception as e:
            print(f"Error en traducción: {e}")
            return text