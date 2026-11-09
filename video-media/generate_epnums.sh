#!/usr/bin/env zsh
outfile="$HOME/archuserbtw/scripts/video-media/epnum.txt"
: > "$outfile"
n=$1
a=$2
for (( i=n, j=1; i<n+a; i++, j++ )); do
	print "$j $i" >> "$outfile"
done
