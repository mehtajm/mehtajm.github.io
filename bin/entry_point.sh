#!/bin/bash
set -euo pipefail

echo "Entry point script running"

JEKYLL_PID=""

prepare_bundle() {
    git config --global --add safe.directory '*'
    echo "Preparing Bundler configuration"
    bundle config unset without || true
    bundle config set with "jekyll_plugins other_plugins"
    bundle config set path /usr/local/bundle
    echo "Installing and syncing Ruby dependencies"
    bundle install --jobs 4 --retry 3
}

compute_site_state() {
    find . -type f \
        -not -path './.git/*' \
        -not -path './_site/*' \
        -not -path './node_modules/*' \
        -not -path './vendor/*' \
        -not -path './.bundle/*' \
        -not -path './.jekyll-cache/*' \
        -printf '%p %T@\n' | sort | sha256sum | awk '{print $1}'
}

start_jekyll() {
    echo "Clearing Jekyll cache"
    rm -rf .jekyll-cache .sass-cache
    bundle exec jekyll serve --port=8080 --host=0.0.0.0 --livereload --verbose --trace --force_polling --config _config.yml &
    JEKYLL_PID=$!
}

restart_jekyll() {
    if [[ -n "${JEKYLL_PID}" ]] && kill -0 "${JEKYLL_PID}" 2>/dev/null; then
        kill "${JEKYLL_PID}" 2>/dev/null || true
        wait "${JEKYLL_PID}" 2>/dev/null || true
    fi
    start_jekyll
}

prepare_bundle
start_jekyll

last_state=$(compute_site_state)

while true; do
    sleep 2
    current_state=$(compute_site_state)
    if [[ "$current_state" != "$last_state" ]]; then
        echo "Change detected in site files, restarting Jekyll"
        restart_jekyll
        last_state="$current_state"
    fi
done
