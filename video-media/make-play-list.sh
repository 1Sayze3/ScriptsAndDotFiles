#!/usr/bin/env zsh
links=()
while IFS= read -r line; do
    [[ -n "$line" ]] && links+=("$line")
done < "$HOME/archuserbtw/scripts/video-media/links.txt"
nohup mpv --no-terminal $links >/dev/null 2>&1 & disown
