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
fpath=("$HOME/nacel" $fpath)
source "$HOME/nacel/nacel.plugin.zsh"
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
| `nacel hardware` | Diagnostica tu hardware (CPU, RAM, GPU) y recomienda el modelo ideal |
| `nacel model [set <nombre>]` | Consulta o cambia el modelo activo (ej: `qwen2.5-coder:7b`, `gemma2:2b`) |
| `nacel model auto` | Auto-detecta y configura el mejor modelo para tu equipo |
| `nacel model recommend` | Asistente interactivo guiado de selección de modelos |
| `nacel lang [es\|en]` | Cambia o consulta el idioma activo (Español / Inglés) |
| `nacel help` | Lista completa de comandos y ayuda |

---

## 🧠 Detección Inteligente de Hardware y Modelos

Durante la instalación, Nacel analiza automáticamente las especificaciones de tu máquina (memoria RAM, núcleos de CPU, aceleración GPU/Metal/CUDA) y selecciona el mejor modelo disponible para tu equipo:

| Perfil de Hardware | Modelo Recomendado | Características |
| :--- | :--- | :--- |
| **Gama Alta (Ultra)**<br>*(VRAM ≥ 12GB o Apple Silicon ≥ 24GB)* | **`qwen2.5-coder:14b`** | Máxima profundidad lógica y razonamiento de arquitectura (~9.0GB) |
| **Equilibrado / Desarrollador (Pro)**<br>*(Apple Silicon ≥ 8GB, GPU ≥ 6GB o RAM ≥ 14GB)* | **`qwen2.5-coder:7b`** ⭐ *(Recomendado)* | El estándar de oro: precisión quirúrgica en bash, git, docker y corrección de sintaxis (~4.7GB) |
| **Ligero y Rápido (Light)**<br>*(RAM 6GB - 12GB sin GPU dedicada)* | **`qwen2.5-coder:3b`** ⚡ | Respuesta instantánea, excelente precisión y bajo consumo (~2.0GB) |
| **Conversacional**<br>*(Cualquier equipo ≥ 4GB RAM)* | **`gemma2:2b`** 💬 | Ultraligero de Google, excelente en lenguaje natural y explicaciones (~1.6GB) |
| **Ultraligero (Minimal)**<br>*(Equipos ajustados, RAM ≤ 4GB)* | **`qwen2.5-coder:1.5b`** 🪶 | Mínimo impacto de memoria (~1.0GB RAM) para entornos modestos o VPS |

Para ver el diagnóstico de hardware de tu equipo y la recomendación en cualquier momento:
```bash
nacel hardware
```

Para auto-ajustar Nacel al mejor modelo según tu equipo:
```bash
nacel model auto
```

O para cambiar a cualquier modelo manualmente:
```bash
nacel model set qwen2.5-coder:7b
```

---

## ⚙️ Variables de Entorno y Configuración

Configuración persistente en `~/.config/nacel/config.json`:
```json
{
  "lang": "es",
  "model": "qwen2.5-coder:7b"
}
```

O variables de entorno en tu shell:
```zsh
export NACEL_MODEL="qwen2.5-coder:7b"  # Modelo de Ollama a utilizar (opcional, sobrescribe config.json)
export NACEL_AUTO_MODE="ask"           # Modo ante fallos: "ask", "auto" o "hint"
export NACEL_LANG="es"                 # Idioma forzado: "es" o "en"
```
