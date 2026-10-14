#!/usr/bin/env bash
# ==============================================================================
# Nacel AI - Standalone Installer / Instalador Autónomo
# Copiloto de Terminal y Asistente de IA Local (Ollama)
# ==============================================================================

set -e

NACEL_DIR="${NACEL_DIR:-$HOME/.nacel}"
NACEL_BIN_DIR="$HOME/.local/bin"
NACEL_CONFIG_DIR="$HOME/.config/nacel"
CONFIG_FILE="$NACEL_CONFIG_DIR/config.json"

# Colores ANSI
BOLD="\033[1m"
CYAN="\033[36m"
MAGENTA="\033[35m"
GREEN="\033[32m"
YELLOW="\033[33m"
RED="\033[31m"
DIM="\033[2m"
RESET="\033[0m"

echo -e "${CYAN}╭───────────────────────────────────────────────────────────╮${RESET}"
echo -e "${CYAN}│${RESET}  ${BOLD}${MAGENTA}✨ Nacel AI${RESET} - Asistente de Terminal y Copiloto Local     ${CYAN}│${RESET}"
echo -e "${CYAN}╰───────────────────────────────────────────────────────────╯${RESET}\n"

# 1. Detección de Sistema Operativo
OS_TYPE="linux"
if [[ "$OSTYPE" == "darwin"* ]]; then
  OS_TYPE="macos"
elif grep -qi "microsoft" /proc/version 2>/dev/null || grep -qi "wsl" /proc/version 2>/dev/null; then
  OS_TYPE="wsl2"
fi

echo -e "${CYAN}▶${RESET} Sistema detectado: ${BOLD}${OS_TYPE}${RESET}"

# 2. Verificar Python 3
if ! command -v python3 &>/dev/null; then
  echo -e "${RED}❌ Error: python3 no está instalado.${RESET}"
  echo -e "Por favor instala Python 3 para continuar:"
  if [[ "$OS_TYPE" == "macos" ]]; then
    echo -e "  brew install python3"
  elif command -v pacman &>/dev/null; then
    echo -e "  sudo pacman -S python"
  elif command -v apt &>/dev/null; then
    echo -e "  sudo apt update && sudo apt install -y python3"
  fi
  exit 1
fi

# 3. Preparar directorios
mkdir -p "$NACEL_BIN_DIR"
mkdir -p "$NACEL_CONFIG_DIR"

SCRIPT_SRC_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Si se ejecuta desde un clon local o si se instala directamente
if [[ -f "$SCRIPT_SRC_DIR/nacel.py" ]]; then
  INSTALL_DIR="$SCRIPT_SRC_DIR"
else
  # Si se instala via curl, clonar en ~/.nacel
  INSTALL_DIR="$NACEL_DIR"
  if [[ -d "$INSTALL_DIR/.git" ]]; then
    echo -e "${CYAN}▶${RESET} Actualizando repositorio Nacel en ${INSTALL_DIR}..."
    git -C "$INSTALL_DIR" pull --quiet
  else
    echo -e "${CYAN}▶${RESET} Descargando Nacel en ${INSTALL_DIR}..."
    git clone --depth 1 https://github.com/dannielnavas/nacel.git "$INSTALL_DIR"
  fi
fi

# 4. Crear ejecutable en ~/.local/bin/nacel
chmod +x "$INSTALL_DIR/nacel.py"
ln -sf "$INSTALL_DIR/nacel.py" "$NACEL_BIN_DIR/nacel"
echo -e "${GREEN}✔${RESET} Ejecutable instalado en: ${BOLD}$NACEL_BIN_DIR/nacel${RESET}"

# Asegurar que ~/.local/bin está en el PATH
if [[ ":$PATH:" != *":$NACEL_BIN_DIR:"* ]]; then
  echo -e "${YELLOW}⚠️ Aviso:${RESET} $NACEL_BIN_DIR no parece estar en tu PATH actual."
  echo -e "  Añade 'export PATH=\"\$HOME/.local/bin:\$PATH\"' a tu ~/.zshrc o ~/.bashrc."
fi

# 5. Detección Inteligente de Hardware y Configuración del Mejor Modelo
echo -e "\n${CYAN}▶${RESET} Analizando especificaciones de tu equipo para asignar el modelo óptimo..."

# Ejecutar el asistente de modelo inteligente de Nacel
if ! python3 "$INSTALL_DIR/nacel.py" setup-model "$@"; then
  echo -e "${YELLOW}⚠️ Advertencia: El asistente de modelo tuvo un aviso. Aplicando configuración de respaldo...${RESET}"
  
  # Fallback en Bash puro si python3 fallase
  FALLBACK_MODEL="qwen2.5-coder:7b"
  if [[ "$OS_TYPE" == "macos" ]]; then
    MEM_BYTES=$(sysctl -n hw.memsize 2>/dev/null || echo 0)
    RAM_GB=$(( MEM_BYTES / 1024 / 1024 / 1024 ))
    ARCH=$(uname -m)
    if [[ "$ARCH" != "arm64" && $RAM_GB -lt 8 ]]; then
      FALLBACK_MODEL="qwen2.5-coder:3b"
    fi
  else
    MEM_KB=$(grep MemTotal /proc/meminfo 2>/dev/null | awk '{print $2}')
    RAM_GB=$(( MEM_KB / 1024 / 1024 ))
    if [[ $RAM_GB -lt 6 ]]; then
      FALLBACK_MODEL="qwen2.5-coder:1.5b"
    elif [[ $RAM_GB -lt 12 ]] && ! command -v nvidia-smi &>/dev/null; then
      FALLBACK_MODEL="qwen2.5-coder:3b"
    fi
  fi

  if [[ ! -f "$CONFIG_FILE" ]]; then
    echo -e "{\n  \"lang\": \"es\",\n  \"model\": \"$FALLBACK_MODEL\"\n}" > "$CONFIG_FILE"
  fi
  echo -e "${GREEN}✔${RESET} Modelo de respaldo asignado: ${BOLD}$FALLBACK_MODEL${RESET}"
fi

# 6. Integración con Zsh si existe ~/.zshrc
if [[ -f "$HOME/.zshrc" ]]; then
  if ! grep -q "nacel.plugin.zsh" "$HOME/.zshrc"; then
    echo -e "\n# Nacel AI Plugin" >> "$HOME/.zshrc"
    echo -e "fpath=(\"$INSTALL_DIR\" \$fpath)" >> "$HOME/.zshrc"
    echo -e "source \"$INSTALL_DIR/nacel.plugin.zsh\"" >> "$HOME/.zshrc"
    echo -e "${GREEN}✔${RESET} Integración añadida a ~/.zshrc"
  else
    echo -e "${GREEN}✔${RESET} Integración con ~/.zshrc ya configurada."
  fi
fi

# 7. Resumen de configuración
ACTIVE_MODEL="qwen2.5-coder:7b"
if [[ -f "$CONFIG_FILE" ]]; then
  DETECTED_CFG_MODEL=$(grep -o '"model": *"[^"]*"' "$CONFIG_FILE" 2>/dev/null | cut -d'"' -f4)
  if [[ -n "$DETECTED_CFG_MODEL" ]]; then
    ACTIVE_MODEL="$DETECTED_CFG_MODEL"
  fi
fi

echo -e "\n${GREEN}════════════════════════════════════════════════════════════${RESET}"
echo -e "${BOLD}${MAGENTA}✨ Nacel instalado con éxito.${RESET}"
echo -e "Modelo activo configurado: ${CYAN}${BOLD}${ACTIVE_MODEL}${RESET}"
echo -e "Comandos disponibles:"
echo -e "  • ${CYAN}nacel${RESET}               -> Chat interactivo o reparar último fallo"
echo -e "  • ${CYAN}ask \"<consulta>\"${RESET}    -> Sugiere comandos de terminal"
echo -e "  • ${CYAN}fix${RESET} (o ${BOLD}Ctrl+G${RESET})    -> Diagnostica y corrige el último comando fallido"
echo -e "  • ${CYAN}nacel menu${RESET}          -> Menú interactivo con todas las opciones"
echo -e "  • ${CYAN}nacel hardware${RESET}      -> Ver diagnóstico de hardware de tu equipo"
echo -e "  • ${CYAN}nacel model auto${RESET}    -> Auto-ajustar modelo según tu hardware"
echo -e "  • ${CYAN}nacel model set <m>${RESET} -> Cambia de modelo en cualquier momento"
echo -e "${GREEN}════════════════════════════════════════════════════════════${RESET}\n"
echo -e "Reinicia tu terminal o ejecuta: ${BOLD}source ~/.zshrc${RESET}"
