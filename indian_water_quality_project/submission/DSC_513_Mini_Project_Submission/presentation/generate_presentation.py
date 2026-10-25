#!/usr/bin/env python3
"""
Generate the 18-slide Academic PowerPoint Presentation (.pptx) and
Slide-by-Slide Speaker Notes & Viva Guide (.md) for:
Geographic and Seasonal Analysis of Surface Water Quality in India Using CPCB Monitoring Data
Student: Emmanuel Jobin (2026EMAI20054) | Course: DSC 513 - Introduction to Data Science | IIIT Kottayam
"""

import os
import shutil
import struct
import subprocess
import zipfile
from xml.sax.saxutils import escape

PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
FIG_DIR = os.path.join(PROJECT_DIR, "figures")
PRES_DIR = os.path.join(PROJECT_DIR, "presentation")
os.makedirs(PRES_DIR, exist_ok=True)

PPTX_OUT = os.path.join(PRES_DIR, "CPCB_Water_Quality_Mini_Project_Presentation.pptx")
PPTX_ROOT_COPY = os.path.join(PROJECT_DIR, "CPCB_Water_Quality_Mini_Project_Presentation.pptx")
GUIDE_OUT = os.path.join(PRES_DIR, "Presentation_Speaker_Notes_and_Viva_Guide.md")

# 1 inch = 914400 EMUs (Slide is 10.0 in x 5.625 in = 9144000 x 5143500 EMUs)
EMU = 914400


def emu(inches):
    return int(round(inches * EMU))


def get_png_size(path):
    with open(path, "rb") as f:
        header = f.read(24)
        w, h = struct.unpack(">II", header[16:24])
    return w, h


# Color Palette (Academic Navy, Teal, Warm Amber, Crisp Slate)
NAVY = "1B365D"
DARK_NAVY = "0F2342"
TEAL = "007A78"
AMBER = "D95F02"
SLATE_TEXT = "1E293B"
MUTED_TEXT = "475569"
CARD_BG = "F4F7FA"
CARD_BORDER = "CBD5E1"
ALT_ROW_BG = "EBF1F6"
CODE_BG = "F8FAFC"
CODE_BORDER = "94A3B8"
WHITE = "FFFFFF"
LIGHT_TEAL_BG = "E6F4F1"
LIGHT_AMBER_BG = "FFF5EB"


class SlideBuilder:
    def __init__(self, slide_num, total_slides=18):
        self.slide_num = slide_num
        self.total_slides = total_slides
        self.shapes = []
        self.rels = [
            (
                "rId1",
                "http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideLayout",
                "../slideLayouts/slideLayout7.xml",
            ),
            (
                "rId2",
                "http://schemas.openxmlformats.org/officeDocument/2006/relationships/notesSlide",
                f"../notesSlides/notesSlide{slide_num}.xml",
            ),
        ]
        self.next_id = 2
        self.next_rid = 3
        self.images_used = []  # list of (rid, media_filename, src_path)

    def _id(self):
        i = self.next_id
        self.next_id += 1
        return i

    def add_rect(
        self,
        x,
        y,
        w,
        h,
        fill=CARD_BG,
        border=None,
        border_pt=1.0,
        rounded=False,
    ):
        sid = self._id()
        geom = "roundRect" if rounded else "rect"
        av = '<a:gd name="adj" fmla="val 4000"/>' if rounded else ""
        fill_xml = f'<a:solidFill><a:srgbClr val="{fill}"/></a:solidFill>' if fill else "<a:noFill/>"
        if border:
            bw = int(round(border_pt * 12700))
            ln_xml = f'<a:ln w="{bw}"><a:solidFill><a:srgbClr val="{border}"/></a:solidFill></a:ln>'
        else:
            ln_xml = "<a:ln><a:noFill/></a:ln>"

        xml = (
            f'<p:sp><p:nvSpPr><p:cNvPr id="{sid}" name="Rect {sid}"/>'
            f'<p:cNvSpPr/><p:nvPr/></p:nvSpPr>'
            f'<p:spPr><a:xfrm><a:off x="{emu(x)}" y="{emu(y)}"/>'
            f'<a:ext cx="{emu(w)}" cy="{emu(h)}"/></a:xfrm>'
            f'<a:prstGeom prst="{geom}"><a:avLst>{av}</a:avLst></a:prstGeom>'
            f"{fill_xml}{ln_xml}</p:spPr></p:sp>"
        )
        self.shapes.append(xml)

    def add_textbox(
        self,
        x,
        y,
        w,
        h,
        paragraphs,
        fill=None,
        border=None,
        border_pt=1.0,
        pad=(0.08, 0.06, 0.08, 0.06),
        anchor="t",
        rounded=False,
    ):
        """
        paragraphs: list of dicts or tuples/strings:
          - str: normal paragraph
          - dict: {
              'text': str or list of (run_text, bold, color, size_pt, font, italic),
              'size': 11,
              'bold': False,
              'italic': False,
              'color': SLATE_TEXT,
              'align': 'l'|'ctr'|'r',
              'bullet': False,
              'font': 'Calibri',
              'space_after': 4,
              'space_before': 0
            }
        """
        sid = self._id()
        geom = "roundRect" if rounded else "rect"
        av = '<a:gd name="adj" fmla="val 4000"/>' if rounded else ""
        fill_xml = f'<a:solidFill><a:srgbClr val="{fill}"/></a:solidFill>' if fill else "<a:noFill/>"
        if border:
            bw = int(round(border_pt * 12700))
            ln_xml = f'<a:ln w="{bw}"><a:solidFill><a:srgbClr val="{border}"/></a:solidFill></a:ln>'
        else:
            ln_xml = "<a:ln><a:noFill/></a:ln>"

        l_ins, t_ins, r_ins, b_ins = [emu(p) for p in pad]
        p_xml_list = []

        for p in paragraphs:
            if isinstance(p, str):
                p = {"text": p}
            align = p.get("align", "l")
            bullet = p.get("bullet", False)
            spc_bef = int(p.get("space_before", 0) * 100)
            spc_aft = int(p.get("space_after", 4) * 100)
            def_size = int(round(p.get("size", 11) * 100))
            def_bold = "1" if p.get("bold", False) else "0"
            def_ital = "1" if p.get("italic", False) else "0"
            def_col = p.get("color", SLATE_TEXT)
            def_font = p.get("font", "Calibri")

            if bullet:
                ppr = (
                    f'<a:pPr marL="190500" indent="-142875" algn="{align}">'
                    f'<a:spcBef><a:spcPts val="{spc_bef}"/></a:spcBef>'
                    f'<a:spcAft><a:spcPts val="{spc_aft}"/></a:spcAft>'
                    f'<a:buFont typeface="Arial"/><a:buChar char="•"/></a:pPr>'
                )
            else:
                ppr = (
                    f'<a:pPr marL="0" indent="0" algn="{align}">'
                    f'<a:spcBef><a:spcPts val="{spc_bef}"/></a:spcBef>'
                    f'<a:spcAft><a:spcPts val="{spc_aft}"/></a:spcAft>'
                    f"<a:buNone/></a:pPr>"
                )

            runs = p.get("runs", None)
            if runs is None:
                runs = [
                    (
                        p.get("text", ""),
                        p.get("bold", False),
                        def_col,
                        p.get("size", 11),
                        def_font,
                        p.get("italic", False),
                    )
                ]

            r_xml = []
            for r in runs:
                r_txt = escape(str(r[0]))
                r_b = "1" if (len(r) > 1 and r[1]) else "0"
                r_c = r[2] if len(r) > 2 and r[2] else def_col
                r_sz = int(round((r[3] if len(r) > 3 and r[3] else p.get("size", 11)) * 100))
                r_fn = r[4] if len(r) > 4 and r[4] else def_font
                r_it = "1" if (len(r) > 5 and r[5]) else "0"
                r_xml.append(
                    f'<a:r><a:rPr lang="en-US" sz="{r_sz}" b="{r_b}" i="{r_it}" dirty="0">'
                    f'<a:solidFill><a:srgbClr val="{r_c}"/></a:solidFill>'
                    f'<a:latin typeface="{r_fn}"/><a:cs typeface="{r_fn}"/>'
                    f"</a:rPr><a:t>{r_txt}</a:t></a:r>"
                )
            p_xml_list.append(f"<a:p>{ppr}{''.join(r_xml)}</a:p>")

        xml = (
            f'<p:sp><p:nvSpPr><p:cNvPr id="{sid}" name="TextBox {sid}"/>'
            f'<p:cNvSpPr txBox="1"/><p:nvPr/></p:nvSpPr>'
            f'<p:spPr><a:xfrm><a:off x="{emu(x)}" y="{emu(y)}"/>'
            f'<a:ext cx="{emu(w)}" cy="{emu(h)}"/></a:xfrm>'
            f'<a:prstGeom prst="{geom}"><a:avLst>{av}</a:avLst></a:prstGeom>'
            f"{fill_xml}{ln_xml}</p:spPr>"
            f'<p:txBody><a:bodyPr wrap="square" lIns="{l_ins}" tIns="{t_ins}" rIns="{r_ins}" bIns="{b_ins}" anchor="{anchor}"/>'
            f"<a:lstStyle/>{''.join(p_xml_list)}</p:txBody></p:sp>"
        )
        self.shapes.append(xml)

    def add_header_and_footer(self, section_tag, title_text, subtitle_text=""):
        # Top header bar (0 to 0.78 in)
        self.add_rect(0, 0, 10.0, 0.78, fill=NAVY, border=None)
        self.add_rect(0, 0.78, 10.0, 0.04, fill=TEAL, border=None)

        # Section pill & Slide Title
        self.add_textbox(
            0.35,
            0.06,
            9.3,
            0.68,
            [
                {
                    "text": section_tag.upper(),
                    "size": 8.5,
                    "bold": True,
                    "color": "7FD4D2",
                    "space_after": 1,
                },
                {
                    "text": title_text,
                    "size": 17.5,
                    "bold": True,
                    "color": WHITE,
                    "space_after": 1,
                },
            ]
            + (
                [
                    {
                        "text": subtitle_text,
                        "size": 9.5,
                        "italic": True,
                        "color": "DCE6F1",
                        "space_after": 0,
                    }
                ]
                if subtitle_text
                else []
            ),
            pad=(0.02, 0.02, 0.02, 0.02),
        )

        # Bottom footer bar (5.32 to 5.625 in)
        self.add_rect(0, 5.32, 10.0, 0.305, fill="EEF2F6", border=None)
        self.add_textbox(
            0.35,
            5.34,
            7.5,
            0.25,
            [
                {
                    "text": "Emmanuel Jobin (2026EMAI20054)  |  DSC 513: Introduction to Data Science  |  IIIT Kottayam",
                    "size": 8.5,
                    "color": MUTED_TEXT,
                }
            ],
            pad=(0, 0.02, 0, 0),
        )
        self.add_textbox(
            8.0,
            5.34,
            1.65,
            0.25,
            [
                {
                    "text": f"Slide {self.slide_num} of {self.total_slides}",
                    "size": 8.5,
                    "bold": True,
                    "color": NAVY,
                    "align": "r",
                }
            ],
            pad=(0, 0.02, 0, 0),
        )

    def add_image_fit(self, img_filename, box_x, box_y, box_w, box_h, caption=None):
        src_path = os.path.join(FIG_DIR, img_filename)
        pw, ph = get_png_size(src_path)
        aspect = pw / float(ph)

        avail_h = box_h - (0.24 if caption else 0.0)
        if box_w / avail_h > aspect:
            draw_h = avail_h
            draw_w = draw_h * aspect
        else:
            draw_w = box_w
            draw_h = draw_w / aspect

        draw_x = box_x + (box_w - draw_w) / 2.0
        draw_y = box_y + (avail_h - draw_h) / 2.0

        rid = f"rId{self.next_rid}"
        self.next_rid += 1
        media_name = f"s{self.slide_num}_{img_filename}"
        self.rels.append(
            (
                rid,
                "http://schemas.openxmlformats.org/officeDocument/2006/relationships/image",
                f"../media/{media_name}",
            )
        )
        self.images_used.append((media_name, src_path))

        # Subtle white frame around figure
        self.add_rect(
            draw_x - 0.03,
            draw_y - 0.03,
            draw_w + 0.06,
            draw_h + 0.06,
            fill=WHITE,
            border=CARD_BORDER,
            border_pt=0.75,
        )

        sid = self._id()
        pic_xml = (
            f'<p:pic><p:nvPicPr><p:cNvPr id="{sid}" name="Picture {sid}" descr="{escape(img_filename)}"/>'
            f'<p:cNvPicPr><a:picLocks noGrp="1" noChangeAspect="1"/></p:cNvPicPr><p:nvPr/></p:nvPicPr>'
            f'<p:blipFill><a:blip r:embed="{rid}"/><a:stretch><a:fillRect/></a:stretch></p:blipFill>'
            f'<p:spPr bwMode="auto"><a:xfrm><a:off x="{emu(draw_x)}" y="{emu(draw_y)}"/>'
            f'<a:ext cx="{emu(draw_w)}" cy="{emu(draw_h)}"/></a:xfrm>'
            f'<a:prstGeom prst="rect"><a:avLst/></a:prstGeom><a:noFill/></p:spPr></p:pic>'
        )
        self.shapes.append(pic_xml)

        if caption:
            self.add_textbox(
                box_x,
                draw_y + draw_h + 0.04,
                box_w,
                0.22,
                [
                    {
                        "text": caption,
                        "size": 8.5,
                        "italic": True,
                        "color": MUTED_TEXT,
                        "align": "ctr",
                    }
                ],
                pad=(0.02, 0.01, 0.02, 0.01),
            )

    def add_table(self, x, y, w, h, headers, rows, col_Ratios=None, font_size=9.5):
        sid = self._id()
        ncols = len(headers)
        if not col_Ratios:
            col_Ratios = [1.0 / ncols] * ncols
        total_r = sum(col_Ratios)
        col_widths = [emu(w * (r / total_r)) for r in col_Ratios]
        grid_xml = "".join(f'<a:gridCol w="{cw}"/>' for cw in col_widths)

        total_rows = len(rows) + 1
        row_h = emu(h / total_rows)

        def make_cell(text, is_header=False, row_idx=0, col_idx=0):
            bg = NAVY if is_header else (ALT_ROW_BG if row_idx % 2 == 1 else WHITE)
            fg = WHITE if is_header else SLATE_TEXT
            bold = "1" if (is_header or col_idx == 0) else "0"
            sz = int(round((font_size + (0.5 if is_header else 0)) * 100))
            algn = "l" if col_idx == 0 or len(str(text)) > 18 else "ctr"
            if is_header:
                algn = "l" if col_idx == 0 else "ctr"

            border_xml = (
                '<a:lnL w="6350"><a:solidFill><a:srgbClr val="CBD5E1"/></a:solidFill></a:lnL>'
                '<a:lnR w="6350"><a:solidFill><a:srgbClr val="CBD5E1"/></a:solidFill></a:lnR>'
                '<a:lnT w="6350"><a:solidFill><a:srgbClr val="CBD5E1"/></a:solidFill></a:lnT>'
                '<a:lnB w="6350"><a:solidFill><a:srgbClr val="CBD5E1"/></a:solidFill></a:lnB>'
            )
            return (
                f"<a:tc><a:txBody>"
                f'<a:bodyPr lIns="55000" rIns="55000" tIns="32000" bIns="32000" anchor="ctr"/>'
                f"<a:lstStyle/>"
                f'<a:p><a:pPr algn="{algn}"><a:buNone/></a:pPr>'
                f'<a:r><a:rPr lang="en-US" sz="{sz}" b="{bold}" dirty="0">'
                f'<a:solidFill><a:srgbClr val="{fg}"/></a:solidFill>'
                f'<a:latin typeface="Calibri"/></a:rPr>'
                f"<a:t>{escape(str(text))}</a:t></a:r></a:p></a:txBody>"
                f"<a:tcPr>{border_xml}"
                f'<a:solidFill><a:srgbClr val="{bg}"/></a:solidFill></a:tcPr></a:tc>'
            )

        tr_list = []
        tr_list.append(
            f'<a:tr h="{row_h}">'
            + "".join(make_cell(h_txt, is_header=True, col_idx=ci) for ci, h_txt in enumerate(headers))
            + "</a:tr>"
        )
        for ri, r_vals in enumerate(rows):
            tr_list.append(
                f'<a:tr h="{row_h}">'
                + "".join(
                    make_cell(c_txt, is_header=False, row_idx=ri, col_idx=ci)
                    for ci, c_txt in enumerate(r_vals)
                )
                + "</a:tr>"
            )

        xml = (
            f'<p:graphicFrame><p:nvGraphicFramePr><p:cNvPr id="{sid}" name="Table {sid}"/>'
            f'<p:cNvGraphicFramePr><a:graphicFrameLocks noGrp="1"/></p:cNvGraphicFramePr>'
            f"<p:nvPr/></p:nvGraphicFramePr>"
            f'<p:xfrm><a:off x="{emu(x)}" y="{emu(y)}"/><a:ext cx="{emu(w)}" cy="{emu(h)}"/></p:xfrm>'
            f'<a:graphic><a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/table">'
            f"<a:tbl><a:tblPr firstRow=\"1\" bandRow=\"1\"/>"
            f"<a:tblGrid>{grid_xml}</a:tblGrid>"
            f"{''.join(tr_list)}</a:tbl></a:graphicData></a:graphic></p:graphicFrame>"
        )
        self.shapes.append(xml)

    def to_slide_xml(self):
        return (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<p:sld xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" '
            'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" '
            'xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">'
            "<p:cSld><p:spTree>"
            '<p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr>'
            '<p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/>'
            '<a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr>'
            f"{''.join(self.shapes)}"
            "</p:spTree></p:cSld>"
            "<p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr></p:sld>"
        )

    def to_rels_xml(self):
        rel_items = "".join(
            f'<Relationship Id="{rid}" Type="{rtype}" Target="{target}"/>'
            for rid, rtype, target in self.rels
        )
        return (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            f"{rel_items}</Relationships>"
        )


def make_notes_xml(slide_num, notes_paragraphs):
    p_xml = []
    for line in notes_paragraphs:
        bold = "1" if line.startswith("[") or line.endswith(":") else "0"
        p_xml.append(
            f'<a:p><a:r><a:rPr lang="en-US" sz="1100" b="{bold}" dirty="0"/>'
            f"<a:t>{escape(line)}</a:t></a:r></a:p>"
        )
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<p:notes xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" '
        'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" '
        'xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">'
        "<p:cSld><p:spTree>"
        '<p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr>'
        '<p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/>'
        '<a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr>'
        '<p:sp><p:nvSpPr><p:cNvPr id="2" name="Slide Image Placeholder 1"/>'
        '<p:cNvSpPr><a:spLocks noGrp="1" noRot="1" noChangeAspect="1"/></p:cNvSpPr>'
        '<p:nvPr><p:ph type="sldImg"/></p:nvPr></p:nvSpPr>'
        '<p:spPr><a:xfrm><a:off x="685800" y="1143000"/><a:ext cx="5486400" cy="3086100"/></a:xfrm></p:spPr></p:sp>'
        '<p:sp><p:nvSpPr><p:cNvPr id="3" name="Notes Placeholder 2"/>'
        '<p:cNvSpPr><a:spLocks noGrp="1"/></p:cNvSpPr>'
        '<p:nvPr><p:ph type="body" idx="1"/></p:nvPr></p:nvSpPr>'
        f"<p:spPr/><p:txBody><a:bodyPr/><a:lstStyle/>{''.join(p_xml)}</p:txBody></p:sp>"
        '<p:sp><p:nvSpPr><p:cNvPr id="4" name="Slide Number Placeholder 3"/>'
        '<p:cNvSpPr><a:spLocks noGrp="1"/></p:cNvSpPr>'
        '<p:nvPr><p:ph type="sldNum" sz="quarter" idx="10"/></p:nvPr></p:nvSpPr>'
        '<p:spPr/><p:txBody><a:bodyPr/><a:lstStyle/><a:p>'
        f'<a:r><a:rPr lang="en-US"/><a:t>{slide_num}</a:t></a:r>'
        "</a:p></p:txBody></p:sp>"
        "</p:spTree></p:cSld><p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr></p:notes>"
    )


def make_notes_rels_xml(slide_num):
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        f'<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide" Target="../slides/slide{slide_num}.xml"/>'
        '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/notesMaster" Target="../notesMasters/notesMaster1.xml"/>'
        "</Relationships>"
    )


def build_all_slides():
    slides = []
    notes_dict = {}

    # =========================================================================
    # SLIDE 1: TITLE SLIDE
    # =========================================================================
    s1 = SlideBuilder(1)
    s1.add_rect(0, 0, 10.0, 5.625, fill=DARK_NAVY)
    s1.add_rect(0, 0, 0.28, 5.625, fill=TEAL)
    s1.add_rect(0.28, 3.62, 9.72, 0.04, fill=TEAL)

    s1.add_textbox(
        0.75,
        0.55,
        8.8,
        2.95,
        [
            {
                "text": "DSC 513 – INTRODUCTION TO DATA SCIENCE MINI PROJECT",
                "size": 11,
                "bold": True,
                "color": "7FD4D2",
                "space_after": 10,
            },
            {
                "text": "Geographic and Seasonal Analysis of Surface Water Quality in India Using CPCB Monitoring Data",
                "size": 25,
                "bold": True,
                "color": WHITE,
                "space_after": 12,
            },
            {
                "text": "Data Cleaning, Exploratory Data Analysis, Non-Parametric Hypothesis Testing, Decadal Comparison, and Simple Linear Regression in R",
                "size": 13,
                "italic": True,
                "color": "DCE6F1",
                "space_after": 6,
            },
        ],
    )

    # Student details box
    s1.add_textbox(
        0.75,
        3.82,
        5.1,
        1.45,
        [
            {"text": "Submitted By:", "size": 10, "bold": True, "color": "7FD4D2", "space_after": 3},
            {"text": "Emmanuel Jobin", "size": 16, "bold": True, "color": WHITE, "space_after": 2},
            {"text": "Register Number: 2026EMAI20054", "size": 12, "bold": True, "color": "FCD34D", "space_after": 4},
            {"text": "M.Tech in Data Science / Artificial Intelligence", "size": 10.5, "color": "E2E8F0", "space_after": 2},
            {"text": "Indian Institute of Information Technology (IIIT) Kottayam", "size": 10.5, "color": "E2E8F0"},
        ],
        fill="162E52",
        border="2D4F7C",
        rounded=True,
    )

    # Empirical scope badges on right
    s1.add_textbox(
        6.05,
        3.82,
        3.45,
        1.45,
        [
            {"text": "Verified Empirical Scope:", "size": 10, "bold": True, "color": "7FD4D2", "space_after": 4},
            {"text": "315 Official CPCB CSVs (311,379 raw rows)", "size": 10, "color": WHITE, "bullet": True, "space_after": 3},
            {"text": "109,422 Harmonized Station-Date Records", "size": 10, "color": WHITE, "bullet": True, "space_after": 3},
            {"text": "4,017 Georeferenced Stations (36 States/UTs)", "size": 10, "color": WHITE, "bullet": True, "space_after": 3},
            {"text": "1,990 Historical Kaggle Records (2003–2014)", "size": 10, "color": WHITE, "bullet": True, "space_after": 2},
        ],
        fill="162E52",
        border="2D4F7C",
        rounded=True,
    )
    slides.append(s1)
    notes_dict[1] = [
        "[Slide 1 — Title Slide]",
        "What to say: Good morning/afternoon Professor and classmates. My name is Emmanuel Jobin (Register Number 2026EMAI20054). Today I am presenting my DSC 513 Introduction to Data Science mini project titled 'Geographic and Seasonal Analysis of Surface Water Quality in India Using CPCB Monitoring Data'.",
        "Project Scope: This study uses R and R Markdown to inspect, clean, analyze, and model 315 official CPCB/NWDP CSV files (311,379 raw rows consolidated into 109,422 station-date records across 4,017 stations in 36 States/UTs) alongside a supplementary 1,990-row historical Kaggle dataset (2003–2014).",
        "Likely Lecturer Question: Why did you choose surface water quality in India? -> Because CPCB monitors thousands of river and lake stations nationwide, providing a rich, real-world multi-file dataset with realistic data-quality challenges (encoding, OCR errors, missing values, skewed distributions) ideal for demonstrating an end-to-end R data science workflow.",
    ]

    # =========================================================================
    # SLIDE 2: INTRODUCTION AND MOTIVATION
    # =========================================================================
    s2 = SlideBuilder(2)
    s2.add_header_and_footer(
        "Section 1  |  Background & Context",
        "Introduction and Motivation",
        "Why monitoring physical, chemical, and biological surface-water indicators across India matters",
    )

    s2.add_textbox(
        0.35,
        0.95,
        4.55,
        2.15,
        [
            {"text": "What is Surface-Water Quality?", "size": 13, "bold": True, "color": NAVY, "space_after": 5},
            {
                "text": "Surface-water quality describes the physical, chemical, and biological condition of rivers, lakes, canals, and reservoirs that supply drinking water, irrigation, and aquatic habitats.",
                "size": 10.5,
                "color": SLATE_TEXT,
                "space_after": 6,
            },
            {
                "text": "In India, the Central Pollution Control Board (CPCB) under the National Water Monitoring Programme (NWMP) tracks water bodies to assess compliance with designated best-use standards (e.g., CPCB Class C for drinking water source with conventional treatment).",
                "size": 10.0,
                "color": SLATE_TEXT,
            },
        ],
        fill=CARD_BG,
        border=CARD_BORDER,
        rounded=True,
    )

    s2.add_textbox(
        0.35,
        3.22,
        4.55,
        1.95,
        [
            {"text": "Why Geographic & Seasonal Analysis Matters", "size": 13, "bold": True, "color": TEAL, "space_after": 5},
            {
                "text": "Geographic Variation: River basins traverse diverse geological zones, agricultural plains, and dense urban-industrial corridors across 36 States and Union Territories.",
                "size": 10.0,
                "color": SLATE_TEXT,
                "bullet": True,
                "space_after": 4,
            },
            {
                "text": "Seasonal Hydrology: India's Southwest Monsoon (June–September) dramatically alters river discharge, diluting organic pollutants compared to low-flow Pre-Monsoon summer months (March–May).",
                "size": 10.0,
                "color": SLATE_TEXT,
                "bullet": True,
            },
        ],
        fill=LIGHT_TEAL_BG,
        border=TEAL,
        rounded=True,
    )

    # Right column: 4 core parameters
    s2.add_textbox(
        5.1,
        0.95,
        4.55,
        4.22,
        [
            {"text": "Four Core Water-Quality Indicators Studied", "size": 13, "bold": True, "color": NAVY, "space_after": 6},
            {
                "runs": [
                    ("1. Dissolved Oxygen (DO, mg/L): ", True, NAVY, 10.5, "Calibri", False),
                    ("Oxygen available for fish and aerobic life. CPCB Class C minimum threshold is >= 4.0 mg/L; < 2.0 mg/L indicates severe hypoxia.", False, SLATE_TEXT, 10.0, "Calibri", False),
                ],
                "space_after": 8,
            },
            {
                "runs": [
                    ("2. Biochemical Oxygen Demand (BOD, mg/L): ", True, AMBER, 10.5, "Calibri", False),
                    ("Oxygen consumed by microbes decomposing organic waste over 5 days at 20°C. CPCB Class C limit is <= 3.0 mg/L. High BOD signals sewage or industrial effluent.", False, SLATE_TEXT, 10.0, "Calibri", False),
                ],
                "space_after": 8,
            },
            {
                "runs": [
                    ("3. Potential of Hydrogen (pH, 0–14 scale): ", True, TEAL, 10.5, "Calibri", False),
                    ("Measures acidity or alkalinity. Acceptable CPCB surface-water range is 6.5 to 8.5.", False, SLATE_TEXT, 10.0, "Calibri", False),
                ],
                "space_after": 8,
            },
            {
                "runs": [
                    ("4. Electrical Conductivity (EC, uS/cm): ", True, NAVY, 10.5, "Calibri", False),
                    ("Measures dissolved ionic salts and mineral concentration; elevated by agricultural runoff, industrial discharge, or estuarine salinity intrusion.", False, SLATE_TEXT, 10.0, "Calibri", False),
                ],
                "space_after": 4,
            },
        ],
        fill=CARD_BG,
        border=CARD_BORDER,
        rounded=True,
    )
    slides.append(s2)
    notes_dict[2] = [
        "[Slide 2 — Introduction and Motivation]",
        "What to say: Surface-water quality measures the suitability of rivers and lakes for aquatic ecosystems and human use. We focus on four primary CPCB indicators: Dissolved Oxygen (DO), Biochemical Oxygen Demand (BOD), pH, and Electrical Conductivity (EC).",
        "Why these four parameters: DO and BOD capture the oxygen balance of a river (healthy water needs DO >= 4 mg/L and BOD <= 3 mg/L), pH measures acid-base balance (6.5–8.5), and EC measures dissolved ionic load.",
        "Why geographic and seasonal dimensions: Water quality is not uniform across India—it varies across states and shifts between low-flow summer months and high-flow monsoon months.",
        "Likely Lecturer Question: Why are DO and BOD inversely related? -> Because aerobic bacteria consume dissolved oxygen in the water column while breaking down organic sewage (measured by BOD).",
    ]

    # =========================================================================
    # SLIDE 3: PROBLEM STATEMENT AND OBJECTIVES
    # =========================================================================
    s3 = SlideBuilder(3)
    s3.add_header_and_footer(
        "Section 2  |  Research Scope",
        "Problem Statement and Project Objectives",
        "Defining what the data science workflow investigates without assuming findings in advance",
    )

    s3.add_textbox(
        0.35,
        0.95,
        9.3,
        1.05,
        [
            {"text": "Problem Statement", "size": 12.5, "bold": True, "color": NAVY, "space_after": 3},
            {
                "text": "Official multi-state water-quality archives are distributed across hundreds of separate category CSV files containing inconsistent headers, character-encoded numbers, missing observations, and extreme values. This project investigates how to systematically clean and harmonize 315 CPCB/NWDP CSV files and 1 historical Kaggle archive in R to quantify geographic variations, seasonal monsoon patterns, multi-parameter correlations, and linear predictability of Dissolved Oxygen from BOD.",
                "size": 9.8,
                "color": SLATE_TEXT,
            },
        ],
        fill=LIGHT_AMBER_BG,
        border=AMBER,
        rounded=True,
    )

    s3.add_textbox(
        0.35,
        2.12,
        4.55,
        3.05,
        [
            {"text": "Data Engineering & Descriptive Objectives (1–4)", "size": 11.5, "bold": True, "color": NAVY, "space_after": 5},
            {"text": "1. Schema & File Audit: Inspect 315 CPCB CSV files (Physical, Chemical, Biological) and 1 Kaggle CSV to verify dimensions, column schemas, and data-quality issues.", "size": 9.5, "color": SLATE_TEXT, "bullet": True, "space_after": 4},
            {"text": "2. Reproducible Data Cleaning: Standardize column names, parse numeric/date types, remove exact duplicates, filter physically impossible values (e.g., pH > 14, DO > 25 mg/L), and harmonize state names.", "size": 9.5, "color": SLATE_TEXT, "bullet": True, "space_after": 4},
            {"text": "3. Distributional Analysis: Quantify univariate distributions of DO, BOD, pH, and EC using both parametric (Mean, SD) and non-parametric (Median, IQR) metrics.", "size": 9.5, "color": SLATE_TEXT, "bullet": True, "space_after": 4},
            {"text": "4. Geographic Assessment: Map station coverage across 36 States/UTs and test whether BOD differs significantly across major monitored states.", "size": 9.5, "color": SLATE_TEXT, "bullet": True},
        ],
        fill=CARD_BG,
        border=CARD_BORDER,
        rounded=True,
    )

    s3.add_textbox(
        5.1,
        2.12,
        4.55,
        3.05,
        [
            {"text": "Inferential, Historical & ML Objectives (5–9)", "size": 11.5, "bold": True, "color": TEAL, "space_after": 5},
            {"text": "5. Seasonal Comparison: Classify valid timestamps into Indian hydrological seasons and test differences between Pre-Monsoon and Monsoon water quality.", "size": 9.5, "color": SLATE_TEXT, "bullet": True, "space_after": 4},
            {"text": "6. Multi-Parameter Relationships: Examine non-linear decay and Spearman rank correlations among DO, BOD, pH, and Electrical Conductivity.", "size": 9.5, "color": SLATE_TEXT, "bullet": True, "space_after": 4},
            {"text": "7. Historical Comparison: Compare aggregated state-level medians between the Kaggle baseline (2003–2014) and CPCB dataset (2018–2024) without invalid row-level merging.", "size": 9.5, "color": SLATE_TEXT, "bullet": True, "space_after": 4},
            {"text": "8. Basic Machine Learning: Train and evaluate a Simple Linear Regression model (DO ~ BOD) on an 80:20 train–test split using RMSE, MAE, and R², including sensitivity checks.", "size": 9.5, "color": SLATE_TEXT, "bullet": True},
        ],
        fill=CARD_BG,
        border=CARD_BORDER,
        rounded=True,
    )
    slides.append(s3)
    notes_dict[3] = [
        "[Slide 3 — Problem Statement and Objectives]",
        "What to say: Raw government monitoring files cannot be analyzed directly without careful auditing and preprocessing. We organized the project around 9 concrete objectives spanning data inspection, cleaning, exploratory analysis, non-parametric hypothesis testing, historical state-level comparison, and beginner-level linear regression.",
        "Why state objectives as questions to investigate: In data science, we formulate clear analytical objectives first and let the empirical data determine the findings rather than assuming conclusions in advance.",
        "Likely Lecturer Question: Why did you include both parametric (Mean/SD) and non-parametric (Median/IQR) statistics in Objective 3? -> Because environmental variables like BOD and EC are heavily right-skewed, so the mean is pulled upward by extreme values whereas the median and IQR represent typical water conditions.",
    ]

    # =========================================================================
    # SLIDE 4: EXPECTED ANALYSIS VERSUS ACTUAL FINDINGS
    # =========================================================================
    s4 = SlideBuilder(4)
    s4.add_header_and_footer(
        "Section 2  |  Empirical Audit",
        "Expected Analysis vs. Actual Empirical Findings",
        "Comparing what each research question investigated against what the executed R code actually revealed",
    )

    s4.add_table(
        0.35,
        0.92,
        9.3,
        4.28,
        headers=[
            "Research Question / Planned Investigation",
            "Analysis Performed in R",
            "Actual Empirical Finding",
            "Interpretation & Limitation",
        ],
        rows=[
            [
                "1. File Structure: Do all 315 CPCB CSVs share identical schemas?",
                "Automated schema profiling in 01_data_inspection.R across 3 folders.",
                "311,379 raw rows; 1 Biological CSV misclassified in Chemical folder; OCR header typos found.",
                "Category folders have distinct schemas; consolidated by (station, sample_datetime) into 109,422 rows.",
            ],
            [
                "2. Data Validity: Are raw numeric measurements within physical bounds?",
                "Range checks on pH [0, 14], DO [0, 25 mg/L], and state name regex matching.",
                "Found 89 Kaggle rows & 4 CPCB rows with pH > 14 (up to 748); 11 CPCB DO > 25 mg/L; 98 valid DO = 0.",
                "Replaced impossible values with NA instead of deleting rows, preserving valid co-measured parameters.",
            ],
            [
                "3. Geographic Variation: Does organic pollution (BOD) vary across states?",
                "State boxplots + Kruskal-Wallis test across top 6 monitored states (n = 51,694).",
                "Highly significant difference: Chi-sq = 11,725.65, df = 5, p < 2.2e-16.",
                "Industrial/urbanized states show wider BOD tails; unequal station counts across states limit rankings.",
            ],
            [
                "4. Seasonal Effect: How do Pre-Monsoon and Monsoon DO & BOD compare?",
                "Timestamp parsing + Wilcoxon Rank-Sum test on DO (Pre-Monsoon vs. Monsoon).",
                "Significant difference (W = 3.61e8, p = 5.48e-24); median BOD drops from 2.40 to 2.10 mg/L in Monsoon.",
                "Monsoon rainfall dilutes organic BOD load, while higher summer temperatures slightly shift DO medians.",
            ],
            [
                "5. Historical Comparison: Can Kaggle (2003–14) & CPCB (2018–24) be merged?",
                "Schema & coverage audit + state-level median comparison across 19 matched states.",
                "Row-level merge is invalid (annual means vs. event samples, 4-yr gap); state DO medians stable (~6.3–6.8).",
                "Network expanded >10x (321 to 4,017 stations), so differences reflect station mix, not pure time trends.",
            ],
            [
                "6. Linear Regression: How well does BOD alone linearly predict DO?",
                "lm(DO ~ BOD) on 80:20 split (set.seed(513)) + full-data & station-split checks.",
                "Primary (BOD<=50): DO = 7.0745 - 0.1784*BOD; Test R² = 0.2370, RMSE = 1.6508, MAE = 1.1750 mg/L.",
                "Statistically significant negative association, but modest accuracy (~23.7% variance); not causal.",
            ],
        ],
        col_Ratios=[0.22, 0.22, 0.28, 0.28],
        font_size=8.3,
    )
    slides.append(s4)
    notes_dict[4] = [
        "[Slide 4 — Expected Analysis vs. Actual Findings]",
        "What to say: This table summarizes what each research question was designed to investigate versus what we actually found in the data, along with the honest methodological limitations.",
        "Key highlights to emphasize:",
        "1. During file inspection, we discovered 1 biological CSV file misplaced inside the chemical folder, and 89 rows in Kaggle where pH was > 14 due to column shifts in the raw archive.",
        "2. In seasonal analysis, monsoon dilution lowers median BOD from 2.40 mg/L (Pre-Monsoon) to 2.10 mg/L (Monsoon), while median DO shifts slightly from 6.80 to 6.70 mg/L (p = 5.48e-24).",
        "3. In linear regression, BOD has a statistically significant negative association with DO (slope = -0.1784), explaining 23.7% of test-set DO variance (Test RMSE = 1.6508 mg/L), which is a modest single-predictor fit.",
    ]

    # =========================================================================
    # SLIDE 5: DATASET DESCRIPTION
    # =========================================================================
    s5 = SlideBuilder(5)
    s5.add_header_and_footer(
        "Section 3  |  Data Sources & Inventory",
        "Dataset Description and Actual Verified Dimensions",
        "Primary official CPCB/NWDP multi-file archive and supplementary Kaggle historical baseline",
    )

    s5.add_table(
        0.35,
        0.95,
        9.3,
        2.35,
        headers=[
            "Dataset Component",
            "Source & Custodian",
            "Files",
            "Raw Rows",
            "Cleaned Rows x Cols",
            "Temporal Coverage & Role",
        ],
        rows=[
            [
                "CPCB Physical Category",
                "NWDP / CPCB, Govt. of India",
                "104 CSVs",
                "94,159",
                "Consolidated into Master",
                "2018–2024 | Physical indicators (pH, EC, Turbidity)",
            ],
            [
                "CPCB Chemical Category",
                "NWDP / CPCB, Govt. of India",
                "106 CSVs*",
                "109,683",
                "Consolidated into Master",
                "2018–2024 | Chemical indicators (DO, Ammonia, Nitrate)",
            ],
            [
                "CPCB Biological Category",
                "NWDP / CPCB, Govt. of India",
                "105 CSVs",
                "107,537",
                "Consolidated into Master",
                "2018–2024 | Biological indicators (BOD, Fecal/Total Coliform)",
            ],
            [
                "CPCB Harmonized Master",
                "Processed Primary Dataset",
                "315 CSVs",
                "311,379",
                "109,422 rows x 22 cols",
                "Primary Dataset | 4,017 geocoded stations across 36 States/UTs",
            ],
            [
                "Kaggle Historical Archive",
                "Kaggle (water_dataX.csv)",
                "1 CSV",
                "1,991",
                "1,990 rows x 12 cols",
                "Supplementary | 2003–2014 annual means across 20 matched states",
            ],
        ],
        col_Ratios=[0.20, 0.20, 0.09, 0.11, 0.16, 0.24],
        font_size=8.6,
    )

    s5.add_textbox(
        0.35,
        3.42,
        4.55,
        1.78,
        [
            {"text": "Key Variables & Data Types (CPCB Master: 22 Cols)", "size": 11, "bold": True, "color": NAVY, "space_after": 4},
            {"text": "Categorical / Identifier Fields: station (character, 4,017 stations), state (character, 36 States/UTs), district (character), season (Pre-Monsoon, Monsoon, Post-Monsoon, Winter).", "size": 9.2, "color": SLATE_TEXT, "bullet": True, "space_after": 3},
            {"text": "Temporal & Spatial Fields: sample_datetime (POSIXct), year, month, latitude & longitude (numeric WGS84 coordinates, 0% missing).", "size": 9.2, "color": SLATE_TEXT, "bullet": True, "space_after": 3},
            {"text": "Water Quality Numerics: dissolved_oxygen_mg_l, bod_mg_l, ph, electrical_conductivity_us_cm, turbidity_ntu, nitrate_n_mg_l, fecal_coliform_mpn_100ml.", "size": 9.2, "color": SLATE_TEXT, "bullet": True},
        ],
        fill=CARD_BG,
        border=CARD_BORDER,
        rounded=True,
    )

    s5.add_textbox(
        5.1,
        3.42,
        4.55,
        1.78,
        [
            {"text": "Why the Two Datasets Are Not Merged Row-by-Row", "size": 11, "bold": True, "color": AMBER, "space_after": 4},
            {"text": "1. Different Granularity: CPCB records timestamped monitoring events, whereas Kaggle records annual station summary averages.", "size": 9.2, "color": SLATE_TEXT, "bullet": True, "space_after": 3},
            {"text": "2. Temporal Gap: Kaggle ends in 2014 and CPCB begins in 2018 (4-year discontinuity).", "size": 9.2, "color": SLATE_TEXT, "bullet": True, "space_after": 3},
            {"text": "3. Spatial Schema Difference: CPCB has exact GPS coordinates for 4,017 stations; Kaggle has no coordinates and covers 321 stations. Thus, they are compared only via aggregated state medians.", "size": 9.2, "color": SLATE_TEXT, "bullet": True},
        ],
        fill=LIGHT_AMBER_BG,
        border=AMBER,
        rounded=True,
    )
    slides.append(s5)
    notes_dict[5] = [
        "[Slide 5 — Dataset Description]",
        "What to say: Our project uses two verified local datasets. The primary dataset consists of 315 official CPCB/NWDP CSV files totaling 311,379 raw rows across Physical (104 files), Chemical (106 files), and Biological (105 files) categories. Because the three category folders record different parameters for the same station and timestamp, consolidating them by (station, sample_datetime) produces 109,422 unique station-date observations across 22 columns.",
        "Supplementary dataset: The Kaggle dataset (water_dataX.csv) has 1,991 raw rows (1,990 after removing 1 exact duplicate) and 12 columns covering 2003–2014.",
        "Likely Lecturer Question: Why did 311,379 raw CPCB rows become 109,422 rows in the master table? -> Because Physical, Chemical, and Biological measurements for the same station visit were stored in three separate category folders. Merging on station + timestamp aligns pH/EC, DO, and BOD into a single row per sampling event.",
    ]

    # =========================================================================
    # SLIDE 6: PROJECT WORKFLOW
    # =========================================================================
    s6 = SlideBuilder(6)
    s6.add_header_and_footer(
        "Section 3  |  Methodology Pipeline",
        "End-to-End Reproducible Data Science Workflow",
        "Seven sequential stages implemented across modular R scripts and R Markdown",
    )

    stages = [
        ("1. Data Loading", "Read 315 CPCB CSVs & Kaggle CSV (Latin-1)", NAVY),
        ("2. Inspection", "Audit schemas, types, NAs & misclassified files", TEAL),
        ("3. Cleaning", "Fix headers, types, pH/DO bounds & states", NAVY),
        ("4. EDA & Tests", "Distributions, maps, Kruskal & Wilcoxon tests", TEAL),
        ("5. Linear Model", "80:20 split (seed 513), fit lm(DO ~ BOD)", AMBER),
        ("6. Evaluation", "Test RMSE, MAE, R² & 2 sensitivity checks", NAVY),
        ("7. Conclusion", "Synthesize findings, limits & knit HTML/PDF", TEAL),
    ]
    bx = 0.35
    bw = 1.22
    gap = 0.12
    for idx, (st_title, st_desc, st_col) in enumerate(stages):
        curr_x = bx + idx * (bw + gap)
        s6.add_textbox(
            curr_x,
            1.02,
            bw,
            1.25,
            [
                {"text": st_title, "size": 10.0, "bold": True, "color": WHITE, "align": "ctr", "space_after": 4},
                {"text": st_desc, "size": 8.3, "color": "F1F5F9", "align": "ctr"},
            ],
            fill=st_col,
            border=None,
            rounded=True,
            pad=(0.05, 0.08, 0.05, 0.05),
        )
        if idx < len(stages) - 1:
            s6.add_textbox(
                curr_x + bw,
                1.38,
                gap,
                0.4,
                [{"text": "→", "size": 13, "bold": True, "color": NAVY, "align": "ctr"}],
                pad=(0, 0, 0, 0),
            )

    # 3 Modular Script Cards below
    s6.add_textbox(
        0.35,
        2.50,
        3.0,
        2.65,
        [
            {"text": "Stage 1–2: R/01_data_inspection.R", "size": 11, "bold": True, "color": NAVY, "space_after": 5},
            {"text": "What it contributes: Scans all raw directories without modifying raw files.", "size": 9.3, "color": SLATE_TEXT, "bullet": True, "space_after": 4},
            {"text": "Key actions: Verifies row/column counts, detects the misclassified Tamil Nadu 2018 biological file, and profiles missingness.", "size": 9.3, "color": SLATE_TEXT, "bullet": True, "space_after": 4},
            {"text": "Outputs: dataset_summary.csv & detailed_empirical_inspection.json.", "size": 9.3, "color": TEAL, "bold": True, "bullet": True},
        ],
        fill=CARD_BG,
        border=CARD_BORDER,
        rounded=True,
    )

    s6.add_textbox(
        3.50,
        2.50,
        3.0,
        2.65,
        [
            {"text": "Stage 3: R/02_data_cleaning.R", "size": 11, "bold": True, "color": TEAL, "space_after": 5},
            {"text": "What it contributes: Transforms noisy raw files into analysis-ready datasets.", "size": 9.3, "color": SLATE_TEXT, "bullet": True, "space_after": 4},
            {"text": "Key actions: Repairs OCR header typos, converts character strings to numeric, filters impossible pH/DO, standardizes states & seasons.", "size": 9.3, "color": SLATE_TEXT, "bullet": True, "space_after": 4},
            {"text": "Outputs: nwdp_cpcb_master_water_quality.csv (109,422 rows) & data_cleaning_audit_summary.csv.", "size": 9.3, "color": NAVY, "bold": True, "bullet": True},
        ],
        fill=CARD_BG,
        border=CARD_BORDER,
        rounded=True,
    )

    s6.add_textbox(
        6.65,
        2.50,
        3.0,
        2.65,
        [
            {"text": "Stage 4–7: R/03_exploratory_analysis.R & .Rmd", "size": 11, "bold": True, "color": AMBER, "space_after": 5},
            {"text": "What it contributes: Executes statistical tests, generates 12 300-DPI figures, and trains the linear regression model.", "size": 9.3, "color": SLATE_TEXT, "bullet": True, "space_after": 4},
            {"text": "Key actions: Runs Wilcoxon & Kruskal-Wallis tests, fits lm(DO ~ BOD), runs sensitivity checks, and knits reports.", "size": 9.3, "color": SLATE_TEXT, "bullet": True, "space_after": 4},
            {"text": "Outputs: Figures 01–12, HTML report, and PDF report.", "size": 9.3, "color": NAVY, "bold": True, "bullet": True},
        ],
        fill=CARD_BG,
        border=CARD_BORDER,
        rounded=True,
    )
    slides.append(s6)
    notes_dict[6] = [
        "[Slide 6 — Project Workflow]",
        "What to say: Our workflow follows a modular, reproducible 7-stage pipeline: Data Loading -> Inspection -> Cleaning & Preprocessing -> Exploratory Data Analysis -> Basic Linear Regression -> Evaluation & Sensitivity Checks -> Conclusion.",
        "Why modular scripts: Separating inspection (01_data_inspection.R), cleaning (02_data_cleaning.R), and analysis/modelling (03_exploratory_analysis.R and the .Rmd report) ensures that raw data are never overwritten and every number in the final HTML and PDF reports can be reproduced from scratch.",
    ]

    # =========================================================================
    # SLIDE 7: DATA INSPECTION AND QUALITY PROBLEMS
    # =========================================================================
    s7 = SlideBuilder(7)
    s7.add_header_and_footer(
        "Section 4  |  Data Auditing",
        "Data Inspection and Identified Quality Problems",
        "Empirical anomalies uncovered during automated inspection of the 315 CPCB CSVs and Kaggle dataset",
    )

    s7.add_table(
        0.35,
        0.95,
        5.05,
        4.20,
        headers=["Anomaly Category", "Dataset", "Verified Count / Evidence", "Impact if Uncorrected"],
        rows=[
            [
                "File Misclassification",
                "CPCB Chemical",
                "1 CSV (Tamil Nadu 2018 Biological schema inside Chemical folder)",
                "Blind rbind() fails or corrupts chemical columns with BOD/Coliform.",
            ],
            [
                "OCR Header Typos",
                "CPCB Biological",
                "e.g. 'Biochemical Oxygen Deman (mg/L)' & 'Fecal Coliform (MPN/100ml'",
                "Columns fail to align across states during multi-file ingestion.",
            ],
            [
                "Character Encoding & Strings",
                "Kaggle & CPCB",
                "Latin-1 degree symbols; 'NAN', '-', '' stored in numeric columns",
                "R imports numeric water-quality columns as character vectors.",
            ],
            [
                "Exact Duplicate Rows",
                "Kaggle",
                "1 exact duplicate row (1,991 raw -> 1,990 unique rows); 0 in CPCB",
                "Double-counts identical station-year summary record.",
            ],
            [
                "Impossible pH (> 14)",
                "Kaggle & CPCB",
                "89 rows in Kaggle (pH 69–748 from column shift); 4 rows in CPCB",
                "Distorts Kaggle mean pH to 27.68 (SD = 104.53) instead of 7.23!",
            ],
            [
                "Impossible DO (> 25 mg/L)",
                "CPCB Master",
                "11 rows with DO between 26.0 and 95.0 mg/L (98 rows with DO = 0 kept)",
                "Exceeds physical atmospheric oxygen saturation; skews DO summary.",
            ],
            [
                "Inconsistent State Names",
                "Kaggle & CPCB",
                "1,780 CPCB rows ('odisha'/'Orissa'); Kaggle states embedded in text",
                "Splits identical states into separate groups in geographic plots.",
            ],
        ],
        col_Ratios=[0.23, 0.16, 0.31, 0.30],
        font_size=8.0,
    )

    s7.add_image_fit(
        "01_missingness_overview.png",
        5.55,
        0.98,
        4.10,
        4.15,
        caption="Figure 1: Parameter-wise missingness (%) in CPCB Master (109,422 rows)",
    )
    slides.append(s7)
    notes_dict[7] = [
        "[Slide 7 — Data Inspection and Quality Problems]",
        "What to say: Before cleaning, we audited all files and documented seven concrete data-quality problems. On the left table, you can see the exact counts; on the right, Figure 1 shows parameter-wise missingness in the CPCB Master table.",
        "Critical example to highlight: In the Kaggle dataset, 89 rows had pH values between 69 and 748 because conductivity values were shifted into the pH column in the raw source. Before cleaning, those 89 rows inflated the mean pH to an impossible 27.68! Similarly, in CPCB, pH (1.9% missing), DO (11.4% missing), and BOD (23.0% missing) have strong coverage, whereas Electrical Conductivity is 56.0% missing and trace heavy metals exceed 60% missing.",
        "Likely Lecturer Question: Why did you keep DO = 0 mg/L (98 rows) while removing DO > 25 mg/L (11 rows)? -> Because DO = 0 mg/L is physically real in anoxic, heavily polluted sewage stretches, whereas DO > 25 mg/L is physically impossible under open-air surface water conditions.",
    ]

    # =========================================================================
    # SLIDE 8: DATA CLEANING AND PREPROCESSING
    # =========================================================================
    s8 = SlideBuilder(8)
    s8.add_header_and_footer(
        "Section 4  |  Preprocessing Pipeline",
        "Data Cleaning and Preprocessing in R",
        "What was done, why it was needed, how it was coded in R, and verified before/after impact",
    )

    s8.add_textbox(
        0.35,
        0.95,
        4.85,
        2.15,
        [
            {"text": "What, Why, and How of Key Cleaning Steps (02_data_cleaning.R)", "size": 11, "bold": True, "color": NAVY, "space_after": 4},
            {"text": "1. Schema-Based Routing & Consolidation: Routed all 315 CSVs by actual column headers (catching the misclassified file) and consolidated by (station, sample_datetime) into 109,422 rows.", "size": 9.0, "color": SLATE_TEXT, "bullet": True, "space_after": 3},
            {"text": "2. Safe Type Conversion: Trimmed whitespace, converted 'NAN'/'-'/'' to NA, and applied as.numeric() and as.POSIXct().", "size": 9.0, "color": SLATE_TEXT, "bullet": True, "space_after": 3},
            {"text": "3. Physical Range Validation: Replaced impossible pH (< 0 or > 14: 89 Kaggle, 4 CPCB) and DO (< 0 or > 25 mg/L: 11 CPCB) with NA rather than deleting whole rows.", "size": 9.0, "color": SLATE_TEXT, "bullet": True, "space_after": 3},
            {"text": "4. State & Season Standardization: Mapped 1,780 CPCB state variants to 36 canonical States/UTs; recovered 1,983/1,990 Kaggle states via regex + station_code lookup; derived 4 seasons.", "size": 9.0, "color": SLATE_TEXT, "bullet": True},
        ],
        fill=CARD_BG,
        border=CARD_BORDER,
        rounded=True,
    )

    # Genuine code snippet box
    s8.add_textbox(
        0.35,
        3.20,
        4.85,
        1.98,
        [
            {"text": "Genuine R Code Excerpt (02_data_cleaning.R / .Rmd):", "size": 9.5, "bold": True, "color": TEAL, "space_after": 3},
            {
                "text": "# 1. Replace non-standard missing strings & convert to numeric\nx_clean <- trimws(as.character(x))\nx_clean[x_clean %in% c(\"\", \"NA\", \"NAN\", \"NaN\", \"-\", \"null\")] <- NA\nval_num <- suppressWarnings(as.numeric(x_clean))\n\n# 2. Replace physically impossible pH & DO with NA (keep valid row)\ndf$ph <- ifelse(df$ph < 0 | df$ph > 14, NA_real_, df$ph)\ndf$dissolved_oxygen_mg_l <- ifelse(\n  df$dissolved_oxygen_mg_l < 0 | df$dissolved_oxygen_mg_l > 25,\n  NA_real_, df$dissolved_oxygen_mg_l\n)",
                "size": 8.0,
                "font": "Courier New",
                "color": DARK_NAVY,
                "space_after": 0,
            },
        ],
        fill=CODE_BG,
        border=CODE_BORDER,
        rounded=True,
    )

    s8.add_image_fit(
        "09_cleaning_before_after_ph.png",
        5.35,
        0.95,
        4.30,
        4.20,
        caption="Figure 2: Kaggle pH Before Cleaning (Mean=27.68, Max=748) vs. After Cleaning (Mean=7.23, SD=0.65)",
    )
    slides.append(s8)
    notes_dict[8] = [
        "[Slide 8 — Data Cleaning and Preprocessing]",
        "What to say: This slide explains the exact R implementation of our cleaning pipeline and shows the visual proof of its impact.",
        "Code explanation: First, we strip whitespace and convert string placeholders like 'NAN' or '-' into proper R NA values before calling as.numeric(). Second, using ifelse(), we set physically impossible values (such as pH < 0 or > 14, and DO > 25 mg/L) to NA_real_ instead of dropping the entire row. That way, a station visit with a corrupted pH reading still contributes its valid DO and BOD measurements.",
        "Visual proof (Figure 2): The right plot shows Kaggle pH before and after range validation. Removing the 89 corrupted pH > 14 values restores the distribution from an impossible range (up to 748) to a clean bell-shaped distribution centered at Mean = 7.23 (Median = 7.30).",
    ]

    # =========================================================================
    # SLIDE 9: EXPLORATORY DATA ANALYSIS: DISTRIBUTIONS
    # =========================================================================
    s9 = SlideBuilder(9)
    s9.add_header_and_footer(
        "Section 5  |  Exploratory Data Analysis",
        "Univariate Distributions of Core Water-Quality Parameters",
        "Parametric (Mean, SD) and non-parametric (Median, IQR) statistics across 109,422 CPCB records",
    )

    s9.add_table(
        0.35,
        0.95,
        4.75,
        2.35,
        headers=["Parameter (Dataset)", "Valid N", "Mean", "SD", "Median", "IQR", "Min–Max"],
        rows=[
            ["DO (mg/L) [CPCB]", "96,978", "6.54", "1.87", "6.80", "1.90", "0.00–25.0"],
            ["BOD (mg/L) [CPCB]", "84,272", "5.76", "16.26", "2.30", "2.40", "0.00–1315"],
            ["pH [CPCB]", "107,342", "7.53", "0.61", "7.58", "0.70", "2.00–14.0"],
            ["EC (uS/cm) [CPCB]", "48,160", "3,474.5", "171,821", "395.0", "749.0", "1.0–2.54e7"],
            ["DO (mg/L) [Kaggle]", "1,960", "6.39", "1.33", "6.70", "1.30", "0.00–11.4"],
            ["BOD (mg/L) [Kaggle]", "1,948", "6.94", "29.40", "1.90", "2.40", "0.10–534.5"],
        ],
        col_Ratios=[0.27, 0.13, 0.11, 0.13, 0.11, 0.10, 0.15],
        font_size=8.0,
    )

    s9.add_textbox(
        0.35,
        3.42,
        4.75,
        1.75,
        [
            {"text": "What the Distributions Reveal", "size": 11, "bold": True, "color": NAVY, "space_after": 4},
            {"text": "1. DO & pH are Near-Symmetric: CPCB Dissolved Oxygen has Mean = 6.54 mg/L and Median = 6.80 mg/L (90.8% of records meet CPCB Class C >= 4.0 mg/L). pH is tightly centered at Median = 7.58 (IQR = 0.70).", "size": 9.0, "color": SLATE_TEXT, "bullet": True, "space_after": 3},
            {"text": "2. BOD & EC are Extremely Right-Skewed: CPCB BOD has Median = 2.30 mg/L but Mean = 5.76 mg/L (SD = 16.26, Max = 1,315 mg/L) due to severe urban/industrial sewage outfalls.", "size": 9.0, "color": SLATE_TEXT, "bullet": True, "space_after": 3},
            {"text": "3. Why Non-Parametric Tests Are Required: Extreme skewness in BOD and EC violates normality assumptions, justifying Median/IQR and rank-based tests.", "size": 9.0, "color": TEAL, "bold": True, "bullet": True},
        ],
        fill=CARD_BG,
        border=CARD_BORDER,
        rounded=True,
    )

    s9.add_image_fit(
        "11_four_parameter_distributions.png",
        5.25,
        0.95,
        4.40,
        4.20,
        caption="Figure 3: Four-panel distributions of DO, BOD (log10), pH, and EC (log10) with CPCB thresholds",
    )
    slides.append(s9)
    notes_dict[9] = [
        "[Slide 9 — Exploratory Data Analysis: Distributions]",
        "What to say: We examined the distributions of all four primary parameters using both parametric (Mean, SD) and non-parametric (Median, IQR) metrics.",
        "Key insight: Look at BOD in the table: its Median is 2.30 mg/L (within the 3.0 mg/L CPCB Class C threshold), but its Mean is 5.76 mg/L (more than double the median!) with a standard deviation of 16.26 mg/L. Similarly, Electrical Conductivity has a median of 395 uS/cm but a mean of 3,474.5 uS/cm due to estuarine and industrial brines. This severe right-skewness is why we plot BOD and EC on a log10 scale in Figure 3 and use non-parametric rank tests for inference.",
    ]

    # =========================================================================
    # SLIDE 10: GEOGRAPHIC AND SEASONAL ANALYSIS
    # =========================================================================
    s10 = SlideBuilder(10)
    s10.add_header_and_footer(
        "Section 5  |  Spatial & Temporal Variations",
        "Geographic and Seasonal Water-Quality Patterns",
        "State-level heterogeneity across 36 States/UTs and hydrological monsoon dilution effects",
    )

    s10.add_image_fit(
        "04_state_dissolved_oxygen_boxplot.png",
        0.35,
        0.92,
        4.55,
        2.75,
        caption="Figure 7: Dissolved Oxygen across top 15 monitored states",
    )

    s10.add_image_fit(
        "05_seasonal_bod_variation.png",
        5.10,
        0.92,
        4.55,
        2.75,
        caption="Figure 8: Seasonal BOD variation (log10 scale) vs. 3.0 mg/L threshold",
    )

    s10.add_textbox(
        0.35,
        3.75,
        4.55,
        1.45,
        [
            {"text": "Geographic Findings & Kruskal-Wallis Test", "size": 10.5, "bold": True, "color": NAVY, "space_after": 3},
            {"text": "Monitoring volume is uneven: Maharashtra (14,225 rows), Kerala (11,599), and Assam (8,399) lead total observations.", "size": 8.9, "color": SLATE_TEXT, "bullet": True, "space_after": 2},
            {"text": "Kruskal-Wallis Test across top 6 states (n = 51,694): Chi-sq = 11,725.65, df = 5, p < 2.2e-16.", "size": 8.9, "bold": True, "color": TEAL, "bullet": True, "space_after": 2},
            {"text": "States with dense industrial/urban corridors (Maharashtra, Telangana) exhibit wider hypoxic DO tails (< 4.0 mg/L) than high-rainfall states (Kerala, Odisha).", "size": 8.9, "color": SLATE_TEXT, "bullet": True},
        ],
        fill=CARD_BG,
        border=CARD_BORDER,
        rounded=True,
    )

    s10.add_textbox(
        5.10,
        3.75,
        4.55,
        1.45,
        [
            {"text": "Seasonal Findings & Wilcoxon Rank-Sum Test", "size": 10.5, "bold": True, "color": AMBER, "space_after": 3},
            {"text": "Valid timestamps (109,422 rows) classified into Pre-Monsoon (Mar–May), Monsoon (Jun–Sep), Post-Monsoon (Oct–Nov), and Winter (Dec–Feb).", "size": 8.9, "color": SLATE_TEXT, "bullet": True, "space_after": 2},
            {"text": "Wilcoxon Test (Pre-Monsoon vs. Monsoon DO): W = 360,532,006, p = 5.48e-24 (Pre-Monsoon median DO = 6.80 vs. Monsoon = 6.70 mg/L).", "size": 8.9, "bold": True, "color": NAVY, "bullet": True, "space_after": 2},
            {"text": "Monsoon Dilution: High monsoon river discharge reduces median BOD from 2.40 mg/L (Pre-Monsoon) to 2.10 mg/L (Monsoon).", "size": 8.9, "color": SLATE_TEXT, "bullet": True},
        ],
        fill=LIGHT_AMBER_BG,
        border=AMBER,
        rounded=True,
    )
    slides.append(s10)
    notes_dict[10] = [
        "[Slide 10 — Geographic and Seasonal Analysis]",
        "What to say: This slide presents our geographic and seasonal analyses. On the left (Figure 7), state-wise boxplots show that while most states maintain median DO above 6.0 mg/L, industrialized states like Maharashtra and Telangana experience frequent hypoxic drops below the 4.0 mg/L threshold. A Kruskal-Wallis test across the top 6 states confirms highly significant differences in BOD (Chi-squared = 11,725.65, p < 2.2e-16).",
        "On the right (Figure 8), seasonal BOD boxplots show that Southwest Monsoon rainfall (June–September) dilutes organic waste, lowering median BOD from 2.40 mg/L in Pre-Monsoon to 2.10 mg/L in Monsoon. Meanwhile, the Wilcoxon Rank-Sum test on DO between Pre-Monsoon (6.80 mg/L) and Monsoon (6.70 mg/L) is statistically significant (W = 3.61e8, p = 5.48e-24).",
        "Important limitation to mention: Because the Kaggle dataset only contains annual summaries without sampling months, seasonal analysis is performed exclusively on the timestamped CPCB dataset.",
    ]

    # =========================================================================
    # SLIDE 11: RELATIONSHIPS BETWEEN WATER-QUALITY VARIABLES
    # =========================================================================
    s11 = SlideBuilder(11)
    s11.add_header_and_footer(
        "Section 5  |  Multivariate & Historical Analysis",
        "Relationships Between Water-Quality Variables",
        "Non-linear DO–BOD decay, Spearman rank correlations, and historical vs. modern state medians",
    )

    s11.add_image_fit(
        "08_do_vs_bod_relationship.png",
        0.35,
        0.92,
        4.60,
        2.55,
        caption="Figure 9: DO vs. BOD scatter plot with GAM smoothing curve",
    )

    s11.add_image_fit(
        "06_correlation_matrix.png",
        5.15,
        0.92,
        4.50,
        2.55,
        caption="Figure 10: Spearman rank correlation matrix (complete pairwise observations)",
    )

    s11.add_textbox(
        0.35,
        3.58,
        9.30,
        1.62,
        [
            {"text": "Key Multivariate & Decadal Insights (Correlation != Causation)", "size": 11, "bold": True, "color": NAVY, "space_after": 3},
            {"text": "1. Inverse Non-Linear DO vs. BOD Association (Spearman rho = -0.34): In clean waters (BOD <= 3 mg/L), DO remains high (6–9 mg/L). As BOD rises above 10 mg/L, DO decays non-linearly toward 0 mg/L.", "size": 9.1, "color": SLATE_TEXT, "bullet": True, "space_after": 2},
            {"text": "2. Secondary Correlations: Conductivity vs. BOD is positively correlated (rho = 0.25, as sewage carries dissolved ions), and pH vs. DO shows a weak positive correlation (rho = 0.12, linked to daytime algal photosynthesis). These observational correlations measure statistical co-variation, not direct causation.", "size": 9.1, "color": SLATE_TEXT, "bullet": True, "space_after": 2},
            {"text": "3. Historical vs. Modern State Comparison (19 Matched States with >= 15 Kaggle rows): State median DO remained broadly stable between 2003–2014 and 2018–2024 (e.g., Kerala 6.60 -> 6.80 mg/L), though tenfold station expansion (321 to 4,017 stations) prevents longitudinal trend claims.", "size": 9.1, "color": TEAL, "bold": True, "bullet": True},
        ],
        fill=CARD_BG,
        border=CARD_BORDER,
        rounded=True,
    )
    slides.append(s11)
    notes_dict[11] = [
        "[Slide 11 — Relationships Between Water-Quality Variables]",
        "What to say: Next, we examined how water-quality parameters interact. Figure 9 plots Dissolved Oxygen against BOD across the CPCB archive. It shows a clear inverse relationship: when BOD is low (<= 3 mg/L), DO is healthy (6–9 mg/L), but as BOD exceeds 10 mg/L, DO drops steeply toward hypoxia.",
        "Figure 10 displays the Spearman rank correlation matrix: DO and BOD have rho = -0.34, Conductivity and BOD have rho = +0.25, and pH and DO have rho = +0.12.",
        "Correlation vs. Causation: We explicitly note that correlation in observational monitoring data measures statistical association, not causation, because confounding factors like water temperature, flow rate, and industrial mixing also affect oxygen levels.",
    ]

    # =========================================================================
    # SLIDE 12: WHY USE MACHINE LEARNING?
    # =========================================================================
    s12 = SlideBuilder(12)
    s12.add_header_and_footer(
        "Section 6  |  Basic Machine Learning",
        "Why Use Machine Learning? Simple Linear Regression",
        "Formulating a beginner-friendly supervised learning task to predict Dissolved Oxygen from BOD",
    )

    s12.add_textbox(
        0.35,
        0.95,
        4.55,
        2.10,
        [
            {"text": "What Does a Supervised Prediction Model Do?", "size": 12, "bold": True, "color": NAVY, "space_after": 5},
            {"text": "A supervised regression model learns a mathematical equation from historical training data to predict a continuous numerical target variable (Y) from one or more predictor variables (X).", "size": 9.8, "color": SLATE_TEXT, "bullet": True, "space_after": 4},
            {"text": "Why Simple Linear Regression? It is the most interpretable foundational machine learning model: it estimates an explicit intercept and slope using Ordinary Least Squares (OLS) without black-box complexity.", "size": 9.8, "color": SLATE_TEXT, "bullet": True},
        ],
        fill=CARD_BG,
        border=CARD_BORDER,
        rounded=True,
    )

    s12.add_textbox(
        5.10,
        0.95,
        4.55,
        2.10,
        [
            {"text": "Target (Y) and Predictor (X) Selection", "size": 12, "bold": True, "color": TEAL, "space_after": 5},
            {"text": "Target Variable (Response, Y): Dissolved Oxygen (dissolved_oxygen_mg_l, in mg/L) — primary indicator of aquatic ecosystem survival.", "size": 9.8, "color": SLATE_TEXT, "bullet": True, "space_after": 4},
            {"text": "Predictor Variable (Feature, X): Biochemical Oxygen Demand (bod_mg_l, in mg/L) — primary indicator of organic sewage pollution.", "size": 9.8, "color": SLATE_TEXT, "bullet": True, "space_after": 4},
            {"text": "Both variables are numeric, use identical units (mg/L), and have 80,223 complete paired observations in CPCB.", "size": 9.5, "bold": True, "color": NAVY, "bullet": True},
        ],
        fill=LIGHT_TEAL_BG,
        border=TEAL,
        rounded=True,
    )

    s12.add_textbox(
        0.35,
        3.20,
        9.30,
        2.00,
        [
            {"text": "Why Split Data 80:20 into Training and Testing Sets? (Preventing Data Leakage)", "size": 12, "bold": True, "color": AMBER, "space_after": 5},
            {"text": "Training Set (80% of data): Used exclusively by R's lm() function to estimate the intercept (Beta_0) and slope (Beta_1).", "size": 9.8, "color": SLATE_TEXT, "bullet": True, "space_after": 3},
            {"text": "Testing Set (20% hold-out data): Kept completely separate during training and used only with predict() to evaluate how accurately the model generalizes to unseen observations.", "size": 9.8, "color": SLATE_TEXT, "bullet": True, "space_after": 3},
            {"text": "Scope Note: This single-predictor linear regression is an educational demonstration of supervised machine learning in R, not a complete operational river-forecasting system.", "size": 9.6, "italic": True, "color": DARK_NAVY, "bullet": True},
        ],
        fill=LIGHT_AMBER_BG,
        border=AMBER,
        rounded=True,
    )
    slides.append(s12)
    notes_dict[12] = [
        "[Slide 12 — Why Use Machine Learning?]",
        "What to say: In Section 7 of our report, we introduce a beginner-level machine learning model using Simple Linear Regression. A regression model learns a relationship from training data to predict a continuous target variable from a predictor variable.",
        "Why DO from BOD: Measuring 5-day BOD in a laboratory takes 5 days of incubation, whereas understanding how organic load relates to Dissolved Oxygen is central to water quality management. Both variables are numeric and measured in mg/L.",
        "Why an 80:20 train-test split: If we evaluate a model on the same data used to fit it, we risk overfitting. Holding out 20% of the data as a test set lets us measure true out-of-sample prediction error.",
    ]

    # =========================================================================
    # SLIDE 13: LINEAR REGRESSION: MODEL AND CODE
    # =========================================================================
    s13 = SlideBuilder(13)
    s13.add_header_and_footer(
        "Section 6  |  Model Specification & R Implementation",
        "Linear Regression: Mathematical Model and R Code",
        "Fitting the model on the 80% training set and generating predictions on the 20% test set",
    )

    # Equation banner
    s13.add_textbox(
        0.35,
        0.92,
        9.30,
        0.82,
        [
            {
                "text": "Model Form:   DO = Intercept (β₀) + Slope (β₁) × BOD       |       Fitted Primary Equation:   Predicted DO = 7.0745 − 0.1784 × BOD",
                "size": 12.5,
                "bold": True,
                "color": WHITE,
                "align": "ctr",
                "space_after": 2,
            },
            {
                "text": "(Trained on n = 63,893 observations with set.seed(513); both coefficients statistically significant at p < 2e-16)",
                "size": 9.5,
                "color": "DCE6F1",
                "align": "ctr",
            },
        ],
        fill=NAVY,
        border=TEAL,
        rounded=True,
    )

    # Left: Genuine R Code
    s13.add_textbox(
        0.35,
        1.88,
        4.65,
        3.32,
        [
            {"text": "Actual R Code from Project (.Rmd):", "size": 10.5, "bold": True, "color": TEAL, "space_after": 4},
            {
                "text": "# 1. Select valid non-missing pairs (BOD <= 50 mg/L)\nml_data <- df_cpcb_master %>%\n  select(station, sample_datetime,\n         dissolved_oxygen_mg_l, bod_mg_l) %>%\n  filter(!is.na(dissolved_oxygen_mg_l),\n         !is.na(bod_mg_l), bod_mg_l <= 50)\n\n# 2. Reproducible 80:20 Train-Test Split\nset.seed(513)\nn_total   <- nrow(ml_data)\ntrain_idx <- sample(seq_len(n_total),\n                    size = floor(0.80 * n_total))\ntrain_data <- ml_data[train_idx, ]\ntest_data  <- ml_data[-train_idx, ]\n\n# 3. Train linear model on training set ONLY\ndo_lm_model <- lm(\n  dissolved_oxygen_mg_l ~ bod_mg_l,\n  data = train_data\n)\n\n# 4. Predict on unseen 20% test set\ntest_data$predicted_do <- predict(\n  do_lm_model, newdata = test_data\n)",
                "size": 8.0,
                "font": "Courier New",
                "color": DARK_NAVY,
            },
        ],
        fill=CODE_BG,
        border=CODE_BORDER,
        rounded=True,
    )

    # Right: Step-by-step explanation
    s13.add_textbox(
        5.15,
        1.88,
        4.50,
        3.32,
        [
            {"text": "What Each Step in the Code Does", "size": 11.5, "bold": True, "color": NAVY, "space_after": 6},
            {"text": "1. set.seed(513) & sample(): Fixes the random number generator so the exact same 63,893 training rows and 15,974 test rows are selected every time the report is knitted.", "size": 9.3, "color": SLATE_TEXT, "bullet": True, "space_after": 5},
            {"text": "2. Formula dissolved_oxygen_mg_l ~ bod_mg_l: Tells R that Dissolved Oxygen is the response variable (Y) on the left of '~' and BOD is the predictor variable (X) on the right.", "size": 9.3, "color": SLATE_TEXT, "bullet": True, "space_after": 5},
            {"text": "3. lm(..., data = train_data): Computes the Ordinary Least Squares (OLS) line minimizing the sum of squared residuals strictly on the 80% training set.", "size": 9.3, "color": SLATE_TEXT, "bullet": True, "space_after": 5},
            {"text": "4. predict(do_lm_model, newdata = test_data): Applies the learned equation (7.0745 - 0.1784 * BOD) to each row's BOD value in the held-out 20% test set to return predicted DO (mg/L).", "size": 9.3, "color": SLATE_TEXT, "bullet": True},
        ],
        fill=CARD_BG,
        border=CARD_BORDER,
        rounded=True,
    )
    slides.append(s13)
    notes_dict[13] = [
        "[Slide 13 — Linear Regression: Model and Code]",
        "What to say: Here is the exact R code used to train and test our linear regression model. First, we filter for non-missing DO and BOD pairs with BOD <= 50 mg/L. Second, we set set.seed(513) and sample 80% of indices for train_data and keep the remaining 20% in test_data.",
        "How lm() and predict() work: lm(dissolved_oxygen_mg_l ~ bod_mg_l, data = train_data) estimates the intercept (7.0745 mg/L) and slope (-0.1784 mg/L per mg/L of BOD) using only the training set. Then predict(do_lm_model, newdata = test_data) computes the predicted DO values for the 15,974 unseen test rows.",
        "Likely Lecturer Question: Why did you pass newdata = test_data inside predict()? -> Because omitting newdata would return fitted values on the training set instead of evaluating predictions on the held-out test set.",
    ]

    # =========================================================================
    # SLIDE 14: TRAINING, TESTING, AND MODEL EVALUATION
    # =========================================================================
    s14 = SlideBuilder(14)
    s14.add_header_and_footer(
        "Section 6  |  Quantitative Evaluation",
        "Training, Testing, and Model Evaluation Metrics",
        "Verified observation counts, parameter estimates, and test-set accuracy metrics (RMSE, MAE, R²)",
    )

    s14.add_table(
        0.35,
        0.95,
        4.65,
        2.65,
        headers=["Model Quantity / Evaluation Metric", "Verified Value"],
        rows=[
            ["All Valid (DO, BOD) Pairs in Cleaned CPCB", "80,223 observations"],
            ["Retained Pairs (Analytical Cutoff BOD <= 50)", "79,867 (99.56% of valid pairs)"],
            ["Excluded Extreme Pairs (BOD > 50 mg/L)", "356 (0.44%, BOD 51–486 mg/L)"],
            ["Training Set Size (80%, set.seed(513))", "63,893 observations"],
            ["Testing Set Size (20%, held-out)", "15,974 observations"],
            ["Intercept (β₀) [Baseline DO at BOD = 0]", "7.0745 mg/L (p < 2e-16)"],
            ["Slope (β₁) [DO change per +1 mg/L BOD]", "-0.1784 mg/L (t = -145.9)"],
            ["Training Set R-squared (R²)", "0.2499 (24.99% variance)"],
            ["Test Set R-squared (R²)", "0.2370 (23.70% variance)"],
            ["Test Set RMSE (Root Mean Squared Error)", "1.6508 mg/L"],
            ["Test Set MAE (Mean Absolute Error)", "1.1750 mg/L"],
        ],
        col_Ratios=[0.60, 0.40],
        font_size=8.4,
    )

    s14.add_textbox(
        5.15,
        0.95,
        4.50,
        2.65,
        [
            {"text": "Understanding the Evaluation Metrics Simply", "size": 11.5, "bold": True, "color": NAVY, "space_after": 5},
            {
                "runs": [
                    ("1. RMSE (1.6508 mg/L): ", True, AMBER, 9.8, "Calibri", False),
                    ("Root Mean Squared Error = sqrt(mean((actual - predicted)^2)). It measures the typical prediction error in mg/L, penalizing large errors more heavily.", False, SLATE_TEXT, 9.3, "Calibri", False),
                ],
                "space_after": 6,
            },
            {
                "runs": [
                    ("2. MAE (1.1750 mg/L): ", True, TEAL, 9.8, "Calibri", False),
                    ("Mean Absolute Error = mean(abs(actual - predicted)). On average, our linear prediction differs from actual test-set DO by 1.18 mg/L.", False, SLATE_TEXT, 9.3, "Calibri", False),
                ],
                "space_after": 6,
            },
            {
                "runs": [
                    ("3. Test R-squared (0.2370): ", True, NAVY, 9.8, "Calibri", False),
                    ("Proportion of variance in test-set DO explained by BOD (23.70%). Because Test R² (0.2370) is very close to Train R² (0.2499), the model does not overfit.", False, SLATE_TEXT, 9.3, "Calibri", False),
                ],
            },
        ],
        fill=CARD_BG,
        border=CARD_BORDER,
        rounded=True,
    )

    s14.add_textbox(
        0.35,
        3.72,
        9.30,
        1.48,
        [
            {"text": "What the Slope (-0.1784) and Metrics Mean in Practice", "size": 11, "bold": True, "color": TEAL, "space_after": 4},
            {"text": "Physical Meaning of Slope: Each 1 mg/L increase in BOD is associated with an average decrease of 0.1784 mg/L in Dissolved Oxygen. When BOD reaches ~17.2 mg/L, predicted DO falls below the CPCB Class C threshold of 4.0 mg/L.", "size": 9.3, "color": SLATE_TEXT, "bullet": True, "space_after": 3},
            {"text": "Honest Assessment of Accuracy: A Test R² of 0.2370 and RMSE of 1.6508 mg/L represent modest predictive accuracy. BOD alone captures ~23.7% of DO variation, while the remaining ~76.3% depends on water temperature, flow turbulence/re-aeration, salinity, and photosynthesis.", "size": 9.3, "color": SLATE_TEXT, "bullet": True},
        ],
        fill=LIGHT_TEAL_BG,
        border=TEAL,
        rounded=True,
    )
    slides.append(s14)
    notes_dict[14] = [
        "[Slide 14 — Training, Testing, and Model Evaluation]",
        "What to say: This slide summarizes all verified numbers from our model evaluation. Out of 80,223 complete (DO, BOD) pairs, applying our analytical cutoff of BOD <= 50 mg/L retains 79,867 pairs (99.56%), split into 63,893 training rows and 15,974 testing rows.",
        "How to explain the metrics: On the unseen test set, the model achieves Test R² = 0.2370 (explaining 23.7% of DO variance), Test RMSE = 1.6508 mg/L, and Test MAE = 1.1750 mg/L. Notice that Train R² (0.2499) and Test R² (0.2370) match closely, confirming zero overfitting. However, we describe this accuracy as modest rather than high because a single variable (BOD) cannot capture physical factors like water temperature or river turbulence.",
    ]

    # =========================================================================
    # SLIDE 15: ACTUAL VERSUS PREDICTED VALUES
    # =========================================================================
    s15 = SlideBuilder(15)
    s15.add_header_and_footer(
        "Section 6  |  Visual Model Diagnostics",
        "Test Set Evaluation: Actual vs. Predicted Dissolved Oxygen",
        "Visualizing predictions across the 15,974 held-out test observations against the 1:1 reference line",
    )

    s15.add_image_fit(
        "12_linear_regression_actual_vs_predicted.png",
        0.35,
        0.95,
        5.35,
        4.20,
        caption="Figure 12: Actual vs. Predicted DO on the 20% Test Set (N = 15,974, RMSE = 1.65 mg/L, R² = 0.24)",
    )

    s15.add_textbox(
        5.85,
        0.95,
        3.80,
        4.20,
        [
            {"text": "How to Read This Diagnostic Plot", "size": 11.5, "bold": True, "color": NAVY, "space_after": 6},
            {"text": "1. The 1:1 Reference Line (Dashed Orange): Represents perfect prediction (Predicted DO = Actual DO). Points lying close to this diagonal line are accurately predicted by the model.", "size": 9.3, "color": SLATE_TEXT, "bullet": True, "space_after": 6},
            {"text": "2. Dense Cluster Around 6.0–7.1 mg/L: Most Indian surface waters have low BOD (1–3 mg/L) and actual DO between 6 and 8 mg/L, where the points cluster tightly around the 1:1 line.", "size": 9.3, "color": SLATE_TEXT, "bullet": True, "space_after": 6},
            {"text": "3. Why Predictions Cap at 7.07 mg/L (Horizontal Upper Ceiling): Because BOD >= 0 and the slope (-0.1784) is negative, the equation 7.0745 - 0.1784 * BOD can never predict a value higher than its intercept (7.0745 mg/L). Actual DO values between 8 and 15 mg/L (caused by cold water or algal photosynthesis) lie to the right of the line.", "size": 9.3, "color": SLATE_TEXT, "bullet": True, "space_after": 6},
            {"text": "4. Scatter in Polluted Waters (DO < 4 mg/L): While higher BOD correctly pulls predicted DO downward along the diagonal, vertical spread reflects unmodeled local re-aeration.", "size": 9.3, "color": SLATE_TEXT, "bullet": True},
        ],
        fill=CARD_BG,
        border=CARD_BORDER,
        rounded=True,
    )
    slides.append(s15)
    notes_dict[15] = [
        "[Slide 15 — Actual vs. Predicted Values]",
        "What to say: Figure 12 compares Actual Dissolved Oxygen on the horizontal axis against Predicted Dissolved Oxygen on the vertical axis for all 15,974 test-set observations.",
        "Key features to point out to the lecturer:",
        "1. The dashed orange line is the 1:1 reference line where Predicted DO equals Actual DO.",
        "2. Notice the flat horizontal ceiling at Y = 7.07 mg/L: because BOD cannot be negative and our slope is negative (-0.1784), the highest possible prediction from 7.0745 - 0.1784 * BOD occurs when BOD = 0, giving 7.0745 mg/L. That visually explains why a single linear predictor cannot predict supersaturated DO values above 7.1 mg/L.",
    ]

    # =========================================================================
    # SLIDE 16: SENSITIVITY CHECKS AND LIMITATIONS
    # =========================================================================
    s16 = SlideBuilder(16)
    s16.add_header_and_footer(
        "Section 6  |  Robustness & Methodological Rigor",
        "Sensitivity Checks and Model Limitations",
        "Evaluating the BOD <= 50 mg/L analytical cutoff and testing generalization to unseen stations",
    )

    s16.add_table(
        0.35,
        0.95,
        9.30,
        1.85,
        headers=[
            "Model Specification (all with set.seed(513))",
            "Train N",
            "Test N",
            "Intercept (β₀)",
            "Slope (β₁)",
            "Train R²",
            "Test R²",
            "Test RMSE",
            "Test MAE",
        ],
        rows=[
            [
                "1. Primary Model (BOD <= 50 mg/L, Random 80:20 Split)",
                "63,893",
                "15,974",
                "7.0745",
                "-0.1784",
                "0.2499",
                "0.2370",
                "1.6508 mg/L",
                "1.1750 mg/L",
            ],
            [
                "2. Sensitivity Check 1 (All 80,223 Valid Pairs, No Cutoff)",
                "64,178",
                "16,045",
                "6.7236",
                "-0.0849",
                "0.1502",
                "0.1598",
                "1.7528 mg/L",
                "1.2655 mg/L",
            ],
            [
                "3. Sensitivity Check 2 (BOD <= 50, Station-Grouped 80:20 Split)",
                "64,122",
                "15,745",
                "7.0576",
                "-0.1719",
                "0.2248",
                "0.3369",
                "1.5429 mg/L",
                "1.1343 mg/L",
            ],
        ],
        col_Ratios=[0.32, 0.08, 0.08, 0.09, 0.08, 0.08, 0.08, 0.10, 0.09],
        font_size=8.4,
    )

    s16.add_textbox(
        0.35,
        2.92,
        4.55,
        2.28,
        [
            {"text": "Why BOD <= 50 mg/L is an Analytical Choice (Check 1)", "size": 10.5, "bold": True, "color": NAVY, "space_after": 4},
            {"text": "50 mg/L is an analytical filtering choice (not a universal standard) that excludes 356 extreme rows (0.44%, BOD 51–486 mg/L).", "size": 8.9, "color": SLATE_TEXT, "bullet": True, "space_after": 3},
            {"text": "Why the 356 rows distort OLS: DO has a physical floor at 0 mg/L (49.2% of excluded rows already have DO <= 1 mg/L). Fitting a straight line out to BOD = 486 mg/L pulls the slope from -0.1784 to -0.0849 (predicting impossible DO = -34.5 mg/L at BOD = 486) and lowers Test R² from 0.2370 to 0.1598.", "size": 8.9, "color": SLATE_TEXT, "bullet": True, "space_after": 3},
            {"text": "Also, 36 excluded rows report DO > 6 mg/L despite BOD > 50 mg/L (aerated outfalls or reporting anomalies with high leverage).", "size": 8.9, "color": SLATE_TEXT, "bullet": True},
        ],
        fill=CARD_BG,
        border=CARD_BORDER,
        rounded=True,
    )

    s16.add_textbox(
        5.10,
        2.92,
        4.55,
        2.28,
        [
            {"text": "Station-Level Leakage & Limitations (Check 2)", "size": 10.5, "bold": True, "color": TEAL, "space_after": 4},
            {"text": "Station Split Check: Under a random row split, repeated samples from the same station (2,978 unique stations) appear in both train and test sets.", "size": 8.9, "color": SLATE_TEXT, "bullet": True, "space_after": 3},
            {"text": "Holding out 20% of completely unseen stations (596 test stations vs. 2,382 train stations) yields virtually identical slope (-0.1719) and strong generalization (Test RMSE = 1.5429 mg/L, Test R² = 0.3369).", "size": 8.9, "color": SLATE_TEXT, "bullet": True, "space_after": 3},
            {"text": "Remaining Limitations: Observational data cannot prove causation; repeated seasonal samples within the same river basins share spatial/temporal autocorrelation; single predictor omits temperature and flow.", "size": 8.9, "color": AMBER, "bold": True, "bullet": True},
        ],
        fill=LIGHT_TEAL_BG,
        border=TEAL,
        rounded=True,
    )
    slides.append(s16)
    notes_dict[16] = [
        "[Slide 16 — Sensitivity Checks and Limitations]",
        "What to say: We performed two important sensitivity checks to test the assumptions of our primary regression model.",
        "First, in Sensitivity Check 1, we fitted the exact same model on all 80,223 complete pairs without the BOD <= 50 mg/L cutoff. Including the 356 extreme observations (0.44% of the data, where BOD reaches up to 486 mg/L) flattens the slope by more than half (from -0.1784 to -0.0849) and lowers Test R² from 0.2370 to 0.1598. Why? Because Dissolved Oxygen cannot physically drop below 0 mg/L, so extreme BOD points sit along a flat floor near zero and pull the linear OLS line upward.",
        "Second, in Sensitivity Check 2, we addressed station-level data leakage by splitting the 2,978 distinct stations 80:20 (2,382 training stations vs. 596 unseen test stations). The slope (-0.1719) and intercept (7.0576) remain nearly identical, with Test RMSE = 1.5429 mg/L and Test R² = 0.3369, showing that the linear relationship generalizes across stations.",
    ]

    # =========================================================================
    # SLIDE 17: KEY FINDINGS AND CONCLUSION
    # =========================================================================
    s17 = SlideBuilder(17)
    s17.add_header_and_footer(
        "Section 7  |  Synthesis",
        "Key Findings and Project Conclusion",
        "Separating descriptive/inferential EDA findings from predictive machine learning conclusions",
    )

    s17.add_textbox(
        0.35,
        0.95,
        4.55,
        3.25,
        [
            {"text": "Descriptive & Inferential EDA Conclusions", "size": 11.5, "bold": True, "color": NAVY, "space_after": 5},
            {"text": "1. Data Engineering Integrity: Harmonized 315 CPCB CSVs (311,379 raw rows) into 109,422 station-date records and cleaned 1,990 Kaggle records while preserving valid co-measured parameters.", "size": 9.2, "color": SLATE_TEXT, "bullet": True, "space_after": 4},
            {"text": "2. Baseline Compliance vs. Skewed Hotspots: 90.8% of CPCB DO readings meet the >= 4.0 mg/L threshold (Median = 6.80 mg/L), whereas BOD is heavily right-skewed (Median = 2.30, Mean = 5.76, Max = 1,315 mg/L).", "size": 9.2, "color": SLATE_TEXT, "bullet": True, "space_after": 4},
            {"text": "3. Verified Geographic & Seasonal Differences: BOD differs significantly across states (Kruskal-Wallis p < 2.2e-16), and Monsoon dilution lowers median BOD from 2.40 to 2.10 mg/L (Wilcoxon p = 5.48e-24).", "size": 9.2, "color": SLATE_TEXT, "bullet": True, "space_after": 4},
            {"text": "4. Decadal Context: State-level DO medians across 19 matched states remained stable between 2003–2014 and 2018–2024.", "size": 9.2, "color": SLATE_TEXT, "bullet": True},
        ],
        fill=CARD_BG,
        border=CARD_BORDER,
        rounded=True,
    )

    s17.add_textbox(
        5.10,
        0.95,
        4.55,
        3.25,
        [
            {"text": "Predictive Machine Learning Conclusions", "size": 11.5, "bold": True, "color": TEAL, "space_after": 5},
            {"text": "1. Negative Linear Association: Simple Linear Regression (DO = 7.0745 - 0.1784 * BOD) confirms that each +1 mg/L of BOD is associated with a 0.1784 mg/L decrease in DO (p < 2e-16).", "size": 9.2, "color": SLATE_TEXT, "bullet": True, "space_after": 4},
            {"text": "2. Modest Single-Predictor Accuracy: On the 20% test set (n = 15,974), BOD explains 23.70% of DO variance (Test RMSE = 1.6508 mg/L, MAE = 1.1750 mg/L) without overfitting.", "size": 9.2, "color": SLATE_TEXT, "bullet": True, "space_after": 4},
            {"text": "3. Sensitivity & Generalization: Full-data OLS is levered by the 0.44% tail of BOD > 50 mg/L due to the zero-DO floor, while station-grouped splitting confirms cross-station stability (slope = -0.1719).", "size": 9.2, "color": SLATE_TEXT, "bullet": True, "space_after": 4},
            {"text": "4. Scientific Discipline: All findings distinguish statistical association from causation and account for network expansion.", "size": 9.2, "color": SLATE_TEXT, "bullet": True},
        ],
        fill=CARD_BG,
        border=CARD_BORDER,
        rounded=True,
    )

    s17.add_textbox(
        0.35,
        4.32,
        9.30,
        0.88,
        [
            {
                "text": "Achievement of Project Objectives: All 9 stated objectives—from multi-file schema inspection and range-validated preprocessing to non-parametric hypothesis testing, decadal comparison, and validated linear regression—have been fully achieved and verified in the rendered HTML and PDF reports.",
                "size": 10.0,
                "bold": True,
                "color": WHITE,
                "align": "ctr",
            }
        ],
        fill=NAVY,
        border=TEAL,
        rounded=True,
        anchor="ctr",
    )
    slides.append(s17)
    notes_dict[17] = [
        "[Slide 17 — Key Findings and Conclusion]",
        "What to say: To conclude, we separate our findings into descriptive/inferential conclusions on the left and predictive machine learning conclusions on the right. Every objective stated at the start of the report was empirically tested and verified.",
        "Key takeaway: While 90.8% of CPCB surface-water samples meet the basic Class C oxygen threshold (>= 4.0 mg/L), localized organic pollution pockets create severe right-skewed BOD spikes. Simple Linear Regression captures the negative association between BOD and DO (explaining 23.7% of variance with RMSE = 1.65 mg/L), while highlighting why multi-parameter non-linear models are needed for higher accuracy.",
    ]

    # =========================================================================
    # SLIDE 18: FUTURE IMPROVEMENTS AND REFERENCES
    # =========================================================================
    s18 = SlideBuilder(18)
    s18.add_header_and_footer(
        "Section 7  |  Next Steps & Citations",
        "Future Improvements and Verified References",
        "Methodological extensions for future work and official data sources used in this project",
    )

    s18.add_textbox(
        0.35,
        0.95,
        4.55,
        4.20,
        [
            {"text": "Future Improvements & Extensions", "size": 12, "bold": True, "color": NAVY, "space_after": 6},
            {"text": "1. Include Additional Physical & Chemical Predictors: Extend the regression model to include water temperature, pH, electrical conductivity, flow rate, and seasonal indicators to account for the remaining ~76% of DO variance.", "size": 9.4, "color": SLATE_TEXT, "bullet": True, "space_after": 6},
            {"text": "2. Non-Linear & Bounded Regression Models: Use log-transformed BOD, Generalized Additive Models (GAMs), or tree-based models (Random Forests) that naturally respect the physical zero floor of Dissolved Oxygen (DO >= 0 mg/L) across extreme BOD ranges.", "size": 9.4, "color": SLATE_TEXT, "bullet": True, "space_after": 6},
            {"text": "3. Spatiotemporal Cross-Validation: Implement river-basin-blocked and year-blocked cross-validation to evaluate forecasting performance across future monitoring years.", "size": 9.4, "color": SLATE_TEXT, "bullet": True, "space_after": 6},
            {"text": "4. Automated Sensor & Lab QA Checks: Flag anomalous high-DO / high-BOD pairs at data ingestion.", "size": 9.4, "color": SLATE_TEXT, "bullet": True},
        ],
        fill=CARD_BG,
        border=CARD_BORDER,
        rounded=True,
    )

    s18.add_textbox(
        5.10,
        0.95,
        4.55,
        4.20,
        [
            {"text": "Official Data Sources & References Used", "size": 12, "bold": True, "color": TEAL, "space_after": 6},
            {"text": "1. Primary Dataset — CPCB / NWDP (Govt. of India): Central Pollution Control Board (CPCB) & National Water Data Portal (NWDP / National Water Informatics Centre, Ministry of Jal Shakti). Surface Water Quality Monitoring Data (Physical, Chemical, and Biological Categories, 315 state-wise CSV files, 2018–2024).", "size": 9.2, "color": SLATE_TEXT, "bullet": True, "space_after": 6},
            {"text": "2. Supplementary Historical Dataset — Kaggle: Indian Water Quality Data (water_dataX.csv, 1,991 raw records covering historical CPCB/NWMP station annual summaries from 2003–2014).", "size": 9.2, "color": SLATE_TEXT, "bullet": True, "space_after": 6},
            {"text": "3. Regulatory Water-Quality Thresholds: CPCB Designated Best Use Water Quality Criteria (Class C: Drinking water source after conventional treatment and disinfection: DO >= 4.0 mg/L, BOD <= 3.0 mg/L, pH 6.5–8.5).", "size": 9.2, "color": SLATE_TEXT, "bullet": True, "space_after": 6},
            {"text": "4. Software & Reproducible Tooling: R (base R stats, lm, predict), dplyr, tidyr, readr, stringr, ggplot2, knitr, and rmarkdown.", "size": 9.2, "color": SLATE_TEXT, "bullet": True},
        ],
        fill=LIGHT_TEAL_BG,
        border=TEAL,
        rounded=True,
    )
    slides.append(s18)
    notes_dict[18] = [
        "[Slide 18 — Future Improvements and References]",
        "What to say: Finally, Slide 18 outlines four practical directions for future work—adding physical predictors like water temperature, using non-linear models that respect the zero-DO floor, applying basin/time-blocked cross-validation, and automating QA checks—alongside our verified data sources and regulatory references.",
        "Closing statement: Thank you for your attention. I am happy to answer any questions and demonstrate the live R Markdown code or rendered HTML/PDF reports.",
    ]

    return slides, notes_dict


def package_pptx(slides, notes_dict, out_path):
    # Extract reference.pptx from Pandoc to a temp directory
    ref_pptx = "/tmp/pandoc_ref_base.pptx"
    subprocess.run(
        [
            "/Applications/RStudio.app/Contents/Resources/app/quarto/bin/tools/aarch64/pandoc",
            "--print-default-data-file",
            "reference.pptx",
        ],
        stdout=open(ref_pptx, "wb"),
        check=True,
    )

    build_dir = "/tmp/pptx_custom_build"
    if os.path.exists(build_dir):
        shutil.rmtree(build_dir)
    os.makedirs(build_dir)

    with zipfile.ZipFile(ref_pptx, "r") as z:
        z.extractall(build_dir)

    # Remove old slides and notesSlides from template
    slides_dir = os.path.join(build_dir, "ppt", "slides")
    slides_rels_dir = os.path.join(slides_dir, "_rels")
    notes_dir = os.path.join(build_dir, "ppt", "notesSlides")
    notes_rels_dir = os.path.join(notes_dir, "_rels")
    media_dir = os.path.join(build_dir, "ppt", "media")

    for d in [slides_dir, slides_rels_dir, notes_dir, notes_rels_dir, media_dir]:
        if os.path.exists(d):
            shutil.rmtree(d)
        os.makedirs(d, exist_ok=True)

    # Write all 18 slides, slide rels, notes slides, notes rels, and media files
    for s in slides:
        i = s.slide_num
        with open(os.path.join(slides_dir, f"slide{i}.xml"), "w", encoding="utf-8") as f:
            f.write(s.to_slide_xml())
        with open(os.path.join(slides_rels_dir, f"slide{i}.xml.rels"), "w", encoding="utf-8") as f:
            f.write(s.to_rels_xml())
        with open(os.path.join(notes_dir, f"notesSlide{i}.xml"), "w", encoding="utf-8") as f:
            f.write(make_notes_xml(i, notes_dict.get(i, [])))
        with open(os.path.join(notes_rels_dir, f"notesSlide{i}.xml.rels"), "w", encoding="utf-8") as f:
            f.write(make_notes_rels_xml(i))

        for media_name, src_path in s.images_used:
            shutil.copyfile(src_path, os.path.join(media_dir, media_name))

    # Update [Content_Types].xml
    n = len(slides)
    slide_overrides = "".join(
        f'<Override PartName="/ppt/slides/slide{i}.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slide+xml"/>'
        f'<Override PartName="/ppt/notesSlides/notesSlide{i}.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.notesSlide+xml"/>'
        for i in range(1, n + 1)
    )
    layout_overrides = "".join(
        f'<Override PartName="/ppt/slideLayouts/slideLayout{i}.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slideLayout+xml"/>'
        for i in range(1, 12)
    )
    content_types_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
        '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
        '<Default Extension="xml" ContentType="application/xml"/>'
        '<Default Extension="png" ContentType="image/png"/>'
        '<Override PartName="/ppt/presentation.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.presentation.main+xml"/>'
        '<Override PartName="/ppt/slideMasters/slideMaster1.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slideMaster+xml"/>'
        '<Override PartName="/ppt/notesMasters/notesMaster1.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.notesMaster+xml"/>'
        '<Override PartName="/ppt/presProps.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.presProps+xml"/>'
        '<Override PartName="/ppt/viewProps.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.viewProps+xml"/>'
        '<Override PartName="/ppt/theme/theme1.xml" ContentType="application/vnd.openxmlformats-officedocument.theme+xml"/>'
        '<Override PartName="/ppt/theme/theme2.xml" ContentType="application/vnd.openxmlformats-officedocument.theme+xml"/>'
        '<Override PartName="/ppt/tableStyles.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.tableStyles+xml"/>'
        f"{layout_overrides}{slide_overrides}"
        '<Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>'
        '<Override PartName="/docProps/app.xml" ContentType="application/vnd.openxmlformats-officedocument.extended-properties+xml"/>'
        "</Types>"
    )
    with open(os.path.join(build_dir, "[Content_Types].xml"), "w", encoding="utf-8") as f:
        f.write(content_types_xml)

    # Update ppt/_rels/presentation.xml.rels
    slide_rels = "".join(
        f'<Relationship Id="rIdSlide{i}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide" Target="slides/slide{i}.xml"/>'
        for i in range(1, n + 1)
    )
    pres_rels_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideMaster" Target="slideMasters/slideMaster1.xml"/>'
        '<Relationship Id="rId6" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/notesMaster" Target="notesMasters/notesMaster1.xml"/>'
        '<Relationship Id="rId7" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/presProps" Target="presProps.xml"/>'
        '<Relationship Id="rId8" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/viewProps" Target="viewProps.xml"/>'
        '<Relationship Id="rId9" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/theme" Target="theme/theme1.xml"/>'
        '<Relationship Id="rId10" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/tableStyles" Target="tableStyles.xml"/>'
        f"{slide_rels}"
        "</Relationships>"
    )
    with open(os.path.join(build_dir, "ppt", "_rels", "presentation.xml.rels"), "w", encoding="utf-8") as f:
        f.write(pres_rels_xml)

    # Update ppt/presentation.xml
    sld_ids = "".join(
        f'<p:sldId id="{255 + i}" r:id="rIdSlide{i}"/>' for i in range(1, n + 1)
    )
    pres_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<p:presentation xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" '
        'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" '
        'xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" '
        'saveSubsetFonts="1" autoCompressPictures="0">'
        '<p:sldMasterIdLst><p:sldMasterId id="2147483648" r:id="rId1"/></p:sldMasterIdLst>'
        '<p:notesMasterIdLst><p:notesMasterId r:id="rId6"/></p:notesMasterIdLst>'
        f"<p:sldIdLst>{sld_ids}</p:sldIdLst>"
        '<p:sldSz cx="9144000" cy="5143500" type="screen16x9"/>'
        '<p:notesSz cx="6858000" cy="9144000"/>'
        '<p:defaultTextStyle><a:defPPr><a:defRPr lang="en-US"/></a:defPPr></p:defaultTextStyle>'
        "</p:presentation>"
    )
    with open(os.path.join(build_dir, "ppt", "presentation.xml"), "w", encoding="utf-8") as f:
        f.write(pres_xml)

    # Update docProps/core.xml
    core_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" '
        'xmlns:dc="http://purl.org/dc/elements/1.1/" '
        'xmlns:dcterms="http://purl.org/dc/terms/" '
        'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">'
        "<dc:title>Geographic and Seasonal Analysis of Surface Water Quality in India Using CPCB Monitoring Data</dc:title>"
        "<dc:creator>Emmanuel Jobin (2026EMAI20054)</dc:creator>"
        "<dc:subject>DSC 513 Introduction to Data Science Mini Project</dc:subject>"
        "<dc:description>18-Slide Academic Presentation with Speaker Notes</dc:description>"
        "</cp:coreProperties>"
    )
    with open(os.path.join(build_dir, "docProps", "core.xml"), "w", encoding="utf-8") as f:
        f.write(core_xml)

    # Zip into final .pptx
    if os.path.exists(out_path):
        os.remove(out_path)
    with zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, _, files in os.walk(build_dir):
            for file in sorted(files):
                full_p = os.path.join(root, file)
                rel_p = os.path.relpath(full_p, build_dir)
                zf.write(full_p, rel_p)


def write_speaker_notes_guide(notes_dict, out_md):
    lines = [
        "# Formal Academic Presentation Guide & Speaker Notes",
        "",
        "- **Project Title:** Geographic and Seasonal Analysis of Surface Water Quality in India Using CPCB Monitoring Data",
        "- **Student Name:** Emmanuel Jobin",
        "- **Register Number:** 2026EMAI20054",
        "- **Course:** DSC 513 – Introduction to Data Science (IIIT Kottayam)",
        "- **Presentation File:** `CPCB_Water_Quality_Mini_Project_Presentation.pptx` (18 Slides, 16:9 Widescreen, with embedded Speaker Notes)",
        "",
        "---",
        "",
    ]
    for s_num in sorted(notes_dict.keys()):
        notes = notes_dict[s_num]
        header = notes[0].strip("[]")
        lines.append(f"## {header}")
        lines.append("")
        for p in notes[1:]:
            lines.append(f"- {p}")
        lines.append("")
        lines.append("---")
        lines.append("")

    with open(out_md, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


if __name__ == "__main__":
    slides, notes_dict = build_all_slides()
    package_pptx(slides, notes_dict, PPTX_OUT)
    shutil.copyfile(PPTX_OUT, PPTX_ROOT_COPY)
    write_speaker_notes_guide(notes_dict, GUIDE_OUT)
    print(f"[+] Successfully generated {len(slides)}-slide PPTX at: {PPTX_OUT}")
    print(f"[+] Copied PPTX to project root: {PPTX_ROOT_COPY}")
    print(f"[+] Successfully generated Speaker Notes Guide at: {GUIDE_OUT}")

