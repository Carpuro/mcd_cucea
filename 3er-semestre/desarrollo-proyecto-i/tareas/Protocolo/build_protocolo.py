# -*- coding: utf-8 -*-
"""
Desarrollo de Proyecto I - Research protocol filled directly on the official CUCEA template.
Keeps the template cover (UdeG crest, CUCEA and MCD logos), its fonts, numbering and the
footer of the body section (CUCEA logo + page number). Only the guide text is replaced.
All figures come from the thesis repo (ai-automation-risk-jalisco); manufacturing-specific
items that are not yet computed are written as planned work.
"""
import copy
import glob
import os
from docx import Document
from docx.shared import Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

HERE = os.path.dirname(os.path.abspath(__file__))
TEMPLATE = glob.glob(os.path.join(HERE, "plantilla_protocolo_cucea_2026.docx"))[0]
OUT = os.path.join(HERE, "Protocolo_Investigacion_CarlosPulidoRosas.docx")

TITULO = ("Modelo de evaluación del riesgo de sustitución laboral mediante herramientas de ciencia "
          "de datos: inteligencia artificial cognitiva y robótica en la industria manufacturera de "
          "Jalisco")

doc = Document(TEMPLATE)
P = doc.paragraphs
body = doc.element.body

# ---------------- prototypes taken from the template itself -----------------
PROTO = {
    "titulo": copy.deepcopy(P[24]._p),     # centered, bold, 12 pt
    "seccion": copy.deepcopy(P[54]._p),    # numbered section heading (List Paragraph)
    "sub": copy.deepcopy(P[26]._p),        # bold justified subheading
    "cuerpo": copy.deepcopy(P[28]._p),     # justified body, 12 pt, 1.5 spacing
    "sangria": copy.deepcopy(P[55]._p),    # indented body
}

# ---------------- cover: fill only the placeholders --------------------------
def set_text(par, text):
    runs = [r for r in par.runs if r._r.xpath("./w:t")]
    runs[0].text = text
    for r in runs[1:]:
        r.text = ""

set_text(P[10], TITULO)
set_text(P[14], "Carlos Pulido Rosas")
set_text(P[20], "7 de octubre de 2026")
set_text(P[22], "carlos.pulido.rosas@gmail.com")
for r in P[23].runs:                       # keep the anchored CUCEA / MCD logos untouched
    if "Teléfono" in r.text:
        r.text = "Teléfono"

# ---------------- remove the guide, keep the body-section footer ------------
elems = list(body)
cover_break = elems[23]                    # paragraph holding the cover section break
guide_break = elems[35]                    # paragraph holding the body section break (footer2)
final_sect = body.find(qn("w:sectPr"))
body.replace(final_sect, copy.deepcopy(guide_break.find(qn("w:pPr")).find(qn("w:sectPr"))))
for el in elems[24:]:
    if el.tag != qn("w:sectPr"):
        body.remove(el)
END = body.find(qn("w:sectPr"))


# ---------------- formatting per "Lineamientos presentación de trabajos MCD Ver 2.0" ----------
# Times New Roman; text 12 / level-1 headings 14; justified; double spacing in text, single in
# tables, 1.5 in references with hanging indent; 1.25 cm first-line indent; level-1 headings
# centered, bold, uppercase, Roman numerals; level-2 left, bold, Arabic numbering.
FONT = "Times New Roman"
INDENT = 709                     # 1.25 cm in twips
ROMAN = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X", "XI", "XII", "XIII"]
_num = {"sec": 0, "sub": 0}


def _p(text, size=12, bold=False, italic=False, align="both", line=480, first=None, left=None,
       hanging=None, before=0, after=0, keep=False):
    p = OxmlElement("w:p"); ppr = OxmlElement("w:pPr")
    if keep:
        ppr.append(OxmlElement("w:keepNext"))
    sp = OxmlElement("w:spacing")
    sp.set(qn("w:before"), str(int(before * 20))); sp.set(qn("w:after"), str(int(after * 20)))
    sp.set(qn("w:line"), str(line)); sp.set(qn("w:lineRule"), "auto"); ppr.append(sp)
    if first or left or hanging:
        ind = OxmlElement("w:ind")
        if left: ind.set(qn("w:left"), str(left))
        if first: ind.set(qn("w:firstLine"), str(first))
        if hanging: ind.set(qn("w:hanging"), str(hanging))
        ppr.append(ind)
    jc = OxmlElement("w:jc"); jc.set(qn("w:val"), align); ppr.append(jc)
    p.append(ppr)
    r = OxmlElement("w:r"); rp = OxmlElement("w:rPr")
    rf = OxmlElement("w:rFonts")
    for a in ("ascii", "hAnsi", "cs", "eastAsia"):
        rf.set(qn(f"w:{a}"), FONT)
    rp.append(rf)
    if bold: rp.append(OxmlElement("w:b"))
    if italic: rp.append(OxmlElement("w:i"))
    for tag in ("w:sz", "w:szCs"):
        e = OxmlElement(tag); e.set(qn("w:val"), str(int(size * 2))); rp.append(e)
    r.append(rp)
    t = OxmlElement("w:t"); t.text = text; t.set(qn("xml:space"), "preserve")
    r.append(t); p.append(r)
    END.addprevious(p)
    return p


def titulo(t):
    _p(t, size=14, bold=True, align="center", before=0, after=12, keep=True)


def seccion(t):
    _num["sec"] += 1; _num["sub"] = 0
    _p(f"{ROMAN[_num['sec'] - 1]}. {t.upper()}", size=14, bold=True, align="center",
       before=12, after=6, keep=True)


def sub(t):
    _num["sub"] += 1
    _p(f"{_num['sec']}.{_num['sub']}. {t}", bold=True, align="left", before=12, after=0, keep=True)


def par(t):
    _p(t, first=INDENT)


def item(t):
    _p(t, left=INDENT)


def ref(t):
    _p(t, align="left", line=360, left=INDENT, hanging=INDENT)


def caption_table(num, title):
    _p(f"Tabla {num}", bold=True, align="left", line=480, before=12, keep=True)
    _p(title, italic=True, align="left", line=480, keep=True)


def note(t):
    _p(t, size=8, align="left", line=240, before=4, after=8)


def page_break():
    p = OxmlElement("w:p"); r = OxmlElement("w:r"); br = OxmlElement("w:br")
    br.set(qn("w:type"), "page"); r.append(br); p.append(r); END.addprevious(p)


def table(rows, widths_twips):
    tbl = OxmlElement("w:tbl"); tblPr = OxmlElement("w:tblPr")
    jc = OxmlElement("w:jc"); jc.set(qn("w:val"), "center"); tblPr.append(jc)
    lay = OxmlElement("w:tblLayout"); lay.set(qn("w:type"), "fixed"); tblPr.append(lay)
    borders = OxmlElement("w:tblBorders")
    for side in ("top", "left", "bottom", "right", "insideH", "insideV"):
        e = OxmlElement(f"w:{side}"); e.set(qn("w:val"), "single"); e.set(qn("w:sz"), "4")
        e.set(qn("w:color"), "808080"); borders.append(e)
    tblPr.append(borders); tbl.append(tblPr)
    grid = OxmlElement("w:tblGrid")
    for w in widths_twips:
        g = OxmlElement("w:gridCol"); g.set(qn("w:w"), str(w)); grid.append(g)
    tbl.append(grid)
    for ri, row in enumerate(rows):
        tr = OxmlElement("w:tr")
        if ri == 0:
            trPr = OxmlElement("w:trPr"); h = OxmlElement("w:tblHeader"); trPr.append(h); tr.append(trPr)
        for ci, val in enumerate(row):
            tc = OxmlElement("w:tc"); tcPr = OxmlElement("w:tcPr")
            tw = OxmlElement("w:tcW"); tw.set(qn("w:w"), str(widths_twips[ci])); tw.set(qn("w:type"), "dxa")
            tcPr.append(tw)
            if ri == 0:
                shd = OxmlElement("w:shd"); shd.set(qn("w:val"), "clear"); shd.set(qn("w:fill"), "D9D9D9")
                tcPr.append(shd)
            tc.append(tcPr)
            p = OxmlElement("w:p"); ppr = OxmlElement("w:pPr")
            spc = OxmlElement("w:spacing"); spc.set(qn("w:before"), "0"); spc.set(qn("w:after"), "0")
            spc.set(qn("w:line"), "240"); spc.set(qn("w:lineRule"), "auto"); ppr.append(spc)
            jc2 = OxmlElement("w:jc"); jc2.set(qn("w:val"), "left" if ci == 0 else "center"); ppr.append(jc2)
            p.append(ppr)
            r = OxmlElement("w:r"); rp = OxmlElement("w:rPr")
            rf = OxmlElement("w:rFonts")
            for a in ("ascii", "hAnsi", "cs", "eastAsia"):
                rf.set(qn(f"w:{a}"), FONT)
            rp.append(rf)
            if ri == 0: rp.append(OxmlElement("w:b"))
            sz = OxmlElement("w:sz"); sz.set(qn("w:val"), "20"); rp.append(sz)
            r.append(rp); t = OxmlElement("w:t"); t.text = val; t.set(qn("xml:space"), "preserve")
            r.append(t); p.append(r); tc.append(p); tr.append(tc)
        tbl.append(tr)
    END.addprevious(tbl)


# CONTENT lives in contenido_protocolo.py (all facts cited, APA 7)
exec(open(os.path.join(HERE, "contenido_protocolo.py"), encoding="utf-8").read())

from docx.shared import Cm
for s_ in doc.sections:
    s_.left_margin, s_.right_margin = Cm(3.0), Cm(2.5)
    s_.top_margin, s_.bottom_margin = Cm(2.5), Cm(2.5)
doc.save(OUT)
print("DOCX:", OUT)
DL = os.path.join(os.path.expanduser("~"), "Downloads",
                  "Protocolo de investigación MCD con Inteligencia Artificial 2026.docx")
try:
    doc.save(DL); print("DOCX:", DL)
except PermissionError:
    print("No se pudo escribir en Descargas (archivo abierto en Word):", DL)
