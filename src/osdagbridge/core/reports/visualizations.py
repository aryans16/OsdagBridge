"""
Dynamic Data Visualization Module for OsdagBridge Reports.
Programmatically generates high-resolution engineering figures using Matplotlib
for Chapter 5 (Utilization Ratio Summary) and Chapter 7 (Material Quantities).
"""

import os
import logging
import math
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


def generate_ur_summary_chart(ur_data: Dict[str, Optional[float]], output_path: str) -> Optional[str]:
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
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        
        elements = list(ur_data.keys())
        ratios = []
        for value in ur_data.values():
            try:
                ratio = float(value)
                ratios.append(max(0.0, ratio) if math.isfinite(ratio) else None)
            except (TypeError, ValueError):
                ratios.append(None)
        
        fig, ax = plt.subplots(figsize=(CHART_THEME.FIGURE_WIDTH, CHART_THEME.FIGURE_HEIGHT_UR), dpi=CHART_THEME.DPI)
        
        x_indices = range(len(elements))
        bar_width = 0.52
        known = [(index, value) for index, value in enumerate(ratios) if value is not None]
        bars = ax.bar(
            [index for index, _ in known],
            [value for _, value in known],
            width=bar_width,
            color=[COLORS.PASS if value <= 1.0 else COLORS.FAIL for _, value in known],
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
        max_y = max([value for _, value in known] + [1.0])
        for bar, (_, val) in zip(bars, known):
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
        for index, val in enumerate(ratios):
            if val is None:
                ax.annotate("N/A", xy=(index, 0), xytext=(0, 5), textcoords="offset points",
                            ha="center", va="bottom", fontsize=CHART_THEME.FONT_SIZE_VALUE,
                            color=COLORS.TEXT_MUTED)
            
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


def generate_steel_tonnage_chart(steel_data: Dict[str, Optional[float]], output_path: str) -> Optional[str]:
    """
    Generate bar chart for Structural Steel tonnage breakdown (Chapter 7).
    Shows steel quantities for Girders, Cross Bracing, and End Diaphragms.
    """
    try:
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        
        categories = list(steel_data.keys())
        weights = []
        for value in steel_data.values():
            try:
                weight = float(value)
                weights.append(max(0.0, weight) if math.isfinite(weight) else None)
            except (TypeError, ValueError):
                weights.append(None)
        total_tonnage = sum(weight for weight in weights if weight is not None)
        
        fig, ax = plt.subplots(figsize=(CHART_THEME.FIGURE_WIDTH, CHART_THEME.FIGURE_HEIGHT_QTY), dpi=CHART_THEME.DPI)
        
        x_indices = range(len(categories))
        bar_width = 0.48
        
        known = [(index, value) for index, value in enumerate(weights) if value is not None]
        bars = ax.bar(
            [index for index, _ in known],
            [value for _, value in known],
            width=bar_width,
            color=COLORS.STEEL_BLUE,
            edgecolor=COLORS.BORDER_GRAY,
            linewidth=1.0,
            zorder=3
        )
        
        # Add labels with value and percentage of total steel
        max_y = max((value for _, value in known), default=1.0)
        for bar, (_, w) in zip(bars, known):
            pct = (w / total_tonnage * 100.0) if total_tonnage > 0 else None
            ax.annotate(
                f"{w:.2f} MT\n({pct:.1f}%)" if pct is not None else f"{w:.2f} MT",
                xy=(bar.get_x() + bar.get_width() / 2, bar.get_height()),
                xytext=(0, 4),
                textcoords="offset points",
                ha="center",
                va="bottom",
                fontsize=CHART_THEME.FONT_SIZE_VALUE,
                fontweight="bold",
                color=COLORS.TEXT_MAIN
            )
        for index, weight in enumerate(weights):
            if weight is None:
                ax.annotate("N/A", xy=(index, 0), xytext=(0, 5), textcoords="offset points",
                            ha="center", va="bottom", fontsize=CHART_THEME.FONT_SIZE_VALUE,
                            color=COLORS.TEXT_MUTED)
            
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
        
        ax.set_ylim(0, max_y * 1.25 if max_y > 0 else 1)
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


def generate_concrete_vs_rebar_chart(concrete_vol_m3: Optional[float], rebar_wt_mt: Optional[float], output_path: str) -> Optional[str]:
    """Plot concrete volume and reinforcement mass on separate scales."""
    try:
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        observations = (
            ("Concrete Deck Slab Volume", concrete_vol_m3, "Volume (m^3)", COLORS.CONCRETE_GRAY),
            ("Reinforcement Steel Weight", rebar_wt_mt, "Weight (MT)", COLORS.OSDAG_GREEN_DARK),
        )
        fig, axes = plt.subplots(1, 2, figsize=(6.5, CHART_THEME.FIGURE_HEIGHT_QTY), dpi=CHART_THEME.DPI)
        for ax, (title, raw_value, unit, color) in zip(axes, observations):
            try:
                value = float(raw_value)
                if not math.isfinite(value) or value < 0:
                    value = None
            except (TypeError, ValueError):
                value = None
            ax.set_title(title, fontsize=CHART_THEME.FONT_SIZE_LABEL, fontweight="bold", color=COLORS.TEXT_MAIN)
            ax.set_ylabel(unit, fontsize=CHART_THEME.FONT_SIZE_LABEL, color=COLORS.TEXT_MAIN)
            ax.set_xticks([0])
            ax.set_xticklabels([unit], fontsize=CHART_THEME.FONT_SIZE_TICK)
            if value is None:
                ax.text(0, 0.5, "N/A", ha="center", va="center", color=COLORS.TEXT_MUTED)
                ax.set_ylim(0, 1)
            else:
                bar = ax.bar([0], [value], width=0.48, color=color, edgecolor=COLORS.BORDER_GRAY, zorder=3)[0]
                ax.annotate(f"{value:.2f} {unit}", xy=(bar.get_x() + bar.get_width() / 2, value),
                            xytext=(0, 4), textcoords="offset points", ha="center", va="bottom",
                            fontsize=CHART_THEME.FONT_SIZE_VALUE, fontweight="bold", color=COLORS.TEXT_MAIN)
                ax.set_ylim(0, value * 1.25 if value > 0 else 1)
            ax.grid(axis="y", linestyle="--", alpha=CHART_THEME.GRID_ALPHA, color=CHART_THEME.GRID_COLOR, zorder=0)
            ax.set_axisbelow(True)
            ax.spines["top"].set_visible(False)
            ax.spines["right"].set_visible(False)
            ax.spines["left"].set_color(COLORS.BORDER_GRAY)
            ax.spines["bottom"].set_color(COLORS.BORDER_GRAY)
        fig.suptitle("Material Quantities (separate scales)", fontsize=CHART_THEME.FONT_SIZE_TITLE,
                     fontweight="bold", color=COLORS.TEXT_MAIN)
        plt.tight_layout()
        plt.savefig(output_path, dpi=CHART_THEME.DPI, bbox_inches="tight")
        plt.close(fig)
        return output_path
    except Exception as exc:
        logger.error(f"Failed to generate concrete vs rebar chart: {exc}", exc_info=True)
        return None
