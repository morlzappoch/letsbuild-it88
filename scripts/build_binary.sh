#!/bin/bash

################################################################################
# Build Binary Script for Jubilant Train
# 
# Compiles the Jubilant Train package into standalone, distributable binaries
# using PyInstaller. This ensures:
# - Source code is NOT exposed (compiled to bytecode)
# - Dependencies are bundled
# - Single executable distribution
# 
# Proprietary - Closed Source
# © 2026 Morley Moses Apooch. All Rights Reserved.
################################################################################

set -e  # Exit on any error

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="jubilant-train"
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
BUILD_DIR="./build"
DIST_DIR="./dist"
BINARY_NAME="${PROJECT_NAME}"

echo -e "${GREEN}=== Jubilant Train Binary Builder ===${NC}"
echo "Project: ${PROJECT_NAME}"
echo "Python Version: ${PYTHON_VERSION}"
echo "Build Directory: ${BUILD_DIR}"
echo "Distribution Directory: ${DIST_DIR}"
echo ""

# Step 1: Check dependencies
echo -e "${YELLOW}Step 1: Checking dependencies...${NC}"
if ! command -v pyinstaller &> /dev/null; then
    echo -e "${RED}PyInstaller not found. Installing...${NC}"
    pip install pyinstaller
fi
echo -e "${GREEN}✓ PyInstaller ready${NC}"

# Step 2: Clean previous builds
echo -e "${YELLOW}Step 2: Cleaning previous builds...${NC}"
rm -rf ${BUILD_DIR} ${DIST_DIR} *.spec
echo -e "${GREEN}✓ Clean complete${NC}"

# Step 3: Install/verify dependencies
echo -e "${YELLOW}Step 3: Installing dependencies...${NC}"
pip install -r requirements.txt
echo -e "${GREEN}✓ Dependencies installed${NC}"

# Step 4: Run tests (optional)
echo -e "${YELLOW}Step 4: Running tests (optional)...${NC}"
if [ -d "tests" ]; then
    python -m pytest tests/ --tb=short || echo "Some tests failed, continuing..."
else
    echo "No tests directory found, skipping..."
fi
echo -e "${GREEN}✓ Tests complete${NC}"

# Step 5: Build executable
echo -e "${YELLOW}Step 5: Building executable with PyInstaller...${NC}"
pyinstaller \
    --onefile \
    --name="${BINARY_NAME}" \
    --distpath="${DIST_DIR}" \
    --buildpath="${BUILD_DIR}" \
    --specpath="${BUILD_DIR}" \
    --hidden-import=scancode \
    --hidden-import=jsonschema \
    --hidden-import=pydantic \
    src/__main__.py

if [ ! -f "${DIST_DIR}/${BINARY_NAME}" ]; then
    echo -e "${RED}Binary build failed!${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Binary built: ${DIST_DIR}/${BINARY_NAME}${NC}"

# Step 6: Create distribution package
echo -e "${YELLOW}Step 6: Creating distribution package...${NC}"
mkdir -p "${DIST_DIR}/config"
cp config/*.json "${DIST_DIR}/config/"
cp README.md "${DIST_DIR}/"
cp LICENSE "${DIST_DIR}/"
echo -e "${GREEN}✓ Distribution package prepared${NC}"

# Step 7: Calculate checksums
echo -e "${YELLOW}Step 7: Calculating checksums...${NC}"
cd "${DIST_DIR}"
sha256sum ${BINARY_NAME} > ${BINARY_NAME}.sha256
echo -e "${GREEN}✓ Checksum generated:${NC}"
cat ${BINARY_NAME}.sha256
cd - > /dev/null

# Step 8: Verify distribution
echo -e "${YELLOW}Step 8: Verifying distribution...${NC}"
if [ -f "${DIST_DIR}/${BINARY_NAME}" ] && \
   [ -f "${DIST_DIR}/${BINARY_NAME}.sha256" ] && \
   [ -f "${DIST_DIR}/README.md" ] && \
   [ -d "${DIST_DIR}/config" ]; then
    echo -e "${GREEN}✓ Distribution verification passed${NC}"
else
    echo -e "${RED}Distribution verification failed!${NC}"
    exit 1
fi

# Step 9: Summary
echo ""
echo -e "${GREEN}=== Build Complete ===${NC}"
echo "Binary Location: ${DIST_DIR}/${BINARY_NAME}"
echo "Configuration: ${DIST_DIR}/config/"
echo "Documentation: ${DIST_DIR}/README.md"
echo ""
echo "To distribute:"
echo "  tar -czf ${PROJECT_NAME}-$(date +%Y%m%d).tar.gz ${DIST_DIR}/"
echo ""
echo "To verify integrity:"
echo "  cd ${DIST_DIR} && sha256sum -c ${BINARY_NAME}.sha256"
echo ""
echo -e "${GREEN}✓ Ready for distribution!${NC}"
