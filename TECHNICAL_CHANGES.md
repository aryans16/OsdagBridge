# OsdagBridge LaTeX Report Generator Refactoring & Technical Report

**Project:** OsdagBridge Plugin — LaTeX Design Report Generator  
**Organization:** FOSSEE, Indian Institute of Technology Bombay (IIT Bombay)  
**Author:** Aryan  
**Branch:** `dev`  

---

## 1. Executive Summary

This report documents the architectural refactoring, typographical enhancements, and data visualization additions implemented in the **OsdagBridge** LaTeX report generation module. 

The previous report generator presented several layout and visual defects, including missing repeated table headers across page boundaries, content bleeding into footer margins (notably the "G4" girder block on page 30), merged vehicle and footway load tables lacking standardized unit columns, absence of graphical summaries for utilization ratios and material quantities, and hardcoded layout parameters scattered across multiple scripts.

The implementation addresses the six numbered areas in the task brief. Vehicle rows follow the active UI selections; when a requested value cannot be calculated from the current input model, the report identifies it as unavailable instead of substituting a sample value. The saved `Report_After.pdf` still needs to be regenerated from a fresh design run after these code changes.

---

## 2. Specific Files Altered & Created

| File Path | Status | Primary Purpose & Modifications |
|---|:---:|---|
| `src/osdagbridge/core/reports/styles.py` | **Created** | Dedicated single source of truth for color palettes, document geometry, cell padding, row heights, and standardized `longtable` header generators. |
| `src/osdagbridge/core/reports/visualizations.py` | **Created** | Automated headless Matplotlib plotting module for Utilization Ratios (with $UR = 1.0$ red dashed limit) and Material Take-off bar charts. |
| `src/osdagbridge/core/reports/report_generator.py` | **Modified** | Updated LaTeX preamble with centralized geometry (expanded bottom margin & footskip buffer), refined `fancyhdr` footrules, and wired chart generation pipelines. |
| `src/osdagbridge/core/reports/chap2.py` | **Modified** | Refactored multi-page input tables (Typical Section, Components, Girders, Bracing, End Diaphragms, Shear Connectors) to use standardized repeated headers. |
| `src/osdagbridge/core/reports/chap3.py` | **Modified** | Separated Vehicle Live Loads and Footway Live Loads into distinct tables; structured vehicle parameters with unit columns (Total Load, Impact Factor, Braking Load parameters); implemented repeated headers. |
| `src/osdagbridge/core/reports/chap4.py` | **Modified** | Standardized `Reactions at Supports` and `Deflection Summary` tables with `longtable` continuation headers. |
| `src/osdagbridge/core/reports/chap5.py` | **Modified** | Embedded dynamic Utilization Ratio summary chart into Section 5.5; implemented page-break threshold controls between girder blocks to eliminate the G4 footer overlap defect; standardized Table 5.1 through Table 5.22 with repeated headers. |
| `src/osdagbridge/core/reports/chap6.py` | **Modified** | Replaced a hardcoded figure width with a shared style macro. |
| `src/osdagbridge/core/reports/chap7.py` | **Modified** | Embedded Structural Steel Tonnage breakdown chart and Concrete Volume vs. Reinforcement Weight chart; upgraded Bill of Materials (Table 7.1) to use repeated headers. |
| `src/osdagbridge/core/reports/chap8.py` | **Modified** | Replaced hardcoded colors and local table padding with shared style definitions. |

---

## 3. Architecture of Centralized Style Module (`styles.py`)

To eliminate hardcoded formatting parameters scattered across disparate chapter generators, `styles.py` was introduced as the unified styling configuration.

### 3.1 Architecture Overview

```
styles.py (Single Source of Truth)
│
├── ColorPalette (dataclass)
│   ├── Brand: OSDAG_GREEN (#91B014), OSDAG_GREEN_DARK (#64850C), OSDAG_GREEN_LIGHT (#EAF2D3)
│   ├── Structural: STEEL_BLUE (#2B5B84), CONCRETE_GRAY (#7F8C8D)
│   ├── Status: PASS (#27AE60), WARN (#F39C12), FAIL (#C0392B)
│   └── Neutral: TEXT_MAIN, BORDER_GRAY, ROW_ZEBRA
│
├── GeometryConfig (dataclass)
│   ├── Margins: Top = 1.0in, Bottom = 1.25in, Left = 1.0in, Right = 1.0in
│   ├── Header/Footer: headheight = 15pt, headsep = 18pt, footskip = 32pt
│   └── Page-Break Thresholds: \needspace{5\baselineskip} / \needspace{6\baselineskip}
│
├── TableConfig (dataclass)
│   ├── \tabcolsep = 5.5pt, \arraystretch = 1.15, \extrarowheight = 1.2pt
│   └── \LTpre = 4pt, \LTpost = 6pt
│
├── ChartTheme (dataclass)
│   ├── 300 DPI publication resolution, sans-serif typography, soft gridlines
│   └── Threshold line: Red dashed line (linewidth = 1.6, color = #C0392B)
│
└── Standardized Helper Functions
    ├── get_latex_preamble_definitions()
    ├── build_longtable_header()
    ├── format_status_badge()
    └── format_ur_value()
```

### 3.2 Key Rationale for Design Choices
1. **Centralized Tokenization:** Colors and dimensions are defined as immutable frozen dataclasses, ensuring consistency between LaTeX document rendering and Matplotlib chart generation.
2. **Maintenance Simplicity:** Shared colors, page geometry, common table spacing, and chart styling can be changed centrally. Table column widths that depend on the chapter's data remain alongside their table definitions.
3. **Encapsulated Continuation Logic:** The `build_longtable_header()` helper abstracts the verbose LaTeX boilerplate (`\endfirsthead`, `\endhead`, `\endfoot`, `\endlastfoot`), guaranteeing standard table headers across all pages.

---

## 4. Key Code & LaTeX / PyLaTeX Modifications

### 4.1 Repeated Table Headers Across Page Breaks (Requirement 1)
- **Problem:** When tables spanned multiple pages, subsequent pages lacked column headers, making engineering checks difficult to interpret.
- **Solution:** Integrated LaTeX `longtable` continuation blocks across all chapter tables:
  ```latex
  \begin{longtable}{<col_spec>}
  \caption{\textbf{<Caption>}}\label{<Label>}\\
  \hline
  <Column Header Row> \\[6pt]
  \hline
  \endfirsthead

  \multicolumn{<N>}{c}{\tablename\ \thetable\ -- \textit{Continued from previous page}} \\[4pt]
  \hline
  <Column Header Row> \\[6pt]
  \hline
  \endhead

  \hline
  \multicolumn{<N>}{r}{\footnotesize\textit{Continued on next page\dots}} \\
  \endfoot

  \hline
  \endlastfoot
  <Data Rows>
  \end{longtable}
  ```
- **Result:** Every page transition repeats the column headers accompanied by standard "Continued" indicators.

### 4.2 Footer Overlap and Vertical Spacing Fixes (Requirement 2)
- **Problem:** On page 30 and other dense check sections, multirow elements (e.g., "G4" girder data) bled directly across the footer separation rule.
- **Solution:**
  1. **Geometry Buffer:** Increased bottom margin to `1.25in` and expanded `footskip` to `32pt` in `styles.py` to create a dedicated safety clearance.
  2. **Footer Rule Spacing:** Adjusted `fancyhdr` footrule vertical offsets from `-20pt` to `-12pt` / `-4pt`, preventing baseline overlaps with the text body.
  3. **Girder Block Pagination:** Implemented clean block-level pagination (`\pagebreak` before girder index transitions) and `\needspace{6\baselineskip}` rules, ensuring multirow cell structures never split awkwardly over page thresholds.
- **Result:** Text and table borders maintain clean separation above footers throughout the document.

### 4.3 Load & Geometry Table Refactoring (Requirement 3)
- **Problem:** Vehicle live loads and footway loads in Chapter 3 were previously combined into a single ambiguous table without unit columns.
- **Solution:**
  1. **Table 3.3 (Vehicle Live Load Parameters):** Restructured into a multi-column table featuring:
     - Vehicle Class (Class A, Class 70R Wheeled/Tracked, Class AA, Class SV, etc.)
     - Total Load (kN)
     - Impact Factor (dynamically computed per IRC 6 Cl. 208)
     - Braking Load sub-headers: *Considered?*, *Value (kN)*, *Eccentricity (m)*
  2. **Table 3.4 (Pedestrian / Footway Live Load):** Separated into an independent table recording footway intensity, provision status, application area, and IRC 6 Cl. 206.1 code clauses.
  3. Vehicle classes now reflect the active UI selection; excluded custom vehicles are omitted. Missing span/lane values no longer trigger hardcoded impact/braking figures. The table includes a centrifugal-force column, marked N/A because the current input model has no curvature data to calculate it.
- **Result:** Better structured loads with explicit units and no invented fallback values. Centrifugal force calculation remains unsupported until bridge curvature inputs and analysis are available.

### 4.4 Utilization Ratio Summary Visualizations (Requirement 4)
- **Problem:** Section 5.5 (Overall Design Check Summary) only contained a tabular summary without graphical insight into design margins.
- **Solution:**
  - Implemented `generate_ur_summary_chart()` in `visualizations.py` using Matplotlib (Agg backend).
  - Primary elements included on X-axis: **Steel Plate Girders**, **Concrete Deck Slab**, **Cross Bracing**, and **End Diaphragms**.
  - Programmatically draws a distinct horizontal reference line at $UR = 1.0$ (Red dashed line, linewidth = 1.6) labeled `Design Limit (UR = 1.00)`.
  - Bars are dynamically colored green (`#27AE60`) for passing ($UR \leq 1.0$) and red (`#C0392B`) for failing ($UR > 1.0$), with numerical ratios and status badges annotated on top of each bar. Missing component results are shown as N/A; they are not filled with sample ratios.
  - Dynamically embedded into Section 5.5 as Figure 5.1.

### 4.5 Material Quantity Bar Charts (Requirement 5)
- **Problem:** Chapter 7 (Material Take-off) lacked visual representation of material distribution.
- **Solution:**
  1. **Structural Steel Tonnage Breakdown:** Generated bar chart comparing steel consumption across Girders, Cross Bracing, and End Diaphragms/Stiffeners in Metric Tonnes (MT), annotated with percentage shares.
  2. **Concrete vs. Reinforcement Chart:** Generated side-by-side chart illustrating Concrete Deck Volume ($m^3$) versus Reinforcement Steel Weight (MT) on separate axes because their units differ.
  3. Missing material quantities are not replaced with sample numbers; unavailable chart categories are labelled N/A.
  3. Embedded into Chapter 7 as Figures 7.1 and 7.2 using LaTeX figure environments.

---

## 5. Visual Enhancements & Polish

Beyond the functional fixes, the following professional aesthetic enhancements were applied:
1. **Typography & Hierarchy:** Standardized section titles, captions, and table fonts to improve legibility.
2. **Unified Status Highlighting:** Color-coded status badges (`\textcolor{passGreen}{\textbf{PASS}}` and `\textcolor{failRed}{\textbf{FAIL}}`) applied consistently across all design checks.
3. **Table Row Padding:** Standardized row height (`\arraystretch = 1.15`, `\extrarowheight = 1.2pt`) to give numerical data adequate breathing room without excessive document expansion.
4. **Figure Formatting:** Embedded figures with 300 DPI resolution, consistent aspect ratios, and clean captions centered in accordance with standard engineering reporting practices.

---

## 6. Verification and Comparison

- Python syntax compilation and focused report-generation smoke checks passed for selected vehicle handling, missing-data handling, style macros, and the three chart functions. The smoke-test chart previews were visually inspected.
- The existing `src/Report_after.tex` references temporary image files that no longer exist and still contains the previous hardcoded braking value. It and the paired PDF do not reflect the final code changes. Regenerate the report from a real bridge design run, then inspect all pages before submission.
- `Report_Before.pdf` remains the original baseline artifact for comparison.
