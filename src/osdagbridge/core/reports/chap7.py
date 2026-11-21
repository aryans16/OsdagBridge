# =============================================================================
# Chapter 7: Material Take-off & Quantity Summary
# Refactored for FOSSEE OsdagBridge LaTeX Report Generator
# - Programmatically embeds bar charts for Structural Steel tonnage and Concrete vs Rebar
# - Converts Bill of Materials table to standardized LongTable with repeated headers
# =============================================================================

from osdagbridge.core.reports.styles import build_longtable_header, TABLE_STYLE


def ch7_quantities(input_dict, fig_paths=None):
    fig_paths = fig_paths or {}
    
    # ── Table 7.1: Bill of Materials with Repeated LongTable Headers ──────
    t71_header = build_longtable_header(
        col_spec="|C{1.0cm}|L{3.8cm}|C{2.6cm}|C{1.6cm}|C{1.8cm}|C{1.8cm}|C{1.8cm}|",
        caption="Bill of Materials (Steel, Concrete, and Reinforcement Quantities)",
        headers=["S.N.", "Item Description", "Volume Formula", "Qty", "Total Vol (m³)", "Unit Wt (MT)", "Total Wt (MT)"],
        label="tab:ch7-bom"
    )

    t71_body = (
        r"""1 & Structural Steel (IS 2062) for Girders & """ + str(input_dict.get("steel_girders_vol_formula", "N.A.")) + r""" & """ + str(input_dict.get("steel_girders_qty", "N.A.")) + r""" & """ + str(input_dict.get("steel_girders_vol_total", "N.A.")) + r""" & """ + str(input_dict.get("steel_girders_wt_single", "N.A.")) + r""" & """ + str(input_dict.get("steel_girders_wt_total", "N.A.")) + r""" \\[6pt]
\hline
2(a) & Cross Bracing - Top Chord & """ + str(input_dict.get("bracing_top_vol_formula", "N.A.")) + r""" & """ + str(input_dict.get("bracing_top_qty", "N.A.")) + r""" & """ + str(input_dict.get("bracing_top_vol_total", "N.A.")) + r""" & """ + str(input_dict.get("bracing_top_wt_single", "N.A.")) + r""" & """ + str(input_dict.get("bracing_top_wt_total", "N.A.")) + r""" \\[6pt]
\hline
2(b) & Cross Bracing - Bottom Chord & """ + str(input_dict.get("bracing_bot_vol_formula", "N.A.")) + r""" & """ + str(input_dict.get("bracing_bot_qty", "N.A.")) + r""" & """ + str(input_dict.get("bracing_bot_vol_total", "N.A.")) + r""" & """ + str(input_dict.get("bracing_bot_wt_single", "N.A.")) + r""" & """ + str(input_dict.get("bracing_bot_wt_total", "N.A.")) + r""" \\[6pt]
\hline
2(c) & Cross Bracing - Diagonal Chord & """ + str(input_dict.get("bracing_diag_vol_formula", "N.A.")) + r""" & """ + str(input_dict.get("bracing_diag_qty", "N.A.")) + r""" & """ + str(input_dict.get("bracing_diag_vol_total", "N.A.")) + r""" & """ + str(input_dict.get("bracing_diag_wt_single", "N.A.")) + r""" & """ + str(input_dict.get("bracing_diag_wt_total", "N.A.")) + r""" \\[6pt]
\hline
3 & Concrete (M40) for Deck Slab & """ + str(input_dict.get("concrete_deck_vol_formula", "N.A.")) + r""" & """ + str(input_dict.get("concrete_deck_qty", "N.A.")) + r""" & """ + str(input_dict.get("concrete_deck_vol_total", "N.A.")) + r""" & """ + str(input_dict.get("concrete_deck_wt_single", "N.A.")) + r""" & """ + str(input_dict.get("concrete_deck_wt_total", "N.A.")) + r""" \\[6pt]
\hline
4 & Reinforcement Steel (Fe 500) & """ + str(input_dict.get("rebar_deck_vol_formula", "N.A.")) + r""" & """ + str(input_dict.get("rebar_deck_qty", "N.A.")) + r""" & """ + str(input_dict.get("rebar_deck_vol_total", "N.A.")) + r""" & """ + str(input_dict.get("rebar_deck_wt_single", "N.A.")) + r""" & """ + str(input_dict.get("rebar_deck_wt_total", "N.A.")) + r""" \\[6pt]
\hline
5 & Shear Stud Connectors & """ + str(input_dict.get("shear_studs_vol_formula", "N.A.")) + r""" & """ + str(input_dict.get("shear_studs_qty", "N.A.")) + r""" & """ + str(input_dict.get("shear_studs_vol_total", "N.A.")) + r""" & """ + str(input_dict.get("shear_studs_wt_single", "N.A.")) + r""" & """ + str(input_dict.get("shear_studs_wt_total", "N.A.")) + r""" \\[6pt]
\hline
6 & Crash Barrier & """ + str(input_dict.get("crash_barrier_vol_formula", "N.A.")) + r""" & """ + str(input_dict.get("crash_barrier_qty", "N.A.")) + r""" & """ + str(input_dict.get("crash_barrier_vol_total", "N.A.")) + r""" & """ + str(input_dict.get("crash_barrier_wt_single", "N.A.")) + r""" & """ + str(input_dict.get("crash_barrier_wt_total", "N.A.")) + r""" \\[6pt]
\hline"""
    )

    # ── Figures for Material Quantities (Requirement 5) ──────────────────────
    steel_chart_path = fig_paths.get("steel_tonnage")
    concrete_rebar_path = fig_paths.get("concrete_vs_rebar")

    figures_tex = []
    if steel_chart_path:
        p_steel = steel_chart_path.replace("\\", "/")
        figures_tex.append(
            r"""
\begin{figure}[H]
\centering
\includegraphics[width=0.92\textwidth]{""" + p_steel + r"""}
\caption{\textbf{Structural Steel Tonnage Breakdown}}
\label{fig:ch7-steel-tonnage}
\end{figure}
"""
        )

    if concrete_rebar_path:
        p_conc = concrete_rebar_path.replace("\\", "/")
        figures_tex.append(
            r"""
\begin{figure}[H]
\centering
\includegraphics[width=0.78\textwidth]{""" + p_conc + r"""}
\caption{\textbf{Concrete Volume ($m^3$) vs. Reinforcement Steel Weight (MT)}}
\label{fig:ch7-concrete-rebar}
\end{figure}
"""
        )

    figures_block = "\n".join(figures_tex)

    return r"""
\chapter{Material Take-off \& Quantity Summary}
\label{ch:material-takeoff}

This chapter details the bill of quantities (BOQ) and provides graphical summaries of the structural materials required for the bridge superstructure, including structural steel tonnage, concrete volume, and reinforcement steel weights.

\section{Bill of Materials}
\label{sec:bom-table}

\begingroup
\setlength{\tabcolsep}{3.5pt}
""" + t71_header + t71_body + r"""
\end{longtable}
\endgroup

\section{Material Quantity Visualizations}
\label{sec:material-charts}

The following charts illustrate the distribution of structural steel among components and compare the overall concrete volume against reinforcement tonnage.

""" + figures_block + r"""
"""
