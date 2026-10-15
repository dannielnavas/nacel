#!/usr/bin/env python3
"""
Nacel - Asistente Lógico de Terminal y Copiloto de Programación para Zsh & Bash.
Soporte Bilingüe: Español (es) & Inglés (en).
Configuración persistente en ~/.config/nacel/config.json.
"""

import sys
import os
import re
import json
import urllib.request
import urllib.error
import subprocess
import platform
import shutil
import time
import select

try:
    import readline
except ImportError:
    pass

# ==============================================================================
# CONFIGURACIÓN Y CONSTANTES
# ==============================================================================
CONFIG_DIR = os.path.expanduser("~/.config/nacel")
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")

# Códigos de Color ANSI
CYAN = "\033[36m"
MAGENTA = "\033[35m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
RED = "\033[31m"
BLUE = "\033[34m"
BOLD = "\033[1m"
DIM = "\033[2m"
ITALIC = "\033[3m"
RESET = "\033[0m"

# Detección y limpieza de buffers de terminal
ANSI_ESCAPE_REGEX = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])|\x1b\([B0]')
PROMPT_CHARS = {'❯', '$', '#', '%', '➜', '>', '⚡', '»'}

# ==============================================================================
# INTERNACIONALIZACIÓN (I18N) - ESPAÑOL & INGLÉS
# ==============================================================================
TEXTS = {
    "es": {
        "persona": (
            "Eres Nacel, un asistente inteligente de terminal, copiloto de programación y experto en ingeniería de software multiplataforma (con soporte de primera clase para WSL2, CachyOS / Arch Linux, Ubuntu / Debian y macOS).\n"
            "Directrices de entorno:\n"
            "- Identifica y adapta tus respuestas según el sistema operativo del usuario.\n"
            "- En macOS: aprovecha Homebrew (brew), launchctl, pbcopy y utilidades de Apple Silicon / Intel.\n"
            "- En CachyOS / Arch Linux: utiliza pacman, paru/yay, kernels optimizados y repositorios de CachyOS.\n"
            "- En Ubuntu / Debian: utiliza apt, dpkg, systemd y convenciones estándar de Debian/Ubuntu.\n"
            "- En WSL2: maneja la interoperabilidad con Windows (/mnt/c, wslpath, wslview, clip.exe, explorer.exe).\n"
            "- Eres sumamente analítico, cortés, sereno, didáctico y perspicaz.\n"
            "- Responde SIEMPRE en ESPAÑOL de forma fluida, natural, concisa y elegante.\n"
            "- Vas directo a la raíz del problema con rigor técnico y claridad didáctica.\n"
        ),
        "box_explain": "Análisis Lógico de Código: {source}",
        "box_debug": "Depuración Lógica y Causa Raíz",
        "box_fix": "Diagnóstico y Solución de Error",
        "box_ask": "Sugerencia de Comando",
        "box_chat": "Canal de Comunicación Directo",
        "box_query": "Análisis Lógico",
        "chat_welcome_1": "Nacel a su servicio.",
        "chat_welcome_2": "Puedo explicar código, depurar errores y sugerir comandos de terminal.",
        "chat_welcome_3": "Escribe 'q' o 'exit' para salir, 'clear' para limpiar pantalla.",
        "chat_farewell": "Sesión finalizada. ¡Hasta pronto!",
        "chat_session_ended": "Sesión finalizada. ¡Hasta pronto!",
        "menu_action": "Acción:",
        "menu_exec": "Ejecutar",
        "menu_prompt": "En el prompt",
        "menu_copy": "Copiar",
        "menu_quit": "Salir:",
        "copied_ok": "✔ Copiado al portapapeles con éxito.",
        "copied_err": "⚠️ No se pudo copiar al portapapeles.",
        "failed_label": "Falló:",
        "cause_label": "Causa lógica:",
        "action_label": "Qué toca hacer:",
        "solution_label": "Solución sugerida:",
        "query_label": "Consulta:",
        "explanation_label": "Explicación:",
        "suggested_label": "Comando sugerido:",
        "ollama_offline": "Ollama no responde en {host}. Inícialo con 'ollama serve' o abre la aplicación.",
        "command_success_no_error": "✔ El comando previo ('{cmd}') terminó con éxito (código 0). No hay ningún error para corregir.",
        "no_error_found": "💡 No hay ningún comando previo registrado para analizar.",
        "no_code_found": "💡 No se detectó código ni contenido para analizar.",
        "no_debug_target": "💡 No se proporcionó ningún mensaje o traza de error para depurar.",
        "stdin_label": "Entrada estándar (stdin)",
        "snippet_label": "Fragmento / Comando",
        "processing_explain": "Procesando estructura y deduciendo funcionamiento con {model}...",
        "processing_debug": "Aislando variables y deduciendo el origen de la anomalía...",
        "processing_fix": "Examinando la anomalía con {model}...",
        "processing_ask": "Consultando {model}...",
    },
    "en": {
        "persona": (
            "You are Nacel, an intelligent terminal assistant, coding copilot, and expert software engineer across platforms (with first-class support for WSL2, CachyOS / Arch Linux, Ubuntu / Debian, and macOS).\n"
            "Environment guidelines:\n"
            "- Identify and tailor your recommendations to the user's specific OS environment.\n"
            "- On macOS: utilize Homebrew (brew), launchctl, pbcopy, and Apple Silicon / Intel paths.\n"
            "- On CachyOS / Arch Linux: prioritize pacman, paru/yay, optimized kernels, and CachyOS repos.\n"
            "- On Ubuntu / Debian: prioritize apt, dpkg, systemd, and Debian/Ubuntu packages.\n"
            "- On WSL2: account for Windows interoperability (/mnt/c, wslpath, wslview, clip.exe, explorer.exe).\n"
            "- You are analytical, courteous, composed, articulate, and perceptive.\n"
            "- ALWAYS respond in ENGLISH in a fluent, natural, concise, and articulate manner.\n"
            "- Address the root cause directly with technical rigor and didactic clarity.\n"
        ),
        "box_explain": "Logical Code Analysis: {source}",
        "box_debug": "Logical Debugging & Root Cause Analysis",
        "box_fix": "Error Diagnosis & Solution",
        "box_ask": "Command Suggestion",
        "box_chat": "Direct Communication Channel",
        "box_query": "Logical Analysis",
        "chat_welcome_1": "Nacel at your service.",
        "chat_welcome_2": "I can explain code, debug errors, and suggest terminal commands.",
        "chat_welcome_3": "Type 'q' or 'exit' to quit, 'clear' to clear screen.",
        "chat_farewell": "Session ended. See you soon!",
        "chat_session_ended": "Session ended. See you soon!",
        "menu_action": "Action:",
        "menu_exec": "Execute",
        "menu_prompt": "In prompt",
        "menu_copy": "Copy",
        "menu_quit": "Quit:",
        "copied_ok": "✔ Copied to clipboard successfully.",
        "copied_err": "⚠️ Could not copy to clipboard.",
        "failed_label": "Failed:",
        "cause_label": "Logical cause:",
        "action_label": "Recommended action:",
        "solution_label": "Suggested solution:",
        "query_label": "Query:",
        "explanation_label": "Explanation:",
        "suggested_label": "Suggested command:",
        "ollama_offline": "Ollama is not responding at {host}. Start it with 'ollama serve' or open the app.",
        "command_success_no_error": "✔ The previous command ('{cmd}') completed successfully with exit code 0. No error detected to fix.",
        "no_error_found": "💡 No recent command registered to analyze.",
        "no_code_found": "💡 No code or content detected to analyze.",
        "no_debug_target": "💡 No error message or trace provided to debug.",
        "stdin_label": "Standard input (stdin)",
        "snippet_label": "Snippet / Command",
        "processing_explain": "Processing structure and deducing mechanics with {model}...",
        "processing_debug": "Isolating variables and deducing the root cause...",
        "processing_fix": "Examining anomaly with {model}...",
        "processing_ask": "Querying {model}...",
    }
}

# ==============================================================================
# GESTIÓN DE CONFIGURACIÓN Y MODELO
# ==============================================================================
def load_config() -> dict:
    if os.path.isfile(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return {}

def save_config(cfg: dict):
    try:
        os.makedirs(CONFIG_DIR, exist_ok=True)
        with open(CONFIG_FILE, "w") as f:
            json.dump(cfg, f, indent=2)
    except Exception as e:
        print_tty(f"{YELLOW}⚠️ No se pudo guardar configuración: {e}{RESET}")

def get_current_model() -> str:
    """Prioridad: NACEL_MODEL > config.json['model'] > DILIX_MODEL > modelo recomendado para el hardware."""
    env_model = os.environ.get("NACEL_MODEL", "").strip()
    if env_model:
        return env_model
    cfg = load_config()
    cfg_model = cfg.get("model", "").strip()
    if cfg_model:
        return cfg_model
    legacy_model = os.environ.get("DILIX_MODEL", "").strip()
    if legacy_model:
        return legacy_model
    try:
        rec = get_model_recommendation()
        return rec.get("recommended_model", "qwen2.5-coder:7b")
    except Exception:
        return "qwen2.5-coder:7b"

def get_ollama_host() -> str:
    return os.environ.get("NACEL_HOST", os.environ.get("OLLAMA_HOST", "http://localhost:11434"))

def get_current_language() -> str:
    """Obtiene el idioma activo: prioridad NACEL_LANG > DILIX_LANG > config.json."""
    env_lang = os.environ.get("NACEL_LANG", os.environ.get("DILIX_LANG", "")).lower().strip()
    if env_lang in ("es", "en"):
        return env_lang
    cfg = load_config()
    cfg_lang = cfg.get("lang", "").lower().strip()
    if cfg_lang in ("es", "en"):
        return cfg_lang
    return ""

def ensure_language() -> str:
    """Si no hay idioma configurado, pide al usuario seleccionarlo por primera vez y lo guarda."""
    lang = get_current_language()
    if lang:
        return lang

    print_tty()
    print_tty(f"{CYAN}╭─ {BOLD}{MAGENTA}✨ Nacel{RESET} {CYAN}• {BOLD}Configuración Inicial / Initial Setup{RESET} {CYAN}" + "─" * 16 + f"{RESET}")
    print_tty(f"{CYAN}│{RESET} Selecciona tu idioma preferido / Select your preferred language:")
    print_tty(f"{CYAN}│{RESET}   {CYAN}[1]{RESET} Español  (Spanish - Predeterminado)")
    print_tty(f"{CYAN}│{RESET}   {CYAN}[2]{RESET} English  (Inglés)")
    print_tty(f"{CYAN}╰" + "─" * 65 + f"{RESET}")
    print_tty(f" {BOLD}Opción / Choice [1/2] (Enter para Español):{RESET} ", end="")

    choice = read_key().strip()
    print_tty()

    selected = "en" if choice in ("2", "en", "english") else "es"

    cfg = load_config()
    cfg["lang"] = selected
    if "model" not in cfg:
        cfg["model"] = get_current_model()
    save_config(cfg)

    if selected == "en":
        print_tty(f" {GREEN}✔ Language configured to English.{RESET} Saved in ~/.config/nacel/config.json\n")
    else:
        print_tty(f" {GREEN}✔ Idioma configurado a Español.{RESET} Guardado en ~/.config/nacel/config.json\n")

    return selected

def t(key: str, **kwargs) -> str:
    lang = get_current_language() or "es"
    text = TEXTS.get(lang, TEXTS["es"]).get(key, TEXTS["es"].get(key, key))
    if kwargs:
        try:
            return text.format(**kwargs)
        except Exception:
            return text
    return text

# ==============================================================================
# ENTORNO Y TERMINAL UTILITIES
# ==============================================================================
def print_tty(msg="", end="\n"):
    try:
        with open("/dev/tty", "w") as tty:
            tty.write(msg + end)
            tty.flush()
    except Exception:
        sys.stderr.write(msg + end)
        sys.stderr.flush()

def read_key(timeout=None) -> str:
    """Lee una sola pulsación de tecla, con soporte para timeout y /dev/tty."""
    # 1. Intentar /dev/tty primero (funciona incluso si stdin está redirigido o pipeado via curl)
    try:
        with open("/dev/tty", "r") as tty:
            import tty as tty_module
            import termios
            fd = tty.fileno()
            old_settings = termios.tcgetattr(fd)
            try:
                tty_module.setraw(fd)
                if timeout is not None and timeout > 0:
                    r, _, _ = select.select([tty], [], [], timeout)
                    if not r:
                        return "\r"
                ch = tty.read(1)
                if ch == "\x1b":
                    r, _, _ = select.select([tty], [], [], 0.05)
                    if r:
                        tty.read(2)
                        return "ESC"
                    return "q"
                return ch
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    except Exception:
        pass

    # 2. Si /dev/tty falla o no existe, intentar stdin
    if sys.stdin.isatty():
        try:
            line = input()
            return line.strip()[:1] if line.strip() else "\r"
        except Exception:
            return "\r"
    else:
        try:
            ch = sys.stdin.read(1)
            return ch if ch else "\r"
        except Exception:
            return "\r"

def input_tty(prompt="") -> str:
    """Lee una línea de texto del usuario asegurando acceso a la terminal /dev/tty."""
    if prompt:
        print_tty(prompt, end="")
    try:
        with open("/dev/tty", "r") as tty:
            return tty.readline().strip()
    except Exception:
        try:
            return input().strip()
        except Exception:
            return ""

def clean_command(cmd: str) -> str:
    cmd = cmd.strip()
    if cmd.startswith("```"):
        lines = cmd.splitlines()
        if len(lines) >= 2 and lines[-1].startswith("```"):
            cmd = "\n".join(lines[1:-1]).strip()
        else:
            cmd = re.sub(r"^```[a-zA-Z]*\n?", "", cmd).rstrip("`").strip()
    if cmd.startswith("`") and cmd.endswith("`") and len(cmd) > 1:
        cmd = cmd[1:-1].strip()
    return cmd

def is_wsl() -> bool:
    try:
        uname_rel = platform.uname().release.lower()
        return "microsoft" in uname_rel or "wsl" in uname_rel or os.path.exists("/mnt/c/Windows")
    except Exception:
        return False

def copy_to_clipboard(text: str) -> bool:
    system = platform.system().lower()
    wsl_env = is_wsl()
    try:
        if system == "darwin":
            p = subprocess.Popen(["pbcopy"], stdin=subprocess.PIPE)
            p.communicate(text.encode("utf-8"))
            return p.returncode == 0
        elif wsl_env and subprocess.run(["which", "clip.exe"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode == 0:
            p = subprocess.Popen(["clip.exe"], stdin=subprocess.PIPE)
            p.communicate(text.encode("utf-8"))
            return p.returncode == 0
        else:
            if subprocess.run(["which", "wl-copy"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode == 0:
                p = subprocess.Popen(["wl-copy"], stdin=subprocess.PIPE)
                p.communicate(text.encode("utf-8"))
                return p.returncode == 0
            elif subprocess.run(["which", "xclip"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode == 0:
                p = subprocess.Popen(["xclip", "-selection", "clipboard"], stdin=subprocess.PIPE)
                p.communicate(text.encode("utf-8"))
                return p.returncode == 0
            elif subprocess.run(["which", "xsel"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode == 0:
                p = subprocess.Popen(["xsel", "--clipboard", "--input"], stdin=subprocess.PIPE)
                p.communicate(text.encode("utf-8"))
                return p.returncode == 0
            elif wsl_env:
                p = subprocess.Popen(["clip.exe"], stdin=subprocess.PIPE)
                p.communicate(text.encode("utf-8"))
                return p.returncode == 0
    except Exception:
        pass
    return False

def get_os_info() -> str:
    system = platform.system().lower()
    wsl_env = is_wsl()

    if system == "darwin":
        return f"macOS ({platform.mac_ver()[0]})"
    elif system == "linux" or wsl_env:
        distro_str = "Linux"
        if os.path.exists("/etc/os-release"):
            try:
                with open("/etc/os-release") as f:
                    data = {}
                    for line in f:
                        if "=" in line:
                            k, v = line.strip().split("=", 1)
                            data[k] = v.strip('"')
                    distro = data.get("PRETTY_NAME", data.get("NAME", "Linux"))
                    distro_id = data.get("ID", "").lower()
                    if "cachyos" in distro_id or "cachyos" in distro.lower():
                        distro_str = "CachyOS (Arch-based, package manager: paru/pacman, kernel: linux-cachyos)"
                    elif "arch" in distro_id:
                        distro_str = "Arch Linux (package manager: pacman/paru/yay)"
                    elif "ubuntu" in distro_id or "debian" in distro_id:
                        distro_str = f"{distro} (package manager: apt)"
                    else:
                        distro_str = distro
            except Exception:
                pass
        if is_wsl:
            return f"{distro_str} (WSL2 environment on Windows)"
        return distro_str
    return platform.platform()

def check_ollama() -> bool:
    host = get_ollama_host()
    try:
        req = urllib.request.Request(f"{host}/api/tags", headers={"User-Agent": "Nacel/1.0"})
        with urllib.request.urlopen(req, timeout=1.5) as resp:
            return resp.status == 200
    except Exception:
        return False

# ==============================================================================
# DETECCIÓN DE HARDWARE Y RECOMENDACIÓN INTELIGENTE DE MODELOS
# ==============================================================================
def get_system_hardware() -> dict:
    """Detecta las especificaciones clave del hardware (RAM, CPU, GPU/Aceleración, OS, WSL2)."""
    hw = {
        "os": platform.system(),
        "os_name": get_os_info(),
        "arch": platform.machine(),
        "cpu_name": "Procesador genérico",
        "cpu_cores": os.cpu_count() or 1,
        "ram_gb": 0.0,
        "gpu_name": None,
        "vram_gb": 0.0,
        "acceleration": "CPU Multithread",
        "is_wsl": False,
        "is_apple_silicon": False,
    }

    system_lower = platform.system().lower()
    uname_rel = platform.uname().release.lower()
    if system_lower == "linux":
        if "microsoft" in uname_rel or "wsl" in uname_rel or os.path.exists("/mnt/c/Windows"):
            hw["is_wsl"] = True

    # macOS: Detección precisa de Apple Silicon vs Intel Mac
    if system_lower == "darwin":
        try:
            mem = subprocess.check_output(["sysctl", "-n", "hw.memsize"], stderr=subprocess.DEVNULL).decode().strip()
            hw["ram_gb"] = round(int(mem) / (1024**3), 1)
        except Exception:
            pass
        try:
            cpu = subprocess.check_output(["sysctl", "-n", "machdep.cpu.brand_string"], stderr=subprocess.DEVNULL).decode().strip()
            if cpu:
                hw["cpu_name"] = cpu
        except Exception:
            pass
        if hw["arch"] in ("arm64", "aarch64") or "Apple" in hw["cpu_name"]:
            hw["is_apple_silicon"] = True
            hw["gpu_name"] = f"{hw['cpu_name']} (GPU)"
            hw["vram_gb"] = hw["ram_gb"]
            hw["acceleration"] = "Metal (Memoria Unificada Apple Silicon)"
        else:
            hw["acceleration"] = "CPU (Intel Mac)"
    else:
        # Linux / WSL2
        try:
            with open("/proc/meminfo", "r") as f:
                for line in f:
                    if line.startswith("MemTotal:"):
                        kb = int(line.split()[1])
                        hw["ram_gb"] = round(kb / (1024**2), 1)
                        break
        except Exception:
            pass
        try:
            with open("/proc/cpuinfo", "r") as f:
                for line in f:
                    if "model name" in line:
                        hw["cpu_name"] = line.split(":", 1)[1].strip()
                        break
        except Exception:
            pass

    # Verificación de GPU dedicada NVIDIA (Linux nativo y WSL2 con CUDA passthrough)
    if shutil.which("nvidia-smi"):
        try:
            out = subprocess.check_output(
                ["nvidia-smi", "--query-gpu=name,memory.total", "--format=csv,noheader,nounits"],
                stderr=subprocess.DEVNULL
            ).decode().strip()
            if out:
                first = out.splitlines()[0].split(",")
                hw["gpu_name"] = first[0].strip()
                hw["vram_gb"] = round(float(first[1].strip()) / 1024, 1)
                hw["acceleration"] = f"NVIDIA CUDA ({hw['vram_gb']}GB VRAM)"
        except Exception:
            pass

    return hw

def get_installed_ollama_models() -> list:
    """Retorna la lista de modelos descargados actualmente en el servidor Ollama."""
    host = get_ollama_host()
    # 1. API HTTP de Ollama
    try:
        req = urllib.request.Request(f"{host}/api/tags", headers={"User-Agent": "Nacel/1.0"})
        with urllib.request.urlopen(req, timeout=1.5) as resp:
            if resp.status == 200:
                data = json.loads(resp.read().decode())
                return [m.get("name", "") for m in data.get("models", []) if m.get("name")]
    except Exception:
        pass

    # 2. CLI de Ollama como respaldo
    if shutil.which("ollama"):
        try:
            out = subprocess.check_output(["ollama", "list"], stderr=subprocess.DEVNULL).decode().strip()
            lines = out.splitlines()
            models = []
            for line in lines[1:]:
                parts = line.split()
                if parts:
                    models.append(parts[0])
            return models
        except Exception:
            pass
    return []

def get_model_recommendation(hw=None) -> dict:
    """Evalúa el hardware del equipo y selecciona el modelo óptimo con razonamiento técnico."""
    if hw is None:
        hw = get_system_hardware()

    ram = hw.get("ram_gb", 0.0)
    vram = hw.get("vram_gb", 0.0)
    is_apple_silicon = hw.get("is_apple_silicon", False)
    has_nvidia = "CUDA" in hw.get("acceleration", "")

    # Clasificación en Tiers
    if (has_nvidia and vram >= 12.0) or (is_apple_silicon and ram >= 24.0) or (ram >= 32.0):
        tier = "ultra"
        tier_label = "Gama Alta / Máximo Rendimiento"
        rec = "qwen2.5-coder:14b"
        reason = "Tu equipo cuenta con memoria y aceleración de alto nivel para ejecutar modelos de 14B con razonamiento arquitectónico avanzado."
    elif (is_apple_silicon and ram >= 8.0) or (has_nvidia and vram >= 6.0) or (ram >= 14.0):
        tier = "pro"
        tier_label = "Equilibrado / Recomendado (Desarrollo y Terminal)"
        rec = "qwen2.5-coder:7b"
        reason = "El estándar de oro para terminal y copiloto: precisión quirúrgica en bash, git, docker y corrección de sintaxis."
    elif (has_nvidia and vram >= 3.5) or (ram >= 6.0):
        tier = "light"
        tier_label = "Ligero y Rápido (Respuesta instantánea)"
        rec = "qwen2.5-coder:3b"
        reason = "Excelente velocidad y bajo consumo (~2.0GB). Mucho más inteligente que modelos de 1.5B para shell y scripts."
    else:
        tier = "minimal"
        tier_label = "Ultraligero / Recursos limitados"
        rec = "qwen2.5-coder:1.5b"
        reason = "Mínimo consumo (~1.0GB RAM), ideal para equipos con poca memoria sin ralentizar el sistema."

    catalog = [
        {
            "id": "1",
            "model": "qwen2.5-coder:7b",
            "tag": "Recomendado ⭐" if rec == "qwen2.5-coder:7b" else "Potente",
            "desc": "Máxima precisión en bash, sintaxis y corrección de errores (~4.7GB)",
            "min_ram": "8GB+ RAM / VRAM"
        },
        {
            "id": "2",
            "model": "qwen2.5-coder:3b",
            "tag": "Recomendado ⭐" if rec == "qwen2.5-coder:3b" else "Ultrarrápido ⚡",
            "desc": "Respuesta inmediata, excelente equilibrio y bajo consumo (~2.0GB)",
            "min_ram": "4GB - 8GB RAM"
        },
        {
            "id": "3",
            "model": "llama3.2:1b",
            "tag": "Diagnóstico y Errores 🎯" if rec != "llama3.2:1b" else "Recomendado ⭐",
            "desc": "Modelo ultracompacto de Meta (~1.3GB), ágil y muy certero diagnosticando errores",
            "min_ram": "2GB - 4GB RAM"
        },
        {
            "id": "4",
            "model": "gemma2:2b",
            "tag": "Conversacional 💬",
            "desc": "Ultraligero de Google, excelente en español y explicaciones (~1.6GB)",
            "min_ram": "4GB+ RAM"
        },
        {
            "id": "5",
            "model": "qwen2.5-coder:1.5b",
            "tag": "Recomendado ⭐" if rec == "qwen2.5-coder:1.5b" else "Mínimo consumo 🪶",
            "desc": "Consumo mínimo para equipos con muy poca memoria RAM (~1.0GB)",
            "min_ram": "2GB - 4GB RAM"
        },
        {
            "id": "6",
            "model": "qwen2.5-coder:14b",
            "tag": "Recomendado ⭐" if rec == "qwen2.5-coder:14b" else "Experto 🔥",
            "desc": "Máxima profundidad lógica y razonamiento de arquitectura (~9.0GB)",
            "min_ram": "16GB - 24GB+ VRAM"
        }
    ]

    return {
        "hardware": hw,
        "tier": tier,
        "tier_label": tier_label,
        "recommended_model": rec,
        "reason": reason,
        "catalog": catalog
    }

def is_prompt_header(s: str) -> bool:
    s = s.strip()
    if not s:
        return False
    # Encabezados de prompts multilínea (ruta, user@host, rama git, tiempo)
    if (s.startswith("~") or s.startswith("/") or "@" in s) and (" on " in s or " in " in s or "(" in s or "[" in s):
        return True
    if re.match(r"^[a-zA-Z0-9_.-]+@[a-zA-Z0-9_.-]+[: ].*", s):
        return True
    if re.match(r"^(~|/)[a-zA-Z0-9_/.-]*(\s+on\s+|\s+in\s+|\s+\().*", s):
        return True
    return False

def clean_trailing_prompt(filtered: list) -> list:
    while filtered:
        s = filtered[-1].strip()
        if not s:
            filtered.pop()
            continue
        if s in PROMPT_CHARS:
            filtered.pop()
            continue
        if any(s.endswith(p) for p in PROMPT_CHARS) and (s.startswith("~") or s.startswith("/") or "@" in s or is_prompt_header(s)):
            filtered.pop()
            continue
        if is_prompt_header(s):
            filtered.pop()
            continue
        break
    return filtered

def extract_command_output(raw_scrollback: str, last_cmd: str, last_code: str = "1") -> str:
    """
    Aísla con precisión quirúrgica únicamente la salida/traza de error producida por last_cmd:
    1. Limpia secuencias de escape ANSI.
    2. Localiza la invocación de last_cmd buscando de abajo hacia arriba.
    3. Toma las líneas inmediatamente posteriores al comando.
    4. Trunca en el siguiente prompt o banner interactivo de Nacel.
    5. Limpia líneas residuales de prompt.
    """
    if not raw_scrollback or not raw_scrollback.strip():
        return ""

    cleaned = ANSI_ESCAPE_REGEX.sub("", raw_scrollback)
    lines = [l.rstrip() for l in cleaned.splitlines()]

    # Eliminar líneas vacías al final
    while lines and not lines[-1].strip():
        lines.pop()

    if not lines:
        return ""

    cmd_clean = last_cmd.strip()
    cmd_tokens = cmd_clean.split()
    first_token = cmd_tokens[0] if cmd_tokens else ""

    cmd_idx = -1
    # Buscar de abajo hacia arriba la línea donde se ejecutó last_cmd
    for i in range(len(lines) - 1, -1, -1):
        line = lines[i].strip()
        # Ignorar líneas que sean llamadas a fix o nacel
        if line.startswith("fix") or line.startswith("nacel fix") or line == "nacel":
            continue
        if any(line.startswith(f"{p} fix") or line.startswith(f"{p} nacel") for p in PROMPT_CHARS):
            continue
        if "¿Analizar con Nacel?" in line or "Analyze with Nacel?" in line:
            continue
        if line.startswith("╭─ ❌") or line.startswith("╰─"):
            continue

        if cmd_clean and cmd_clean in line:
            cmd_idx = i
            break

    # Si no se encontró la línea con el comando completo, buscar por primer token ejecutable
    if cmd_idx == -1 and first_token:
        for i in range(len(lines) - 1, -1, -1):
            line = lines[i].strip()
            if line.startswith("fix") or line.startswith("nacel"):
                continue
            if any(line.startswith(f"{p} fix") or line.startswith(f"{p} nacel") for p in PROMPT_CHARS):
                continue
            if "¿Analizar con Nacel?" in line or "Analyze with Nacel?" in line:
                continue
            if line.startswith("╭─ ❌") or line.startswith("╰─"):
                continue
            if first_token in line:
                cmd_idx = i
                break

    if cmd_idx != -1:
        target_lines = lines[cmd_idx + 1:]
    else:
        target_lines = lines[-40:]

    filtered = []
    for l in target_lines:
        s = l.strip()
        # Cortar en banners interactivos posteriores
        if "¿Analizar con Nacel?" in s or "Analyze with Nacel?" in s:
            break
        if s.startswith("╭─ ❌") or s.startswith("╰─") or "Type nacel or fix" in s or "Escribe nacel o fix" in s:
            break
        # Cortar en prompt o invocaciones posteriores
        if s in ("fix", "nacel", "nacel fix") or any(s.startswith(f"{p} fix") or s.startswith(f"{p} nacel") for p in PROMPT_CHARS):
            break
        if s in PROMPT_CHARS:
            break
        if is_prompt_header(s) or (any(s.endswith(p) for p in PROMPT_CHARS) and ("~" in s or "/" in s or "@" in s or " on " in s)):
            break
        filtered.append(l)

    filtered = clean_trailing_prompt(filtered)

    # Limitar salida si excede 50 líneas para preservar contexto y atención del modelo
    if len(filtered) > 50:
        filtered = ["[... output truncated / salida truncada ...]"] + filtered[-45:]

    return "\n".join(filtered).strip()

def get_last_history_command() -> str:
    """Recupera el último comando ejecutado desde el entorno o los archivos de historial."""
    for var in ("__NACEL_LAST_CMD", "DILIX_LAST_CMD"):
        val = os.environ.get(var, "").strip()
        if val:
            return val

    home = os.path.expanduser("~")
    hist_files = [
        os.path.join(home, ".zsh_history"),
        os.path.join(home, ".bash_history"),
        os.path.join(home, ".local/share/fish/fish_history"),
    ]
    for hf in hist_files:
        if os.path.isfile(hf):
            try:
                with open(hf, "r", errors="ignore") as f:
                    lines = f.readlines()
                for line in reversed(lines):
                    line = line.strip()
                    if not line:
                        continue
                    if line.startswith(":") and ";" in line:
                        cmd = line.split(";", 1)[1].strip()
                    elif line.startswith("- cmd:"):
                        cmd = line.replace("- cmd:", "", 1).strip()
                    else:
                        cmd = line.strip()

                    if cmd and not any(cmd.startswith(x) for x in ("nacel", "dilix", "fix", "ask", "history", "exit", "clear")):
                        return cmd
            except Exception:
                pass
    return ""

def get_terminal_scrollback(lines=120) -> str:
    """
    Captura de scrollback inteligente multiplataforma sin truncamiento arbitrario:
    1. WezTerm nativo (macOS/Linux)
    2. WezTerm en WSL2 (wezterm.exe)
    3. Tmux capture-pane
    4. Kitty get-text
    5. Zellij dump-screen
    6. macOS Apple Terminal (osascript)
    7. macOS iTerm2 (osascript)
    """
    term_prog = os.environ.get("TERM_PROGRAM", "")

    # 1. WezTerm nativo
    if term_prog == "WezTerm" or os.environ.get("WEZTERM_PANE"):
        try:
            res = subprocess.run(
                ["wezterm", "cli", "get-text", "--start-line", f"-{lines}"],
                capture_output=True, text=True, timeout=1.5
            )
            if res.returncode == 0 and res.stdout.strip():
                return res.stdout
        except Exception:
            pass

    # 2. WezTerm en WSL2
    if is_wsl():
        try:
            res = subprocess.run(
                ["wezterm.exe", "cli", "get-text", "--start-line", f"-{lines}"],
                capture_output=True, text=True, timeout=1.5
            )
            if res.returncode == 0 and res.stdout.strip():
                return res.stdout
        except Exception:
            pass

    # 3. Tmux
    if os.environ.get("TMUX"):
        try:
            res = subprocess.run(
                ["tmux", "capture-pane", "-p", "-S", f"-{lines}"],
                capture_output=True, text=True, timeout=1.5
            )
            if res.returncode == 0 and res.stdout.strip():
                return res.stdout
        except Exception:
            pass

    # 4. Kitty
    if os.environ.get("KITTY_PID") or term_prog == "kitty":
        try:
            res = subprocess.run(
                ["kitty", "@", "get-text", "--extent", "screen"],
                capture_output=True, text=True, timeout=1.5
            )
            if res.returncode == 0 and res.stdout.strip():
                return res.stdout
        except Exception:
            pass

    # 5. Zellij
    if os.environ.get("ZELLIJ"):
        try:
            res = subprocess.run(
                ["zellij", "action", "dump-screen"],
                capture_output=True, text=True, timeout=1.5
            )
            if res.returncode == 0 and res.stdout.strip():
                return res.stdout
        except Exception:
            pass

    # 6. macOS Apple Terminal
    if platform.system() == "Darwin" and term_prog == "Apple_Terminal":
        try:
            res = subprocess.run(
                ["osascript", "-e", 'tell application "Terminal" to get history of selected tab of front window'],
                capture_output=True, text=True, timeout=1.5
            )
            if res.returncode == 0 and res.stdout.strip():
                return res.stdout
        except Exception:
            pass

    # 7. macOS iTerm2
    if platform.system() == "Darwin" and term_prog == "iTerm.app":
        for app_name in ("iTerm2", "iTerm"):
            try:
                res = subprocess.run(
                    ["osascript", "-e", f'tell application "{app_name}" to tell current session of current window to get text'],
                    capture_output=True, text=True, timeout=1.5
                )
                if res.returncode == 0 and res.stdout.strip():
                    return res.stdout
            except Exception:
                pass

    # Fallback general para WezTerm
    try:
        res = subprocess.run(
            ["wezterm", "cli", "get-text", "--start-line", f"-{lines}"],
            capture_output=True, text=True, timeout=1.0
        )
        if res.returncode == 0 and res.stdout.strip():
            return res.stdout
    except Exception:
        pass

    return ""

def render_box(title: str, content_lines: list):
    print_tty()
    print_tty(f"{CYAN}╭─ {BOLD}{MAGENTA}✨ Nacel{RESET} {CYAN}• {BOLD}{title}{RESET} {CYAN}" + "─" * 42 + f"{RESET}")
    for line in content_lines:
        print_tty(f"{CYAN}│{RESET} {line}")
    print_tty(f"{CYAN}╰" + "─" * 55 + f"{RESET}")

def interactive_menu(command: str):
    while True:
        menu_text = (
            f" {BOLD}{t('menu_action')}{RESET} "
            f"[{GREEN}↵ Enter{RESET}/{GREEN}e{RESET}] {t('menu_exec')}  "
            f"[{YELLOW}m{RESET}] {t('menu_prompt')}  "
            f"[{CYAN}c{RESET}] {t('menu_copy')}  "
            f"[{DIM}q{RESET}] {t('menu_quit')} "
        )
        print_tty(menu_text, end="")
        key = read_key()
        print_tty()

        if key in ("\r", "\n", "e", "E"):
            sys.stdout.write(f"EXEC:{command}\n")
            sys.stdout.flush()
            break
        elif key in ("m", "M"):
            sys.stdout.write(f"MODIFY:{command}\n")
            sys.stdout.flush()
            break
        elif key in ("c", "C"):
            if copy_to_clipboard(command):
                print_tty(f" {GREEN}{t('copied_ok')}{RESET}")
            else:
                print_tty(f" {YELLOW}{t('copied_err')}{RESET}")
        elif key in ("q", "Q", "\x03", "\x1b", "ESC"):
            sys.stdout.write("CANCEL:\n")
            sys.stdout.flush()
            break

# ==============================================================================
# CLIENTE OLLAMA
# ==============================================================================
def query_ollama_json(prompt: str) -> dict:
    host = get_ollama_host()
    model = get_current_model()
    if not check_ollama():
        return {
            "error": "OLLAMA_OFFLINE",
            "message": t("ollama_offline", host=host)
        }

    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "format": "json",
        "options": {"temperature": 0.15}
    }

    try:
        req = urllib.request.Request(
            f"{host}/api/generate",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=25) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            raw_text = data.get("response", "").strip()
            try:
                return json.loads(raw_text)
            except Exception:
                match = re.search(r"\{.*\}", raw_text, re.DOTALL)
                if match:
                    return json.loads(match.group(0))
            return {"raw": raw_text}
    except Exception as e:
        return {"error": "API_ERROR", "message": str(e)}

def stream_ollama_text(prompt: str, context: list = None) -> (str, list):
    host = get_ollama_host()
    model = get_current_model()
    if not check_ollama():
        print_tty(f"{RED}❌ Error: {t('ollama_offline', host=host)}{RESET}")
        return "", context

    payload = {
        "model": model,
        "prompt": prompt,
        "stream": True,
        "options": {"temperature": 0.3}
    }
    if context:
        payload["context"] = context

    full_response = []
    final_context = context

    try:
        req = urllib.request.Request(
            f"{host}/api/generate",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            for line in resp:
                if line:
                    data = json.loads(line.decode("utf-8"))
                    chunk = data.get("response", "")
                    print_tty(chunk, end="")
                    full_response.append(chunk)
                    if data.get("done") and "context" in data:
                        final_context = data["context"]
        print_tty()
        return "".join(full_response), final_context
    except Exception as e:
        print_tty(f"\n{RED}❌ Error: {e}{RESET}")
        return "".join(full_response), final_context

# ==============================================================================
# COMANDOS: IDIOMA Y MODELO
# ==============================================================================
def handle_lang(args: list):
    cfg = load_config()
    current = get_current_language() or "es"

    if args:
        target = args[0].lower().strip()
        if target in ("es", "spanish", "español"):
            cfg["lang"] = "es"
            save_config(cfg)
            print_tty(f"{GREEN}✔ Idioma configurado a Español.{RESET} Nacel responderá en español.")
            return
        elif target in ("en", "english", "inglés", "ingles"):
            cfg["lang"] = "en"
            save_config(cfg)
            print_tty(f"{GREEN}✔ Language configured to English.{RESET} Nacel will respond in English.")
            return
        else:
            print_tty(f"{YELLOW}Opción no reconocida: '{target}'. Use 'es' o 'en'.{RESET}")
            return

    print_tty()
    print_tty(f"{CYAN}╭─ {BOLD}{MAGENTA}✨ Nacel{RESET} {CYAN}• {BOLD}Idioma / Language Settings{RESET} {CYAN}" + "─" * 25 + f"{RESET}")
    print_tty(f"{CYAN}│{RESET} Idioma actual / Current language: {GREEN}{BOLD}{'English' if current == 'en' else 'Español'}{RESET}")
    print_tty(f"{CYAN}│{RESET} Selecciona una opción para cambiar / Select to change:")
    print_tty(f"{CYAN}│{RESET}   {CYAN}[1]{RESET} Español  (Spanish)")
    print_tty(f"{CYAN}│{RESET}   {CYAN}[2]{RESET} English  (Inglés)")
    print_tty(f"{CYAN}╰" + "─" * 55 + f"{RESET}")
    print_tty(f" {BOLD}Opción / Choice [1/2]:{RESET} ", end="")
    choice = read_key().strip()
    print_tty()

    if choice in ("1", "es"):
        cfg["lang"] = "es"
        save_config(cfg)
        print_tty(f"{GREEN}✔ Idioma establecido a Español.{RESET}")
    elif choice in ("2", "en"):
        cfg["lang"] = "en"
        save_config(cfg)
        print_tty(f"{GREEN}✔ Language set to English.{RESET}")
    else:
        print_tty(f"{DIM}Sin cambios / No changes made.{RESET}")

def render_hardware_box(hw=None, rec=None, installed=None):
    """Muestra una caja visual con el diagnóstico de hardware y la recomendación."""
    if hw is None:
        hw = get_system_hardware()
    if rec is None:
        rec = get_model_recommendation(hw)
    if installed is None:
        installed = get_installed_ollama_models()

    active_model = get_current_model()
    lines = [
        f"{BOLD}🖥️ Sistema Operativo / OS:{RESET} {CYAN}{hw['os_name']} ({hw['arch']}){RESET}",
        f"{BOLD}⚙️ Procesador / CPU:{RESET} {CYAN}{hw['cpu_name']} ({hw['cpu_cores']} núcleos){RESET}",
        f"{BOLD}🧠 Memoria RAM:{RESET} {CYAN}{hw['ram_gb']} GB{RESET}",
        f"{BOLD}⚡ Aceleración de Hardware:{RESET} {GREEN}{hw['acceleration']}{RESET}",
        f"{BOLD}🏷️ Perfil Detectado:{RESET} {MAGENTA}{rec['tier_label']}{RESET}",
        f"{BOLD}🤖 Modelo Activo Actual:{RESET} {CYAN}{BOLD}{active_model}{RESET}",
        f"{BOLD}🎯 Modelo Recomendado Óptimo:{RESET} {YELLOW}{BOLD}{rec['recommended_model']}{RESET}",
    ]
    render_box("Diagnóstico de Hardware y Recomendación de IA", lines)

    print_tty(f"\n{BOLD}💡 ¿Por qué {CYAN}{rec['recommended_model']}{RESET}{BOLD}?{RESET}")
    print_tty(f"  {rec['reason']}\n")

    if installed:
        installed_str = ", ".join([f"{CYAN}{m}{RESET}" for m in installed])
        print_tty(f"{BOLD}📦 Modelos detectados en tu Ollama local:{RESET} {installed_str}\n")

def setup_model(interactive=True, auto_select=False, model_override="", pull_after=True) -> str:
    """
    Ejecuta el asistente de selección de modelo para el instalador o comandos CLI:
    1. Diagnostica hardware.
    2. Sugiere el mejor modelo según RAM y GPU.
    3. Muestra catálogo con badges [Recomendado] y [Instalado].
    4. Guarda en ~/.config/nacel/config.json.
    5. Descarga automáticamente el modelo vía Ollama si está disponible.
    """
    hw = get_system_hardware()
    rec_info = get_model_recommendation(hw)
    rec_model = rec_info["recommended_model"]
    installed = get_installed_ollama_models()
    catalog = rec_info["catalog"]

    if model_override:
        chosen_model = model_override.strip()
    elif auto_select or not interactive:
        chosen_model = rec_model
    else:
        render_hardware_box(hw, rec_info, installed)
        print_tty(f"{BOLD}Selecciona el modelo de IA para configurar en Nacel:{RESET}")

        option_map = {}
        idx = 1
        for item in catalog:
            m_name = item["model"]
            is_rec = (m_name == rec_model)
            is_inst = any(m_name in inst for inst in installed)

            badges = []
            if is_rec:
                badges.append(f"{YELLOW}{BOLD}[Recomendado ⭐]{RESET}")
            if is_inst:
                badges.append(f"{GREEN}[Instalado ✔]{RESET}")
            badge_str = " ".join(badges) if badges else ""

            print_tty(f"  {CYAN}[{idx}]{RESET} {BOLD}{m_name:<20}{RESET} {badge_str:<26} {DIM}{item['desc']}{RESET}")
            option_map[str(idx)] = m_name
            idx += 1

        print_tty(f"  {CYAN}[{idx}]{RESET} {BOLD}{'Personalizado...':<20}{RESET} {DIM}Escribir manualmente cualquier otro modelo de Ollama{RESET}")
        custom_idx = str(idx)

        print_tty(f"\n{BOLD}Elige una opción [1-{idx}] (Enter para {rec_model} en 10s):{RESET} ", end="")
        choice = read_key(timeout=10).strip()
        print_tty()

        if choice in option_map:
            chosen_model = option_map[choice]
        elif choice == custom_idx:
            print_tty(f"{CYAN}❯{RESET} {BOLD}Ingresa el nombre del modelo de Ollama (ej: llama3.2:1b):{RESET} ", end="")
            chosen_model = input_tty().strip()
            if not chosen_model:
                chosen_model = rec_model
        else:
            chosen_model = rec_model

    # Guardar en config.json respetando otros parámetros (ej: lang)
    cfg = load_config()
    cfg["model"] = chosen_model
    if "lang" not in cfg:
        cfg["lang"] = "es"
    save_config(cfg)
    print_tty(f"\n{GREEN}✔ Modelo configurado en Nacel:{RESET} {CYAN}{BOLD}{chosen_model}{RESET}")
    print_tty(f"{DIM}Guardado en {CONFIG_FILE}{RESET}")

    # Descarga automática vía Ollama
    if pull_after:
        ollama_bin = shutil.which("ollama")
        is_already_installed = any(chosen_model in inst for inst in installed)
        if is_already_installed:
            print_tty(f"{GREEN}✔ El modelo {BOLD}{chosen_model}{RESET}{GREEN} ya está listo localmente en tu Ollama.{RESET}")
        elif ollama_bin or check_ollama():
            print_tty(f"\n{CYAN}▶ Descargando modelo {BOLD}{chosen_model}{RESET}{CYAN} en Ollama...{RESET}")
            try:
                ret = subprocess.run(["ollama", "pull", chosen_model])
                if ret.returncode == 0:
                    print_tty(f"\n{GREEN}✔ Modelo {BOLD}{chosen_model}{RESET}{GREEN} descargado e instalado con éxito.{RESET}")
                else:
                    print_tty(f"\n{YELLOW}⚠️ No se pudo completar la descarga automática (código {ret.returncode}).{RESET}")
                    print_tty(f"Ejecuta: '{BOLD}ollama pull {chosen_model}{RESET}' cuando tengas conexión.")
            except Exception as e:
                print_tty(f"\n{YELLOW}⚠️ No se pudo ejecutar ollama pull: {e}{RESET}")
                print_tty(f"Ejecuta: '{BOLD}ollama pull {chosen_model}{RESET}' manualmente.")
        else:
            print_tty(f"\n{YELLOW}⚠️ Ollama no está instalado o no se encuentra en el PATH.{RESET}")
            print_tty(f"Para usar Nacel con IA local, descarga Ollama desde: {CYAN}https://ollama.com{RESET}")
            print_tty(f"Luego descarga el modelo recomendado con: {BOLD}ollama pull {chosen_model}{RESET}")

    return chosen_model

def handle_hardware(args: list = None):
    """Muestra el diagnóstico de hardware y sugerencias de modelo."""
    hw = get_system_hardware()
    rec = get_model_recommendation(hw)
    installed = get_installed_ollama_models()
    render_hardware_box(hw, rec, installed)
    print_tty(f"{BOLD}Comandos de gestión:{RESET}")
    print_tty(f"  • {GREEN}nacel model auto{RESET}      -> Configura automáticamente {rec['recommended_model']}")
    print_tty(f"  • {GREEN}nacel model recommend{RESET} -> Asistente interactivo para cambiar de modelo")
    print_tty(f"  • {GREEN}nacel model set <m>{RESET}   -> Cambia a cualquier modelo manual\n")

def handle_model(args: list):
    cfg = load_config()

    # nacel model auto / autotune
    if args and args[0].lower() in ("auto", "autotune", "tune"):
        setup_model(interactive=False, auto_select=True, pull_after=True)
        return

    # nacel model recommend / rec / wizard / setup
    if args and args[0].lower() in ("recommend", "rec", "recomendar", "setup", "wizard"):
        setup_model(interactive=True, auto_select=False, pull_after=True)
        return

    # nacel model list / ls
    if args and args[0].lower() in ("list", "ls"):
        hw = get_system_hardware()
        rec = get_model_recommendation(hw)
        installed = get_installed_ollama_models()
        active = get_current_model()
        print_tty(f"\n{BOLD}🤖 Modelo activo:{RESET} {CYAN}{BOLD}{active}{RESET}")
        print_tty(f"{BOLD}🎯 Recomendado para tu hardware:{RESET} {YELLOW}{BOLD}{rec['recommended_model']}{RESET} ({rec['tier_label']})\n")
        print_tty(f"{BOLD}📦 Modelos instalados en Ollama local:{RESET}")
        if installed:
            for m in installed:
                cur = f" {GREEN}(Activo){RESET}" if m == active else ""
                print_tty(f"  • {CYAN}{m}{RESET}{cur}")
        else:
            print_tty(f"  {DIM}(No se detectaron modelos descargados en Ollama){RESET}")
        print_tty(f"\n{BOLD}💡 Catálogo de modelos recomendados para Nacel:{RESET}")
        for item in rec["catalog"]:
            print_tty(f"  • {GREEN}{item['model']:<20}{RESET} {DIM}{item['desc']}{RESET}")
        print_tty(f"\n{DIM}Para cambiar de modelo ejecuta: nacel model set <nombre_del_modelo>{RESET}\n")
        return

    # nacel model set <nombre>
    if len(args) >= 2 and args[0].lower() in ("set", "use"):
        new_model = args[1].strip()
        cfg["model"] = new_model
        save_config(cfg)
        print_tty(f"{GREEN}✔ Modelo establecido a:{RESET} {CYAN}{BOLD}{new_model}{RESET}")
        print_tty(f"{DIM}Guardado en {CONFIG_FILE}{RESET}")
        installed = get_installed_ollama_models()
        if not any(new_model in inst for inst in installed):
            print_tty(f"{YELLOW}💡 Nota: {new_model} no parece estar descargado en tu Ollama aún.{RESET}")
            print_tty(f"Puedes descargarlo ejecutando: {BOLD}ollama pull {new_model}{RESET}")
        return

    # Si se pasa un argumento directo como modelo (ej: nacel model qwen2.5-coder:7b)
    if len(args) == 1 and args[0].lower() not in ("status", "info"):
        new_model = args[0].strip()
        cfg["model"] = new_model
        save_config(cfg)
        print_tty(f"{GREEN}✔ Modelo establecido a:{RESET} {CYAN}{BOLD}{new_model}{RESET}")
        return

    # nacel model (sin argumentos o status)
    handle_status()
    hw = get_system_hardware()
    rec = get_model_recommendation(hw)
    installed = get_installed_ollama_models()

    print_tty(f"\n{BOLD}🎯 Modelo óptimo recomendado para tu equipo:{RESET} {YELLOW}{BOLD}{rec['recommended_model']}{RESET}")
    print_tty(f"  {DIM}{rec['reason']}{RESET}\n")

    if installed:
        installed_str = ", ".join([f"{CYAN}{m}{RESET}" for m in installed])
        print_tty(f"{BOLD}📦 Modelos instalados en Ollama:{RESET} {installed_str}\n")

    print_tty(f"{BOLD}💡 Opciones y Comandos de Modelo:{RESET}")
    print_tty(f"  • {GREEN}nacel model auto{RESET}      -> Configurar automáticamente el mejor modelo para tu equipo")
    print_tty(f"  • {GREEN}nacel model recommend{RESET} -> Asistente interactivo guiado de selección")
    print_tty(f"  • {GREEN}nacel model list{RESET}      -> Listar modelos instalados y catálogo completo")
    print_tty(f"  • {GREEN}nacel model set <m>{RESET}   -> Cambiar manualmente de modelo (ej: {rec['recommended_model']})")
    print_tty(f"  • {GREEN}nacel hardware{RESET}        -> Ver diagnóstico detallado de CPU, RAM y GPU\n")

# ==============================================================================
# FUNCIONALIDADES PRINCIPALES (EXPLAIN, DEBUG, FIX, ASK, CHAT)
# ==============================================================================
def handle_explain(args: list):
    lang = ensure_language()
    model = get_current_model()
    code_content = ""
    source_label = ""

    if not sys.stdin.isatty():
        code_content = sys.stdin.read().strip()
        source_label = t("stdin_label")
    elif args and os.path.isfile(args[0]):
        filepath = args[0]
        try:
            with open(filepath, "r", errors="ignore") as f:
                lines = f.readlines()
            if len(lines) > 400:
                code_content = "".join(lines[:400])
                source_label = f"{filepath} (head 400 lines)"
            else:
                code_content = "".join(lines)
                source_label = filepath
        except Exception as e:
            print_tty(f"{RED}❌ {e}{RESET}")
            return
    elif args:
        code_content = " ".join(args).strip()
        source_label = t("snippet_label")
    else:
        print_tty(f"{YELLOW}Uso / Usage:{RESET} nacel explain <archivo | 'comando' | pipe>")
        return

    if not code_content:
        print_tty(f"{YELLOW}{t('no_code_found')}{RESET}")
        return

    print_tty()
    print_tty(f"{CYAN}╭─ {BOLD}{MAGENTA}✨ Nacel{RESET} {CYAN}• {BOLD}{t('box_explain', source=source_label)}{RESET} {CYAN}" + "─" * 20 + f"{RESET}")
    print_tty(f"{DIM}{t('processing_explain', model=model)}{RESET}\n")

    if lang == "en":
        prompt = f"""{t('persona')}
Dissect and explain the following code or command with rigorous logical precision.
Source: {source_label}

```
{code_content}
```

Structure your response:
1. **General Logical Purpose**: (1-2 concise sentences on what it achieves).
2. **Execution Flow & Mechanics**: (step-by-step breakdown of internal mechanics).
3. **Critical Evaluation**: (algorithmic efficiency, edge cases, vulnerabilities, or improvements).

Maintain your composed, sharp analytical demeanor."""
    else:
        prompt = f"""{t('persona')}
Disecciona y explica el siguiente código o comando con rigor analítico.
Origen: {source_label}

```
{code_content}
```

Estructura tu respuesta exactamente así:
1. **Propósito Lógico General**: (1 o 2 oraciones concisas de qué hace).
2. **Flujo de Ejecución y Mecánica Interna**: (desglose paso a paso de los componentes clave).
3. **Evaluación Crítica**: (eficiencia algorítmica, casos borde, vulnerabilidades o mejoras si las hay).

Mantén tu tono sobrio, impecable y directo al grano."""

    stream_ollama_text(prompt)
    print_tty(f"{CYAN}╰" + "─" * 65 + f"{RESET}\n")

def handle_debug(args: list):
    lang = ensure_language()
    error_content = ""
    source = ""

    if not sys.stdin.isatty():
        error_content = sys.stdin.read().strip()
        source = t("stdin_label")
    elif args and os.path.isfile(args[0]):
        try:
            with open(args[0], "r", errors="ignore") as f:
                error_content = f.read()[-3000:]
            source = args[0]
        except Exception as e:
            print_tty(f"{RED}❌ {e}{RESET}")
            return
    elif args:
        error_content = " ".join(args).strip()
        source = t("snippet_label")
    else:
        last_cmd = os.environ.get("__NACEL_LAST_CMD", "").strip() or os.environ.get("DILIX_LAST_CMD", "").strip() or get_last_history_command()
        last_code = os.environ.get("__NACEL_LAST_CODE", "").strip() or "1"
        raw_scrollback = get_terminal_scrollback(120)
        extracted = extract_command_output(raw_scrollback, last_cmd, last_code) if raw_scrollback else ""
        error_content = extracted if extracted else (raw_scrollback[-3000:].strip() if raw_scrollback else "")
        source = f"Terminal trace ({last_cmd})" if last_cmd else "Terminal scrollback"

    if not error_content:
        print_tty(f"{YELLOW}{t('no_debug_target')}{RESET}")
        return

    print_tty()
    print_tty(f"{CYAN}╭─ {BOLD}{MAGENTA}✨ Nacel{RESET} {CYAN}• {BOLD}{t('box_debug')}{RESET} {CYAN}" + "─" * 30 + f"{RESET}")
    print_tty(f"{DIM}{t('processing_debug')}{RESET}\n")

    if lang == "en":
        prompt = f"""{t('persona')}
Debug the following system anomaly, error trace, or code failure ({source}):
```
{error_content}
```

Structure your response:
1. **Root Cause**: (Exact deduction of what failed logically and why).
2. **Logical Analysis**: (Concise explanation of the failure mechanism).
3. **Remediation Procedure**: (Exact step-by-step fix and corrected code/command).

Be analytical, precise, and direct."""
    else:
        prompt = f"""{t('persona')}
El usuario solicita depuración de una anomalía o error en su sistema/código ({source}):
```
{error_content}
```

Estructura tu respuesta:
1. **Causa Raíz (Root Cause)**: (Diagnóstico exacto de qué falló y por qué ocurrió lógicamente).
2. **Deducción y Análisis**: (Explicación concisa del mecanismo de fallo).
3. **Procedimiento de Solución**: (Instrucciones exactas y código o comando corregido).

Sé analítico, preciso y no uses rodeos."""

    stream_ollama_text(prompt)
    print_tty(f"{CYAN}╰" + "─" * 65 + f"{RESET}\n")

def handle_fix(last_cmd: str, last_code: str, error_msg: str = ""):
    lang = ensure_language()
    model = get_current_model()

    # 1. Recuperar comando previo si viene vacío
    last_cmd = last_cmd.strip()
    if not last_cmd:
        last_cmd = os.environ.get("__NACEL_LAST_CMD", "").strip() or os.environ.get("DILIX_LAST_CMD", "").strip() or get_last_history_command()

    if not last_cmd:
        print_tty(f"{YELLOW}{t('no_error_found')}{RESET}")
        sys.stdout.write("CANCEL:\n")
        return

    # 2. Recuperar código de salida previo
    last_code = str(last_code).strip()
    if not last_code:
        last_code = os.environ.get("__NACEL_LAST_CODE", "").strip() or "1"

    # 3. ÚNICAMENTE cuando es un error: si exit code es 0 y no hay error explícito ni stdin
    has_explicit_err = bool(error_msg.strip())
    has_piped_input = not sys.stdin.isatty()

    if last_code == "0" and not has_explicit_err and not has_piped_input:
        print_tty(f"{GREEN}{t('command_success_no_error', cmd=last_cmd)}{RESET}")
        sys.stdout.write("CANCEL:\n")
        return

    # 4. Obtención precisa del comando y su salida de error
    command_output = ""
    if has_piped_input:
        try:
            command_output = sys.stdin.read().strip()
        except Exception:
            pass

    if not command_output and has_explicit_err:
        command_output = error_msg.strip()

    if not command_output:
        raw_scrollback = get_terminal_scrollback(lines=120)
        command_output = extract_command_output(raw_scrollback, last_cmd, last_code)

    if not command_output:
        if lang == "en":
            command_output = f"(No standard output or error trace was emitted to the terminal; the command exited with code {last_code}.)"
        else:
            command_output = f"(El comando terminó con código de error {last_code} sin emitir trazas de error ni salida estándar en la terminal.)"

    print_tty(f"{DIM}✨ Nacel {t('processing_fix', model=model)}{RESET}")

    if lang == "en":
        prompt = f"""{t('persona')}
Environment Context:
Operating System: {get_os_info()}
Current directory: {os.getcwd()}

The following terminal command failed with an error:
==================================================
COMMAND EXECUTED:
{last_cmd}

EXIT CODE:
{last_code}

ERROR OUTPUT / TERMINAL TRACE:
{command_output}
==================================================

Analyze the exact root cause directly from the command and error output above.
Formulate the exact corrected command to resolve the issue.
Respond ONLY in this valid JSON format:
{{
  "causa": "Direct 1-sentence logical explanation of why it failed in English based on the error trace.",
  "que_hacer": "Clear, concise instruction of what to do in English.",
  "comando": "Exact corrected executable terminal command, no markdown, no quotes"
}}"""
    else:
        prompt = f"""{t('persona')}
Contexto del entorno:
Sistema Operativo: {get_os_info()}
Directorio actual: {os.getcwd()}

El siguiente comando de terminal falló con error:
==================================================
COMANDO EJECUTADO:
{last_cmd}

CÓDIGO DE SALIDA (EXIT CODE):
{last_code}

SALIDA / TRAZA DE ERROR DEL COMANDO:
{command_output}
==================================================

Analiza la causa raíz exacta basándote directamente en el comando ejecutado y su salida de error.
Formula el comando exacto y corregido para resolver la anomalía.
Responde ÚNICAMENTE en este formato JSON válido:
{{
  "causa": "Explicación directa de 1 frase del por qué falló de manera lógica en español basándote en la traza de error.",
  "que_hacer": "Instrucción clara y concisa de qué toca hacer en español.",
  "comando": "Comando exacto de terminal corregido para solucionar o reintentar, sin markdown ni explicaciones adicionales"
}}"""

    result = query_ollama_json(prompt)
    if "error" in result:
        print_tty(f"{RED}❌ Error: {result.get('message')}{RESET}")
        sys.stdout.write("CANCEL:\n")
        return

    causa = result.get("causa", "The command returned an unexpected error code.")
    que_hacer = result.get("que_hacer", "Verify command syntax or dependencies.")
    comando = clean_command(result.get("comando", ""))

    lines = [
        f"{BOLD}{RED}❌ {t('failed_label')}{RESET} {CYAN}{last_cmd}{RESET} {DIM}(exit code: {last_code}){RESET}",
        f"{BOLD}🔍 {t('cause_label')}{RESET} {causa}",
        f"{BOLD}💡 {t('action_label')}{RESET} {que_hacer}",
    ]
    if comando:
        lines.append(f"{BOLD}⚡ {t('solution_label')}{RESET}")
        lines.append(f"  {GREEN}{BOLD}{comando}{RESET}")

    render_box(t("box_fix"), lines)

    if comando:
        interactive_menu(comando)
    else:
        sys.stdout.write("CANCEL:\n")

def handle_ask(query: str):
    lang = ensure_language()
    model = get_current_model()
    if not query.strip():
        print_tty(f"{YELLOW}Uso: ask \"consulta\" / Usage: ask \"query\"{RESET}")
        sys.stdout.write("CANCEL:\n")
        return

    print_tty(f"{DIM}✨ Nacel {t('processing_ask', model=model)}{RESET}")

    if lang == "en":
        prompt = f"""{t('persona')}
Environment Context:
Operating System: {get_os_info()}
Current directory: {os.getcwd()}

The user requires an exact terminal command for the following task:
Query: {query}

Respond ONLY in this valid JSON format:
{{
  "explicacion": "Brief 1-sentence explanation of what the command does in English.",
  "comando": "Exact executable terminal command, no markdown, no quotes"
}}"""
    else:
        prompt = f"""{t('persona')}
Contexto del entorno:
Sistema Operativo: {get_os_info()}
Directorio actual: {os.getcwd()}

El usuario necesita un comando exacto para la siguiente tarea en su terminal:
Consulta: {query}

Responde ÚNICAMENTE en este formato JSON válido:
{{
  "explicacion": "Explicación breve de 1 frase del comando y su lógica en español.",
  "comando": "Comando exacto de terminal ejecutable, sin explicaciones, sin markdown"
}}"""

    result = query_ollama_json(prompt)
    if "error" in result:
        print_tty(f"{RED}❌ Error: {result.get('message')}{RESET}")
        sys.stdout.write("CANCEL:\n")
        return

    explicacion = result.get("explicacion", "Command suggested.")
    comando = clean_command(result.get("comando", ""))

    if not comando:
        print_tty(f"{RED}❌ Could not formulate command.{RESET}")
        sys.stdout.write("CANCEL:\n")
        return

    lines = [
        f"{BOLD}{t('query_label')}{RESET} {query}",
        f"{DIM}{t('explanation_label')}{RESET} {explicacion}",
        f"{BOLD}{t('suggested_label')}{RESET}",
        f"  {GREEN}{BOLD}{comando}{RESET}"
    ]
    render_box(t("box_ask"), lines)
    interactive_menu(comando)

def handle_chat():
    lang = ensure_language()
    model = get_current_model()
    print_tty()
    print_tty(f"{CYAN}╭─ {BOLD}{MAGENTA}✨ Nacel{RESET} {CYAN}• {BOLD}{t('box_chat')}{RESET} {CYAN}" + "─" * 32 + f"{RESET}")
    print_tty(f"{CYAN}│{RESET} {t('chat_welcome_1')}")
    print_tty(f"{CYAN}│{RESET} {t('chat_welcome_2')}")
    print_tty(f"{CYAN}│{RESET} {DIM}{t('chat_welcome_3')} [{lang.upper()} • {model}]{RESET}")
    print_tty(f"{CYAN}╰" + "─" * 65 + f"{RESET}\n")

    conversation_context = None

    while True:
        try:
            prompt_symbol = f"{MAGENTA}✨ nacel{RESET} {CYAN}❯{RESET} "
            user_input = input(prompt_symbol).strip()
        except (KeyboardInterrupt, EOFError):
            print_tty(f"\n{MAGENTA}✨ Nacel:{RESET} {t('chat_session_ended')}")
            break

        if not user_input:
            continue

        if user_input.lower() in ("exit", "quit", "q"):
            print_tty(f"{MAGENTA}✨ Nacel:{RESET} {t('chat_farewell')}")
            break

        if user_input.lower() == "clear":
            os.system("clear")
            continue

        if user_input.lower() in ("lang", "idioma"):
            handle_lang([])
            lang = ensure_language()
            continue

        prompt = f"""{t('persona')}
The user is interacting with you directly:
"{user_input}"

Respond with clarity, precision, and elegance."""

        print_tty(f"\n{MAGENTA}✨ Nacel:{RESET} ", end="")
        _, conversation_context = stream_ollama_text(prompt, context=conversation_context)
        print_tty()

def handle_query(query_parts: list):
    lang = ensure_language()
    query = " ".join(query_parts).strip()
    if not query:
        handle_chat()
        return

    cmd_keywords = [
        "como", "cómo", "comando", "ver", "listar", "borrar", "eliminar",
        "matar", "buscar", "instalar", "puerto", "proceso", "git", "docker",
        "crear", "mover", "copiar", "permisos", "chmod", "curl", "find",
        "how", "kill", "list", "show", "delete", "search", "port", "process"
    ]
    query_lower = query.lower()
    is_command_request = any(k in query_lower for k in cmd_keywords)

    if is_command_request and len(query.split()) < 14:
        handle_ask(query)
    else:
        print_tty()
        print_tty(f"{CYAN}╭─ {BOLD}{MAGENTA}✨ Nacel{RESET} {CYAN}• {BOLD}{t('box_query')}{RESET} {CYAN}" + "─" * 44 + f"{RESET}\n")
        prompt = f"""{t('persona')}
Query / Request:
{query}

Provide a logically impeccable, technically sharp, and didactic response."""
        stream_ollama_text(prompt)
        print_tty(f"\n{CYAN}╰" + "─" * 65 + f"{RESET}\n")

# ==============================================================================
# COMANDOS: MENÚ, ESTADO Y AYUDA
# ==============================================================================
def handle_status():
    lang = ensure_language()
    ollama_ok = check_ollama()
    host = get_ollama_host()
    model = get_current_model()
    status_str = f"{GREEN}Activo y respondiendo / Active{RESET}" if ollama_ok else f"{RED}Inactivo / Offline ({host}){RESET}"
    os_info = get_os_info()
    hw = get_system_hardware()
    rec = get_model_recommendation(hw)
    hw_str = f"{hw['cpu_name']} ({hw['cpu_cores']} núcleos) • {hw['ram_gb']}GB RAM"
    lines = [
        f"{BOLD}🖥️ Sistema Operativo / OS:{RESET} {CYAN}{os_info}{RESET}",
        f"{BOLD}⚙️ Hardware:{RESET} {CYAN}{hw_str}{RESET}",
        f"{BOLD}⚡ Aceleración / Engine:{RESET} {GREEN}{hw['acceleration']}{RESET}",
        f"{BOLD}🤖 Modelo de IA / Model:{RESET} {CYAN}{BOLD}{model}{RESET}",
        f"{BOLD}🎯 Recomendado para tu equipo:{RESET} {YELLOW}{rec['recommended_model']}{RESET}",
        f"{BOLD}🔌 Servidor Ollama / Host:{RESET} {status_str}",
        f"{BOLD}📁 Configuración / Config:{RESET} {CONFIG_FILE}",
        f"{BOLD}🌐 Idioma actual / Language:{RESET} {GREEN}{lang.upper()}{RESET}",
    ]
    render_box("Estado y Configuración / Status", lines)

def handle_help():
    lang = ensure_language()
    if lang == "en":
        print_tty(f"\n{CYAN}╭─ {BOLD}{MAGENTA}✨ Nacel{RESET} {CYAN}• {BOLD}All Available Commands & Options{RESET} {CYAN}" + "─" * 22 + f"{RESET}")
        print_tty(f"{CYAN}│{RESET} {BOLD}Interactive Commands:{RESET}")
        print_tty(f"{CYAN}│{RESET}   {GREEN}nacel menu{RESET}                 Open interactive control center with all options")
        print_tty(f"{CYAN}│{RESET}   {GREEN}nacel{RESET}                      Start interactive chat (or fix error if last command failed)")
        print_tty(f"{CYAN}│{RESET}   {GREEN}nacel chat{RESET}                 Open conversational channel with memory")
        print_tty(f"{CYAN}│{RESET}")
        print_tty(f"{CYAN}│{RESET} {BOLD}Code & Troubleshooting:{RESET}")
        print_tty(f"{CYAN}│{RESET}   {GREEN}nacel explain <file|cmd>{RESET}   Explain code mechanics, architecture, or pipes")
        print_tty(f"{CYAN}│{RESET}   {GREEN}nacel debug <error|file>{RESET}   Analyze error trace, determine root cause & fix")
        print_tty(f"{CYAN}│{RESET}   {GREEN}nacel fix{RESET}                  Diagnose and repair the last failed command")
        print_tty(f"{CYAN}│{RESET}   {GREEN}Ctrl + G{RESET}                   Global hotkey to analyze the last command failure")
        print_tty(f"{CYAN}│{RESET}")
        print_tty(f"{CYAN}│{RESET} {BOLD}Natural Language Queries:{RESET}")
        print_tty(f"{CYAN}│{RESET}   {GREEN}ask \"<query>\"{RESET}             Suggest terminal command and run or modify it")
        print_tty(f"{CYAN}│{RESET}   {GREEN}nacel \"<query>\"{RESET}           Answer technical question or suggest command")
        print_tty(f"{CYAN}│{RESET}")
        print_tty(f"{CYAN}│{RESET} {BOLD}Configuration & Settings:{RESET}")
        print_tty(f"{CYAN}│{RESET}   {GREEN}nacel model [set <name>]{RESET}  View active model or change it (e.g. gemma2:2b)")
        print_tty(f"{CYAN}│{RESET}   {GREEN}nacel lang [en|es]{RESET}        View or switch active language")
        print_tty(f"{CYAN}│{RESET}   {GREEN}nacel help{RESET}                 Display all available options")
        print_tty(f"{CYAN}╰" + "─" * 65 + f"{RESET}\n")
    else:
        print_tty(f"\n{CYAN}╭─ {BOLD}{MAGENTA}✨ Nacel{RESET} {CYAN}• {BOLD}Todos los Comandos y Opciones Disponibles{RESET} {CYAN}" + "─" * 15 + f"{RESET}")
        print_tty(f"{CYAN}│{RESET} {BOLD}Comandos Interactivos:{RESET}")
        print_tty(f"{CYAN}│{RESET}   {GREEN}nacel menu{RESET}                 Abre el menú interactivo con todas las opciones")
        print_tty(f"{CYAN}│{RESET}   {GREEN}nacel{RESET}                      Chat interactivo (o repara si el comando previo falló)")
        print_tty(f"{CYAN}│{RESET}   {GREEN}nacel chat{RESET}                 Abre canal de chat interactivo con memoria")
        print_tty(f"{CYAN}│{RESET}")
        print_tty(f"{CYAN}│{RESET} {BOLD}Código y Solución de Problemas:{RESET}")
        print_tty(f"{CYAN}│{RESET}   {GREEN}nacel explain <archivo|cmd>{RESET} Explica arquitectura y funcionamiento de código")
        print_tty(f"{CYAN}│{RESET}   {GREEN}nacel debug <error|archivo>{RESET} Analiza traza de error, causa raíz y solución")
        print_tty(f"{CYAN}│{RESET}   {GREEN}nacel fix{RESET}                  Diagnostica y soluciona el último comando fallido")
        print_tty(f"{CYAN}│{RESET}   {GREEN}Ctrl + G{RESET}                   Atajo de teclado para analizar el último error")
        print_tty(f"{CYAN}│{RESET}")
        print_tty(f"{CYAN}│{RESET} {BOLD}Consultas en Lenguaje Natural:{RESET}")
        print_tty(f"{CYAN}│{RESET}   {GREEN}ask \"<consulta>\"{RESET}          Sugiere comando de terminal y permite ejecutarlo")
        print_tty(f"{CYAN}│{RESET}   {GREEN}nacel \"<consulta>\"{RESET}        Responde preguntas técnicas o sugiere comandos")
        print_tty(f"{CYAN}│{RESET}")
        print_tty(f"{CYAN}│{RESET} {BOLD}Configuración y Ajustes:{RESET}")
        print_tty(f"{CYAN}│{RESET}   {GREEN}nacel model [set <nombre>]{RESET} Ver o cambiar modelo activo (ej: gemma2:2b)")
        print_tty(f"{CYAN}│{RESET}   {GREEN}nacel lang [es|en]{RESET}        Ver o cambiar el idioma activo")
        print_tty(f"{CYAN}│{RESET}   {GREEN}nacel help{RESET}                 Muestra todas las opciones disponibles")
        print_tty(f"{CYAN}╰" + "─" * 65 + f"{RESET}\n")

def handle_menu():
    lang = ensure_language()
    while True:
        print_tty()
        if lang == "en":
            print_tty(f"{CYAN}╭─ {BOLD}{MAGENTA}✨ Nacel{RESET} {CYAN}• {BOLD}Interactive Control Center & Options{RESET} {CYAN}" + "─" * 17 + f"{RESET}")
            print_tty(f"{CYAN}│{RESET} Choose an option to execute:")
            print_tty(f"{CYAN}│{RESET}   {CYAN}[1]{RESET} 💬  Interactive Chat          (Start conversational channel)")
            print_tty(f"{CYAN}│{RESET}   {CYAN}[2]{RESET} 💡  Ask / Command Suggestion   (Generate exact terminal commands)")
            print_tty(f"{CYAN}│{RESET}   {CYAN}[3]{RESET} 🛠️  Diagnose & Fix Error       (Inspect last failed command)")
            print_tty(f"{CYAN}│{RESET}   {CYAN}[4]{RESET} 📖  Explain Code or File       (Dissect architecture & logic)")
            print_tty(f"{CYAN}│{RESET}   {CYAN}[5]{RESET} 🐛  Debug Error or Trace       (Deduce root cause & solutions)")
            print_tty(f"{CYAN}│{RESET}   {CYAN}[6]{RESET} 🌐  Language Settings          (Switch between English & Spanish)")
            print_tty(f"{CYAN}│{RESET}   {CYAN}[7]{RESET} 🤖  Model & System Status      (Inspect Ollama engine & model)")
            print_tty(f"{CYAN}│{RESET}   {CYAN}[8]{RESET} 📋  Help & Cheatsheet          (Print all command syntaxes)")
            print_tty(f"{CYAN}│{RESET}   {CYAN}[0]{RESET} 🚪  Exit                       (Return to terminal)")
            print_tty(f"{CYAN}╰" + "─" * 65 + f"{RESET}")
            print_tty(f" {BOLD}Select an option [0-8]:{RESET} ", end="")
        else:
            print_tty(f"{CYAN}╭─ {BOLD}{MAGENTA}✨ Nacel{RESET} {CYAN}• {BOLD}Centro de Control y Opciones Disponibles{RESET} {CYAN}" + "─" * 12 + f"{RESET}")
            print_tty(f"{CYAN}│{RESET} Selecciona una opción para ejecutar:")
            print_tty(f"{CYAN}│{RESET}   {CYAN}[1]{RESET} 💬  Chat interactivo           (Conversar directamente con Nacel)")
            print_tty(f"{CYAN}│{RESET}   {CYAN}[2]{RESET} 💡  Consultar comando          (Generar comandos en lenguaje natural)")
            print_tty(f"{CYAN}│{RESET}   {CYAN}[3]{RESET} 🛠️  Diagnosticar último error  (Analizar y reparar último fallo)")
            print_tty(f"{CYAN}│{RESET}   {CYAN}[4]{RESET} 📖  Explicar código o archivo  (Analizar arquitectura y código)")
            print_tty(f"{CYAN}│{RESET}   {CYAN}[5]{RESET} 🐛  Depurar error o traza      (Deducir causa raíz y corregir)")
            print_tty(f"{CYAN}│{RESET}   {CYAN}[6]{RESET} 🌐  Configuración de idioma    (Alternar entre Español e Inglés)")
            print_tty(f"{CYAN}│{RESET}   {CYAN}[7]{RESET} 🤖  Modelo y estado del motor  (Ver modelo activo y estado de Ollama)")
            print_tty(f"{CYAN}│{RESET}   {CYAN}[8]{RESET} 📋  Ver todos los comandos     (Guía completa de atajos y sintaxis)")
            print_tty(f"{CYAN}│{RESET}   {CYAN}[0]{RESET} 🚪  Salir                      (Regresar a la terminal)")
            print_tty(f"{CYAN}╰" + "─" * 65 + f"{RESET}")
            print_tty(f" {BOLD}Selecciona una opción [0-8]:{RESET} ", end="")

        choice = read_key().strip()
        print_tty()

        if choice in ("0", "q", "Q", "ESC"):
            break
        elif choice == "1":
            handle_chat()
            break
        elif choice == "2":
            prompt_text = "Query / Consulta: " if lang == "en" else "Escribe tu consulta o tarea: "
            print_tty(f"{CYAN}❯{RESET} {BOLD}{prompt_text}{RESET}", end="")
            try:
                q = input().strip()
                if q:
                    handle_ask(q)
            except (KeyboardInterrupt, EOFError):
                pass
            break
        elif choice == "3":
            handle_fix("", "1", "")
            break
        elif choice == "4":
            prompt_text = "Enter file path or code snippet: " if lang == "en" else "Ruta del archivo o código a explicar: "
            print_tty(f"{CYAN}❯{RESET} {BOLD}{prompt_text}{RESET}", end="")
            try:
                target = input().strip()
                if target:
                    handle_explain([target])
            except (KeyboardInterrupt, EOFError):
                pass
            break
        elif choice == "5":
            prompt_text = "Enter error message or log file: " if lang == "en" else "Mensaje de error, archivo o traza a depurar: "
            print_tty(f"{CYAN}❯{RESET} {BOLD}{prompt_text}{RESET}", end="")
            try:
                err = input().strip()
                if err:
                    handle_debug([err])
            except (KeyboardInterrupt, EOFError):
                pass
            break
        elif choice == "6":
            handle_lang([])
            lang = ensure_language()
        elif choice == "7":
            handle_model([])
            print_tty(f"\n{DIM}Presiona cualquier tecla para continuar... / Press any key to continue...{RESET}")
            read_key()
        elif choice == "8":
            handle_help()
            print_tty(f"\n{DIM}Presiona cualquier tecla para volver al menú... / Press any key to return...{RESET}")
            read_key()
        else:
            print_tty(f"{YELLOW}Opción no válida / Invalid option.{RESET}")

# ==============================================================================
# ENTRADA PRINCIPAL (CLI)
# ==============================================================================
def main():
    if len(sys.argv) < 2:
        handle_chat()
        return

    command = sys.argv[1].lower()
    args = sys.argv[2:]

    if command in ("menu", "options", "opciones"):
        handle_menu()
    elif command in ("help", "--help", "-h", "commands", "comandos"):
        handle_help()
    elif command in ("model", "models", "status", "info"):
        handle_model(args)
    elif command in ("hardware", "hw", "specs"):
        handle_hardware(args)
    elif command in ("setup-model", "--setup-model"):
        auto_sel = any(a in ("--auto", "-y", "--yes") for a in args)
        no_pull = "--no-pull" in args
        custom_m = ""
        for i, a in enumerate(args):
            if a == "--model" and i + 1 < len(args):
                custom_m = args[i + 1]
        setup_model(interactive=not auto_sel, auto_select=auto_sel, model_override=custom_m, pull_after=not no_pull)
    elif command in ("--recommend-json", "recommend-json"):
        hw = get_system_hardware()
        rec = get_model_recommendation(hw)
        rec["installed_models"] = get_installed_ollama_models()
        sys.stdout.write(json.dumps(rec, indent=2) + "\n")
    elif command in ("lang", "language", "idioma"):
        handle_lang(args)
    elif command in ("get-lang", "lang-code"):
        sys.stdout.write(ensure_language() + "\n")
    elif command == "explain":
        handle_explain(args)
    elif command == "debug":
        handle_debug(args)
    elif command == "chat":
        handle_chat()
    elif command == "ask":
        query = " ".join(args)
        handle_ask(query)
    elif command == "fix":
        cmd = args[0] if len(args) > 0 else ""
        code = args[1] if len(args) > 1 else ""
        err = " ".join(args[2:]) if len(args) > 2 else ""
        handle_fix(cmd, code, err)
    elif command == "query":
        handle_query(args)
    else:
        handle_query(sys.argv[1:])

if __name__ == "__main__":
    main()
