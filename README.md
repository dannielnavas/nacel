# 🤖 Nacel - Terminal AI Assistant & Copilot

Nacel es un copiloto de terminal, asistente de desarrollo y diagnóstico de comandos impulsado por IA local (Ollama). Funciona de forma 100% privada y local, sin enviar datos a la nube.

Diseñado con soporte de primer nivel para:
- 🍎 **macOS** (Apple Silicon & Intel, Homebrew)
- 🐧 **CachyOS** & Arch Linux (Pacman, Paru, Yay, kernels optimizados)
- 🐧 **Ubuntu** & Debian (APT, PPAs)
- 🪟 **WSL2** (Windows Subsystem for Linux, interoperabilidad con Windows)

---

## ⚡ Instalación y Carga

### Opción 1: En tus Dotfiles (Recomendada)
En tu archivo `~/.zshrc`:
```zsh
fpath=("$HOME/dotfiles/zsh/plugins/nacel" $fpath)
source "$HOME/dotfiles/zsh/plugins/nacel/nacel.plugin.zsh"
```

### Opción 2: Con Oh-My-Zsh
Clona o enlaza el repositorio en tu carpeta de plugins personalizados:
```bash
git clone https://github.com/dannielnavas/nacel "${ZSH_CUSTOM:-$HOME/.oh-my-zsh/custom}/plugins/nacel"
```
Y añade `nacel` a tu lista de plugins en `~/.zshrc`:
```zsh
plugins=(... nacel)
```

### Opción 3: Con Zinit
```zsh
zinit light dannielnavas/nacel
```

---

## 🚀 Comandos Principales

| Comando | Descripción |
| :--- | :--- |
| `nacel menu` | Menú interactivo con todas las opciones disponibles |
| `nacel` | Abre canal de chat interactivo o repara el último comando que falló |
| `nacel chat` | Inicia canal de conversación continuo con memoria |
| `ask "<consulta>"` | Sugiere comandos de terminal a partir de lenguaje natural |
| `fix` / `Ctrl+G` | Diagnostica la causa raíz y repara el comando que falló |
| `nacel explain <archivo>` | Explica la arquitectura y lógica del código seleccionado |
| `nacel debug <archivo/error>`| Analiza trazas de error y deduce el origen de la anomalía |
| `nacel model [set <nombre>]` | Consulta o cambia el modelo activo (ej: `gemma2:2b`, `qwen2.5-coder:7b`) |
| `nacel lang [es\|en]` | Cambia o consulta el idioma activo (Español / Inglés) |
| `nacel help` | Lista completa de comandos y ayuda |

---

## 🧠 Modelos Recomendados

Nacel se conecta a cualquier modelo instalado en tu Ollama local (`http://localhost:11434`):

- **`gemma2:2b`** *(Recomendado por defecto)*: Ligero (~1.6GB VRAM), ultra rápido y excelente en español y razonamiento conversacional.
- **`qwen2.5-coder:7b`**: El mejor copiloto de programación y comandos de terminal open source.
- **`qwen2.5-coder:1.5b`**: Consumo mínimo (~1GB VRAM) para máquinas con recursos muy limitados.

Para cambiar de modelo en cualquier momento:
```bash
nacel model set gemma2:2b
```

---

## ⚙️ Variables de Entorno y Configuración

Configuración persistente en `~/.config/nacel/config.json`:
```json
{
  "lang": "es",
  "model": "gemma2:2b"
}
```

O variables de entorno en tu shell:
```zsh
export NACEL_MODEL="gemma2:2b"    # Modelo de Ollama a utilizar
export NACEL_AUTO_MODE="ask"      # Modo ante fallos: "ask", "auto" o "hint"
export NACEL_LANG="es"            # Idioma forzado: "es" o "en"
```
