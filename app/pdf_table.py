import os
from typing import List, Tuple
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib.pagesizes import landscape, A3
from reportlab.lib import colors
from tkinter import messagebox

from app.rules import (get_rules_for, RATIO_RANGE_NEXSA, RATIO_RANGE_ESCALAB, SHIFT_RANGE, RATIO_RANGE_SPEC)
from app.validation import (validate_row, in_range, apply_red)
from app.functions import resource_path
from app.systemConfig import get_system_config
from app.watermark import draw_image_watermark

def export_txt_to_pdf(system, output_dir, system_var: bool, ionGun_var: bool, isISS: bool, isOE:bool):
    pdf_path = os.path.join(output_dir, "BestModeData_V3.pdf")
    pdf = SimpleDocTemplate(pdf_path, pagesize=landscape(A3), topMargin=30)
    wrong_modes: List[Tuple[str, str]] = []

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

    cfg = get_system_config(system_var, ionGun_var, isISS)
    
    if not cfg:
        messagebox.showerror("Error", "Select correct system")
        return None
    
    max_i = cfg["rows"]
    system_type = cfg["system"]

    results_sorted = sorted(system.results, key=lambda m: int(str(m.index).strip("[]")))
    sorted_by_idx = {int(str(m.index).strip("[]")): m for m in results_sorted}

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

        for i in range(max_i + 1):
            m = sorted_by_idx.get(i)
            if m is None:
                data.append(_empty_row_for_index())
            else:
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

    try:
        rules = get_rules_for(system_name=system_type, preset="default")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to load rules for {system_type}: {e}")
        return None

    row = 2
    for i in range(max_i + 1):
        m = sorted_by_idx.get(i)
        if m is None:
            row += 1
            continue

        for param, rng in validate_row(m, rules):
            col = param_col_index.get(param)
            if col is not None:
                apply_red_local(style, col, row)
                wrong_modes.append([m.index, param, rng])
        if m.specification == "OK" and not in_range_local(m.ratio, *ratio_range_spec):
            apply_red_local(style, param_col_index["ratio"], row)
            wrong_modes.append([m.index, "ratio", ratio_range_spec])
        elif not in_range_local(m.ratio, *ratio_range): 
            apply_red_local(style, param_col_index["ratio"], row)
            wrong_modes.append([m.index, "ratio", ratio_range])
        if not in_range_local(m.X_shift, *shift_range):
            apply_red_local(style, param_col_index["Xshift"], row)
            wrong_modes.append([m.index, "Xshift", shift_range])
        if not in_range_local(m.Y_shift, *shift_range):
            apply_red_local(style, param_col_index["Yshift"], row)
            wrong_modes.append([m.index, "Yshift", shift_range])
        if m.specification and str(m.specification).strip().upper() != "OK":
            apply_red_local(style, param_col_index["specification"], row)
            wrong_modes.append([m.index, "specification", ''])

        row += 1

    table.setStyle(style)
    try:
        watermark_path = resource_path(f"assets/{system_type}.jpg")
        pdf.build([
            table
            ],
            onFirstPage=lambda c, d: draw_image_watermark(c, d, watermark_path),
            onLaterPages=lambda c, d: draw_image_watermark(c, d, watermark_path))
    except Exception as e:
        messagebox.showerror(
            "Permission denied",
            f"Cannot write to '{pdf_path}'.\n\nThe file may be open in another application. "
            "Please close it and try again."
        )
        return None
    
    return wrong_modes

def _empty_row_for_index():
    return ["", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", ""]