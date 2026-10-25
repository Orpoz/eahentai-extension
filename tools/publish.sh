#!/bin/bash
# Regenerates the store from the last build and pushes it to the `repo` branch.
# Usage: tools/publish.sh "commit message"
set -e
TOOLS="$(cd "$(dirname "$0")" && pwd)"
STORE=/c/eabuild/store            # a clone of this repository checked out on the `repo` branch
cd "$STORE"
git pull -q
python -I "$TOOLS/make_store.py" /c/eabuild/extensions-source/src/en/eahentai/build . "$(cat /c/eabuild/signing/cert.sha256)" > /dev/null
git add -A
git commit -m "${1:-Update store}"
git push
