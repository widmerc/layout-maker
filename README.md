# Layout Maker — QGIS 4 Plugin

> Kartenlayouts auf Knopfdruck — professionell, einheitlich, druckfertig.

![QGIS Version](https://img.shields.io/badge/QGIS-4.x-green)
![Python](https://img.shields.io/badge/Python-3.x-blue)
![License](https://img.shields.io/badge/License-GPL--2.0-orange)

---

## Was macht dieses Plugin?

**Layout Maker** nimmt dir die mühsame Handarbeit beim Erstellen von Drucklayouts ab. Statt jedes Mal von Null anzufangen — Kartenrahmen ziehen, Logo einfügen, Faltmarken setzen, Massstab anpassen — erledigt das Plugin all das automatisch. Du öffnest den Dialog, wählst deine Einstellungen, klickst auf **Start** — und bekommst ein druckfertiges A4-Layout direkt im QGIS Layout-Manager.

Ideal für GIS-Fachleute, die täglich oder wöchentlich Karten für Kunden, Berichte oder interne Ablage erstellen müssen.

---

## Was kann das Plugin heute?

- **Automatisches A4-Layout** — Mit einem Klick wird ein vollständiges Drucklayout aus deiner aktuellen Kartenansicht erstellt
- **Faltmarken (Faltmarken)** — Präzise Faltmarkierungen werden automatisch gesetzt, die Strichstärke ist einstellbar
- **Eigenes Logo** — Dein Logo (`icons/logo.png`) wird automatisch ins Layout eingebettet
- **Kartenausschnitt wählen** — Mit dem integrierten Ausschnitt-Werkzeug kannst du den Kartenbereich interaktiv auf dem Canvas festlegen
- **Mehrsprachigkeit** — Die Benutzeroberfläche ist übersetzbar (Deutsch, Englisch und weitere Sprachen via `i18n/`)
- **Papierformate** — A0 bis A5 sowie benutzerdefinierte Grössen werden unterstützt
- **Hoch- und Querformat** — Ausrichtung frei wählbar
- **Einfaches UI** — Klarer Qt6-Dialog ohne unnötige Komplexität

---

## So wird das Plugin installiert

### Empfehlung: Über den QGIS Plugin-Manager

1. QGIS 4 öffnen
2. **Plugins → Erweiterungen verwalten und installieren**
3. Nach **Layout Maker** suchen
4. Auf **Installieren** klicken — fertig

### Manuell als ZIP

1. Neueste Version als ZIP von der [Releases-Seite](https://github.com/widmerc/layout-maker/releases) herunterladen
2. In QGIS: **Plugins → Erweiterungen verwalten und installieren → Aus ZIP installieren**
3. ZIP-Datei auswählen und installieren

---

## So wird das Plugin verwendet

1. Ein QGIS 4-Projekt mit mindestens einem Layer öffnen
2. **Plugins → Layout Maker** anklicken oder das Symbol in der Werkzeugleiste verwenden
3. Im Dialog die gewünschten Einstellungen vornehmen:
   - Kartenausschnitt mit dem Ausschnitt-Werkzeug interaktiv auf der Karte festlegen
   - Papierformat und Ausrichtung wählen
   - Faltmarkenstärke anpassen
4. Auf **Start** klicken
5. Das Layout öffnet sich im QGIS-Layoutmanager — bereit zum Export als PDF oder Bild

**Systemvoraussetzungen:** QGIS 4.0 oder neuer (Qt6), Windows / macOS / Linux. Keine zusätzlichen Python-Pakete nötig.

---

## Was wir als nächstes einbauen wollen

Diese Ideen stammen aus der Analyse ähnlicher Plugins ([AutoLayoutTool](https://plugins.qgis.org/plugins/AutoLayoutTool/), [Quick Print Layout Creator](https://plugins.qgis.org/plugins/quickprintlayoutcreator/), [Maps Printer](https://gisplugins.com/plugins/mapsprinter/), [Layout Panel](https://plugins.qgis.org/plugins/layout_panel-main/), [Exportar Layouts a PDF](https://plugins.qgis.org/plugins/exportar_layouts/)) sowie aus Kundenfeedback.

### Vorlagen & Templates

- **Layout-Vorlagen speichern und laden** — Einmal konfigurierten Stil (Logo-Position, Faltmarken, Massstabsbalken) als Vorlage speichern und bei jedem neuen Projekt wieder laden; ähnlich wie beim Quick Print Layout Creator
- **Mehrere Vorlagen verwalten** — z. B. «Kundenpräsentation», «Interner Bericht», «Feldeinsatz»
- **Unternehmens-CI direkt im Plugin** — Farben, Schriften und Logo-Pfad einmalig hinterlegen, nicht pro Layout neu setzen

### Karten-Elemente

- **Automatischer Massstabsbalken** — wird proportional zur Kartengrösse gesetzt (wie AutoLayoutTool)
- **Nordpfeil** — frei positionierbar, aus einer Auswahl an Stilen
- **Automatische Legende** — nur sichtbare Layer werden aufgeführt, Stil anpassbar
- **Titelblock / Beschriftungsfeld** — Projekttitel, Datum, Bearbeiter, Massstab als ausfüllbare Felder

### Export

- **Direkt-Export als PDF** — ohne Umweg über den Layout-Manager, ein Klick genügt
- **Batch-Export mehrerer Layouts** — alle vorhandenen Layouts in einem Schritt als PDF exportieren (Maps Printer / Exportar Layouts a PDF)
- **Auflösung wählbar** — 150 / 300 / 600 dpi für verschiedene Verwendungszwecke
- **Dateiname automatisch generieren** — z. B. `Projektname_Datum_Massstab.pdf`

### Automatisierung & Atlas

- **Atlas-Unterstützung** — Layout automatisch für jeden Feature einer Vektorebene generieren (z. B. eine Karte pro Gemeinde oder Parzelle); inspiriert von QGIS Atlas und Quick Print Layout Creator
- **Mehrere Layer gleichzeitig** — Pro Layer ein eigenes Layout erstellen und alle auf einmal exportieren

### Benutzeroberfläche

- **Vorschau im Dialog** — Miniaturvorschau des Layouts direkt im Einstellungsdialog
- **Layout-Panel im Hauptfenster** — Schneller Zugriff auf alle Layouts ohne den Layout-Manager zu öffnen (wie Layout Panel Plugin)
- **Zuletzt verwendete Einstellungen merken** — Dialog öffnet mit den letzten gewählten Werten

---

## Feature-Requests: Was sich unsere Kunden wünschen könnten

Die folgenden Ideen sind noch nicht geplant, aber naheliegende Anfragen aus der Praxis. Wer diese Funktion braucht, kann gerne ein [Issue auf GitHub](https://github.com/widmerc/layout-maker/issues) eröffnen.

- **QR-Code im Layout** — Link zum Projekt oder zu Online-Karte direkt ins Drucklayout einbetten
- **Koordinatengitter / Graticule** — optionales Gitternetz mit Koordinatenbeschriftung für technische Karten
- **Mehrere Kartenrahmen** — z. B. Übersichtskarte + Detailkarte auf demselben Blatt
- **Stempelfeld mit digitaler Signatur** — für Planungsdokumente, die einen Visumsstempel benötigen
- **Druckserien nach Attribut** — Karten automatisch für alle Werte eines bestimmten Attributfeldes (z. B. alle Kantone, alle Bauprojekte) erzeugen
- **Export in andere Formate** — GeoPDF (mit eingebetteten Layern), SVG, georeferenziertes TIFF
- **Beschriftung dynamisch aus Layerattributen** — Kartentitel und Metadaten werden automatisch aus den Attributen des gewählten Features befüllt
- **Integrierter Plausibilitätscheck** — Warnung wenn Layer ausgeblendet, CRS nicht übereinstimmt oder Kartenausschnitt leer ist

---

## Bekannte Einschränkungen

- Erfordert QGIS 4.0+ (Qt6). Nicht kompatibel mit QGIS 3.x (Qt5).
- Derzeit kein automatisierter Test-Suite; manuelle Tests in QGIS 4.

---

## Changelog

### v0.2.0
- Faltmarken mit konfigurierbarer Strichstärke
- Mehrsprachigkeit (i18n)
- Logo-Einbettung
- UI-Überarbeitung und Qt6-Kompatibilität
- Mehrere Papierformate (A0–A5 und benutzerdefiniert)

### v0.1.0
- Erste Version: A4-Layout-Generierung mit UI-Dialog

---

## Mitmachen

Pull Requests sind willkommen. Bitte:
- Code einfach und lesbar halten — keine unnötigen Abhängigkeiten
- Änderungen mit QGIS 4.x testen
- Bei grösseren Änderungen zuerst ein [Issue](https://github.com/widmerc/layout-maker/issues) eröffnen

---

## Autor

**Claude Widmer**  
Geograph & GIS-Enthusiast, Universität Zürich  
GitHub: [@widmerc](https://github.com/widmerc)

---

## Lizenz

Dieses Plugin ist freie Software unter der [GNU General Public License v2 oder später](https://www.gnu.org/licenses/gpl-2.0.html).
