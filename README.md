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

### Opción C: Compilar EXE manualmente

```bash
# Instalar PyInstaller
pip install pyinstaller

# Compilar con icono
python -m PyInstaller --onefile --windowed --icon="icon.ico" --add-data "languages.py;." --add-data "settings_dialog.py;." --add-data "ai_manager_dialog.py;." --add-data "prompt_editor_dialog.py;." --add-data "translation_worker.py;." --add-data "providers;providers" --add-data "assets;assets" --add-data "icon.ico;." --hidden-import PyQt6 --hidden-import PyQt6.QtCore --hidden-import PyQt6.QtGui --hidden-import PyQt6.QtWidgets --hidden-import pandas --hidden-import chardet --hidden-import requests --name="SkyrimAITranslator" main.py

# El EXE se generará en:
dist\SkyrimAITranslator.exe
```

---

## 📦 Dependencias

### Requisitos del sistema

- Windows 7 / 8 / 10 / 11 (64-bit)
- Ollama (Opcional)
- 4 GB RAM mínimo
- 8 GB RAM recomendado
- 500 MB de espacio libre

### Dependencias Python (requirements.txt)

```txt
PyQt6>=6.4.0
pandas>=1.5.0
chardet>=5.0.0
requests>=2.28.0
pyinstaller>=5.0.0
pillow>=9.0.0
```

### 🤖 Modelos IA recomendados

| Modelo | Tamaño | Uso recomendado |
|----------|----------|----------|
| qwen2.5:1.5b | ~1.5 GB | Ligero y rápido |
| qwen2.5:3b | ~3 GB | Equilibrio calidad/velocidad |
| gemma2:2b | ~1.5 GB | Eficiente y preciso |
| mistral | ~4.5 GB | Mayor calidad |
| llama3.2:3b | ~2.5 GB | Moderno y eficiente |

---

## 📖 Uso

### Flujo de trabajo completo

```text
1. xEdit → Exportar → Archivo TXT
2. App → Abrir TXT → Traducir
3. App → Exportar → Archivo TXT traducido
4. xEdit → Importar → Traducciones aplicadas
```

### Paso 1: Exportar desde xEdit

1. Abre xEdit con tu plugin cargado
2. Selecciona el plugin
3. Haz clic derecho → Apply Script
4. Selecciona `Skyrim_Texts_Export`
5. El archivo se guardará en:

```text
Edit Scripts\Skyrim_Texts_Export.txt
```

### Paso 2: Abrir en la aplicación

```text
Archivo → Abrir TXT de xEdit
```

Selecciona:

```text
Skyrim_Texts_Export.txt
```

### Paso 3: Traducir

Opciones disponibles:

- Traducir seleccionados → Filas seleccionadas
- Retraducir seleccionados → Ignora caché
- Traducir visibles → Filas filtradas
- Traducir todo → Todas las filas

### Paso 4: Exportar traducciones

```text
Herramientas → Exportar traducciones para xEdit
```

Guardar como:

```text
Skyrim_Texts_Translated.txt
```

### Paso 5: Importar en xEdit

1. Copia el archivo en:

```text
Edit Scripts\
```

2. Ejecuta:

```text
Apply Script → Skyrim_Texts_Import
```

---

## ⚙️ Configuración

### Acceso

```text
IA → Configuración IA
```

### Idiomas disponibles

| Código | Idioma |
|----------|----------|
| Spanish | Español |
| English | Inglés |
| French | Francés |
| German | Alemán |
| Italian | Italiano |
| Portuguese | Portugués |
| Russian | Ruso |
| Japanese | Japonés |
| Chinese | Chino |
| Korean | Coreano |

### Temperatura recomendada

| Valor | Resultado |
|----------|----------|
| 0.1 - 0.2 | Traducciones limpias y literales |
| 0.3 - 0.5 | Traducciones más naturales |
| 0.6 - 1.0 | Traducciones creativas |

### Temas visuales

#### 🌙 Oscuro

- Diseño moderno
- Colores optimizados para largas sesiones
- Recomendado

#### ☀️ Claro

- Estilo clásico
- Fondo blanco
- Mayor contraste

---

## 🛠️ Scripts de xEdit

### Exportar (Skyrim_Texts_Export.pas)

```pascal
{
  Exporta textos:
  FULL
  DESC
  CNAM
  DNAM
  BOOK_TEXT

  Formato:
  FormID|Signature|EDID|Field|Original
}
```

### Importar (Skyrim_Texts_Import.pas)

```pascal
{
  Importa traducciones desde:
  Skyrim_Texts_Translated.txt

  Formato:
  FormID|Signature|EDID|Field|Translated
}
```

---

## 📁 Estructura del proyecto

```text
SkyrimAITranslator/
├── main.py
├── languages.py
├── settings_dialog.py
├── ai_manager_dialog.py
├── prompt_editor_dialog.py
├── translation_worker.py
├── providers/
│   └── local_provider.py
├── assets/
│   └── app_logo.png
├── config/
│   ├── settings.json
│   ├── translation_cache.json
│   └── auto_save.json
├── xEdit_Scripts/
│   ├── Skyrim_Texts_Export.pas
│   └── Skyrim_Texts_Import.pas
├── icon.ico
├── requirements.txt
├── README.md
└── .gitignore
```

---

## 🐛 Solución de problemas

### Error: "Ollama no está instalado"

**Solución**

- Instala Ollama
- Verifica que el servicio esté ejecutándose
- Descarga modelos desde:

```text
IA → Administrar modelos Ollama
```

---

### Error: "No se pudo leer el archivo"

**Solución**

- Verifica que el archivo sea UTF-8
- Asegúrate de usar el separador `|`
- Guarda como UTF-8 sin BOM usando Notepad++

---

### Error: "El icono no aparece en el EXE"

**Solución**

- Verifica que `icon.ico` contenga múltiples tamaños
- Recompila usando:

```bash
--icon="icon.ico"
```

- Actualiza la caché de iconos de Windows

---

### Error: "La IA traduce con caracteres extraños"

**Solución**

1. Abre:

```text
IA → Editor de Prompt
```

2. Verifica que el prompt indique:

- Traducir usando escritura nativa
- No usar explicaciones
- No usar transliteraciones

Ejemplo:

- Japonés → Kanji/Kana
- Chino → Caracteres chinos
- Coreano → Hangul

---

## 🤝 Contribuir

1. Haz Fork del repositorio
2. Crea una rama

```bash
git checkout -b feature/nueva-funcionalidad
```

3. Realiza tus cambios

```bash
git commit -m "Añade nueva funcionalidad"
```

4. Sube los cambios

```bash
git push origin feature/nueva-funcionalidad
```

5. Abre un Pull Request

---

## 🚀 Próximas mejoras

- Lectura directa de archivos `.esp`
- Lectura directa de archivos `.esm`
- Lectura directa de archivos `.esl`
- Compatibilidad con `.strings`
- Arrastrar y soltar archivos
- Traducción automática al abrir archivos
- Más proveedores IA
- Instalador para Windows
- Actualización automática
- Traducción por lotes de múltiples archivos

---

## 🐞 Reportar problemas

Al abrir un Issue incluye:

- Versión de Windows
- Versión de Skyrim AI Translator
- Modelo IA utilizado
- Pasos para reproducir el problema
- Capturas de pantalla
- Logs si están disponibles

---

## 📜 Licencia

Este proyecto está distribuido bajo la licencia MIT.

---

## 👨‍💻 Autor

### Artlyse.dev

Desarrollado para la comunidad de modding de Skyrim con soporte para traducción mediante IA local y herramientas compatibles con xEdit.

---

<p align="center">
  <img src="assets/app_logo.png" width="96">
</p>

<p align="center">
  <strong>Skyrim AI Translator</strong><br>
  Traduce mods de Skyrim con IA local, rapidez y consistencia.
</p>
