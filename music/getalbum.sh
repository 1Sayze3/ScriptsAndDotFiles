#!/bin/env zsh
yt-dlp \
    -f "ba/b" \
    -x \
    --audio-format opus \
    --audio-quality 0 \
    --embed-metadata \
    --parse-metadata "%(playlist_index,track_number|)s:%(meta_track)s" \
    --parse-metadata "artist:(?P<artist>[^,]+)" \
    -P "$HOME/Music/" \
    -o "%(playlist_channel,channel,uploader)s/%(album)s/%(title)s.%(ext)s" \
    --no-config-locations --no-lazy-playlist --no-windows-filenames "$@"
