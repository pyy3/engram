# Bash completion for engram
# Add to ~/.bashrc: source ~/.engram/completions/engram.bash

_engram_completions() {
    local cur prev commands
    COMPREPLY=()
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"

    commands="init start end search sync index qdrant hooks template status version help"

    case "$prev" in
        engram)
            COMPREPLY=($(compgen -W "$commands" -- "$cur"))
            return 0
            ;;
        qdrant)
            COMPREPLY=($(compgen -W "download start stop status logs" -- "$cur"))
            return 0
            ;;
        hooks)
            COMPREPLY=($(compgen -W "install remove status" -- "$cur"))
            return 0
            ;;
        template)
            COMPREPLY=($(compgen -W "create list install info" -- "$cur"))
            return 0
            ;;
        search)
            COMPREPLY=($(compgen -W "--chunks --json --global --since --root" -- "$cur"))
            return 0
            ;;
        sync)
            COMPREPLY=($(compgen -W "--dry-run --all" -- "$cur"))
            return 0
            ;;
        index)
            COMPREPLY=($(compgen -W "--incremental --status --reset" -- "$cur"))
            return 0
            ;;
        init)
            COMPREPLY=($(compgen -W "--template" -- "$cur"))
            return 0
            ;;
        --template)
            # List available templates
            local templates_dir="${ENGRAM_HOME:-$HOME/.engram}/templates"
            if [ -d "$templates_dir" ]; then
                COMPREPLY=($(compgen -W "$(ls "$templates_dir" 2>/dev/null)" -- "$cur"))
            fi
            return 0
            ;;
    esac
}

complete -F _engram_completions engram
