#!/usr/bin/env zsh




cd "$1"
echo "Querying LRCLIB database for synchronized lyrics..."
for track in *.opus; do
        [ -e "$track" ] || continue
        
        
        title=$(ffprobe -v error -show_entries stream_tags=title -of default=noprint_wrappers=1:nokey=1 "$track")
        artist=$(ffprobe -v error -show_entries stream_tags=artist -of default=noprint_wrappers=1:nokey=1 "$track")

        if [ -n "$title" ] && [ -n "$artist" ]; then
            echo "Searching LRCLIB for: $artist - $title"
            
            # Step A: Try direct exact lookup first
            lyric_data=$(curl -s -G --data-urlencode "artist=$artist" --data-urlencode "title=$title" "https://lrclib.net/api/get")
            lyrics=$(echo "$lyric_data" | jq -r '.syncedLyrics // .plainLyrics' 2>/dev/null)

            # Step B: Fallback to global search endpoint if direct lookup returned nothing or null
            if [ -z "$lyrics" ] || [ "$lyrics" = "null" ]; then
                echo " -> Strict match failed. Trying global fuzzy search..."
                lyric_data=$(curl -s -G --data-urlencode "q=$artist $title" "https://lrclib.net/api/search")
                lyrics=$(echo "$lyric_data" | jq -r '.[0].syncedLyrics // .[0].plainLyrics' 2>/dev/null)
            fi

            # Step C: If lyrics are found anywhere, save as a .lrc file matching the audio file name
            if [ -n "$lyrics" ] && [ "$lyrics" != "null" ]; then
                # Strip the .opus extension and append .lrc
                lrc_file="${track%.opus}.lrc"

                echo " -> Lyrics found! Injecting metadata and saving to $lrc_file..."
                # 1. Write the mandatory matching tags rmpc requires to the top of the file
                echo "[ar:$artist]" > "$lrc_file"
                echo "[ti:$title]" >> "$lrc_file"
                echo "$lyrics" >> "$lrc_file"
            else
                echo " -> No lyrics found on LRCLIB database via fallback search."
            fi
        fi
done
echo "All tracks processed! Informing MPD..."
mpc update
cd
