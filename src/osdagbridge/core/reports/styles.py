"""
Centralized Formatting and Style System for OsdagBridge Reports.
Single Source of Truth for all layout rules, visual attributes, table formatting,
and chart themes across all report chapters.
"""

import re
from dataclasses import dataclass
from typing import List, Optional, Tuple, Dict, Any


# =============================================================================
# 1. COLOR PALETTE (Single Source of Truth)
# =============================================================================

@dataclass(frozen=True)
class ColorPalette:
    """Official OsdagBridge color specifications for LaTeX and Matplotlib."""
    # Brand Primary
    OSDAG_GREEN: str = "#91B014"
    OSDAG_GREEN_DARK: str = "#64850C"
    OSDAG_GREEN_LIGHT: str = "#EAF2D3"
    
    # Secondary Structural Colors
    STEEL_BLUE: str = "#2B5B84"
    STEEL_BLUE_LIGHT: str = "#EBF2F8"
    CONCRETE_GRAY: str = "#7F8C8D"
    CONCRETE_LIGHT: str = "#F2F4F4"
    
    # Status Indicators
    PASS: str = "#27AE60"         # Green for UR <= 1.0
    WARN: str = "#F39C12"         # Amber for near-limit
    FAIL: str = "#C0392B"         # Red for UR > 1.0 / Failing
    
    # Typography & Structure
    TEXT_MAIN: str = "#2C3E50"
    TEXT_MUTED: str = "#7F8C8D"
    BORDER_GRAY: str = "#BDC3C7"
    BORDER_LIGHT: str = "#E0E0E0"
    ROW_ZEBRA: str = "#F8F9FA"


COLORS = ColorPalette()


# =============================================================================
# 2. DOCUMENT GEOMETRY & SPACING CONSTANTS
# =============================================================================

@dataclass(frozen=True)
class GeometryConfig:
    """Global page geometry parameters preventing footer overlap."""
    PAPER_SIZE: str = "a4paper"
    MARGIN_TOP: str = "1.0in"
    MARGIN_BOTTOM: str = "1.25in"   # Increased bottom margin prevents table bleed into footer
    MARGIN_LEFT: str = "1.0in"
    MARGIN_RIGHT: str = "1.0in"
    HEAD_HEIGHT: str = "15pt"
    HEAD_SEP: str = "18pt"
    FOOT_SKIP: str = "32pt"         # Generous foot separation ensures buffer before footer line
    NEEDSPACE_TABLE: int = 5        # Baselines required before placing a table
    NEEDSPACE_SECTION: int = 4      # Baselines required before starting a section


GEOMETRY = GeometryConfig()


# =============================================================================
# 3. TABLE STYLING CONFIGURATION
# =============================================================================

@dataclass(frozen=True)
class TableConfig:
    """Standardized table layout and spacing parameters."""
    TABCOLSEP: str = "5.5pt"         # Column padding
    ARRAYSTRETCH: float = 1.15       # Row height multiplier
    EXTRAROWHEIGHT: str = "1.2pt"    # Extra cell height
    ARRAYRULEWIDTH: str = "0.5pt"    # Border line thickness
    LTPRE: str = "4pt"               # Spacing before longtable
    LTPOST: str = "6pt"              # Spacing after longtable
    ROW_HEIGHT_PT: str = "6pt"       # Standard row break spacing e.g. \\[6pt]


TABLE_STYLE = TableConfig()


# =============================================================================
# 4. MATPLOTLIB VISUALIZATION THEME
# =============================================================================

@dataclass(frozen=True)
class ChartTheme:
    """Visualization formatting constants for high-resolution report charts."""
    DPI: int = 300
    FIGURE_WIDTH: float = 8.5
    FIGURE_HEIGHT_UR: float = 4.2
    FIGURE_HEIGHT_QTY: float = 4.0
    FONT_FAMILY: str = "DejaVu Sans"
    FONT_SIZE_TITLE: int = 12
    FONT_SIZE_LABEL: int = 10
    FONT_SIZE_TICK: int = 9
    FONT_SIZE_VALUE: int = 8.5
    THRESHOLD_LINE_COLOR: str = COLORS.FAIL
    THRESHOLD_LINE_STYLE: str = "--"
    THRESHOLD_LINE_WIDTH: float = 1.6
    GRID_ALPHA: float = 0.4
    GRID_COLOR: str = "#D5D8DC"


CHART_THEME = ChartTheme()


# =============================================================================
# 5. LATEX MACROS AND DEFINITIONS GENERATOR
# =============================================================================

def get_latex_preamble_definitions() -> str:
    """Generate LaTeX color and formatting definitions consumed by the preamble."""
    return f"""
% --- Centralized Colors (from styles.py) ---
\\definecolor{{osdagGreen}}{{HTML}}{{{COLORS.OSDAG_GREEN.lstrip('#')}}}
\\definecolor{{osdagGreenDark}}{{HTML}}{{{COLORS.OSDAG_GREEN_DARK.lstrip('#')}}}
\\definecolor{{osdagGreenLight}}{{HTML}}{{{COLORS.OSDAG_GREEN_LIGHT.lstrip('#')}}}
\\definecolor{{steelBlue}}{{HTML}}{{{COLORS.STEEL_BLUE.lstrip('#')}}}
\\definecolor{{steelBlueLight}}{{HTML}}{{{COLORS.STEEL_BLUE_LIGHT.lstrip('#')}}}
\\definecolor{{passGreen}}{{HTML}}{{{COLORS.PASS.lstrip('#')}}}
\\definecolor{{warnAmber}}{{HTML}}{{{COLORS.WARN.lstrip('#')}}}
\\definecolor{{failRed}}{{HTML}}{{{COLORS.FAIL.lstrip('#')}}}
\\definecolor{{tableZebra}}{{HTML}}{{{COLORS.ROW_ZEBRA.lstrip('#')}}}
\\definecolor{{borderGray}}{{HTML}}{{{COLORS.BORDER_GRAY.lstrip('#')}}}

% --- Global Table Geometry & Padding (from styles.py) ---
\\setlength{{\\tabcolsep}}{{{TABLE_STYLE.TABCOLSEP}}}
\\renewcommand{{\\arraystretch}}{{{TABLE_STYLE.ARRAYSTRETCH}}}
\\setlength{{\\extrarowheight}}{{{TABLE_STYLE.EXTRAROWHEIGHT}}}
\\setlength{{\\arrayrulewidth}}{{{TABLE_STYLE.ARRAYRULEWIDTH}}}
\\setlength{{\\LTpre}}{{{TABLE_STYLE.LTPRE}}}
\\setlength{{\\LTpost}}{{{TABLE_STYLE.LTPOST}}}

% --- Threshold Constraints to Prevent Footer Margin Bleed ---
\\BeforeBeginEnvironment{{table}}{{\\needspace{{{GEOMETRY.NEEDSPACE_TABLE}\\baselineskip}}}}
\\BeforeBeginEnvironment{{longtable}}{{\\needspace{{{GEOMETRY.NEEDSPACE_TABLE}\\baselineskip}}}}

% --- Custom Column Specifications ---
\\newcolumntype{{L}}[1]{{>{{\\raggedright\\arraybackslash}}p{{#1}}}}
\\newcolumntype{{C}}[1]{{>{{\\centering\\arraybackslash}}p{{#1}}}}
\\newcolumntype{{R}}[1]{{>{{\\raggedleft\\arraybackslash}}p{{#1}}}}
\\newcolumntype{{M}}[1]{{>{{\\centering\\arraybackslash\\vspace{{2pt}}}}m{{#1}}}}
"""


# =============================================================================
# 6. STANDARDIZED LONGTABLE BUILDER (Repeated Headers Across Page Breaks)
# =============================================================================

def build_longtable_header(
    col_spec: str,
    caption: str,
    headers: List[str],
    label: Optional[str] = None,
    show_continued: bool = True
) -> str:
    """
    Generate standard PyLaTeX/LaTeX LongTable preamble ensuring headers repeat
    across all page breaks with standard continuation notices.
    
    Satisfies Requirement 1: Column headers repeat on every subsequent page.
    """
    n_cols = len(headers)
    caption_safe = re.sub(r'(?<!\\)&', r'\&', caption)
    safe_headers = [re.sub(r'(?<!\\)&', r'\&', h) for h in headers]
    hdr_line = " & ".join(f"\\textbf{{{h}}}" for h in safe_headers) + f" \\\\[{TABLE_STYLE.ROW_HEIGHT_PT}]"
    
    label_cmd = f"\\label{{{label}}}" if label else ""
    
    continued_header = (
        f"\\multicolumn{{{n_cols}}}{{c}}{{\\tablename\\ \\thetable\\ -- \\textit{{Continued from previous page}}}} \\\\[4pt]\n"
        f"\\hline\n"
        f"{hdr_line}\n"
        f"\\hline\n"
    ) if show_continued else f"{hdr_line}\n\\hline\n"
    
    continued_footer = (
        f"\\hline\n"
        f"\\multicolumn{{{n_cols}}}{{r}}{{\\footnotesize\\textit{{Continued on next page\\dots}}}} \\\\\n"
    ) if show_continued else "\\hline\n"

    return (
        f"\\begin{{longtable}}{{{col_spec}}}\n"
        f"\\caption{{\\textbf{{{caption_safe}}}}}{label_cmd}\\\\\n"
        f"\\hline\n"
        f"{hdr_line}\n"
        f"\\hline\n"
        f"\\endfirsthead\n\n"
        f"{continued_header}"
        f"\\endhead\n\n"
        f"{continued_footer}"
        f"\\endfoot\n\n"
        f"\\hline\n"
        f"\\endlastfoot\n"
    )


# =============================================================================
# 7. FORMATTING & STATUS HELPER FUNCTIONS
# =============================================================================

def format_status_badge(passed: Optional[bool], text_pass: str = "PASS", text_fail: str = "FAIL") -> str:
    """Return formatted status text with consistent color styling."""
    if passed is None:
        return "---"
    if passed:
        return f"\\textcolor{{passGreen}}{{\\textbf{{{text_pass}}}}}"
    return f"\\textcolor{{failRed}}{{\\textbf{{{text_fail}}}}}"


def format_ur_value(ur_val: Any) -> str:
    """Format Utilization Ratio with red highlighting when failing (UR > 1.0)."""
    try:
        val = float(ur_val)
        formatted = f"{val:.2f}"
        if val > 1.0:
            return f"\\textcolor{{failRed}}{{\\textbf{{{formatted}}}}}"
        return formatted
    except (ValueError, TypeError):
        return str(ur_val) if ur_val not in (None, "") else "---"
