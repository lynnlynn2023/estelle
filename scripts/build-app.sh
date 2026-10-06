#!/bin/zsh
set -euo pipefail

SCRIPT_DIR="${0:A:h}"
PROJECT_DIR="${SCRIPT_DIR:h}"
APP_DIR="${PROJECT_DIR}/dist/艾丝蒂尔桌宠.app"
CONTENTS_DIR="${APP_DIR}/Contents"

cd "${PROJECT_DIR}"

rm -rf "${APP_DIR}"
mkdir -p "${CONTENTS_DIR}/MacOS" "${CONTENTS_DIR}/Resources"
xcrun clang \
    -fobjc-arc \
    -O2 \
    -mmacosx-version-min=13.0 \
    -framework Cocoa \
    -framework QuartzCore \
    "${PROJECT_DIR}/Sources/EstellePet/main.m" \
    -o "${CONTENTS_DIR}/MacOS/EstellePet"
cp "${PROJECT_DIR}/Support/Info.plist" "${CONTENTS_DIR}/Info.plist"
cp "${PROJECT_DIR}"/Sources/EstellePet/Resources/*.png "${CONTENTS_DIR}/Resources/"

chmod +x "${CONTENTS_DIR}/MacOS/EstellePet"
codesign --force --deep --sign - "${APP_DIR}"
echo "${APP_DIR}"
