# languages.py - Diccionario completo de traducciones para la interfaz

LANGUAGES = {
    "Spanish": {
        "code": "es",
        "name": "Español",
        "translations": {
            # Ventana principal
            "window_title": "Skyrim AI Translator v0.6",
            "no_file_loaded": "📂 Ningún archivo cargado",
            "total": "📊 Total: {0}",
            "translated": "✅ Traducidos: {0}",
            "pending": "⏳ Pendientes: {0}",
            "search_placeholder": "🔍 Buscar por FormID, EDID, texto original o traducción...",
            
            # Botones
            "btn_export": "💾 Exportar TXT traducido",
            "btn_copy_original": "📋 Copiar Original → Traducción",
            "btn_translate_selected": "🤖 Traducir Selección",
            "btn_translate_visible": "👁️ Traducir Visibles",
            "btn_translate_all": "🌐 Traducir Todo",
            "btn_all": "📋 Todos",
            "btn_pending": "⏳ Pendientes",
            "btn_translated": "✅ Traducidos",
            "btn_cancel": "❌ Cancelar traducción",
            
            # Menú Archivo
            "menu_file": "📁 Archivo",
            "menu_open": "📂 Abrir TXT de xEdit",
            "menu_export": "💾 Exportar TXT traducido",
            "menu_save_project": "💾 Guardar proyecto",
            "menu_open_project": "📂 Abrir proyecto",
            "menu_auto_save": "💾 Guardado automático",
            "menu_exit": "❌ Salir",
            
            # Menú Herramientas
            "menu_tools": "🛠️ Herramientas",
            "menu_load_dictionary": "📚 Cargar Diccionario",
            "menu_apply_dictionary": "⚡ Aplicar Diccionario",
            "menu_copy_original": "📋 Copiar Original → Traducción",
            
            # Menú IA
            "menu_ai": "🤖 IA",
            "menu_ai_settings": "⚙️ Configuración IA",
            "menu_ai_manager": "📥 Descargar / Configurar IA",
            "menu_prompt_editor": "✏️ Editar Prompt de IA",
            "menu_translate_selected": "🤖 Traducir Selección",
            "menu_translate_visible": "👁️ Traducir Visibles",
            "menu_translate_all": "🌐 Traducir Todo",
            
            # Menú Ayuda
            "menu_help": "❓ Ayuda",
            "menu_about": "ℹ️ Acerca de",
            
            # Diálogos y mensajes
            "msg_about_title": "Acerca de Skyrim AI Translator",
            "msg_about_text": "Skyrim AI Translator v0.6\n\nTraduce archivos FULL de Skyrim usando IA.\nSoporte para Ollama y diccionarios personalizados.\n\nCreado para la comunidad de modding de Skyrim.",
            
            "msg_warning": "Aviso",
            "msg_no_rows": "No hay filas para traducir.",
            "msg_select_rows": "Selecciona una o varias filas.",
            "msg_no_file": "Primero abre un archivo.",
            "msg_no_dictionary": "Primero carga un diccionario.",
            "msg_dictionary_loaded": "Se cargaron {0} entradas.",
            "msg_dictionary_applied": "{0} registros actualizados.",
            "msg_exported": "Archivo exportado correctamente.",
            "msg_project_saved": "Proyecto guardado correctamente.",
            "msg_project_loaded": "📂 Proyecto cargado: {0} | Registros: {1}",
            "msg_file_loaded": "📂 Archivo cargado: {0} | Registros: {1} | Encoding: {2}",
            "msg_translation_finished": "Se tradujeron {0} registro(s).\nCaché guardada en: {1}",
            "msg_cancel_translation": "La traducción se cancelará al terminar el registro actual.",
            "msg_cache_dictionary": "Todos los textos ya estaban en caché o diccionario. Se aplicaron {0} traducciones.",
            "msg_confirm_translate_all": "Vas a traducir {0} registros. Esto puede tardar bastante.\n\n¿Continuar?",
            "msg_confirm_exit": "¿Estás seguro de que quieres salir?",
            "msg_language_changed": "Idioma cambiado a {0}.\n\nAlgunos cambios requieren reiniciar la aplicación para aplicarse completamente.",
            
            # Errores
            "error_title": "Error",
            "error_reading_file": "Error al abrir archivo",
            "error_exporting": "Error al exportar",
            "error_saving_project": "Error al guardar proyecto",
            "error_loading_project": "Error al abrir proyecto",
            "error_ai": "Error IA",
            "error_dictionary": "Error",
            
            # Tabla
            "col_formid": "FormID",
            "col_edid": "EDID",
            "col_original": "Original",
            "col_translation": "Traducción",
            "col_status": "Estado",
            "status_translated": "Traducido",
            "status_pending": "Pendiente",
            
            # Configuración
            "settings_title": "Configuración",
            "settings_language": "🌐 Idioma de la interfaz",
            "settings_restart_hint": "Reinicia la aplicación para aplicar todos los cambios"
        }
    },
    
    "English": {
        "code": "en",
        "name": "English",
        "translations": {
            "window_title": "Skyrim AI Translator v0.6",
            "no_file_loaded": "📂 No file loaded",
            "total": "📊 Total: {0}",
            "translated": "✅ Translated: {0}",
            "pending": "⏳ Pending: {0}",
            "search_placeholder": "🔍 Search by FormID, EDID, original text or translation...",
            
            "btn_export": "💾 Export Translated TXT",
            "btn_copy_original": "📋 Copy Original → Translation",
            "btn_translate_selected": "🤖 Translate Selected",
            "btn_translate_visible": "👁️ Translate Visible",
            "btn_translate_all": "🌐 Translate All",
            "btn_all": "📋 All",
            "btn_pending": "⏳ Pending",
            "btn_translated": "✅ Translated",
            "btn_cancel": "❌ Cancel translation",
            
            "menu_file": "📁 File",
            "menu_open": "📂 Open xEdit TXT",
            "menu_export": "💾 Export Translated TXT",
            "menu_save_project": "💾 Save Project",
            "menu_open_project": "📂 Open Project",
            "menu_auto_save": "💾 Auto Save",
            "menu_exit": "❌ Exit",
            
            "menu_tools": "🛠️ Tools",
            "menu_load_dictionary": "📚 Load Dictionary",
            "menu_apply_dictionary": "⚡ Apply Dictionary",
            "menu_copy_original": "📋 Copy Original → Translation",
            
            "menu_ai": "🤖 AI",
            "menu_ai_settings": "⚙️ AI Settings",
            "menu_ai_manager": "📥 Download / Configure AI",
            "menu_prompt_editor": "✏️ Edit AI Prompt",
            "menu_translate_selected": "🤖 Translate Selected",
            "menu_translate_visible": "👁️ Translate Visible",
            "menu_translate_all": "🌐 Translate All",
            
            "menu_help": "❓ Help",
            "menu_about": "ℹ️ About",
            
            "msg_about_title": "About Skyrim AI Translator",
            "msg_about_text": "Skyrim AI Translator v0.6\n\nTranslate FULL files from Skyrim using AI.\nSupport for Ollama and custom dictionaries.\n\nCreated for the Skyrim modding community.",
            
            "msg_warning": "Warning",
            "msg_no_rows": "No rows to translate.",
            "msg_select_rows": "Select one or more rows.",
            "msg_no_file": "Open a file first.",
            "msg_no_dictionary": "Load a dictionary first.",
            "msg_dictionary_loaded": "Loaded {0} entries.",
            "msg_dictionary_applied": "{0} records updated.",
            "msg_exported": "File exported successfully.",
            "msg_project_saved": "Project saved successfully.",
            "msg_project_loaded": "📂 Project loaded: {0} | Records: {1}",
            "msg_file_loaded": "📂 File loaded: {0} | Records: {1} | Encoding: {2}",
            "msg_translation_finished": "Translated {0} record(s).\nCache saved to: {1}",
            "msg_cancel_translation": "Translation will be cancelled after the current record.",
            "msg_cache_dictionary": "All texts were already in cache or dictionary. Applied {0} translations.",
            "msg_confirm_translate_all": "You are about to translate {0} records. This may take a while.\n\nContinue?",
            "msg_confirm_exit": "Are you sure you want to exit?",
            "msg_language_changed": "Language changed to {0}.\n\nSome changes require restarting the application to apply fully.",
            
            "error_title": "Error",
            "error_reading_file": "Error opening file",
            "error_exporting": "Error exporting",
            "error_saving_project": "Error saving project",
            "error_loading_project": "Error opening project",
            "error_ai": "AI Error",
            "error_dictionary": "Error",
            
            "col_formid": "FormID",
            "col_edid": "EDID",
            "col_original": "Original",
            "col_translation": "Translation",
            "col_status": "Status",
            "status_translated": "Translated",
            "status_pending": "Pending",
            
            "settings_title": "Settings",
            "settings_language": "🌐 Interface Language",
            "settings_restart_hint": "Restart the application to apply all changes"
        }
    },
    
    "French": {
        "code": "fr",
        "name": "Français",
        "translations": {
            "window_title": "Skyrim AI Translator v0.6",
            "no_file_loaded": "📂 Aucun fichier chargé",
            "total": "📊 Total: {0}",
            "translated": "✅ Traduits: {0}",
            "pending": "⏳ En attente: {0}",
            "search_placeholder": "🔍 Rechercher par FormID, EDID, texte original ou traduction...",
            
            "btn_export": "💾 Exporter TXT traduit",
            "btn_copy_original": "📋 Copier Original → Traduction",
            "btn_translate_selected": "🤖 Traduire la sélection",
            "btn_translate_visible": "👁️ Traduire les visibles",
            "btn_translate_all": "🌐 Tout traduire",
            "btn_all": "📋 Tous",
            "btn_pending": "⏳ En attente",
            "btn_translated": "✅ Traduits",
            "btn_cancel": "❌ Annuler la traduction",
            
            "menu_file": "📁 Fichier",
            "menu_open": "📂 Ouvrir TXT xEdit",
            "menu_export": "💾 Exporter TXT traduit",
            "menu_save_project": "💾 Sauvegarder le projet",
            "menu_open_project": "📂 Ouvrir le projet",
            "menu_auto_save": "💾 Sauvegarde automatique",
            "menu_exit": "❌ Quitter",
            
            "menu_tools": "🛠️ Outils",
            "menu_load_dictionary": "📚 Charger le dictionnaire",
            "menu_apply_dictionary": "⚡ Appliquer le dictionnaire",
            "menu_copy_original": "📋 Copier Original → Traduction",
            
            "menu_ai": "🤖 IA",
            "menu_ai_settings": "⚙️ Configuration IA",
            "menu_ai_manager": "📥 Télécharger / Configurer IA",
            "menu_prompt_editor": "✏️ Éditer le prompt IA",
            "menu_translate_selected": "🤖 Traduire la sélection",
            "menu_translate_visible": "👁️ Traduire les visibles",
            "menu_translate_all": "🌐 Tout traduire",
            
            "menu_help": "❓ Aide",
            "menu_about": "ℹ️ À propos",
            
            "msg_about_title": "À propos de Skyrim AI Translator",
            "msg_about_text": "Skyrim AI Translator v0.6\n\nTraduit les fichiers FULL de Skyrim avec l'IA.\nSupport pour Ollama et dictionnaires personnalisés.\n\nCréé pour la communauté de modding Skyrim.",
            
            "msg_warning": "Avertissement",
            "msg_no_rows": "Aucune ligne à traduire.",
            "msg_select_rows": "Sélectionnez une ou plusieurs lignes.",
            "msg_no_file": "Ouvrez d'abord un fichier.",
            "msg_no_dictionary": "Chargez d'abord un dictionnaire.",
            "msg_dictionary_loaded": "{0} entrées chargées.",
            "msg_dictionary_applied": "{0} enregistrements mis à jour.",
            "msg_exported": "Fichier exporté avec succès.",
            "msg_project_saved": "Projet sauvegardé avec succès.",
            "msg_project_loaded": "📂 Projet chargé: {0} | Enregistrements: {1}",
            "msg_file_loaded": "📂 Fichier chargé: {0} | Enregistrements: {1} | Encodage: {2}",
            "msg_translation_finished": "{0} enregistrement(s) traduits.\nCache sauvegardé dans: {1}",
            "msg_confirm_exit": "Êtes-vous sûr de vouloir quitter ?",
            
            "error_title": "Erreur",
            "error_reading_file": "Erreur lors de l'ouverture du fichier",
            "error_exporting": "Erreur lors de l'exportation",
            
            "col_formid": "FormID",
            "col_edid": "EDID",
            "col_original": "Original",
            "col_translation": "Traduction",
            "col_status": "Statut",
            "status_translated": "Traduit",
            "status_pending": "En attente",
            
            "settings_title": "Configuration",
            "settings_language": "🌐 Langue de l'interface",
            "settings_restart_hint": "Redémarrez l'application pour appliquer tous les changements"
        }
    },
    
    "German": {
        "code": "de",
        "name": "Deutsch",
        "translations": {
            "window_title": "Skyrim AI Translator v0.6",
            "no_file_loaded": "📂 Keine Datei geladen",
            "total": "📊 Gesamt: {0}",
            "translated": "✅ Übersetzt: {0}",
            "pending": "⏳ Ausstehend: {0}",
            "search_placeholder": "🔍 Suche nach FormID, EDID, Originaltext oder Übersetzung...",
            
            "btn_export": "💾 Übersetzte TXT exportieren",
            "btn_copy_original": "📋 Original → Übersetzung kopieren",
            "btn_translate_selected": "🤖 Auswahl übersetzen",
            "btn_translate_visible": "👁️ Sichtbare übersetzen",
            "btn_translate_all": "🌐 Alle übersetzen",
            "btn_all": "📋 Alle",
            "btn_pending": "⏳ Ausstehend",
            "btn_translated": "✅ Übersetzt",
            "btn_cancel": "❌ Übersetzung abbrechen",
            
            "menu_file": "📁 Datei",
            "menu_open": "📂 xEdit TXT öffnen",
            "menu_export": "💾 Übersetzte TXT exportieren",
            "menu_save_project": "💾 Projekt speichern",
            "menu_open_project": "📂 Projekt öffnen",
            "menu_auto_save": "💾 Automatisch speichern",
            "menu_exit": "❌ Beenden",
            
            "menu_tools": "🛠️ Werkzeuge",
            "menu_load_dictionary": "📚 Wörterbuch laden",
            "menu_apply_dictionary": "⚡ Wörterbuch anwenden",
            "menu_copy_original": "📋 Original → Übersetzung kopieren",
            
            "menu_ai": "🤖 KI",
            "menu_ai_settings": "⚙️ KI-Einstellungen",
            "menu_ai_manager": "📥 KI herunterladen / konfigurieren",
            "menu_prompt_editor": "✏️ KI-Prompt bearbeiten",
            "menu_translate_selected": "🤖 Auswahl übersetzen",
            "menu_translate_visible": "👁️ Sichtbare übersetzen",
            "menu_translate_all": "🌐 Alle übersetzen",
            
            "menu_help": "❓ Hilfe",
            "menu_about": "ℹ️ Über",
            
            "msg_about_title": "Über Skyrim AI Translator",
            "msg_about_text": "Skyrim AI Translator v0.6\n\nÜbersetzt FULL-Dateien von Skyrim mit KI.\nUnterstützung für Ollama und benutzerdefinierte Wörterbücher.\n\nErstellt für die Skyrim-Modding-Community.",
            
            "msg_warning": "Warnung",
            "msg_no_rows": "Keine Zeilen zum Übersetzen.",
            "msg_select_rows": "Wählen Sie eine oder mehrere Zeilen aus.",
            "msg_no_file": "Öffnen Sie zuerst eine Datei.",
            "msg_no_dictionary": "Laden Sie zuerst ein Wörterbuch.",
            "msg_dictionary_loaded": "{0} Einträge geladen.",
            "msg_dictionary_applied": "{0} Einträge aktualisiert.",
            "msg_exported": "Datei erfolgreich exportiert.",
            "msg_project_saved": "Projekt erfolgreich gespeichert.",
            "msg_project_loaded": "📂 Projekt geladen: {0} | Einträge: {1}",
            "msg_file_loaded": "📂 Datei geladen: {0} | Einträge: {1} | Kodierung: {2}",
            "msg_translation_finished": "{0} Eintrag(e) übersetzt.\nCache gespeichert in: {1}",
            "msg_confirm_exit": "Sind Sie sicher, dass Sie beenden möchten?",
            
            "error_title": "Fehler",
            "error_reading_file": "Fehler beim Öffnen der Datei",
            "error_exporting": "Fehler beim Exportieren",
            
            "col_formid": "FormID",
            "col_edid": "EDID",
            "col_original": "Original",
            "col_translation": "Übersetzung",
            "col_status": "Status",
            "status_translated": "Übersetzt",
            "status_pending": "Ausstehend",
            
            "settings_title": "Einstellungen",
            "settings_language": "🌐 Oberflächensprache",
            "settings_restart_hint": "Starten Sie die Anwendung neu, um alle Änderungen zu übernehmen"
        }
    }
}


def get_text(key, language="Spanish", **kwargs):
    """Obtiene un texto traducido según el idioma"""
    lang_data = LANGUAGES.get(language, LANGUAGES["Spanish"])
    text = lang_data["translations"].get(key, key)
    
    if kwargs:
        try:
            text = text.format(**kwargs)
        except:
            pass
    
    return text


def get_language_name(code):
    """Obtiene el nombre del idioma por su código"""
    for lang, data in LANGUAGES.items():
        if data["code"] == code:
            return data["name"]
    return "Spanish"


def get_language_code(language):
    """Obtiene el código del idioma"""
    lang_data = LANGUAGES.get(language, LANGUAGES["Spanish"])
    return lang_data["code"]