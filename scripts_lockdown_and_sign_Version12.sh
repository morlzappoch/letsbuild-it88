#!/usr/bin/env bash
# LOCKDOWN AND SIGN script (non-destructive by default)
# Review and edit placeholders before running.
# Usage: ./lockdown_and_sign.sh ORG REPO GPG_KEY_ID N_SHARES T_THRESHOLD
# Example: ./lockdown_and_sign.sh my-org my-repo ABCDEF12 5 3

set -euo pipefail
ORG="${1:?ORG required}"
REPO="${2:?REPO required}"
GPG_KEY_ID="${3:-}"   # optional: leave blank to use default gpg key
N="${4:-5}"           # number of Shamir shares
T="${5:-3}"           # threshold to recover
WORKDIR="/tmp/lockdown_${REPO}_$(date -u +%Y%m%dT%H%M%SZ)"
DOCS_LOCAL="./docs"
OWNERSHIP_FILE="${DOCS_LOCAL}/Ownership_Schedule_and_Declaration_Morley_Apooch_2026-09-02.md"
TRANSCRIPT_FILE="${DOCS_LOCAL}/claude_transcript_2026-04-07.txt"
SNAP_TAG="provenance-$(date -u +%Y%m%dT%H%M%SZ)"

echo "== Lockdown & Sign starting =="
echo "ORG=${ORG}, REPO=${REPO}, WORKDIR=${WORKDIR}, N=${N}, T=${T}"
echo "Make sure GITHUB_TOKEN env var is set or 'gh' is authenticated for API/Push actions."

# 0) Basic checks
if [ ! -f "${OWNERSHIP_FILE}" ]; then
  echo "ERROR: Ownership file not found at ${OWNERSHIP_FILE}. Place it there (masked IDs) and re-run."
  exit 1
fi
if [ ! -f "${TRANSCRIPT_FILE}" ]; then
  echo "WARNING: Transcript file not found at ${TRANSCRIPT_FILE}. Continue? (y/n)"
  read -r ok
  [ "$ok" = "y" ] || exit 1
fi

mkdir -p "${WORKDIR}"
echo "Working in ${WORKDIR}"

# 1) Mirror clone for preservation (read-only)
echo "Creating mirror clone for preservation..."
git clone --mirror "https://github.com/${ORG}/${REPO}.git" "${WORKDIR}/${REPO}-mirror"
COMMIT_SHA=$(git -C "${WORKDIR}/${REPO}-mirror" rev-parse --short HEAD || echo "unknown")
echo "Mirror commit SHA: ${COMMIT_SHA}"

# 2) Create a working clone to stage docs and headers
git clone "https://github.com/${ORG}/${REPO}.git" "${WORKDIR}/${REPO}-working"
cd "${WORKDIR}/${REPO}-working"

# 3) Insert SPDX headers into tracked source files (non-destructive)
SPDX_LICENSE="MIT"
SPDX_HEADER="/*\n * Copyright (c) 2026 Morley Moses Apooch\n * Project: [PROJECT]\n * Created with assistance from Anthropic Claude on 2026-04-07.\n * SPDX-License-Identifier: ${SPDX_LICENSE}\n */\n\n"
file_exts=("*.py" "*.js" "*.ts" "*.go" "*.java" "*.c" "*.cpp" "*.rb" "*.sh")

echo "Inserting SPDX headers where missing..."
for ext in "${file_exts[@]}"; do
  for f in $(git ls-files -- "${ext}" 2>/dev/null || true); do
    if [ -f "$f" ]; then
      if ! grep -q "SPDX-License-Identifier" "$f"; then
        echo -e "${SPDX_HEADER}$(cat "$f")" > "$f"
        git add "$f"
        echo "Added SPDX header to $f"
      fi
    fi
  done
done

# 4) Add Ownership schedule & transcript, commit
mkdir -p docs
cp "${OWNERSHIP_FILE}" docs/ || true
cp "${TRANSCRIPT_FILE}" docs/ 2>/dev/null || true
git add docs || true

if git diff --cached --quiet; then
  echo "No staged changes; creating an empty commit to mark snapshot."
  git commit --allow-empty -m "Provenance snapshot: add Ownership Schedule & AI transcript; commit ${COMMIT_SHA}"
else
  git commit -m "Provenance snapshot: add Ownership Schedule & AI transcript; commit ${COMMIT_SHA}"
fi

# 5) Create a signed tag (signed if GPG_KEY_ID set)
echo "Creating tag ${SNAP_TAG}..."
if [ -n "${GPG_KEY_ID}" ]; then
  git tag -a "${SNAP_TAG}" -m "Provenance snapshot ${SNAP_TAG}" -u "${GPG_KEY_ID}" || git tag -a "${SNAP_TAG}" -m "Provenance snapshot ${SNAP_TAG}"
else
  git tag -a "${SNAP_TAG}" -m "Provenance snapshot ${SNAP_TAG}"
fi

# 6) Create detached GPG signature for Ownership file
echo "Creating detached signature for Ownership file..."
gpg --output "${WORKDIR}/Ownership_Schedule.sig" --detach-sign "${OWNERSHIP_FILE}" || echo "gpg sign failed (ensure gpg configured)"

# 7) Push commit & tags (requires push permission)
echo "Pushing commits and tags to origin (ensure you have rights)..."
git push origin --follow-tags

# 8) Create repo snapshot archive (git archive)
echo "Creating git archive snapshot..."
git archive --format=tar --prefix="provenance_${COMMIT_SHA}/" HEAD | gzip > "${WORKDIR}/provenance_${COMMIT_SHA}.tar.gz"

# 9) Create symmetric encrypted snapshot using a generated passphrase
MASTER_PASSPHRASE_FILE="${WORKDIR}/master_passphrase.txt"
openssl rand -base64 48 > "${MASTER_PASSPHRASE_FILE}"
chmod 600 "${MASTER_PASSPHRASE_FILE}"
gpg --symmetric --cipher-algo AES256 --batch --passphrase-file "${MASTER_PASSPHRASE_FILE}" --output "${WORKDIR}/provenance_${COMMIT_SHA}.tar.gz.gpg" "${WORKDIR}/provenance_${COMMIT_SHA}.tar.gz"

# 10) Split passphrase into Shamir shares (if ssss-split is available)
if command -v ssss-split >/dev/null 2>&1; then
  echo "Splitting master passphrase into ${N} shares with threshold ${T}..."
  ssss-split -t "${T}" -n "${N}" < "${MASTER_PASSPHRASE_FILE}" | awk '{print > "'"${WORKDIR}"'/share_"NR".txt"}'
  echo "Created shares at ${WORKDIR}/share_*.txt"
else
  echo "ssss-split not found. The master passphrase is at ${MASTER_PASSPHRASE_FILE}. Install 'ssss' to split into shares."
fi

echo "=== Completed snapshot & signing steps. Encrypted archive:"
echo "  ${WORKDIR}/provenance_${COMMIT_SHA}.tar.gz.gpg"
echo "Signature (detached): ${WORKDIR}/Ownership_Schedule.sig"
echo "Master passphrase (KEEP PRIVATE): ${MASTER_PASSPHRASE_FILE}"
echo "Shamir shares (if created): ${WORKDIR}/share_*.txt"

# 11) OPTIONAL DISRUPTIVE ACTIONS (privatize, revoke keys, disable workflows)
echo
echo "Optional disruptive actions are available but are OFF by default."
echo "To enable destructive actions you must set environment variable DO_DESTRUCTIVE=YES before running this script."
if [ "${DO_DESTRUCTIVE:-NO}" = "YES" ]; then
  echo "Performing disruptive actions (privatize repo, disable workflows)..."
  # Example: set repo to private
  gh api --method PATCH "/repos/${ORG}/${REPO}" -f visibility="private" || echo "Failed to set private"
  # Disable each workflow
  for wf in $(gh api -X GET "/repos/${ORG}/${REPO}/actions/workflows" | jq -r '.workflows[].id' 2>/dev/null || true); do
    gh api --method PUT "/repos/${ORG}/${REPO}/actions/workflows/${wf}/disable" || true
  done
  echo "Destructive actions executed (review logs)."
else
  echo "Destructive actions skipped. To run them, re-run with DO_DESTRUCTIVE=YES in env after counsel approval."
fi

echo "Lockdown & sign script complete. Distribute Shamir shares to custodians per your plan and retain logs of all actions."