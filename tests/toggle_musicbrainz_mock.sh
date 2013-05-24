#!/bin/bash
# Usage: $ source toggle_musicbrainz_mock.sh

if [ "$MUSICBRAINZ_MOCK" = "yes" ]; then
    echo "Musicbrainz Mock: OFF"
    export MUSICBRAINZ_MOCK=no
else
    echo "Musicbrainz Mock: ON"
    export MUSICBRAINZ_MOCK=yes
fi  
