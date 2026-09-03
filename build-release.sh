#!/bin/bash

# ==============================================================================
# CLEAN HANDS CLEAN MONEY - SOVEREIGN BUILD SCRIPT
# Owner: Morley Moses Apooch
# Protocol: Global Asset Protection Lock v1.0
# ==============================================================================

set -e # Exit immediately if a command exits with a non-zero status

echo "🔒 Initializing Sovereign Build Process..."
echo "Owner Verification: Morley Moses Apooch"

# 1. Clean Previous Builds
echo "🧹 Cleaning previous build artifacts..."
rm -rf android/app/build
rm -rf ios/build
rm -rf release/

# 2. Verify Ownership (Security Check)
echo "🔍 Verifying Ownership Lock..."
if ! grep -q "Morley Moses Apooch" src/security/morley_lock.js; then
    echo "❌ CRITICAL ERROR: Owner mismatch detected in morley_lock.js!"
    echo "Aborting build to prevent unauthorized distribution."
    exit 1
fi
echo "✅ Ownership Verified."

# 3. Install Dependencies (If needed)
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install
fi

# 4. Build Android APK with Obfuscation
echo "🚀 Building Obfuscated Android Release..."
mkdir -p release

# Command breakdown:
# --release: Production build
# --obfuscate: Renames classes/methods to prevent reverse engineering
# --split-debug-info: Saves symbols locally ONLY (NEVER uploaded)
flutter build apk --release \
  --obfuscate \
  --split-debug-info=release/debug_symbols \
  --target-platform android-arm64

# 5. Move APK to Release Folder
mv android/app/build/outputs/apk/release/app-release.apk release/clean-hands-clean-money-v1.0.apk

# 6. Generate SHA-256 Hash for Evidence
echo "🔐 Generating Cryptographic Evidence..."
HASH=$(sha256sum release/clean-hands-clean-money-v1.0.apk | awk '{print $1}')
echo "Build Hash: $HASH"

# Save hash to a local evidence file (Keep this offline!)
echo "{\"file\": \"clean-hands-clean-money-v1.0.apk\", \"hash\": \"$HASH\", \"owner\": \"Morley Moses Apooch\", \"timestamp\": \"$(date -Iseconds)\"}" > release/evidence_package.json

# 7. Final Status
echo ""
echo "✅ BUILD COMPLETE"
echo "----------------------------------------"
echo "Artifact: release/clean-hands-clean-money-v1.0.apk"
echo "Evidence: release/evidence_package.json"
echo "Debug Symbols: release/debug_symbols/ (KEEP OFFLINE)"
echo "----------------------------------------"
echo "⚠️ WARNING: DO NOT UPLOAD 'debug_symbols' TO ANY SERVER."
echo "⚠️ WARNING: This build is signed for Sovereign Distribution ONLY."
echo ""
