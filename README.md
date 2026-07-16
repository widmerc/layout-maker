# Layout Maker — QGIS Plugin

> Professional, consistent, print-ready map layouts at the click of a button.

![QGIS Version](https://img.shields.io/badge/QGIS-3.x%20%7C%204.x-green)
![Qt](https://img.shields.io/badge/Qt-5%20%7C%206-blue)
![Python](https://img.shields.io/badge/Python-3.x-blue)
![License](https://img.shields.io/badge/License-GPL--2.0-orange)

---

## What it does

**Layout Maker** automates the creation of print-ready map layouts. Instead of manually drawing map frames and placing fold marks, the plugin handles everything for you.
Open the dialog, choose your settings, click Start, and get a finished layout based on your title block template directly in the QGIS Layout Manager.

Perfect for GIS professionals who regularly produce maps for clients, reports, or internal documentation.
---

## Features

- **Falzmarken** (fold marks) — set or remove fold marks on an existing print layout, grid size configurable (default A4)
- **Plan erstellen** — build a brand-new layout either by drawing a map extent or from a predefined paper size, with an optional **Plankopf** (title block) attached to any corner and the map area filling the rest automatically
- **Interactive extent tool** to select the map area on the canvas
- **Multi-language UI** (German, English, French)
- **Paper formats** A0–A4 and custom sizes
- **Settings dialog** for plugin-wide preferences (e.g. fold mark grid size)
- **Built-in help page** (Hilfe button in the main dialog)
- **Qt5 & Qt6 compatible** — works in both QGIS 3.x and QGIS 4.x

---

## Installation

**Via Plugin Manager (recommended):**
1. Open QGIS 3.x or 4.x
2. Go to **Plugins → Manage and Install Plugins**
3. Search for **Layout Maker** and click **Install**

**Manually from ZIP:**
1. Download the latest release from the [Releases page](https://github.com/widmerc/layout-maker/releases)
2. In QGIS: **Plugins → Manage and Install Plugins → Install from ZIP**

**Requirements:** QGIS 3.16+ or QGIS 4.0+, Windows / macOS / Linux. No additional Python packages needed.

---

## Usage

1. Open a QGIS project with at least one layer
2. Click **Plugins → Layout Maker** or use the toolbar icon
3. Pick **Falzmarken** (to set/remove fold marks on an existing layout) or **Plan erstellen** (to build a new one)
4. For a new plan: draw an extent on the map or pick a predefined paper size, set the scale, optionally attach a Plankopf template, then confirm
5. The layout opens in the QGIS Layout Manager — ready to export as PDF or image

---

## Changelog

### v0.3.0
- **QGIS 3.x support** — tested and compatible with QGIS 3.16+
- **Qt5 & Qt6 dual support** — runs on both QGIS 3 (Qt5) and QGIS 4 (Qt6)
- `metadata.txt` updated with `supportsQt6=True` and correct version range

### v0.2.0
- Fold marks with configurable line width
- Multi-language support (i18n)
- Logo embedding
- UI rework and Qt6 compatibility
- Multiple paper formats (A0–A5 and custom)

### v0.1.0
- Initial release: A4 layout generation with UI dialog

---

## Planned & Ideas

Things that could go into future versions — open an [issue](https://github.com/widmerc/layout-maker/issues) if you want to see something prioritised.

**Templates & Styles**
- Save and load layout templates (logo position, fold marks, scale bar style)
- Manage multiple templates (e.g. "Client Presentation", "Internal Report", "Field Use")
- Store company CI (colors, fonts, logo path) once, reuse everywhere

**Map Elements**
- Auto scale bar proportional to map size
- North arrow (selectable style, free positioning)
- Auto legend showing only visible layers
- Title block with project name, date, author, scale as fillable fields

**Export**
- One-click PDF export without opening the Layout Manager
- Batch export of all layouts to PDF
- Selectable DPI (150 / 300 / 600)
- Auto-generated filenames (e.g. `ProjectName_Date_Scale.pdf`)

**Atlas & Automation**
- Atlas support — generate one layout per feature (e.g. one map per municipality)
- Multi-layer export — one layout per layer, exported in one step

**UI**
- Live preview in the dialog
- Layout panel docked in the main QGIS window
- Remember last used settings

**Further ideas**
- Custom logo embedding
- QR code in the layout (link to project or online map)
- Coordinate grid / graticule with labels
- Multiple map frames (overview map + detail map on one sheet)
- Stamp field with digital signature for planning documents
- Print series by attribute (e.g. all municipalities, all building projects)
- Export to GeoPDF (with embedded layers), SVG, georeferenced TIFF
- Dynamic labels from layer attributes (title and metadata filled from feature attributes)
- Built-in sanity check — warn if layers are hidden, CRS mismatch, or extent is empty
- Dark mode UI support
- Drag-and-drop element positioning in dialog preview
- WMS/WCS background layer support in layout
- Paper roll formats for large-format plotters
- Watermark / draft stamp overlay
- Automatic CRS labelling in the layout
- Support for multi-page layouts (e.g. title page + map pages)

---

## Contributing

Pull requests are welcome. Please:
- Keep the code simple and readable — no unnecessary dependencies
- Test changes with QGIS 3.x and 4.x
- Open an [issue](https://github.com/widmerc/layout-maker/issues) first for larger changes

---

## Author

**Claude Widmer**
<br>Geographer & GIS enthusiast<br>
GitHub: [@widmerc](https://github.com/widmerc)<br>
PersonalWebsite: [https://www.claudewidmer.ch/](https://www.claudewidmer.ch/)

---

## License

Free software under the [GNU General Public License v2 or later](https://www.gnu.org/licenses/gpl-2.0.html).
