# ==============================================================================
# NACEL BASH PLUGIN
# Asistente Lógico de Terminal, Copiloto de IA y Diagnóstico Inteligente.
# Soporte nativo para GNU Bash en macOS, Linux y WSL2.
# ==============================================================================

# 1. Resolución dinámica del directorio del plugin
NACEL_BASH_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"

if [[ ! -f "$NACEL_BASH_DIR/nacel.py" ]]; then
  if [[ -f "$HOME/nacel/nacel.py" ]]; then
    NACEL_BASH_DIR="$HOME/nacel"
  elif [[ -f "$HOME/.nacel/nacel.py" ]]; then
    NACEL_BASH_DIR="$HOME/.nacel"
  elif [[ -f "$HOME/.local/bin/nacel" ]]; then
    NACEL_BASH_DIR="$HOME/.local/bin"
  fi
fi

export __NACEL_SCRIPT="${NACEL_BASH_DIR}/nacel.py"

# Si el usuario definió DILIX_MODEL previamente y no NACEL_MODEL, sincronizarlo
if [[ -n "$DILIX_MODEL" && -z "$NACEL_MODEL" ]]; then
  export NACEL_MODEL="$DILIX_MODEL"
fi

# Modos ante error: "ask", "auto", "hint"
export NACEL_AUTO_MODE="${NACEL_AUTO_MODE:-${DILIX_AUTO_MODE:-ask}}"

# ==============================================================================
# 2. FUNCIONES INTERNAS
# ==============================================================================

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

__nacel_run_action() {
  local action_type="$1"
  local cmd="$2"

  case "$action_type" in
    EXEC)
      if [[ -n "$cmd" ]]; then
        history -s "$cmd"
        echo -e "\033[1;32m▶ Running / Ejecutando:\033[0m $cmd"
        eval "$cmd"
      fi
      ;;
    MODIFY)
      if [[ -n "$cmd" ]]; then
        history -s "$cmd"
        echo -e "\033[1;36m▶ Comando sugerido (añadido al historial):\033[0m $cmd"
        echo -e "\033[2mPulsa ↑ (flecha arriba) para editar o presiona Enter para ejecutar:\033[0m"
        read -e -i "$cmd" -p "❯ " edited_cmd
        if [[ -n "$edited_cmd" ]]; then
          history -s "$edited_cmd"
          eval "$edited_cmd"
        fi
      fi
      ;;
    CANCEL|*)
      ;;
  esac
}

# ==============================================================================
# 3. COMANDOS PRINCIPALES (ask, fix, nacel)
# ==============================================================================

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

  # Únicamente actuar cuando sea un error
  if [[ "${exit_code:-0}" -eq 0 && -z "$user_extra" ]]; then
    local lang=$(__nacel_get_lang)
    if [[ "$lang" == "en" ]]; then
      echo -e "\033[1;32m✔ The previous command ('$target_cmd') completed successfully with exit code 0. No error detected to fix.\033[0m"
    else
      echo -e "\033[1;32m✔ El comando previo ('$target_cmd') terminó con éxito (código 0). No hay ningún error para corregir.\033[0m"
    fi
    return 0
  fi

  __NACEL_CMD_ACTIVE=""

  local output
  output=$(python3 "$__NACEL_SCRIPT" fix "$target_cmd" "$exit_code" "$user_extra")
  local action="${output%%:*}"
  local cmd="${output#*:}"
  __nacel_run_action "$action" "$cmd"
}

nacel() {
  local nacel_py="$__NACEL_SCRIPT"

  if [[ $# -eq 0 ]]; then
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
    hardware|hw|specs)
      shift
      python3 "$nacel_py" hardware "$@"
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

# Alias y compatibilidad retrospectiva
alias nacel-menu="nacel menu"
alias nacel-options="nacel menu"
alias nacel-help="nacel help"
alias dilix="nacel"
alias dilix-menu="nacel menu"
alias dilix-options="nacel menu"
alias dilix-help="nacel help"

# ==============================================================================
# 4. ATAJOS DE TECLADO INTERACTIVOS (Readline)
# ==============================================================================
if [[ $- == *i* ]]; then
  bind -x '"\C-g": fix' 2>/dev/null
fi

# ==============================================================================
# 5. HOOK AUTOMÁTICO EN BASH (PROMPT_COMMAND)
# ==============================================================================
__nacel_bash_prompt_cmd() {
  local last_code=$?

  local last_cmd
  last_cmd=$(HISTTIMEFORMAT= history 1 2>/dev/null | sed -e 's/^[ ]*[0-9]*[ ]*//')

  if [[ -n "$last_cmd" && "$last_cmd" != fix* && "$last_cmd" != ask* && "$last_cmd" != nacel* && "$last_cmd" != dilix* && "$last_cmd" != __nacel* ]]; then
    export __NACEL_LAST_CMD="$last_cmd"
    export __NACEL_LAST_CODE=$last_code

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
            if read -t 5 -n 1 reply 2>/dev/null; then
              echo ""
              if [[ "$reply" == "y" || "$reply" == "Y" || "$reply" == "s" || "$reply" == "S" ]]; then
                fix
              fi
            else
              echo ""
            fi
            ;;
          hint|*)
            echo -e "\033[31m╭─ ❌ Failed with exit code $last_code\033[0m \033[33m•\033[0m \033[36mType \033[1mnacel\033[0m\033[36m or \033[1mfix\033[0m\033[36m to analyze or press \033[1m[Ctrl+G]\033[0m"
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
            if read -t 5 -n 1 reply 2>/dev/null; then
              echo ""
              if [[ "$reply" == "s" || "$reply" == "S" || "$reply" == "y" || "$reply" == "Y" ]]; then
                fix
              fi
            else
              echo ""
            fi
            ;;
          hint|*)
            echo -e "\033[31m╭─ ❌ Falló con código $last_code\033[0m \033[33m•\033[0m \033[36mEscribe \033[1mnacel\033[0m\033[36m o \033[1mfix\033[0m\033[36m para analizar o pulsa \033[1m[Ctrl+G]\033[0m"
            ;;
        esac
      fi
    fi
  fi
}

if [[ -z "$PROMPT_COMMAND" ]]; then
  PROMPT_COMMAND="__nacel_bash_prompt_cmd"
elif [[ "$PROMPT_COMMAND" != *"__nacel_bash_prompt_cmd"* ]]; then
  PROMPT_COMMAND="__nacel_bash_prompt_cmd; $PROMPT_COMMAND"
fi

# ==============================================================================
# 6. AUTOCOMPLETADO EN BASH
# ==============================================================================
_nacel_bash_complete() {
  local cur prev
  cur="${COMP_WORDS[COMP_CWORD]}"
  prev="${COMP_WORDS[COMP_CWORD-1]}"

  local subcommands="menu chat ask fix explain debug hardware model lang help"
  local model_subcommands="set auto recommend list status"

  if [[ $COMP_CWORD -eq 1 ]]; then
    COMPREPLY=( $(compgen -W "$subcommands" -- "$cur") )
  elif [[ $COMP_CWORD -eq 2 && "$prev" == "model" ]]; then
    COMPREPLY=( $(compgen -W "$model_subcommands" -- "$cur") )
  elif [[ $COMP_CWORD -eq 2 && "$prev" == "lang" ]]; then
    COMPREPLY=( $(compgen -W "es en" -- "$cur") )
  fi
}
complete -F _nacel_bash_complete nacel dilix
