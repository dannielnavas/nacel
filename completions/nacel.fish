# ==============================================================================
# Nacel AI - Fish Autocompletions
# ==============================================================================

# Deshabilitar autocompletado de archivos por defecto a menos que se especifique
complete -c nacel -f

# Subcomandos principales de primer nivel
complete -c nacel -n "__fish_is_first_token" -a "menu" -d "Abre el menú interactivo con todas las opciones"
complete -c nacel -n "__fish_is_first_token" -a "chat" -d "Canal de conversación continuo con memoria"
complete -c nacel -n "__fish_is_first_token" -a "ask" -d "Consulta en lenguaje natural para obtener comandos"
complete -c nacel -n "__fish_is_first_token" -a "fix" -d "Diagnostica y repara el comando fallido previo"
complete -c nacel -n "__fish_is_first_token" -a "explain" -d "Explica arquitectura y lógica de código"
complete -c nacel -n "__fish_is_first_token" -a "debug" -d "Depura trazas de error y causa raíz"
complete -c nacel -n "__fish_is_first_token" -a "hardware" -d "Diagnóstico de hardware y recomendación de modelo"
complete -c nacel -n "__fish_is_first_token" -a "model" -d "Ver o cambiar modelo de IA y estado de Ollama"
complete -c nacel -n "__fish_is_first_token" -a "lang" -d "Ver o cambiar idioma activo (es/en)"
complete -c nacel -n "__fish_is_first_token" -a "help" -d "Muestra la lista de todas las opciones"

# Completar archivos para explain y debug
complete -c nacel -n "__fish_seen_subcommand_from explain debug" -F

# Subcomandos de model
complete -c nacel -n "__fish_seen_subcommand_from model" -a "set" -d "Establecer modelo (ej: llama3.2:1b, qwen2.5-coder:7b)"
complete -c nacel -n "__fish_seen_subcommand_from model" -a "auto" -d "Auto-configurar modelo óptimo según hardware"
complete -c nacel -n "__fish_seen_subcommand_from model" -a "recommend" -d "Asistente interactivo guiado de selección"
complete -c nacel -n "__fish_seen_subcommand_from model" -a "list" -d "Listar modelos instalados y catálogo"
complete -c nacel -n "__fish_seen_subcommand_from model" -a "status" -d "Ver estado actual del modelo y Ollama"

# Opciones de modelos para nacel model set
complete -c nacel -n "__fish_seen_subcommand_from model; and __fish_seen_subcommand_from set" -a "llama3.2:1b" -d "Ultracompacto de Meta (~1.3GB), ágil y certero en errores"
complete -c nacel -n "__fish_seen_subcommand_from model; and __fish_seen_subcommand_from set" -a "qwen2.5-coder:7b" -d "Estándar de oro en precisión de terminal y bash (~4.7GB)"
complete -c nacel -n "__fish_seen_subcommand_from model; and __fish_seen_subcommand_from set" -a "qwen2.5-coder:3b" -d "Respuesta rápida y excelente equilibrio (~2.0GB)"
complete -c nacel -n "__fish_seen_subcommand_from model; and __fish_seen_subcommand_from set" -a "gemma2:2b" -d "Ultraligero de Google, excelente en explicaciones (~1.6GB)"
complete -c nacel -n "__fish_seen_subcommand_from model; and __fish_seen_subcommand_from set" -a "qwen2.5-coder:1.5b" -d "Consumo mínimo para RAM ajustada (~1.0GB)"
complete -c nacel -n "__fish_seen_subcommand_from model; and __fish_seen_subcommand_from set" -a "qwen2.5-coder:14b" -d "Máxima profundidad lógica y arquitectura (~9.0GB)"

# Subcomandos de lang
complete -c nacel -n "__fish_seen_subcommand_from lang" -a "es" -d "Español / Spanish"
complete -c nacel -n "__fish_seen_subcommand_from lang" -a "en" -d "English / Inglés"

# Compatibilidad con alias dilix
complete -c dilix -w nacel
