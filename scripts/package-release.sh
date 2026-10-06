#!/bin/zsh
set -euo pipefail

SCRIPT_DIR="${0:A:h}"
PROJECT_DIR="${SCRIPT_DIR:h}"
APP_PATH="${PROJECT_DIR}/dist/艾丝蒂尔桌宠.app"
RELEASE_DIR="${PROJECT_DIR}/release"
ARCHIVE_PATH="${RELEASE_DIR}/艾丝蒂尔桌宠-macOS-arm64.zip"

"${SCRIPT_DIR}/build-app.sh"
mkdir -p "${RELEASE_DIR}"
rm -f "${ARCHIVE_PATH}"
ditto -c -k --sequesterRsrc --keepParent "${APP_PATH}" "${ARCHIVE_PATH}"

echo "${ARCHIVE_PATH}"
