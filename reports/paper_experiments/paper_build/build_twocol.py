"""Builds the paper in an IEEE-style two-column A4 layout, from the same text as the LNCS version.
Usage: build_twocol.py <exp dir> <out.docx>"""
import re, sys
from pathlib import Path
from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK, WD_LINE_SPACING
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Mm, Pt

S, OUT = Path(sys.argv[1]), Path(sys.argv[2])
FONT = "Times New Roman"
COL = 8.89  # column width in cm
AUTHORS = "Lê Minh Kha, Nguyễn Đông Quân, and Trương Đình Tú"
ADDRESS = "Faculty of Information Technology, Ton Duc Thang University, Ho Chi Minh City, Vietnam"
EMAIL = "[corresponding author e-mail]"
L_, C_, J_ = WD_ALIGN_PARAGRAPH.LEFT, WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.JUSTIFY

src = (S / "build_paper.py").read_text(encoding="utf-8")
exec(src[src.index("REFS = {"):src.index("order = []")])
order = []


def roman(n):
    out = ""
    for v, s in ((10, "X"), (9, "IX"), (5, "V"), (4, "IV"), (1, "I")):
        while n >= v:
            out += s; n -= v
    return out


def cite(m):
    nums = []
    for k in m.group(1).split(","):
        k = k.strip()
        if k not in order:
            order.append(k)
        nums.append(order.index(k) + 1)
    return "[" + ", ".join(map(str, sorted(nums))) + "]"


doc = Document()
st = doc.styles["Normal"]; st.font.name = FONT; st.font.size = Pt(10)
st.element.rPr.rFonts.set(qn("w:eastAsia"), FONT); st.element.rPr.rFonts.set(qn("w:cs"), FONT)
st.paragraph_format.space_after = Pt(0); st.paragraph_format.space_before = Pt(0)
hy = OxmlElement("w:autoHyphenation"); hy.set(qn("w:val"), "true")
anchor = doc.settings.element.find(qn("w:characterSpacingControl"))  # schema order matters to Word
anchor.addprevious(hy); doc.settings.element.find(qn("w:zoom")).set(qn("w:percent"), "100")


def geometry(sec, cols):
    sec.page_width, sec.page_height = Mm(210), Mm(297)
    sec.top_margin, sec.bottom_margin = Mm(19), Mm(43)
    sec.left_margin = sec.right_margin = Mm(14)
    sec.header_distance = sec.footer_distance = Mm(10)
    c = sec._sectPr.find(qn("w:cols"))
    if c is None:
        c = OxmlElement("w:cols"); sec._sectPr.append(c)
    c.set(qn("w:num"), str(cols)); c.set(qn("w:space"), "239")  # 4.22 mm gap


def runs(p, text, size=None):
    text = re.sub(r"\{c:([^}]+)\}", cite, text)
    for tok in re.split(r"(\*\*[^*]+\*\*|\*[^*]+\*)", text):
        if not tok:
            continue
        if tok.startswith("**"):
            r = p.add_run(tok[2:-2]); r.bold = True
        elif tok.startswith("*"):
            r = p.add_run(tok[1:-1]); r.italic = True
        else:
            r = p.add_run(tok)
        if size:
            r.font.size = Pt(size)
    return p


def para(align=J_, before=0, after=0, keep=False):
    p = doc.add_paragraph(); p.alignment = align; f = p.paragraph_format
    f.space_before, f.space_after, f.keep_with_next = Pt(before), Pt(after), keep
    return p


def P(text, indent=True, size=None, align=None, after=0):
    p = para(after=2); p.paragraph_format.first_line_indent = Cm(0.36)
    p.paragraph_format.line_spacing_rule = WD_LINE_SPACING.EXACTLY; p.paragraph_format.line_spacing = Pt(11.5)
    return runs(p, text, size)


counts = [0, 0]


def heading1(text):
    p = para(C_, 8, 4, True); r = p.add_run(text); r.font.small_caps = True


def H1(t):
    counts[0] += 1; counts[1] = 0
    heading1(f"{roman(counts[0])}. " + re.sub(r"^\d+(\.\d+)?\s+", "", t))


def H2(t):
    counts[1] += 1
    p = para(L_, 6, 3, True); r = p.add_run(f"{chr(64 + counts[1])}. " + re.sub(r"^\d+(\.\d+)?\s+", "", t)); r.italic = True


def L(items, numbered=False):
    for i, t in enumerate(items, 1):
        p = para(after=2); f = p.paragraph_format
        f.left_indent, f.first_line_indent = Cm(0.5), Cm(-0.36)
        runs(p, (f"{i}) " if numbered else "– ") + t)


def CAP(text, before=None, after=None):
    p = para(C_, 8, 3, True)
    m = re.match(r"\*\*Table ([IVX]+)\.\*\* (.*)", text, re.S)
    if m:
        r = p.add_run(f"TABLE {m.group(1)}"); r.font.size = Pt(8); r.add_break(WD_BREAK.LINE)
        runs(p, m.group(2), 8)
    else:
        runs(p, text, 8)


def border(cell, **kw):
    tc = cell._tc.get_or_add_tcPr(); b = tc.find(qn("w:tcBorders"))
    if b is None:
        b = OxmlElement("w:tcBorders"); tc.append(b)
    for edge, sz in kw.items():
        e = OxmlElement(f"w:{edge}"); e.set(qn("w:val"), "single"); e.set(qn("w:sz"), str(sz))
        e.set(qn("w:color"), "000000"); b.append(e)


def no_hyphen(p):
    """Word needs this element before spacing, indent and alignment."""
    pPr = p._p.get_or_add_pPr(); e = OxmlElement("w:suppressAutoHyphens")
    later = [c for c in pPr if c.tag in (qn("w:spacing"), qn("w:ind"), qn("w:jc"))]
    later[0].addprevious(e) if later else pPr.append(e)


# column widths in cm for tables that need more than plain scaling, by table number
WIDTHS = {1: [1.6, 1.15, 1.0, 2.75, 2.3], 3: [2.75, 0.85, 1.6, 1.4, 2.2], 4: [3.1, 0.75, 0.75, 1.6, 1.4, 1.2],
          6: [1.35, 1.15, 1.15, 0.95, 2.2, 0.95, 1.05], 9: [1.6, 1.95, 1.95, 1.65, 1.65], 10: [2.6, 0.85, 1.5, 1.5, 1.4, 0.95]}
tables = [0]


def T(rows, widths, size=7.5, left_cols=1):
    tables[0] += 1
    scale = (COL - 0.1) / sum(widths); widths = WIDTHS.get(tables[0]) or [w * scale for w in widths]
    t = doc.add_table(rows=len(rows), cols=len(rows[0])); t.alignment = WD_TABLE_ALIGNMENT.CENTER; t.autofit = False
    for j, wd in enumerate(widths):
        t.columns[j].width = Cm(wd)
    mar = OxmlElement("w:tblCellMar")  # narrow side padding, so cells fit one column
    for side in ("left", "right"):
        e = OxmlElement(f"w:{side}"); e.set(qn("w:w"), "20"); e.set(qn("w:type"), "dxa"); mar.append(e)
    look = t._tbl.tblPr.find(qn("w:tblLook")); look.addprevious(mar) if look is not None else t._tbl.tblPr.append(mar)
    for i, row in enumerate(rows):
        t.rows[i]._tr.get_or_add_trPr().append(OxmlElement("w:cantSplit"))
        for j, v in enumerate(row):
            c = t.cell(i, j); c.width = Cm(widths[j]); p = c.paragraphs[0]
            p.alignment = L_ if j < left_cols else C_
            p.paragraph_format.line_spacing_rule = WD_LINE_SPACING.EXACTLY; p.paragraph_format.line_spacing = Pt(9)
            if i < len(rows) - 1:
                p.paragraph_format.keep_with_next = True
            runs(p, str(v), size); no_hyphen(p)
            if i == 0:
                for r in p.runs:
                    r.bold = True
                border(c, top=8, bottom=4)
            if i == len(rows) - 1:
                border(c, bottom=8)
    sp = doc.add_paragraph(); sp.paragraph_format.line_spacing_rule = WD_LINE_SPACING.EXACTLY
    sp.paragraph_format.line_spacing = Pt(7)


def FIG(path, width, cap):
    p = para(C_, 6, 0, True); p.add_run().add_picture(str(path), width=Cm(COL - 0.1))
    runs(para(C_, 3, 8), cap, 8)


text = (S / "paper_text.py").read_text(encoding="utf-8")
text = re.sub(r"\bTable (\d+)", lambda m: "Table " + roman(int(m.group(1))), text)
first = [True]  # used by the shared text block
TITLE = re.match(r'TITLE = "([^"]+)"', text).group(1)
abstract = re.search(r'runs\(p, "\*\*Abstract\.\*\* (.*?)", 9\)\n', text).group(1)
keywords = re.search(r'runs\(p, "\*\*Keywords:\*\* (.*?)", 9\)\n', text).group(1).replace(" · ", ", ").lower()

geometry(doc.sections[0], 1)
p = para(C_, 0, 10); r = p.add_run(TITLE); r.font.size = Pt(22)
p.paragraph_format.line_spacing = 1.0; no_hyphen(p)
p = para(C_, 0, 4); p.add_run(AUTHORS).font.size = Pt(11)
p = para(C_, 0, 12); r = p.add_run(ADDRESS); r.italic = True; r.add_break(WD_BREAK.LINE); p.add_run(EMAIL)
geometry(doc.add_section(WD_SECTION.CONTINUOUS), 2)

p = para(after=4); r = p.add_run("Abstract—"); r.bold = True; r.italic = True; r.font.size = Pt(9)
for rr in runs(p, abstract, 9).runs[1:]:
    rr.bold = True
p = para(after=4); r = p.add_run("Keywords—"); r.bold = True; r.italic = True; r.font.size = Pt(9)
for rr in runs(p, keywords + "", 9).runs[1:]:
    rr.bold = True; rr.italic = True

rest = text[text.index('H1("1   Introduction")'):]
marker = 'p = doc.add_paragraph(); p.paragraph_format.space_before = Pt(10)'
head, tail = rest[:rest.index(marker)], rest[rest.index(marker):]
exec(head.replace("q = doc.add_paragraph();", "q = doc.add_paragraph(); q.alignment = L_;").replace("runs(q, line, 9)", "runs(q, line, 8)"))

heading1("Declarations")
for m in re.finditer(r'runs\(p, "(\*\*(?:Ethics and data|Disclosure of Interests)\.\*\*.*?)", 9\)', tail):
    P(m.group(1))

heading1("References")
for i, k in enumerate(order, 1):
    p = para(L_, after=1.5); f = p.paragraph_format
    f.left_indent, f.first_line_indent = Cm(0.6), Cm(-0.6)
    r = p.add_run(f"[{i}]\t{REFS[k]}"); r.font.size = Pt(8)
    f.tab_stops.add_tab_stop(Cm(0.6))
assert not set(REFS) - set(order)
geometry(doc.add_section(WD_SECTION.CONTINUOUS), 1)  # lets the last columns balance

cp = doc.core_properties
cp.title = TITLE; cp.author = "Lê Minh Kha, Nguyễn Đông Quân, Trương Đình Tú"; cp.comments = ""
doc.save(OUT); print("saved refs", len(order))
