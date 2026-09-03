# Jubilant Train 🚂

**Owner:** Morley Moses Apooch  
**Origin:** Yorkton, Saskatchewan, Canada  
**Status:** Proprietary / Closed Source / AI-Compliant  
**License:** Proprietary (See [LICENSE](LICENSE))

## Overview
`Jubilant Train` is a secure, automated pipeline designed to prepare, sanitize, and validate code and data for AI-assisted development and model training. It enforces the **MoProtect Methodology** to ensure all outputs are free from incompatible open-source licenses (GPL/AGPL) and properly disclose AI usage.

## Key Features
- **License Sanitization:** Automatically scans inputs for prohibited licenses and flags or removes non-compliant components.
- **AI Disclosure Injection:** Ensures every generated artifact includes the mandatory human-AI authorship statement.
- **Local-First Processing:** All data processing happens on-premise; no data leaves your machine.
- **Audit Trail Generation:** Produces immutable JSON logs of every scan and modification for legal evidence.
- **Compliance Validation:** Checks for WIPO, copyright, and AI disclosure requirements before deployment.

## The MoProtect Integration
This tool implements the 4-step MoProtect Protocol:

1. **Disclosure:** Auto-inserts AI usage headers into all generated code.
2. **Sanitization:** Filters out GPL/AGPL code and flagged dependencies.
3. **Human Assertion:** Validates human review checkpoints and sign-offs.
4. **Sealing:** Hashes final artifacts for timestamping and legal evidence.

See [mo_protect_protocol.md](docs/mo_protect_protocol.md) for full methodology details.

## Quick Start

### Installation
```bash
pip install -r requirements.txt
```

### Basic Usage

**Sanitize a file or directory:**
```bash
python -m jubilant_train.sanitizer --input ./src --output ./sanitized
```

**Run compliance validation:**
```bash
python -m jubilant_train.validator --check ./output
```

**Generate audit log:**
```bash
python -m jubilant_train.sanitizer --input ./src --audit audit.json
```

## Project Structure
```
jubilant-train/
├── README.md                          # This file
├── LICENSE                            # Proprietary License
├── .gitignore                         # Git exclusion rules
├── requirements.txt                   # Python dependencies
├── src/
│   ├── __init__.py                   # Package initialization
│   ├── sanitizer.py                  # License & content sanitizer
│   ├── validator.py                  # AI disclosure & compliance checker
│   └── trainer.py                    # (Optional) Local model fine-tuning
├── config/
│   ├── allowed_licenses.json         # Whitelist of compatible licenses
│   └── banned_patterns.json          # Blacklist of prohibited patterns
├── docs/
│   ├── mo_protect_protocol.md        # MoProtect methodology
│   └── audit_log_template.md         # Audit log specification
└── scripts/
    ├── build_binary.sh               # PyInstaller compilation script
    └── run_audit.sh                  # ScanCode wrapper for dependency audit
```

## Legal Notice
This software is **proprietary and closed-source**. The source code is provided only for authorized users under the Proprietary License. Reverse engineering, unauthorized distribution, or misuse is prohibited and subject to legal action.

**AI Disclosure:** This project was developed with AI-assisted tools in compliance with the MoProtect methodology. All outputs include mandatory disclosure statements.

**Intellectual Property:** Protected under the Berne Convention, Canadian Copyright Act, and WIPO agreements.

© 2026 Morley Moses Apooch. All Rights Reserved.

## Support & Contributions
This is a closed-source project. Contributions are not accepted. For support, contact the project owner.

## License
See [LICENSE](LICENSE) for full terms.