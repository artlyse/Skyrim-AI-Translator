<p align="center">
  <img src="assets/app_logo.png" alt="Skyrim AI Translator" width="128" height="128">
</p>

<h1 align="center">Skyrim AI Translator</h1>

<p align="center">
  <strong>Traducción automática para mods de Skyrim usando IA local</strong>
</p>

<p align="center">
  <a href="#-características">Características</a> •
  <a href="#-instalación">Instalación</a> •
  <a href="#-uso">Uso</a> •
  <a href="#-configuración">Configuración</a> •
  <a href="#-descargas">Descargas</a> •
  <a href="#-contribuir">Contribuir</a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/version-0.8.1-blue" alt="Version">
  <img src="https://img.shields.io/badge/license-MIT-green" alt="License">
  <img src="https://img.shields.io/badge/python-3.10+-blue" alt="Python">
  <img src="https://img.shields.io/badge/platform-Windows-0078d7" alt="Platform">
  <img src="https://img.shields.io/github/downloads/artlyse/Skyrim-AI-Translator/total" alt="Downloads">
</p>

---

## 📖 Descripción

**Skyrim AI Translator** es una herramienta diseñada para la comunidad de modding de Skyrim que permite traducir automáticamente archivos de texto de plugins (`.esp`, `.esm`, `.esl`) utilizando modelos de Inteligencia Artificial locales a través de [Ollama](https://ollama.com/).

La aplicación soporta múltiples campos de texto como `FULL` (nombre), `DESC` (descripción), `CNAM`, `DNAM` y `BOOK_TEXT`, y es compatible con los formatos de exportación de xEdit.

---

## ✨ Características

### 🎯 Traducción IA
- **Modelos locales**: Soporte para Ollama (qwen2.5, gemma2, mistral, llama3, etc.)
- **Multi-idioma**: Traducción a Español, Inglés, Francés, Alemán, Italiano, Portugués, Ruso, Japonés, Chino y Coreano
- **Modo Mock**: Sin necesidad de IA para pruebas y demostraciones

### 🔄 Gestión de traducciones
- **Caché multidioma**: Las traducciones se guardan por idioma para consistencia
- **Reconstrucción de caché**: Traduce todos los textos únicos con consistencia
- **Retraducción forzada**: Sin usar caché para obtener nuevas versiones
- **Diccionario importado**: Soporte para diccionarios JSON personalizados

### 📁 Formatos soportados
- `FormID|Signature|EDID|Field|Original` (exportación completa)
- `FormID|EDID|FULL` (exportación simple)

### 🎨 Interfaz
- **10 idiomas**: Interfaz completamente traducible
- **Tema oscuro/Claro**: Dos temas visuales
- **Transparencia ajustable**: Control de opacidad de la ventana
- **Tamaño de fuente**: Ajustable según preferencia

### 🔧 Herramientas
- **Exportación a xEdit**: Genera archivos listos para importar
- **Exportación de diccionario**: Guarda traducciones en formato JSON
- **Auto-save**: Guardado automático al cerrar
- **Limpieza de IA**: Elimina explicaciones no deseadas

---

## 📥 Descargas

| Plataforma | Descarga | Versión |
|------------|----------|---------|
| **Windows** | [SkyrimAITranslator.exe](https://github.com/artlyse/Skyrim-AI-Translator/releases/latest) | v0.8.1 |
| **Código fuente** | [Source code (zip)](https://github.com/artlyse/Skyrim-AI-Translator/archive/refs/heads/main.zip) | Última |

---

## 🚀 Instalación

### Opción A: Ejecutable portátil (Recomendado)

1. Descarga el archivo `SkyrimAITranslator.exe` desde [Releases](https://github.com/artlyse/Skyrim-AI-Translator/releases)
2. Ejecuta el archivo (no requiere instalación)
3. Opcional: Instala [Ollama](https://ollama.com/) para usar modelos IA locales

### Opción B: Desde código fuente

```bash
# Clonar repositorio
git clone https://github.com/artlyse/Skyrim-AI-Translator.git
cd Skyrim-AI-Translator

# Crear entorno virtual (opcional)
python -m venv venv
venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar
python main.py
