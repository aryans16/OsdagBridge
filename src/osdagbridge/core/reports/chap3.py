# =============================================================================
# Chapter 3: Loads and Load Combinations
# Refactored for FOSSEE OsdagBridge LaTeX Report Generator
# - Separated Vehicle Live Loads and Footway Live Loads into distinct tables
# - Structured unit columns (Total Load, Impact Factor, Braking Load parameters)
# - Standardized longtable headers with \endfirsthead and \endhead across page breaks
# =============================================================================

from osdagbridge.core.utils.common import (
    KEY_CB_LOAD,
    KEY_LL_CUSTOM_VEHICLES,
    KEY_LL_FOOTPATH_PRESSURE_MODE,
    KEY_LL_FOOTPATH_PRESSURE_VALUE,
    KEY_LL_IRC_70R_BOGIE,
    KEY_LL_IRC_70R_TRACKED,
    KEY_LL_IRC_70R_WHEELED,
    KEY_LL_IRC_AA_TRACKED,
    KEY_LL_IRC_AA_WHEELED,
    KEY_LL_IRC_CLASS_A,
    KEY_LL_IRC_CLASS_FATIGUE,
    KEY_LL_IRC_CLASS_SV,
    KEY_MATERIAL_DECK_DENSITY,
    KEY_MATERIAL_GIRDER_DENSITY,
    KEY_PL_SELF_WEIGHT_FACTOR,
    KEY_RL_LOAD_VALUE,
    KEY_SL_DAMPING,
    KEY_SL_DEAD_LOAD_MODE,
    KEY_SL_DEAD_LOAD_VALUE,
    KEY_SL_HORIZONTAL_COEFF,
    KEY_SL_IMPORTANCE_FACTOR,
    KEY_SL_LIVE_LOAD_MODE,
    KEY_SL_LIVE_LOAD_VALUE,
    KEY_SL_SEISMIC_ZONE,
    KEY_SL_SOIL_TYPE,
    KEY_SL_SPECTRAL_COEFF,
    KEY_SL_TIME_PERIOD,
    KEY_SL_VERTICAL_COEFF,
    KEY_SL_ZONE_FACTOR,
    KEY_SPAN,
    KEY_TL_BRIDGE_TEMP_MAX,
    KEY_TL_BRIDGE_TEMP_MIN,
    KEY_TL_HIGHEST_MAX_TEMP,
    KEY_TL_LOWEST_MIN_TEMP,
    KEY_TL_TEMP_FALL,
    KEY_TL_TEMP_RISE,
    KEY_WC_LD_LANE_TABLE_COUNT,
    KEY_WC_MATERIAL,
    KEY_WC_THICKNESS,
    KEY_WL_AVG_EXPOSED_HEIGHT,
    KEY_WL_BASIC_WIND_SPEED,
    KEY_WL_HOURLY_MEAN_WIND,
    KEY_WL_HOURLY_WIND_PRESSURE,
    KEY_WL_LONGITUDINAL_WIND_FORCE,
    KEY_WL_TERRAIN_TYPE,
    KEY_WL_TRANSVERSE_WIND_FORCE,
    KEY_WL_VERTICAL_WIND_FORCE
)

from osdagbridge.core.reports.report_utils import _tex, _render_value
from osdagbridge.core.reports.styles import build_longtable_header, TABLE_STYLE


def ch3_loads(input_dict):
    from osdagbridge.core.utils.codes.irc6_2017 import IRC6_2017

    span = input_dict.get(KEY_SPAN)
    span_m = None
    if span not in (None, ""):
        try:
            span_m = float(span)
        except Exception:
            span_m = None

    # Calculate Impact Factors per IRC 6
    try:
        im_a = IRC6_2017.cl_208_2_impact_factor(span_m) if span_m is not None else None
        im_a_str = f"{1.0 + im_a:.3f}" if im_a is not None else "N/A"
    except Exception:
        im_a_str = "N/A"

    try:
        im_heavy = IRC6_2017.cl_208_3_impact_factor(span_m) if span_m is not None else None
        im_heavy_str = f"{1.0 + im_heavy:.3f}" if im_heavy is not None else "N/A"
    except Exception:
        im_heavy_str = "N/A"

    # Calculate Braking Force per IRC 6 Cl. 211
    lanes = input_dict.get(KEY_WC_LD_LANE_TABLE_COUNT)
    lanes_int = None
    if lanes not in (None, ""):
        try:
            lanes_int = max(1, int(lanes))
        except Exception:
            lanes_int = None

    try:
        braking_force_t = IRC6_2017.cl_211_2_braking_force(lanes_int) if lanes_int is not None else None
        braking_force_kN = braking_force_t * 9.81 if braking_force_t is not None else None
        braking_force_val_str = f"{braking_force_kN:.2f}" if braking_force_kN is not None else "N/A"
    except Exception:
        braking_force_val_str = "N/A"

    # ─────────────────────────────────────────────────────────────────────────
    # 1. Structure Vehicle Live Load Table (Requirement 3)
    # Columns: vehicle class, selected-load total, impact, braking, eccentricity,
    # and centrifugal force. Centrifugal demand is N/A because curvature is not
    # represented by the current bridge input model.
    # ─────────────────────────────────────────────────────────────────────────
    vehicle_rows = []

    def add_vehicle_row(name, total_load, impact, braking, eccentricity):
        values = (name, total_load, impact, braking, eccentricity, "N/A")
        vehicle_rows.append(
            " & ".join(_tex(str(value)) for value in values)
            + f" \\\\[{TABLE_STYLE.ROW_HEIGHT_PT}]\n\\hline"
        )

    standard_vehicles = (
        (KEY_LL_IRC_CLASS_A, "Class A", "554", im_a_str, braking_force_val_str, "1.2"),
        (KEY_LL_IRC_70R_WHEELED, "Class 70R (Wheeled)", "1000", im_heavy_str, braking_force_val_str, "1.2"),
        (KEY_LL_IRC_70R_TRACKED, "Class 70R (Tracked)", "700", im_heavy_str, braking_force_val_str, "1.2"),
        (KEY_LL_IRC_AA_WHEELED, "Class AA (Wheeled)", "400", im_heavy_str, braking_force_val_str, "1.2"),
        (KEY_LL_IRC_AA_TRACKED, "Class AA (Tracked)", "700", im_heavy_str, braking_force_val_str, "1.2"),
        (KEY_LL_IRC_70R_BOGIE, "Class 70R (Bogie)", "400", im_heavy_str, braking_force_val_str, "1.2"),
        (KEY_LL_IRC_CLASS_SV, "Class SV", "3920", "N/A", "---", "---"),
        (KEY_LL_IRC_CLASS_FATIGUE, "Class Fatigue", "400", "N/A", "---", "---"),
    )
    for key, name, total_load, impact, braking, eccentricity in standard_vehicles:
        if input_dict.get(key, False):
            add_vehicle_row(name, total_load, impact, braking, eccentricity)

    custom_vehicles = input_dict.get(KEY_LL_CUSTOM_VEHICLES) or []
    if isinstance(custom_vehicles, list):
        for vehicle in custom_vehicles:
            if isinstance(vehicle, dict):
                if not vehicle.get("included", True):
                    continue
                name = vehicle.get("name")
            else:
                name = str(vehicle)
            if name:
                add_vehicle_row(name, "As defined", "N/A", "N/A", "N/A")

    if not vehicle_rows:
        vehicle_rows.append(
            r"No vehicle class selected & \multicolumn{5}{c|}{N/A} \\\\" + f"[{TABLE_STYLE.ROW_HEIGHT_PT}]\n\\hline"
        )

    vehicle_table_body = "\n".join(vehicle_rows)

    # ─────────────────────────────────────────────────────────────────────────
    # 2. Footway Live Load Details (Requirement 3: Separate Table)
    # ─────────────────────────────────────────────────────────────────────────
    fp_mode = input_dict.get(KEY_LL_FOOTPATH_PRESSURE_MODE, "")
    fp_value = input_dict.get(KEY_LL_FOOTPATH_PRESSURE_VALUE, "")
    if str(fp_mode).strip().lower() in ("as per irc 6", "as per irc6", "automatic", ""):
        try:
            fp_intensity = f"{IRC6_2017.cl_206_1_footway_load():.3f} kN/m²"
            fp_clause = "IRC 6:2017 Cl. 206.1"
        except Exception:
            fp_intensity = "5.000 kN/m²"
            fp_clause = "IRC 6:2017 Cl. 206.1"
    elif fp_value not in (None, ""):
        fp_intensity = f"{fp_value} kN/m²"
        fp_clause = "User Defined / IRC 6"
    else:
        fp_intensity = "5.000 kN/m²"
        fp_clause = "IRC 6:2017 Cl. 206.1"

    footpath_presence = input_dict.get("superstructure.footpath", "None")
    footpath_str = str(footpath_presence) if footpath_presence not in (None, "", "None") else "None / Not Applicable"

    # Wind Load
    vz_val = input_dict.get(KEY_WL_HOURLY_MEAN_WIND)
    pz_val = input_dict.get(KEY_WL_HOURLY_WIND_PRESSURE)
    if not vz_val or not pz_val:
        try:
            _vb = input_dict.get(KEY_WL_BASIC_WIND_SPEED) or input_dict.get('wind_speed')
            _h = input_dict.get(KEY_WL_AVG_EXPOSED_HEIGHT)
            _ter = {
                "Plain Terrain": "plain",
                "Terrain with Obstructions": "obstructed",
            }.get(str(input_dict.get(KEY_WL_TERRAIN_TYPE, "")).strip(), "plain")
            _res = IRC6_2017.table_12(float(_h), _ter, float(_vb))
            if not vz_val:
                vz_val = _res.get("Vz")
            if not pz_val:
                pz_val = _res.get("Pz")
        except Exception:
            pass
    vz_str = f"{float(vz_val):.2f} m/s" if vz_val not in (None, "") else "N/A"
    pz_str = f"{float(pz_val):.2f} N/m²" if pz_val not in (None, "") else "N/A"

    # Seismic Load
    sl_zone_factor = input_dict.get(KEY_SL_ZONE_FACTOR)
    sl_spectral = input_dict.get(KEY_SL_SPECTRAL_COEFF)
    sl_ah = input_dict.get(KEY_SL_HORIZONTAL_COEFF)
    sl_av = input_dict.get(KEY_SL_VERTICAL_COEFF)
    if not sl_ah or not sl_zone_factor:
        try:
            _zone = input_dict.get(KEY_SL_SEISMIC_ZONE) or input_dict.get('seismic_zone')
            _zmap = {"1": "I", "2": "II", "3": "III", "4": "IV", "5": "V"}
            _z = str(_zone).strip().upper()
            if _z.isdigit():
                _z = _zmap.get(_z)
            _smap = {"Type I – Rocky or Hard": 1, "Type II – Medium Soil": 2, "Type III – Soft Soil": 3}
            _st = _smap.get(str(input_dict.get(KEY_SL_SOIL_TYPE, "")), 1)
            _tp = input_dict.get(KEY_SL_TIME_PERIOD)
            _damp = input_dict.get(KEY_SL_DAMPING) or "5"
            _dl_v = input_dict.get(KEY_SL_DEAD_LOAD_VALUE)
            _ll_v = input_dict.get(KEY_SL_LIVE_LOAD_VALUE)
            _dead = float(_dl_v) if str(input_dict.get(KEY_SL_DEAD_LOAD_MODE, "")) == "Custom" and _dl_v else 0.0
            _live = float(_ll_v) if str(input_dict.get(KEY_SL_LIVE_LOAD_MODE, "")) == "Custom" and _ll_v else 0.0
            _res = IRC6_2017.cl_218_5_1(
                zone=f"Zone {_z}", soil_type=_st, dead_load_kN=_dead,
                live_load_kN=_live, period_T=float(_tp) if _tp else None,
                damping_percent=float(_damp)
            )
            if not sl_zone_factor:
                sl_zone_factor = _res.get("Z")
            if not sl_spectral:
                sl_spectral = _res.get("Sa_g_adjusted")
            if not sl_ah:
                sl_ah = _res.get("Ah")
            if not sl_av:
                sl_av = round(_res.get("Ah", 0) * 2 / 3, 4)
        except Exception:
            pass

    # Temperature Load
    tl_temp_min = tl_temp_max = tl_rise = tl_fall = "N/A"
    try:
        _tmax = input_dict.get(KEY_TL_HIGHEST_MAX_TEMP) or input_dict.get('shade_temp_max')
        _tmin = input_dict.get(KEY_TL_LOWEST_MIN_TEMP) or input_dict.get('shade_temp_min')
        if _tmax and _tmin:
            _res = IRC6_2017.cl_215_2_effective_bridge_temperature(float(_tmax), float(_tmin), 'metallic', False)
            _bt_min = _res.get('T_min', 0)
            _bt_max = _res.get('T_max', 0)
            _mean = (_bt_max + _bt_min) / 2.0
            tl_temp_min = f"{_bt_min:.2f}"
            tl_temp_max = f"{_bt_max:.2f}"
            tl_rise = f"{_bt_max - _mean:.2f}"
            tl_fall = f"{_mean - _bt_min:.2f}"
    except Exception:
        pass

    # Load Combinations
    _LOAD_LABEL_MAP = {
        'dead_load': 'DL',
        'surfacing': 'SIDL',
        'live_load': 'LL',
        'wind_load': 'WL',
        'thermal_load': 'TL',
        'vehicle_collision': 'VC',
        'barge_impact': 'BI',
        'floating_bodies': 'FB',
        'seismic': 'EQ',
    }

    def _fmt_factors(factors):
        parts = []
        for load, val in factors.items():
            label = _LOAD_LABEL_MAP.get(load, load.upper())
            if isinstance(val, dict):
                add = val.get('adding')
                rel = val.get('relieving')
                add_s = f"{add:.2f}" if add is not None else '--'
                rel_s = f"{rel:.2f}" if rel is not None else '--'
                parts.append(f"{label}({add_s}/{rel_s})")
            else:
                if val is None:
                    continue
                parts.append(f"{label}({val:.2f})")
        return ' + '.join(parts)

    uls_combos = IRC6_2017.uls_load_combinations()
    sls_combos = IRC6_2017.sls_load_combinations()
    lc_rows = []
    for i, combo in enumerate(uls_combos, start=1):
        cases = _fmt_factors(combo['factors'])
        lc_rows.append(f"ULS-{i:02d} & {cases} \\\\[{TABLE_STYLE.ROW_HEIGHT_PT}]\n\\hline")
    for i, combo in enumerate(sls_combos, start=1):
        cases = _fmt_factors(combo['factors'])
        lc_rows.append(f"SLS-{i:02d} & {cases} \\\\[{TABLE_STYLE.ROW_HEIGHT_PT}]\n\\hline")

    lc_rows_str = "\n".join(lc_rows)

    # ─────────────────────────────────────────────────────────────────────────
    # Assembly with Standard Repeated Headers (build_longtable_header)
    # ─────────────────────────────────────────────────────────────────────────
    hdr_t31 = build_longtable_header(
        col_spec="|L{5.5cm}|p{10.0cm}|",
        caption="Dead Load -- Self Weight",
        headers=["Parameter", "Value"],
        label="tab:ch3-dl-sw"
    )

    hdr_t32 = build_longtable_header(
        col_spec="|L{5.5cm}|p{10.0cm}|",
        caption="Dead Load for Surfacing (DW)",
        headers=["Parameter", "Value"],
        label="tab:ch3-dl-dw"
    )

    # Table 3.3: Vehicle load parameters; centrifugal values remain explicit when unsupported.
    vehicle_headers = [
        r"\textbf{Vehicle Class}",
        r"\textbf{\makecell{Total Load\\(kN)}}",
        r"\textbf{\makecell{Impact\\Factor}}",
        r"\textbf{\makecell{Braking Load\\(kN)}}",
        r"\textbf{\makecell{Eccentricity\\(m)}}",
        r"\textbf{\makecell{Centrifugal Force\\(kN)}}",
    ]
    row_end = chr(92) * 2
    vehicle_header_row = " & ".join(vehicle_headers) + " " + row_end
    t33_header = "\n".join([
        r"\begin{longtable}{|C{2.5cm}|C{1.7cm}|C{1.7cm}|C{1.7cm}|C{1.8cm}|C{2.0cm}|}",
        r"\caption{\textbf{Vehicle Live Load Parameters (IRC 6:2017)}}\label{tab:ch3-live-loads}" + row_end,
        r"\hline",
        vehicle_header_row,
        r"\hline",
        r"\endfirsthead",
        "",
        r"\multicolumn{6}{c}{\tablename\ \thetable\ -- \textit{Continued from previous page}} " + row_end + "[4pt]",
        r"\hline",
        vehicle_header_row,
        r"\hline",
        r"\endhead",
        "",
        r"\hline",
        r"\multicolumn{6}{r}{\footnotesize\textit{Continued on next page\dots}} " + row_end,
        r"\endfoot",
        "",
        r"\hline",
        r"\endlastfoot",
    ]) + "\n"

    # Table 3.4: Distinct Footway Live Load Table
    hdr_t34 = build_longtable_header(
        col_spec="|L{6.0cm}|p{9.5cm}|",
        caption="Pedestrian / Footway Live Load Details",
        headers=["Parameter", "Design Value / Specification"],
        label="tab:ch3-footway"
    )

    hdr_t35 = build_longtable_header(
        col_spec="|L{5.5cm}|p{10.0cm}|",
        caption="Wind Load (WL) --- per IRC 6:2017",
        headers=["Parameter", "Value"],
        label="tab:ch3-wind"
    )

    hdr_t36 = build_longtable_header(
        col_spec="|L{5.5cm}|p{10.0cm}|",
        caption=r"Earthquake Load (EL) --- per IRC 6 \& IRC SP:114",
        headers=["Parameter", "Value"],
        label="tab:ch3-seismic"
    )

    hdr_t37 = build_longtable_header(
        col_spec="|L{5.5cm}|p{10.0cm}|",
        caption="Temperature Load (TL) --- per IRC 6:2017",
        headers=["Parameter", "Value"],
        label="tab:ch3-temperature"
    )

    hdr_t38 = build_longtable_header(
        col_spec="|C{3.5cm}|p{12.0cm}|",
        caption=r"Governing Design Load Combinations (ULS \& SLS)",
        headers=["Combination ID", r"Governing Load Cases \& Partial Factors"],
        label="tab:ch3-combos"
    )

    return r"""
\chapter{Loads and Load Combinations}

This section summarizes all dead loads, vehicle live loads, pedestrian loads, environmental loads (wind, seismic, thermal), and the governing limit-state load combinations considered for the structural analysis and design of the bridge.

\vspace{0.8em}
""" + hdr_t31 + r"""
\textnormal{Steel Self-Weight Applied} & """ + (_render_value(input_dict, KEY_MATERIAL_GIRDER_DENSITY, ' kN/m\\textsuperscript{3}')) + r""" \\[6pt]
\hline
\textnormal{Concrete Deck Weight} & """ + (_render_value(input_dict, KEY_MATERIAL_DECK_DENSITY, ' kN/m\\textsuperscript{3}')) + r""" \\[6pt]
\hline
\textnormal{Self-Weight Factor} & """ + (_render_value(input_dict, KEY_PL_SELF_WEIGHT_FACTOR)) + r""" \\[6pt]
\end{longtable}

\vspace{0.8em}
""" + hdr_t32 + r"""
\textnormal{Wearing Course Load} & """ + (_render_value(input_dict, KEY_WC_MATERIAL)) + r""" x """ + (_render_value(input_dict, KEY_WC_THICKNESS)) + r""" \\[6pt]
\hline
\textnormal{Additional SIDL (Crash Barrier)} & """ + (_render_value(input_dict, KEY_CB_LOAD)) + r""" kN/m per barrier \\[6pt]
\hline
\textnormal{Railing Load} & """ + (_render_value(input_dict, KEY_RL_LOAD_VALUE)) + r""" kN/m\sdstar{} \\[6pt]
\end{longtable}

\vspace{0.8em}
""" + t33_header + vehicle_table_body + r"""
\end{longtable}
\noindent\textit{Vehicle rows follow the active UI selection. Braking loads follow IRC 6:2017 Cl. 211. Centrifugal force is reported as N/A because the current bridge inputs do not provide curvature data for its calculation.}

\vspace{1.0em}
""" + hdr_t34 + r"""
\textnormal{Footpath Provision} & """ + _tex(footpath_str) + r""" \\[6pt]
\hline
\textnormal{Footway Live Load Intensity} & """ + _tex(fp_intensity) + r""" \\[6pt]
\hline
\textnormal{Application Mode} & """ + _tex(str(fp_mode) if fp_mode else "Automatic per IRC 6") + r""" \\[6pt]
\hline
\textnormal{Governing Code Reference} & """ + _tex(fp_clause) + r""" \\[6pt]
\end{longtable}
\noindent\textit{Note: Footway live load is applied on designated pedestrian walkways simultaneously with vehicular live loads as prescribed in IRC 6:2017 Clause 206.1.}

\vspace{0.8em}
""" + hdr_t35 + r"""
\textnormal{Basic Wind Speed, $V_b$} & """ + (_render_value(input_dict, 'wind_speed', ' m/s')) + r""" [from Project Location] \\[6pt]
\hline
\textnormal{Terrain Type} & """ + (_render_value(input_dict, KEY_WL_TERRAIN_TYPE)) + r""" \\[6pt]
\hline
\textnormal{Average Exposed Height, $H$} & """ + (_render_value(input_dict, KEY_WL_AVG_EXPOSED_HEIGHT, ' m')) + r""" \\[6pt]
\hline
\textnormal{Hourly Mean Wind Speed, $V_z$} & """ + (_render_value(input_dict, KEY_WL_HOURLY_MEAN_WIND, ' m/s')) + r""" \\[6pt]
\hline
\textnormal{Hourly Wind Pressure, $P_z$} & """ + (_render_value(input_dict, KEY_WL_HOURLY_WIND_PRESSURE, ' N/m\\textsuperscript{2}')) + r""" \\[6pt]
\hline
\textnormal{Transverse Wind Force} & """ + (_render_value(input_dict, KEY_WL_TRANSVERSE_WIND_FORCE, ' kN')) + r""" \\[6pt]
\hline
\textnormal{Longitudinal Wind Force} & """ + (_render_value(input_dict, KEY_WL_LONGITUDINAL_WIND_FORCE, ' kN')) + r""" \\[6pt]
\hline
\textnormal{Vertical Wind Force} & """ + (_render_value(input_dict, KEY_WL_VERTICAL_WIND_FORCE, ' kN')) + r""" \\[6pt]
\end{longtable}

\vspace{0.8em}
""" + hdr_t36 + r"""
\textnormal{Seismic Zone} & """ + (_render_value(input_dict, 'seismic_zone')) + r""" [from Project Location] \\[6pt]
\hline
\textnormal{Zone Factor, $Z$} & """ + (_render_value(input_dict, KEY_SL_ZONE_FACTOR)) + r""" \\[6pt]
\hline
\textnormal{Importance Factor, $I$} & """ + (_render_value(input_dict, KEY_SL_IMPORTANCE_FACTOR)) + r""" \\[6pt]
\hline
\textnormal{Type of Soil} & """ + (_render_value(input_dict, KEY_SL_SOIL_TYPE)) + r""" \\[6pt]
\hline
\textnormal{Spectral Acceleration Coeff., $S_a/g$} & """ + (_render_value(input_dict, KEY_SL_SPECTRAL_COEFF)) + r""" \\[6pt]
\hline
\textnormal{Horizontal Seismic Coeff., $A_h$} & """ + (_render_value(input_dict, KEY_SL_HORIZONTAL_COEFF)) + r""" \\[6pt]
\hline
\textnormal{Vertical Seismic Coeff., $A_v$} & """ + (_render_value(input_dict, KEY_SL_VERTICAL_COEFF)) + r""" \\[6pt]
\end{longtable}

\vspace{0.8em}
""" + hdr_t37 + r"""
\textnormal{Maximum Shade Temperature} & """ + (_render_value(input_dict, 'shade_temp_max')) + r""" $^\circ$C \\[6pt]
\hline
\textnormal{Minimum Shade Temperature} & """ + (_render_value(input_dict, 'shade_temp_min')) + r""" $^\circ$C \\[6pt]
\hline
\textnormal{Effective Bridge Temp. Range} & """ + (_render_value(input_dict, KEY_TL_BRIDGE_TEMP_MIN)) + r""" to """ + (_render_value(input_dict, KEY_TL_BRIDGE_TEMP_MAX)) + r""" $^\circ$C \\[6pt]
\hline
\textnormal{Temperature Rise / Fall for Design} & +""" + (_render_value(input_dict, KEY_TL_TEMP_RISE)) + r""" $^\circ$C / \textminus{}""" + (_render_value(input_dict, KEY_TL_TEMP_FALL)) + r""" $^\circ$C \\[6pt]
\end{longtable}

\vspace{0.8em}
""" + hdr_t38 + lc_rows_str + r"""
\end{longtable}

\noindent\textit{Note: All IRC 6 load combinations are auto-generated by OsdagBridge per Table B.1 to B.4. Partial safety factors for Ultimate Limit State (ULS) and Serviceability Limit State (SLS) are rigorously applied.}
"""
