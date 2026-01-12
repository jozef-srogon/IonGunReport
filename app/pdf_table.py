import os
from typing import List, Tuple
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib.pagesizes import landscape, A3
from reportlab.lib import colors
from tkinter import messagebox

from app.rules import (get_rules_for, RATIO_RANGE_NEXSA, RATIO_RANGE_ESCALAB, SHIFT_RANGE, RATIO_RANGE_SPEC)
from app.validation import (validate_row, in_range, apply_red)

def export_txt_to_pdf(system, output_dir, system_var: bool, ionGun_var: bool, isISS: bool, isOE:bool):
    pdf_path = os.path.join(output_dir, "BestModeData_V3.pdf")
    pdf = SimpleDocTemplate(pdf_path, pagesize=landscape(A3))
    wrong_modes: List[Tuple[str, str]] = []

    def _get_system_type() -> str:
        SYSTEM_TYPE_MAP = {
            (True,  True,  True):  "NEXSA_MAGCIS_ISS",
            (True,  True,  False): "NEXSA_MAGCIS",
            (True,  False, True):  "NEXSA_EX06_ISS",
            (True,  False, False): "EX06",
            (False, True,  False): "ESQ_MAGCIS",
            (False, False, False): "EX06",
        }
        key = (system_var, ionGun_var, isISS)
        return SYSTEM_TYPE_MAP.get(key, "")
    
    
    def _build_table_data():
        headers1 = [
            "Date and Time", "", "Ion Energy", "", "Electron Energy", "", "Fil",
            "Extractor", "Condenser", "Drift", "Magnet", "Focus", "X Shift", "Y Shift", "Ratio",
            "Sample Current", "", "", "Mode Type", "Passed Specification"
        ]
        headers2 = [
            "", "", "(eV)", "(μA)", "(eV)", "(mA)", "(eV)",
            "(eV)", "(eV)", "(eV)", "(A)", "(eV)", "", "", "",
            "(work)", "(max)", "(aim)", "", ""
        ]
        data = [headers1, headers2]

        for m in system.results:
            data.append([
                f"{m.index} {m.date}", m.setup,
                m.ion_energy_eV, m.ion_energy_uA,
                m.electron_energy_eV, m.electron_energy_mA,
                m.fil, m.extractor, m.condensor,
                m.drift, m.magnet, m.focus,
                m.X_shift, m.Y_shift, m.ratio,
                m.sample_current_work, m.sample_current_max,
                m.sample_current_aim, m.mode, m.specification
            ])
        return data

    def _make_table_style(font_size: int = 9) -> TableStyle:
        style_cmds = [
            ('BACKGROUND', (0, 0), (-1, 1), colors.lightgrey),
            ('GRID', (0, 0), (-1, -1), 0.25, colors.black),
            ('FONTNAME', (0, 0), (-1, 1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), font_size),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ]

        horizontal_spans = [
            (15, 0, 17, 0),
            (4,  0,  5, 0),
            (2,  0,  3, 0),
        ]
        for c0, r0, c1, r1 in horizontal_spans:
            style_cmds.append(('SPAN', (c0, r0), (c1, r1)))
            style_cmds.append(('ALIGN', (c0, r0), (c1, r1), 'CENTER'))

        vertical_cols = [12, 13, 14, 18, 19, 0, 1]
        for col in vertical_cols:
            style_cmds.append(('SPAN', (col, 0), (col, 1)))
            style_cmds.append(('VALIGN', (col, 0), (col, 1), 'MIDDLE'))
            style_cmds.append(('ALIGN', (col, 0), (col, 1), 'CENTER'))

        return TableStyle(style_cmds)

    table_data = _build_table_data()
    table = Table(table_data)
    style = _make_table_style()

    system_type = _get_system_type()
    if not system_type:
        messagebox.showerror("Error", "Select correct system")
        return []

    try:
        rules = get_rules_for(system_name=system_type, preset="default")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to load rules for {system_type}: {e}")
        return []

    param_col_index = {
        "extractor": 7,
        "condensor": 8,
        "drift": 9,
        "magnet": 10,
        "Xshift": 12,
        "Yshift": 13,
        "ratio": 14,
        "specification": 19
    }

    apply_red_local = apply_red if not isOE else (lambda *args, **kwargs: None)
    in_range_local = in_range
    ratio_range = RATIO_RANGE_NEXSA if system_var else RATIO_RANGE_ESCALAB
    ratio_range_spec = RATIO_RANGE_SPEC
    shift_range = SHIFT_RANGE
    

    for row, m in enumerate(system.results, start=2):
        idx_str = str(m.index)

        for param in validate_row(m, rules):
            col = param_col_index.get(param)
            if col is not None:
                apply_red_local(style, col, row)
                wrong_modes.append((m.index, param))
        if m.specification == "OK" and not in_range_local(m.ratio, *ratio_range_spec):
            apply_red_local(style, param_col_index["ratio"], row)
            wrong_modes.append([m.index, "ratio"])
        elif not in_range_local(m.ratio, *ratio_range): 
            apply_red_local(style, param_col_index["ratio"], row)
            wrong_modes.append([m.index, "ratio"])

        if not in_range_local(m.X_shift, *shift_range):
            apply_red_local(style, param_col_index["Xshift"], row)
            wrong_modes.append([m.index, "Xshift"])

        if not in_range_local(m.Y_shift, *shift_range):
            apply_red_local(style, param_col_index["Yshift"], row)
            wrong_modes.append([m.index, "Yshift"])

        if m.specification and str(m.specification).strip().upper() != "OK":
            apply_red_local(style, param_col_index["specification"], row)
            wrong_modes.append([m.index, "specification"])

    
    table.setStyle(style)
    try:
        pdf.build([table])
    except Exception as e:
        messagebox.showerror(
            "Permission denied",
            f"Cannot write to '{pdf_path}'.\n\nThe file may be open in another application. "
            "Please close it and try again."
        )
        return None
    
    return wrong_modes
