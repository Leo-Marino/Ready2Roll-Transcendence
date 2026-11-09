#!/bin/sh
set -e
cd "$(dirname "$0")"

[ -f index.html ] && [ -d src/vue ] || { echo "Run this from srcs/frontend"; exit 1; }

# 1) Create public/fonts directory and auto-import Giphurs if downloaded in ~/Downloads or current dir
mkdir -p public/fonts src/assets

for z in ./[Gg]iphurs*.zip "$HOME/Downloads"/[Gg]iphurs*.zip; do
  if [ -f "$z" ]; then
    echo "Found $z -> extracting to public/fonts/..."
    unzip -o -j "$z" "*.ttf" "*.otf" "*.woff2" -d public/fonts/ 2>/dev/null || true
  fi
done

for f in ./[Gg]iphurs*.ttf ./[Gg]iphurs*.otf ./[Gg]iphurs*.woff2 \
         "$HOME/Downloads"/[Gg]iphurs*.ttf "$HOME/Downloads"/[Gg]iphurs*.otf "$HOME/Downloads"/[Gg]iphurs*.woff2; do
  if [ -f "$f" ]; then
    cp "$f" public/fonts/
  fi
done

# 2) Update index.html: Keep Bruno Ace for Ready2Roll + load 100/200/300/400 fallback weights
sed -i -E 's#family=[^"]+#family=Bruno+Ace\&family=Outfit:wght@100;200;300;400\&display=swap#' index.html

# 3) Generate @font-face rules dynamically if Giphurs files exist in public/fonts/
cat > src/assets/fonts.css <<'EOF'
/* Auto-loaded Giphurs local/downloaded fonts */
EOF

for fontfile in public/fonts/*[Gg]iphurs*; do
  if [ -f "$fontfile" ]; then
    fname=$(basename "$fontfile")
    weight="100 900"
    case "$fname" in
      *[Tt]hin*) weight="100" ;;
      *[Ee]xtra[Ll]ight*|*[Uu]ltra[Ll]ight*) weight="200" ;;
      *[Ll]ight*) weight="300" ;;
      *[Rr]egular*) weight="400" ;;
    esac
    cat >> src/assets/fonts.css <<EOF
@font-face {
  font-family: "Giphurs";
  src: url("/fonts/$fname");
  font-weight: $weight;
  font-style: normal;
  font-display: swap;
}
EOF
  fi
done

# 4) Write all weight rules (100, 200, 300, 400) + keep Ready2Roll in Bruno Ace
cat >> src/assets/fonts.css <<'EOF'
:root {
  --font-logo: "Bruno Ace", sans-serif;
  --font-main: "Giphurs", "Outfit", sans-serif;
  --font-body: "Giphurs", "Outfit", sans-serif;
  --font-display: "Giphurs", "Outfit", sans-serif;
}

body, button, input, textarea, select {
  font-family: var(--font-main) !important;
  font-weight: 300;
}

/* 🔒 Ready2Roll Logo ONLY -> Bruno Ace */
.logo,
.logo-text,
.logo span {
  font-family: var(--font-logo) !important;
  font-weight: bold !important;
}

/* 1️⃣ Giphurs Thin 100 -> Video & Event Descriptions */
.event-description-truncated,
.stats-desc,
.viewer-desc,
.preview-desc,
.video-description,
.event-description,
.video-desc,
.event-desc,
.description-box,
.description-box p,
.user-text p,
.video-info p,
.event-info p {
  font-family: var(--font-main) !important;
  font-weight: 100 !important;
}

/* 2️⃣ Giphurs ExtraLight 200 -> Comments & Messages */
.message-text,
.message-bubble,
.contact-last-msg,
.chat-input-area input,
.rc-bubble,
.rc-input,
.rc-chip,
.comment-text,
.comment-content,
.comment-body,
.comments-list li,
.comments-list p,
.txt span {
  font-family: var(--font-main) !important;
  font-weight: 200 !important;
}

/* 3️⃣ Giphurs Light 300 -> Names of Users */
.name-row h2,
.user-text strong,
.user-text small,
.contact-name,
.user-link span,
.follow-item span,
.preview-username,
.owner-name,
.comment-author,
.comment-user,
.txt strong {
  font-family: var(--font-main) !important;
  font-weight: 300 !important;
}

/* 4️⃣ Giphurs Regular 400 -> 3anawin (Titles & Headings) */
h1,
h2:not(.name-row h2),
h3,
h4,
.page-title,
.results-title,
.section-title,
.event-title,
.card-title,
.preview-title,
.chat-header h2,
.panel-head,
.rc-title,
.modal-header h3 {
  font-family: var(--font-main) !important;
  font-weight: 400 !important;
}
EOF

# 5) Ensure fonts.css is imported at the bottom of main.js so it overrides component styles
sed -i '/fonts\.css/d' src/main.js
sed -i "/import App/a import './assets/fonts.css'" src/main.js

# 6) Clean up hardcoded fonts in .vue files (except Bruno Ace on .logo-text)
sed -i '/jf-openhuninn\.css/d' src/vue/*.vue
sed -i -E \
  -e "s/'jf-openhuninn', 'Huninn', sans-serif/var(--font-main)/g" \
  -e "s/['\"]Huninn['\"], sans-serif/var(--font-main)/g" \
  -e "s/font-family: Huninn;/font-family: var(--font-main);/g" \
  -e "s/font-family: sans-serif/font-family: var(--font-main)/g" \
  src/vue/*.vue

echo "✅ Fonts updated successfully!"
ls -1 public/fonts/
