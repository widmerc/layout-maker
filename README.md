# Layout Maker — QGIS 4 Plugin

> A QGIS 4 plugin for automated print layout creation with fold marks, multi-language support, and an intuitive UI dialog.

![QGIS Version](https://img.shields.io/badge/QGIS-4.x-green)
![Python](https://img.shields.io/badge/Python-3.x-blue)
![License](https://img.shields.io/badge/License-GPL--2.0-orange)

---

## Overview

**Layout Maker** is a lightweight QGIS 4 plugin (Qt6) that automates the creation of print-ready map layouts. It provides a clean UI dialog to generate A4 layouts with fold marks (*Faltmarken*), set fold mark thickness, and supports multiple languages via true i18n.

The plugin is intentionally simple — no bloat, pure Python, no external dependencies beyond QGIS itself.

---

## Features

- 🗺️ **Automatic A4 Layout Generation** — Creates a complete print layout from your current map view with one click
- 📐 **Fold Marks (Faltmarken)** — Adds precise fold marks to your layout, configurable in thickness
- 🌍 **Multi-language Support (i18n)** — Fully internationalized; translations live in `i18n/`
- 🖼️ **Custom Logo** — Embeds your logo (`icons/logo.png`) automatically into the layout
- 🎛️ **UI Dialog** — Clean Qt6-based dialog with a start button and layout options
- 📦 **Extent Tool** — Helper tool to capture the current map extent for layout framing

---

## Requirements

| Requirement | Version |
|---|---|
| QGIS | 4.0 or higher |
| Python | 3.x (bundled with QGIS) |
| Qt | 6.x (via QGIS 4) |
| OS | Windows, macOS, Linux |

No additional Python packages are required.

---

## Installation

### From QGIS Plugin Manager (recommended)

1. Open QGIS 4
2. Go to **Plugins → Manage and Install Plugins**
3. Search for **Layout Maker**
4. Click **Install**

### Manual Installation (ZIP)

1. Download the latest release ZIP from the [Releases page](https://github.com/widmerc/layout-maker/releases)
2. In QGIS: **Plugins → Manage and Install Plugins → Install from ZIP**
3. Select the downloaded ZIP file and click **Install Plugin**

### From Source

```bash
# Clone the repository
git clone https://github.com/widmerc/layout-maker.git

# Copy the folder into your QGIS plugins directory:
# Windows: %APPDATA%\QGIS\QGIS3\profiles\default\python\plugins\
# macOS:   ~/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/
# Linux:   ~/.local/share/QGIS/QGIS3/profiles/default/python/plugins/

cp -r layout-maker ~/.local/share/QGIS/QGIS3/profiles/default/python/plugins/layout_maker
```

Then activate the plugin in **Plugins → Manage and Install Plugins**.

---

## Usage

1. Open a QGIS 4 project with at least one layer loaded
2. Go to **Plugins → Layout Maker** or click the Layout Maker icon in the toolbar
3. The UI dialog opens — configure your layout options:
   - Set the map extent (use the **Extent Tool** to capture it interactively)
   - Adjust fold mark thickness
   - Choose your output format
4. Click **Start** to generate the layout
5. The layout opens in the QGIS Print Layout Manager, ready for export (PDF, image, etc.)

---

## Repository Structure

```
layout-maker/
├── __init__.py                  # Plugin entry point
├── layout_maker.py              # Main plugin class (toolbar action, menu entry)
├── layout_maker_dialog.py       # UI dialog logic
├── layout_maker.ui              # Qt Designer UI file
├── dialogs.py                   # Additional dialog helpers
├── layout_template_script.py    # Core layout generation logic
├── faltmarken_script.py         # Fold marks (Faltmarken) drawing logic
├── extent_tool.py               # Map canvas extent capture tool
├── metadata.txt                 # QGIS plugin metadata
├── i18n/                        # Translation files (.ts / .qm)
│   └── ...
├── icons/                       # Plugin icons and logo
│   └── logo.png
└── README.md                    # This file
```

---

## Development

### Running Tests

Currently no automated test suite. Testing is done manually in QGIS 4.

### Adding a Translation

1. Add a new `.ts` file in `i18n/` for your language (e.g., `layout_maker_de.ts`)
2. Use Qt Linguist or `pylupdate6` to update strings
3. Compile with `lrelease` to generate `.qm` files
4. The plugin loads translations automatically based on the QGIS locale setting

### Contributing

Pull requests are welcome. Please:
- Keep the code simple and readable — no unnecessary dependencies
- Test changes with QGIS 4.x before submitting
- Open an [issue](https://github.com/widmerc/layout-maker/issues) first for larger changes

---

## Known Issues & Limitations

- Requires QGIS 4.0+ (Qt6). Not compatible with QGIS 3.x (Qt5).
- The A4 format is currently fixed — other paper sizes are planned for a future release.

---

## Changelog

### v0.2.0
- Added fold marks (Faltmarken) with configurable thickness
- Added i18n/multi-language support
- Added custom logo embedding
- UI cleanup and Qt6 compatibility

### v0.1.0
- Initial release: basic A4 layout generation with UI dialog

---

## Author

**Claude Widmer**  
GIS enthusiast & geographer, University of Zurich  
GitHub: [@widmerc](https://github.com/widmerc)

---

## License

This plugin is free software; you can redistribute it and/or modify it under the terms of the [GNU General Public License](https://www.gnu.org/licenses/gpl-2.0.html) as published by the Free Software Foundation, version 2 or later.
