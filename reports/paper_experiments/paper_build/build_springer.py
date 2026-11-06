"""Builds the paper on Springer's official Word proceedings template (splnproc2510), with macros removed.
Usage: build_springer.py <exp dir> <unpacked template dir> <out.docx>"""
import re, shutil, sys, zipfile
from pathlib import Path
from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt

S, TPL, OUT = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
AUTHORS = "Lê Minh Kha, Nguyễn Đông Quân, and Trương Đình Tú"
RUN_LEFT = "M. K. Lê et al."
RUN_RIGHT = "How Much Does a Phishing URL Gate Depend on Domain Popularity?"
ADDRESS = "Faculty of Information Technology, Ton Duc Thang University, Ho Chi Minh City, Vietnam"
EMAIL = "[corresponding author e-mail]"


def clean_template():
    """Copy the template package without macros, the custom ribbon and the sample chart."""
    work = OUT.parent / "tpl_clean"
    shutil.rmtree(work, ignore_errors=True); shutil.copytree(TPL, work)
    for rel in ("customUI", "word/charts"):
        shutil.rmtree(work / rel, ignore_errors=True)
    for rel in ("word/vbaProject.bin", "word/vbaData.xml", "word/_rels/vbaProject.bin.rels"):
        (work / rel).unlink(missing_ok=True)

    def edit(rel, fn):
        f = work / rel; f.write_text(fn(f.read_text(encoding="utf-8-sig")), encoding="utf-8")

    def types(s):
        s = re.sub(r'<Override PartName="/(word/vbaData\.xml|word/charts/[^"]*|customUI/[^"]*)"[^>]*/>', "", s)
        s = re.sub(r'<Default Extension="(bin|ICO|ico|png)"[^>]*/>', "", s)
        return s.replace("application/vnd.ms-word.document.macroEnabled.main+xml",
                         "application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml")

    def drop_rels(pattern):
        return lambda s: re.sub(r'<Relationship [^>]*Target="[^"]*(?:%s)[^"]*"[^>]*/>' % pattern, "", s)

    edit("[Content_Types].xml", types)
    edit("word/_rels/document.xml.rels", drop_rels("vbaProject|vbaData|charts/"))
    edit("_rels/.rels", drop_rels("customUI"))
    # running heads; the page-number fields stay as they are
    edit("word/header1.xml", lambda s: re.sub(r"F\.\s*Author and S\.\s*Author", RUN_LEFT, s))
    edit("word/header2.xml", lambda s: re.sub(r"Contribution Title \(shortened if too long\)", RUN_RIGHT, s))
    path = OUT.parent / "tpl_clean.docx"
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        names = sorted(p for p in work.rglob("*") if p.is_file())
        for p in sorted(names, key=lambda p: p.name != "[Content_Types].xml"):
            z.write(p, p.relative_to(work).as_posix())
    return path


src = (S / "build_paper.py").read_text(encoding="utf-8")
exec(src[src.index("REFS = {"):src.index("order = []")])
order = []


def cite(m):
    nums = []
    for k in m.group(1).split(","):
        k = k.strip()
        if k not in order:
            order.append(k)
        nums.append(order.index(k) + 1)
    return "[" + ", ".join(map(str, sorted(nums))) + "]"


doc = Document(str(clean_template()))
body = doc.element.body
for el in list(body):
    if el.tag != qn("w:sectPr"):
        body.remove(el)
first = [True]
C = WD_ALIGN_PARAGRAPH.CENTER


def para(style):
    p = doc.add_paragraph(); p.style = doc.styles[style]
    return p


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


def P(text, indent=True, size=None, align=None, after=0):
    p = para("Normal" if indent and not first[0] else "p1a"); first[0] = False
    return runs(p, text, size)


def heading(t, style):
    para(style).add_run(re.sub(r"^\d+(\.\d+)?\s+", "", t)); first[0] = True


def H1(t):
    heading(t, "heading1")


def H2(t):
    heading(t, "heading2")


def L(items, numbered=False):
    for t in items:
        runs(para("numitem" if numbered else "dashitem"), t)
    first[0] = True


def CAP(text, before=None, after=None):
    runs(para("tablecaption"), text)


def border(cell, **kw):
    tc = cell._tc.get_or_add_tcPr(); b = tc.find(qn("w:tcBorders"))
    if b is None:
        b = OxmlElement("w:tcBorders"); tc.append(b)
    for edge, sz in kw.items():
        e = OxmlElement(f"w:{edge}"); e.set(qn("w:val"), "single"); e.set(qn("w:sz"), str(sz))
        e.set(qn("w:color"), "000000"); b.append(e)


def T(rows, widths, size=8.5, left_cols=1):
    t = doc.add_table(rows=len(rows), cols=len(rows[0])); t.alignment = WD_TABLE_ALIGNMENT.CENTER; t.autofit = False
    for j, wd in enumerate(widths):
        t.columns[j].width = Cm(wd)
    mar = OxmlElement("w:tblCellMar")  # narrow side padding, so headers stay on one line
    for side in ("left", "right"):
        e = OxmlElement(f"w:{side}"); e.set(qn("w:w"), "50"); e.set(qn("w:type"), "dxa"); mar.append(e)
    look = t._tbl.tblPr.find(qn("w:tblLook")); look.addprevious(mar) if look is not None else t._tbl.tblPr.append(mar)
    for i, row in enumerate(rows):
        t.rows[i]._tr.get_or_add_trPr().append(OxmlElement("w:cantSplit"))
        for j, v in enumerate(row):
            c = t.cell(i, j); c.width = Cm(widths[j]); p = c.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT if j < left_cols else C
            p.paragraph_format.first_line_indent = Cm(0); p.paragraph_format.line_spacing = Pt(10.5)
            if i < len(rows) - 1:
                p.paragraph_format.keep_with_next = True
            runs(p, str(v), size)
            if i == 0:
                for r in p.runs:
                    r.bold = True
                border(c, top=8, bottom=4)
            if i == len(rows) - 1:
                border(c, bottom=8)
    sp = doc.add_paragraph(); sp.paragraph_format.space_after = Pt(4)
    sp.paragraph_format.line_spacing = Pt(6)
    first[0] = True


def FIG(path, width, cap):
    p = para("image"); p.paragraph_format.keep_with_next = True
    p.add_run().add_picture(str(path), width=Cm(width))
    runs(para("figurecaption"), cap); first[0] = True


text = (S / "paper_text.py").read_text(encoding="utf-8")
TITLE = re.match(r'TITLE = "([^"]+)"', text).group(1)
abstract = re.search(r'runs\(p, "(\*\*Abstract\.\*\*.*?)", 9\)\n', text).group(1)
keywords = re.search(r'runs\(p, "(\*\*Keywords:\*\*.*?)", 9\)\n', text).group(1).replace(" · ", ", ") + "."

para("papertitle").add_run(TITLE)
para("author").add_run(AUTHORS)
p = para("address"); p.add_run(ADDRESS); p.add_run().add_break(WD_BREAK.LINE); p.add_run(EMAIL)
runs(para("abstract"), abstract)
runs(para("keywords"), keywords)

rest = text[text.index('H1("1   Introduction")'):]
head, tail = rest[:rest.index('p = doc.add_paragraph(); p.paragraph_format.space_before = Pt(10)')], rest
exec(head.replace("q = doc.add_paragraph();", "q = doc.add_paragraph(); q.alignment = WD_ALIGN_PARAGRAPH.LEFT;"))
for m in re.finditer(r'runs\(p, "(\*\*(?:Ethics and data|Disclosure of Interests)\.\*\*.*?)", 9\)', tail):
    runs(para("acknowlegments"), m.group(1))

p = para("heading1"); p.add_run("References")
pPr = p._p.get_or_add_pPr(); num = OxmlElement("w:numPr")
for tag, val in (("w:ilvl", "0"), ("w:numId", "0")):
    e = OxmlElement(tag); e.set(qn("w:val"), val); num.append(e)
pPr.append(num)
for k in order:
    p = para("referenceitem"); p.add_run(REFS[k]); p.alignment = WD_ALIGN_PARAGRAPH.LEFT
assert not set(REFS) - set(order)

cp = doc.core_properties
cp.title = TITLE; cp.author = "Lê Minh Kha, Nguyễn Đông Quân, Trương Đình Tú"; cp.last_modified_by = ""; cp.comments = ""
cp.subject = ""; cp.keywords = ""
doc.save(OUT); print("saved refs", len(order))
