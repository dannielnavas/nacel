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
    """Prioridad: NACEL_MODEL > config.json['model'] > DILIX_MODEL > gemma2:2b."""
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
    return "gemma2:2b"

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
        cfg["model"] = "gemma2:2b"
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

def read_key():
    if not sys.stdin.isatty():
        try:
            ch = sys.stdin.read(1)
            return ch if ch else "q"
        except Exception:
            return "q"

    try:
        with open("/dev/tty", "r") as tty:
            import tty as tty_module
            import termios
            fd = tty.fileno()
            old_settings = termios.tcgetattr(fd)
            try:
                tty_module.setraw(fd)
                ch = tty.read(1)
                if ch == "\x1b":
                    import select
                    r, _, _ = select.select([tty], [], [], 0.05)
                    if r:
                        tty.read(2)
                        return "ESC"
                    return "q"
                return ch
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    except Exception:
        try:
            line = input()
            return line.strip()[:1] if line.strip() else "\r"
        except Exception:
            return "q"

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

def copy_to_clipboard(text: str) -> bool:
    system = platform.system().lower()
    is_wsl = (
        "microsoft" in platform.uname().release.lower()
        or "wsl" in platform.uname().release.lower()
        or os.path.exists("/mnt/c/Windows")
    )
    try:
        if system == "darwin":
            p = subprocess.Popen(["pbcopy"], stdin=subprocess.PIPE)
            p.communicate(text.encode("utf-8"))
            return p.returncode == 0
        elif is_wsl and subprocess.run(["which", "clip.exe"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode == 0:
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
            elif is_wsl:
                p = subprocess.Popen(["clip.exe"], stdin=subprocess.PIPE)
                p.communicate(text.encode("utf-8"))
                return p.returncode == 0
    except Exception:
        pass
    return False

def get_os_info() -> str:
    system = platform.system().lower()
    is_wsl = (
        "microsoft" in platform.uname().release.lower()
        or "wsl" in platform.uname().release.lower()
        or os.path.exists("/mnt/c/Windows")
    )

    if system == "darwin":
        return f"macOS ({platform.mac_ver()[0]})"
    elif system == "linux" or is_wsl:
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

def get_terminal_scrollback(lines=30) -> str:
    """
    Captura de scrollback inteligente multiplataforma:
    1. WezTerm nativo (macOS/Linux)
    2. WezTerm en WSL2 (wezterm.exe)
    3. Tmux capture-pane
    4. Kitty get-text
    """
    # 1. WezTerm nativo
    try:
        res = subprocess.run(
            ["wezterm", "cli", "get-text", "--start-line", f"-{lines}"],
            capture_output=True, text=True, timeout=1
        )
        if res.returncode == 0 and res.stdout.strip():
            raw_lines = [l.strip() for l in res.stdout.splitlines() if l.strip()]
            return "\n".join(raw_lines[-20:])
    except Exception:
        pass

    # 2. WezTerm en WSL2 (interoperabilidad con Windows)
    try:
        res = subprocess.run(
            ["wezterm.exe", "cli", "get-text", "--start-line", f"-{lines}"],
            capture_output=True, text=True, timeout=1
        )
        if res.returncode == 0 and res.stdout.strip():
            raw_lines = [l.strip() for l in res.stdout.splitlines() if l.strip()]
            return "\n".join(raw_lines[-20:])
    except Exception:
        pass

    # 3. Tmux
    if os.environ.get("TMUX"):
        try:
            res = subprocess.run(
                ["tmux", "capture-pane", "-p", "-S", f"-{lines}"],
                capture_output=True, text=True, timeout=1
            )
            if res.returncode == 0 and res.stdout.strip():
                raw_lines = [l.strip() for l in res.stdout.splitlines() if l.strip()]
                return "\n".join(raw_lines[-20:])
        except Exception:
            pass

    # 4. Kitty
    if os.environ.get("KITTY_PID"):
        try:
            res = subprocess.run(
                ["kitty", "@", "get-text", "--extent", "screen"],
                capture_output=True, text=True, timeout=1
            )
            if res.returncode == 0 and res.stdout.strip():
                raw_lines = [l.strip() for l in res.stdout.splitlines() if l.strip()]
                return "\n".join(raw_lines[-20:])
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

def handle_model(args: list):
    cfg = load_config()

    if len(args) >= 2 and args[0].lower() in ("set", "use"):
        new_model = args[1].strip()
        cfg["model"] = new_model
        save_config(cfg)
        print_tty(f"{GREEN}✔ Modelo establecido a:{RESET} {CYAN}{BOLD}{new_model}{RESET}")
        print_tty(f"{DIM}Guardado en ~/.config/nacel/config.json{RESET}")
        return

    # Si se pasa un argumento directo como modelo (ej: nacel model gemma2:2b)
    if len(args) == 1 and args[0].lower() not in ("list", "status"):
        new_model = args[0].strip()
        cfg["model"] = new_model
        save_config(cfg)
        print_tty(f"{GREEN}✔ Modelo establecido a:{RESET} {CYAN}{BOLD}{new_model}{RESET}")
        return

    handle_status()
    print_tty(f"\n{BOLD}💡 Modelos recomendados para Nacel:{RESET}")
    print_tty(f"  • {GREEN}gemma2:2b{RESET}         -> Ultraligero, rápido y excelente en conversación/español")
    print_tty(f"  • {GREEN}qwen2.5-coder:7b{RESET}  -> El mejor copiloto de programación y comandos terminal")
    print_tty(f"  • {GREEN}qwen2.5-coder:1.5b{RESET}-> Mínimo consumo de recursos (~1GB VRAM)")
    print_tty(f"\n{DIM}Para cambiar de modelo ejecuta: nacel model set <nombre_del_modelo>{RESET}")

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
        error_content = get_terminal_scrollback(30)
        source = "Terminal scrollback"

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
    if not last_cmd.strip():
        print_tty(f"{YELLOW}{t('no_error_found')}{RESET}")
        sys.stdout.write("CANCEL:\n")
        return

    scrollback = error_msg.strip() if error_msg.strip() else get_terminal_scrollback(25)
    print_tty(f"{DIM}✨ Nacel {t('processing_fix', model=model)}{RESET}")

    if lang == "en":
        prompt = f"""{t('persona')}
Environment Context:
Operating System: {get_os_info()}
Current directory: {os.getcwd()}

The following terminal command just failed:
Command executed: {last_cmd}
Exit code: {last_code}
Terminal output / error trace context:
{scrollback}

Analyze the logical cause of failure and formulate the exact correction.
Respond ONLY in this valid JSON format:
{{
  "causa": "Direct 1-sentence logical explanation of why it failed in English.",
  "que_hacer": "Clear, concise instruction of what to do in English.",
  "comando": "Exact corrected executable terminal command, no markdown, no quotes"
}}"""
    else:
        prompt = f"""{t('persona')}
Contexto del entorno:
Sistema Operativo: {get_os_info()}
Directorio actual: {os.getcwd()}

El siguiente comando de terminal acaba de fallar:
Comando ejecutado: {last_cmd}
Código de salida (exit code): {last_code}
Contexto / Salida de error de terminal:
{scrollback}

Analiza la causa lógica del fallo y formula la corrección exacta.
Responde ÚNICAMENTE en este formato JSON válido:
{{
  "causa": "Explicación directa de 1 frase del por qué falló de manera lógica en español.",
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
    lines = [
        f"{BOLD}🖥️ Sistema Operativo / OS:{RESET} {CYAN}{os_info}{RESET}",
        f"{BOLD}🤖 Modelo de IA / Model:{RESET} {CYAN}{model}{RESET}",
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
        code = args[1] if len(args) > 1 else "1"
        err = " ".join(args[2:]) if len(args) > 2 else ""
        handle_fix(cmd, code, err)
    elif command == "query":
        handle_query(args)
    else:
        handle_query(sys.argv[1:])

if __name__ == "__main__":
    main()
