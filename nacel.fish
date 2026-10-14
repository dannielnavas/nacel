# ==============================================================================
# NACEL FISH PLUGIN
# Asistente Lógico de Terminal, Copiloto de IA y Diagnóstico Inteligente.
# Soporte nativo para Fish Shell en macOS, Linux y WSL2.
# ==============================================================================

# 1. Resolución dinámica del script principal de Nacel
set -l current_dir (path dirname (status filename))

if test -f "$current_dir/nacel.py"
    set -gx __NACEL_SCRIPT "$current_dir/nacel.py"
else if test -f "$HOME/nacel/nacel.py"
    set -gx __NACEL_SCRIPT "$HOME/nacel/nacel.py"
else if test -f "$HOME/.nacel/nacel.py"
    set -gx __NACEL_SCRIPT "$HOME/.nacel/nacel.py"
else if test -f "$HOME/.local/bin/nacel"
    set -gx __NACEL_SCRIPT "$HOME/.local/bin/nacel"
else
    set -gx __NACEL_SCRIPT "nacel"
end

# Si DILIX_MODEL está definido y NACEL_MODEL no, sincronizarlo
if set -q DILIX_MODEL; and not set -q NACEL_MODEL
    set -gx NACEL_MODEL "$DILIX_MODEL"
end

# Modo ante fallos ("ask", "auto", "hint")
if not set -q NACEL_AUTO_MODE
    if set -q DILIX_AUTO_MODE
        set -gx NACEL_AUTO_MODE "$DILIX_AUTO_MODE"
    else
        set -gx NACEL_AUTO_MODE "ask"
    end
end

# ==============================================================================
# 2. FUNCIONES INTERNAS
# ==============================================================================

function __nacel_get_lang
    if set -q NACEL_LANG
        echo $NACEL_LANG
        return
    end
    set -l cfg "$HOME/.config/nacel/config.json"
    if test -f $cfg
        set -l l (grep -o '"lang": *"[^"]*"' $cfg 2>/dev/null | cut -d'"' -f4)
        if test -n "$l"
            echo $l
            return
        end
    end
    echo "es"
end

function __nacel_run_action
    set -l action_type $argv[1]
    set -l cmd $argv[2]

    switch $action_type
        case EXEC
            if test -n "$cmd"
                echo -e "\033[1;32m▶ Running / Ejecutando:\033[0m $cmd"
                eval $cmd
            end
        case MODIFY
            if test -n "$cmd"
                commandline -r "$cmd"
            end
        case CANCEL
        case '*'
    end
end

# ==============================================================================
# 3. COMANDOS PRINCIPALES (ask, fix, nacel)
# ==============================================================================

function ask -d "Nacel: Sugiere comandos de terminal en lenguaje natural"
    if test (count $argv) -eq 0
        set -l lang (__nacel_get_lang)
        if test "$lang" = "en"
            echo -e "\033[1;33mUsage:\033[0m ask \"your natural language query\""
            echo -e "Example: ask \"how to list listening ports\""
        else
            echo -e "\033[1;33mUso:\033[0m ask \"tu consulta aquí\""
            echo -e "Ejemplo: ask \"como ver puertos en uso\""
        end
        return 1
    end

    set -l output (python3 "$__NACEL_SCRIPT" ask $argv)
    set -l action (string split -m 1 ":" -- $output)[1]
    set -l cmd (string split -m 1 ":" -- $output)[2]
    __nacel_run_action "$action" "$cmd"
end

function fix -d "Nacel: Diagnostica y corrige el comando fallido previo"
    set -l target_cmd "$__NACEL_LAST_CMD"
    set -l exit_code "$__NACEL_LAST_CODE"
    if test -z "$exit_code"
        set exit_code 1
    end
    set -l user_extra "$argv"

    if test -z "$target_cmd" -a -z "$user_extra"
        set -l lang (__nacel_get_lang)
        if test "$lang" = "en"
            echo -e "\033[1;33m💡 No recent failed commands for Nacel to analyze.\033[0m"
        else
            echo -e "\033[1;33m💡 No hay comandos fallidos recientes para que Nacel analice.\033[0m"
        end
        return 0
    end

    set -g __NACEL_CMD_ACTIVE ""

    set -l output (python3 "$__NACEL_SCRIPT" fix "$target_cmd" "$exit_code" "$user_extra")
    set -l action (string split -m 1 ":" -- $output)[1]
    set -l cmd (string split -m 1 ":" -- $output)[2]
    __nacel_run_action "$action" "$cmd"
end

function nacel -d "Nacel: Asistente de IA y Copiloto de Terminal"
    if test (count $argv) -eq 0
        if test -n "$__NACEL_LAST_CMD" -a "$__NACEL_LAST_CODE" -ne 0 2>/dev/null
            fix
        else
            python3 "$__NACEL_SCRIPT" chat
        end
        return
    end

    set -l subcmd $argv[1]
    set -l remaining $argv[2..-1]

    switch $subcmd
        case menu options opciones
            python3 "$__NACEL_SCRIPT" menu $remaining
        case lang language idioma
            python3 "$__NACEL_SCRIPT" lang $remaining
        case model models status info
            python3 "$__NACEL_SCRIPT" model $remaining
        case hardware hw specs
            python3 "$__NACEL_SCRIPT" hardware $remaining
        case explain code
            python3 "$__NACEL_SCRIPT" explain $remaining
        case debug
            python3 "$__NACEL_SCRIPT" debug $remaining
        case chat
            python3 "$__NACEL_SCRIPT" chat $remaining
        case fix
            fix $remaining
        case ask
            ask $remaining
        case help --help -h commands comandos
            python3 "$__NACEL_SCRIPT" help $remaining
        case '*'
            set -l output (python3 "$__NACEL_SCRIPT" query $argv)
            set -l action (string split -m 1 ":" -- $output)[1]
            set -l cmd (string split -m 1 ":" -- $output)[2]
            if test "$action" = "EXEC" -o "$action" = "MODIFY" -o "$action" = "CANCEL"
                __nacel_run_action "$action" "$cmd"
            end
    end
end

# Alias y compatibilidad retrospectiva
alias nacel-menu="nacel menu"
alias nacel-options="nacel menu"
alias nacel-help="nacel help"
alias dilix="nacel"
alias dilix-menu="nacel menu"
alias dilix-options="nacel menu"
alias dilix-help="nacel help"

# ==============================================================================
# 4. ATAJOS DE TECLADO INTERACTIVOS
# ==============================================================================
if status is-interactive
    bind \cg fix
end

# ==============================================================================
# 5. HOOK AUTOMÁTICO ANTE FALLOS (fish_postexec)
# ==============================================================================
function __nacel_postexec --on-event fish_postexec
    set -l last_status $status
    set -l cmd $argv[1]

    # No registrar comandos propios de Nacel
    string match -rq '^(nacel|fix|ask|dilix|__nacel)' -- $cmd; and return

    set -g __NACEL_LAST_CMD "$cmd"
    set -g __NACEL_LAST_CODE $last_status

    if test $last_status -ne 0 -a $last_status -ne 130 -a $last_status -ne 148
        set -l mode $NACEL_AUTO_MODE
        test -z "$mode"; and set mode "ask"
        set -l lang (__nacel_get_lang)

        if test "$lang" = "en"
            switch $mode
                case auto
                    echo ""
                    fix
                case ask
                    echo ""
                    read -n 1 -P (set_color red)"╭─ ❌ Failed ($last_status) "(set_color yellow)"• "(set_color -o cyan)"Analyze with Nacel? [y/N] (or press Ctrl+G): "(set_color normal) reply
                    echo ""
                    if string match -ri '^[ys]$' -- $reply
                        fix
                    end
                case hint '*'
                    echo (set_color red)"╭─ ❌ Failed with exit code $last_status "(set_color yellow)"• "(set_color cyan)"Type "(set_color -o)"nacel"(set_color normal)(set_color cyan)" or "(set_color -o)"fix"(set_color normal)(set_color cyan)" to analyze or press "(set_color -o)"[Ctrl+G]"(set_color normal)
            end
        else
            switch $mode
                case auto
                    echo ""
                    fix
                case ask
                    echo ""
                    read -n 1 -P (set_color red)"╭─ ❌ Falló ($last_status) "(set_color yellow)"• "(set_color -o cyan)"¿Analizar con Nacel? [s/N] (o pulsa Ctrl+G): "(set_color normal) reply
                    echo ""
                    if string match -ri '^[sy]$' -- $reply
                        fix
                    end
                case hint '*'
                    echo (set_color red)"╭─ ❌ Falló con código $last_status "(set_color yellow)"• "(set_color cyan)"Escribe "(set_color -o)"nacel"(set_color normal)(set_color cyan)" o "(set_color -o)"fix"(set_color normal)(set_color cyan)" para analizar o pulsa "(set_color -o)"[Ctrl+G]"(set_color normal)
            end
        end
    end
end
