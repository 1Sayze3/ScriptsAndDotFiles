#!/bin/env zsh

cd "$HOME/Music" || { echo "Music directory not found"; exit; }

echo "Runnin..."

find . -type f \( -name "cover.jpg" -o -name "cover.jpeg" -o -name "cover.png" \) | while read -r cover_file; do
    dir=$(dirname "$cover_file")

    for f in "$dir"/*.opus; do
        if [ -f "$f" ]; then
            opustags --set-cover "$cover_file" -i "$f"
        fi
    done
done

echo "Completed."
