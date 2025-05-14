export EDITOR=vim

export PATH="/app/venv/bin:/app/bin:$PATH"

export TORTOISE_ORM=config.core.tortoise_db.TORTOISE_ORM

alias ll='ls -lhG'
alias l='ll'
alias ..='cd ..'
alias ...='cd ../..'
alias ....='cd ../../..'
alias po='poetry'
alias py='poetry run python3'
alias console='/app/bin/console'
alias myip='echo $(curl -s https://ifconfig.me)'
