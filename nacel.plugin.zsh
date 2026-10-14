# ==============================================================================
# NACEL ZSH PLUGIN
# Asistente Lógico de Terminal, Copiloto de IA y Diagnóstico Inteligente.
# Soporte nativo para: macOS, CachyOS / Arch Linux, Ubuntu / Debian y WSL2.
# ==============================================================================

# 1. Resolución dinámica del directorio del plugin
0="${${ZERO:-${0:#$ZSH_ARGZERO}}:-${(%):-%N}}"
0="${${(M)0:#/*}:-$PWD/$0}"
NACEL_PLUGIN_DIR="${0:A:h}"

# Validar ubicación de nacel.py con fallbacks seguros
if [[ ! -f "$NACEL_PLUGIN_DIR/nacel.py" ]]; then
  if [[ -f "$HOME/dotfiles/zsh/plugins/nacel/nacel.py" ]]; then
    NACEL_PLUGIN_DIR="$HOME/dotfiles/zsh/plugins/nacel"
  elif [[ -f "$HOME/nacel/nacel.py" ]]; then
    NACEL_PLUGIN_DIR="$HOME/nacel"
  elif [[ -f "$HOME/.local/bin/nacel" ]]; then
    NACEL_PLUGIN_DIR="$HOME/.local/bin"
  fi
fi

export __NACEL_SCRIPT="${NACEL_PLUGIN_DIR}/nacel.py"
export NACEL_MODEL="${NACEL_MODEL:-${DILIX_MODEL:-gemma2:2b}}"

# Modos de comportamiento cuando un comando da error:
#   "ask"  -> Pregunta si deseas que Nacel analice el error [s/N] / [y/N]
#   "auto" -> Analiza automáticamente con Nacel cada vez que un comando falle
#   "hint" -> Muestra barra sutil indicando usar 'fix', 'nacel' o Ctrl+G
export NACEL_AUTO_MODE="${NACEL_AUTO_MODE:-${DILIX_AUTO_MODE:-ask}}"

# Agregar directorio del plugin a fpath para autocompletado si no está presente
if [[ -d "$NACEL_PLUGIN_DIR" ]]; then
  fpath=("$NACEL_PLUGIN_DIR" $fpath)
fi

# ==============================================================================
# 2. FUNCIONES INTERNAS Y UTILIDADES
# ==============================================================================

# Obtiene el idioma activo (es / en) configurado en Nacel
__nacel_get_lang() {
  if [[ -n "$NACEL_LANG" ]]; then
    echo "$NACEL_LANG"
    return
  fi
  local cfg="$HOME/.config/nacel/config.json"
  if [[ -f "$cfg" ]]; then
    local l=$(grep -o '"lang": *"[^"]*"' "$cfg" 2>/dev/null | cut -d'"' -f4)
    if [[ -n "$l" ]]; then
      echo "$l"
      return
    fi
  fi
  echo "es"
}

# Ejecuta o inserta el comando según la acción elegida por el usuario
__nacel_run_action() {
  local action_type="$1"
  local cmd="$2"

  case "$action_type" in
    EXEC)
      if [[ -n "$cmd" ]]; then
        print -s "$cmd" # Agrega al historial de Zsh
        echo -e "\033[1;32m▶ Running / Ejecutando:\033[0m $cmd"
        eval "$cmd"
      fi
      ;;
    MODIFY)
      if [[ -n "$cmd" ]]; then
        print -z "$cmd" # Carga el comando en el prompt para editarlo
      fi
      ;;
    CANCEL|*)
      ;;
  esac
}

# ==============================================================================
# 3. COMANDOS PRINCIPALES (ask, fix, nacel)
# ==============================================================================

# Consulta en lenguaje natural para obtener comandos
ask() {
  if [[ $# -eq 0 ]]; then
    local lang=$(__nacel_get_lang)
    if [[ "$lang" == "en" ]]; then
      echo -e "\033[1;33mUsage:\033[0m ask \"your natural language query\""
      echo -e "Example: ask \"how to list listening ports\""
    else
      echo -e "\033[1;33mUso:\033[0m ask \"tu consulta aquí\""
      echo -e "Ejemplo: ask \"como ver puertos en uso\""
    fi
    return 1
  fi

  local output
  output=$(python3 "$__NACEL_SCRIPT" ask "$@")
  local action="${output%%:*}"
  local cmd="${output#*:}"
  __nacel_run_action "$action" "$cmd"
}

# Diagnóstico y corrección lógica de errores para comandos fallidos
fix() {
  local target_cmd="${__NACEL_LAST_CMD:-}"
  local exit_code="${__NACEL_LAST_CODE:-1}"
  local user_extra="$*"

  if [[ -z "$target_cmd" && -z "$user_extra" ]]; then
    local lang=$(__nacel_get_lang)
    if [[ "$lang" == "en" ]]; then
      echo -e "\033[1;33m💡 No recent failed commands for Nacel to analyze.\033[0m"
    else
      echo -e "\033[1;33m💡 No hay comandos fallidos recientes para que Nacel analice.\033[0m"
    fi
    return 0
  fi

  # Reset del flag para evitar bucles
  __NACEL_CMD_ACTIVE=""

  local output
  output=$(python3 "$__NACEL_SCRIPT" fix "$target_cmd" "$exit_code" "$user_extra")
  local action="${output%%:*}"
  local cmd="${output#*:}"
  __nacel_run_action "$action" "$cmd"
}

# Comando multifunción 'nacel': chat, explain, debug, fix, lang, model y consultas
nacel() {
  local nacel_py="$__NACEL_SCRIPT"

  if [[ $# -eq 0 ]]; then
    # Si el comando previo falló, ofrece repararlo; si no, inicia chat interactivo directo
    if [[ -n "$__NACEL_LAST_CMD" && "${__NACEL_LAST_CODE:-0}" -ne 0 ]]; then
      fix
    else
      python3 "$nacel_py" chat
    fi
    return
  fi

  case "$1" in
    menu|options|opciones)
      shift
      python3 "$nacel_py" menu "$@"
      ;;
    lang|language|idioma)
      shift
      python3 "$nacel_py" lang "$@"
      ;;
    model|models|status|info)
      shift
      python3 "$nacel_py" model "$@"
      ;;
    explain|code)
      shift
      python3 "$nacel_py" explain "$@"
      ;;
    debug)
      shift
      python3 "$nacel_py" debug "$@"
      ;;
    chat)
      shift
      python3 "$nacel_py" chat "$@"
      ;;
    fix)
      shift
      fix "$@"
      ;;
    ask)
      shift
      ask "$@"
      ;;
    help|--help|-h|commands|comandos)
      python3 "$nacel_py" help "$@"
      ;;
    *)
      local output
      output=$(python3 "$nacel_py" query "$@")
      local action="${output%%:*}"
      local cmd="${output#*:}"
      if [[ "$action" == "EXEC" || "$action" == "MODIFY" || "$action" == "CANCEL" ]]; then
        __nacel_run_action "$action" "$cmd"
      fi
      ;;
  esac
}

# Alias y compatibilidad con Dilix
alias nacel-menu="nacel menu"
alias nacel-options="nacel menu"
alias nacel-help="nacel help"

# Compatibilidad retrospectiva (backward compatibility)
alias dilix="nacel"
alias dilix-menu="nacel menu"
alias dilix-options="nacel menu"
alias dilix-help="nacel help"

# ==============================================================================
# 4. ATAJOS DE TECLADO INTERACTIVOS (ZLE)
# ==============================================================================
if [[ -o interactive ]]; then
  __nacel_fix_widget() {
    zle -I
    fix
    zle reset-prompt
  }
  zle -N __nacel_fix_widget
  bindkey '^G' __nacel_fix_widget
fi

# ==============================================================================
# 5. HOOKS AUTOMÁTICOS DE ZSH (preexec / precmd)
# ==============================================================================
__nacel_preexec() {
  # No registrar llamadas al propio Nacel o Dilix
  if [[ "$1" != fix* && "$1" != ask* && "$1" != nacel* && "$1" != dilix* && "$1" != __nacel* ]]; then
    export __NACEL_LAST_CMD="$1"
    export __NACEL_CMD_ACTIVE=1
  fi
}

__nacel_precmd() {
  local last_code=$?

  if [[ -n "$__NACEL_CMD_ACTIVE" ]]; then
    export __NACEL_LAST_CODE=$last_code
    export __NACEL_CMD_ACTIVE=""

    # Si el comando falló (exit != 0) y no fue cancelado con Ctrl+C (130) ni suspendido (148)
    if [[ $last_code -ne 0 && $last_code -ne 130 && $last_code -ne 148 ]]; then
      local mode="${NACEL_AUTO_MODE:-ask}"
      local lang=$(__nacel_get_lang)

      if [[ "$lang" == "en" ]]; then
        case "$mode" in
          auto)
            echo ""
            fix
            ;;
          ask)
            echo ""
            echo -en "\033[31m╭─ ❌ Failed ($last_code)\033[0m \033[33m•\033[0m \033[1;36mAnalyze with Nacel? [y/N] (or press Ctrl+G):\033[0m "
            local reply
            if read -t 5 -k 1 reply 2>/dev/null; then
              echo ""
              if [[ "$reply" == "y" || "$reply" == "Y" || "$reply" == "s" || "$reply" == "S" ]]; then
                fix
              fi
            else
              echo ""
            fi
            ;;
          hint|*)
            print -P "%F{red}╭─ ❌ Failed with exit code $last_code%f %F{yellow}•%f %F{cyan}Type %Bnacel%b or %Bfix%b to analyze or press %B[Ctrl+G]%b%f"
            ;;
        esac
      else
        case "$mode" in
          auto)
            echo ""
            fix
            ;;
          ask)
            echo ""
            echo -en "\033[31m╭─ ❌ Falló ($last_code)\033[0m \033[33m•\033[0m \033[1;36m¿Analizar con Nacel? [s/N] (o pulsa Ctrl+G):\033[0m "
            local reply
            if read -t 5 -k 1 reply 2>/dev/null; then
              echo ""
              if [[ "$reply" == "s" || "$reply" == "S" || "$reply" == "y" || "$reply" == "Y" ]]; then
                fix
              fi
            else
              echo ""
            fi
            ;;
          hint|*)
            print -P "%F{red}╭─ ❌ Falló con código $last_code%f %F{yellow}•%f %F{cyan}Escribe %Bnacel%b o %Bfix%b para analizar o pulsa %B[Ctrl+G]%b%f"
            ;;
        esac
      fi
    fi
  fi
}

autoload -Uz add-zsh-hook
add-zsh-hook preexec __nacel_preexec
add-zsh-hook precmd __nacel_precmd
