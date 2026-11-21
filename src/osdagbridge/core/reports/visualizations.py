"""
Dynamic Data Visualization Module for OsdagBridge Reports.
Programmatically generates high-resolution engineering figures using Matplotlib
for Chapter 5 (Utilization Ratio Summary) and Chapter 7 (Material Quantities).
"""

import os
import logging
from typing import Dict, Any, Optional

import matplotlib
# Use non-interactive backend for headless report generation
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from osdagbridge.core.reports.styles import COLORS, CHART_THEME

logger = logging.getLogger(__name__)


def _safe_float(v: Any, default: float = 0.0) -> float:
    try:
        return float(v)
    except (ValueError, TypeError):
        return default


def generate_ur_summary_chart(ur_data: Dict[str, float], output_path: str) -> Optional[str]:
    """
    Generate bar chart for Overall Design Check Summary (Section 5.5).
    
    Shows Utilization Ratio (UR = Demand / Capacity) for all primary elements:
    - Steel Plate Girders
    - Concrete Deck Slab
    - Cross Bracing
    - End Diaphragms
    
    Includes horizontal red dashed threshold line at UR = 1.0.
    """
    try:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        elements = list(ur_data.keys())
        ratios = [max(0.0, _safe_float(v)) for v in ur_data.values()]
        
        # Color each bar based on passing (<= 1.0) vs failing (> 1.0)
        bar_colors = [
            COLORS.PASS if r <= 1.0 else COLORS.FAIL
            for r in ratios
        ]
        
        fig, ax = plt.subplots(figsize=(CHART_THEME.FIGURE_WIDTH, CHART_THEME.FIGURE_HEIGHT_UR), dpi=CHART_THEME.DPI)
        
        x_indices = range(len(elements))
        bar_width = 0.52
        bars = ax.bar(
            x_indices,
            ratios,
            width=bar_width,
            color=bar_colors,
            edgecolor=COLORS.BORDER_GRAY,
            linewidth=1.0,
            zorder=3
        )
        
        # Red dashed threshold line at UR = 1.0 (Critical Requirement)
        ax.axhline(
            y=1.0,
            color=CHART_THEME.THRESHOLD_LINE_COLOR,
            linestyle=CHART_THEME.THRESHOLD_LINE_STYLE,
            linewidth=CHART_THEME.THRESHOLD_LINE_WIDTH,
            label="Design Limit (UR = 1.00)",
            zorder=4
        )
        
        # Value labels above each bar
        max_y = max(ratios + [1.0])
        for bar, val in zip(bars, ratios):
            h = bar.get_height()
            status_text = "PASS" if val <= 1.0 else "FAIL"
            color = COLORS.PASS if val <= 1.0 else COLORS.FAIL
            ax.annotate(
                f"{val:.2f}\n({status_text})",
                xy=(bar.get_x() + bar.get_width() / 2, h),
                xytext=(0, 4),
                textcoords="offset points",
                ha="center",
                va="bottom",
                fontsize=CHART_THEME.FONT_SIZE_VALUE,
                fontweight="bold",
                color=color
            )
            
        ax.set_title(
            "Overall Design Check Summary — Utilization Ratios (Demand / Capacity)",
            fontsize=CHART_THEME.FONT_SIZE_TITLE,
            fontweight="bold",
            pad=14,
            color=COLORS.TEXT_MAIN
        )
        ax.set_ylabel(
            "Utilization Ratio (UR)",
            fontsize=CHART_THEME.FONT_SIZE_LABEL,
            fontweight="semibold",
            color=COLORS.TEXT_MAIN
        )
        ax.set_xticks(x_indices)
        ax.set_xticklabels(elements, fontsize=CHART_THEME.FONT_SIZE_TICK, fontweight="semibold")
        
        # Y-limit ensures threshold line and annotations are clearly visible
        ax.set_ylim(0, max_y * 1.25)
        
        # Subtle horizontal gridlines
        ax.grid(axis="y", linestyle="--", alpha=CHART_THEME.GRID_ALPHA, color=CHART_THEME.GRID_COLOR, zorder=0)
        ax.set_axisbelow(True)
        
        # Clean styling: hide top and right spines
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.spines["left"].set_color(COLORS.BORDER_GRAY)
        ax.spines["bottom"].set_color(COLORS.BORDER_GRAY)
        
        ax.legend(
            loc="upper right",
            framealpha=0.9,
            edgecolor=COLORS.BORDER_GRAY,
            fontsize=CHART_THEME.FONT_SIZE_TICK
        )
        
        plt.tight_layout()
        plt.savefig(output_path, dpi=CHART_THEME.DPI, bbox_inches="tight")
        plt.close(fig)
        
        return output_path
    except Exception as exc:
        logger.error(f"Failed to generate UR summary chart: {exc}", exc_info=True)
        return None


def generate_steel_tonnage_chart(steel_data: Dict[str, float], output_path: str) -> Optional[str]:
    """
    Generate bar chart for Structural Steel tonnage breakdown (Chapter 7).
    Shows steel quantities for Girders, Cross Bracing, and End Diaphragms.
    """
    try:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        categories = list(steel_data.keys())
        weights = [max(0.0, _safe_float(v)) for v in steel_data.values()]
        total_tonnage = sum(weights)
        
        fig, ax = plt.subplots(figsize=(CHART_THEME.FIGURE_WIDTH, CHART_THEME.FIGURE_HEIGHT_QTY), dpi=CHART_THEME.DPI)
        
        x_indices = range(len(categories))
        bar_width = 0.48
        
        bars = ax.bar(
            x_indices,
            weights,
            width=bar_width,
            color=COLORS.STEEL_BLUE,
            edgecolor=COLORS.BORDER_GRAY,
            linewidth=1.0,
            zorder=3
        )
        
        # Add labels with value and percentage of total steel
        max_y = max(weights) if weights else 1.0
        for bar, w in zip(bars, weights):
            pct = (w / total_tonnage * 100.0) if total_tonnage > 0 else 0.0
            ax.annotate(
                f"{w:.2f} MT\n({pct:.1f}%)",
                xy=(bar.get_x() + bar.get_width() / 2, bar.get_height()),
                xytext=(0, 4),
                textcoords="offset points",
                ha="center",
                va="bottom",
                fontsize=CHART_THEME.FONT_SIZE_VALUE,
                fontweight="bold",
                color=COLORS.TEXT_MAIN
            )
            
        ax.set_title(
            f"Structural Steel Tonnage Breakdown (Total: {total_tonnage:.2f} MT)",
            fontsize=CHART_THEME.FONT_SIZE_TITLE,
            fontweight="bold",
            pad=14,
            color=COLORS.TEXT_MAIN
        )
        ax.set_ylabel(
            "Weight (Metric Tonnes - MT)",
            fontsize=CHART_THEME.FONT_SIZE_LABEL,
            fontweight="semibold",
            color=COLORS.TEXT_MAIN
        )
        ax.set_xticks(x_indices)
        ax.set_xticklabels(categories, fontsize=CHART_THEME.FONT_SIZE_TICK, fontweight="semibold")
        
        ax.set_ylim(0, max_y * 1.25 if max_y > 0 else 10)
        ax.grid(axis="y", linestyle="--", alpha=CHART_THEME.GRID_ALPHA, color=CHART_THEME.GRID_COLOR, zorder=0)
        ax.set_axisbelow(True)
        
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.spines["left"].set_color(COLORS.BORDER_GRAY)
        ax.spines["bottom"].set_color(COLORS.BORDER_GRAY)
        
        plt.tight_layout()
        plt.savefig(output_path, dpi=CHART_THEME.DPI, bbox_inches="tight")
        plt.close(fig)
        
        return output_path
    except Exception as exc:
        logger.error(f"Failed to generate steel tonnage chart: {exc}", exc_info=True)
        return None


def generate_concrete_vs_rebar_chart(concrete_vol_m3: float, rebar_wt_mt: float, output_path: str) -> Optional[str]:
    """
    Generate comparison bar chart for Concrete volume (m^3) vs Reinforcement Steel weight (MT) (Chapter 7).
    """
    try:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        categories = ["Concrete Deck Slab\nVolume (m³)", "Reinforcement Steel\nWeight (MT)"]
        values = [max(0.0, _safe_float(concrete_vol_m3)), max(0.0, _safe_float(rebar_wt_mt))]
        units = ["m³", "MT"]
        colors = [COLORS.CONCRETE_GRAY, COLORS.OSDAG_GREEN_DARK]
        
        fig, ax = plt.subplots(figsize=(6.5, CHART_THEME.FIGURE_HEIGHT_QTY), dpi=CHART_THEME.DPI)
        
        x_indices = range(len(categories))
        bar_width = 0.42
        
        bars = ax.bar(
            x_indices,
            values,
            width=bar_width,
            color=colors,
            edgecolor=COLORS.BORDER_GRAY,
            linewidth=1.0,
            zorder=3
        )
        
        max_y = max(values) if values else 1.0
        for bar, val, u in zip(bars, values, units):
            ax.annotate(
                f"{val:.2f} {u}",
                xy=(bar.get_x() + bar.get_width() / 2, bar.get_height()),
                xytext=(0, 4),
                textcoords="offset points",
                ha="center",
                va="bottom",
                fontsize=CHART_THEME.FONT_SIZE_VALUE + 1,
                fontweight="bold",
                color=COLORS.TEXT_MAIN
            )
            
        ax.set_title(
            "Concrete Volume vs. Reinforcement Steel Weight",
            fontsize=CHART_THEME.FONT_SIZE_TITLE,
            fontweight="bold",
            pad=14,
            color=COLORS.TEXT_MAIN
        )
        ax.set_ylabel(
            "Quantity (m³ / MT)",
            fontsize=CHART_THEME.FONT_SIZE_LABEL,
            fontweight="semibold",
            color=COLORS.TEXT_MAIN
        )
        ax.set_xticks(x_indices)
        ax.set_xticklabels(categories, fontsize=CHART_THEME.FONT_SIZE_TICK, fontweight="semibold")
        
        ax.set_ylim(0, max_y * 1.25 if max_y > 0 else 10)
        ax.grid(axis="y", linestyle="--", alpha=CHART_THEME.GRID_ALPHA, color=CHART_THEME.GRID_COLOR, zorder=0)
        ax.set_axisbelow(True)
        
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.spines["left"].set_color(COLORS.BORDER_GRAY)
        ax.spines["bottom"].set_color(COLORS.BORDER_GRAY)
        
        plt.tight_layout()
        plt.savefig(output_path, dpi=CHART_THEME.DPI, bbox_inches="tight")
        plt.close(fig)
        
        return output_path
    except Exception as exc:
        logger.error(f"Failed to generate concrete vs rebar chart: {exc}", exc_info=True)
        return None
