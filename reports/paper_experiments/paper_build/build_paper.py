"""Builds the paper as a Word file with LNCS-like page geometry. Inline: {c:key,key} cites, *italic*, **bold**."""
import re, sys
from pathlib import Path
from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt

S = Path(sys.argv[1]); OUT = Path(sys.argv[2])
FONT = "Times New Roman"

REFS = {
 "phishtime": "Oest, A., Zhang, P., Wardman, B., Nunes, E., Burgis, J., Zand, A., Thomas, K., Doupé, A., Ahn, G.-J.: PhishTime: continuous longitudinal measurement of the effectiveness of anti-phishing blacklists. In: 29th USENIX Security Symposium (2020)",
 "urlnet": "Le, H., Pham, Q., Sahoo, D., Hoi, S.C.H.: URLNet: learning a URL representation with deep learning for malicious URL detection. arXiv:1802.03162 (2018)",
 "sahingoz": "Sahingoz, O.K., Buber, E., Demir, O., Diri, B.: Machine learning based phishing detection from URLs. Expert Syst. Appl. 117, 345–357 (2019). https://doi.org/10.1016/j.eswa.2018.09.029",
 "phiusiil": "Prasad, A., Chandra, S.: PhiUSIIL: a diverse security profile empowered phishing URL detection framework based on similarity index and incremental learning. Comput. Secur. 136, 103545 (2024). https://doi.org/10.1016/j.cose.2023.103545",
 "phreshphish": "Dalton, T., et al.: PhreshPhish: a real-world, high-quality, large-scale phishing website dataset and benchmark. arXiv:2507.10854 (2025)",
 "tranco": "Le Pochat, V., Van Goethem, T., Tajalizadehkhoob, S., Korczyński, M., Joosen, W.: Tranco: a research-oriented top sites ranking hardened against manipulation. In: Network and Distributed System Security Symposium (2019)",
 "xgboost": "Chen, T., Guestrin, C.: XGBoost: a scalable tree boosting system. In: 22nd ACM SIGKDD Conference on Knowledge Discovery and Data Mining, pp. 785–794 (2016). https://doi.org/10.1145/2939672.2939785",
 "lightgbm": "Ke, G., et al.: LightGBM: a highly efficient gradient boosting decision tree. In: Advances in Neural Information Processing Systems, vol. 30 (2017)",
 "lstm": "Hochreiter, S., Schmidhuber, J.: Long short-term memory. Neural Comput. 9(8), 1735–1780 (1997). https://doi.org/10.1162/neco.1997.9.8.1735",
 "birnn": "Schuster, M., Paliwal, K.K.: Bidirectional recurrent neural networks. IEEE Trans. Signal Process. 45(11), 2673–2681 (1997). https://doi.org/10.1109/78.650093",
 "agten": "Agten, P., Joosen, W., Piessens, F., Nikiforakis, N.: Seven months' worth of mistakes: a longitudinal study of typosquatting abuse. In: Network and Distributed System Security Symposium (2015). https://doi.org/10.14722/ndss.2015.23058",
 "damerau": "Damerau, F.J.: A technique for computer detection and correction of spelling errors. Commun. ACM 7(3), 171–176 (1964). https://doi.org/10.1145/363958.363994",
 "winkler": "Winkler, W.E.: String comparator metrics and enhanced decision rules in the Fellegi-Sunter model of record linkage. In: Proceedings of the Section on Survey Research Methods, American Statistical Association, pp. 354–359 (1990)",
 "chatphish": "Koide, T., Nakano, H., Chiba, D.: ChatPhishDetector: detecting phishing sites using large language models. IEEE Access (2024). https://doi.org/10.1109/ACCESS.2024.3483905",
 "phishpedia": "Lin, Y., Liu, R., Divakaran, D.M., Ng, J.Y., Chan, Q.Z., Lu, Y., Si, Y., Zhang, F., Dong, J.S.: Phishpedia: a hybrid deep learning based approach to visually identify phishing webpages. In: 30th USENIX Security Symposium (2021)",
 "greshake": "Greshake, K., Abdelnabi, S., Mishra, S., Endres, C., Holz, T., Fritz, M.: Not what you've signed up for: compromising real-world LLM-integrated applications with indirect prompt injection. In: 16th ACM Workshop on Artificial Intelligence and Security (2023). arXiv:2302.12173",
 "phishagent": "Cao, T., Huang, C., Li, Y., et al.: PhishAgent: a robust multimodal agent for phishing webpage detection. In: AAAI Conference on Artificial Intelligence (2025). https://doi.org/10.1609/aaai.v39i27.35003",
 "mcnemar": "McNemar, Q.: Note on the sampling error of the difference between correlated proportions or percentages. Psychometrika 12(2), 153–157 (1947). https://doi.org/10.1007/BF02295996",
 "wilson": "Wilson, E.B.: Probable inference, the law of succession, and statistical inference. J. Am. Stat. Assoc. 22(158), 209–212 (1927). https://doi.org/10.1080/01621459.1927.10502953",
 "zieni": "Zieni, R., Massari, L., Calzarossa, M.C.: Phishing or not phishing? A survey on the detection of phishing websites. IEEE Access (2023). https://doi.org/10.1109/ACCESS.2023.3247135",
}
order = []


def cite(m):
    nums = []
    for k in m.group(1).split(","):
        k = k.strip()
        if k not in order:
            order.append(k)
        nums.append(order.index(k) + 1)
    return "[" + ", ".join(map(str, sorted(nums))) + "]"


doc = Document()
sec = doc.sections[0]
sec.page_width, sec.page_height = Cm(21), Cm(29.7)
sec.left_margin = sec.right_margin = Cm(4.4)
sec.top_margin = sec.bottom_margin = Cm(5.2)
sec.header_distance = Cm(4.2); sec.footer_distance = Cm(4.2)
st = doc.styles["Normal"]; st.font.name = FONT; st.font.size = Pt(10)
st.element.rPr.rFonts.set(qn("w:eastAsia"), FONT)
st.paragraph_format.space_after = Pt(0); st.paragraph_format.line_spacing = 1.0
for name, size, before, after in (("Heading 1", 12, 12, 6), ("Heading 2", 10, 9, 4)):
    h = doc.styles[name]; h.font.size = Pt(size); h.font.bold = True; h.font.italic = False
    rpr = h.element.get_or_add_rPr()
    rf = rpr.find(qn("w:rFonts"))
    if rf is None:
        rf = OxmlElement("w:rFonts"); rpr.append(rf)
    for a in list(rf.attrib):
        del rf.attrib[a]
    for a in ("w:ascii", "w:hAnsi", "w:eastAsia", "w:cs"):
        rf.set(qn(a), FONT)
    c = rpr.find(qn("w:color"))
    if c is not None:
        rpr.remove(c)
    h.paragraph_format.space_before = Pt(before); h.paragraph_format.space_after = Pt(after)
    h.paragraph_format.keep_with_next = True


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


first = [True]


def P(text, indent=True, size=None, align=WD_ALIGN_PARAGRAPH.JUSTIFY, after=0):
    p = doc.add_paragraph(); p.alignment = align
    if indent and not first[0]:
        p.paragraph_format.first_line_indent = Cm(0.42)
    p.paragraph_format.space_after = Pt(after); first[0] = False
    return runs(p, text, size)


def H1(t):
    doc.add_heading(t, 1); first[0] = True


def H2(t):
    doc.add_heading(t, 2); first[0] = True


def L(items, numbered=False):
    for i, t in enumerate(items, 1):
        p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p.paragraph_format.left_indent = Cm(0.6); p.paragraph_format.first_line_indent = Cm(-0.4)
        p.paragraph_format.space_after = Pt(2)
        runs(p, (f"{i}. " if numbered else "– ") + t)
    first[0] = True


def CAP(text, before=6, after=3):
    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(before); p.paragraph_format.space_after = Pt(after)
    p.paragraph_format.keep_with_next = True
    runs(p, text, 9)


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
    t._tbl.tblPr.append(mar)
    for i, row in enumerate(rows):
        t.rows[i]._tr.get_or_add_trPr().append(OxmlElement("w:cantSplit"))
        for j, v in enumerate(row):
            c = t.cell(i, j); c.width = Cm(widths[j]); p = c.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT if j < left_cols else WD_ALIGN_PARAGRAPH.CENTER
            if i < len(rows) - 1:
                p.paragraph_format.keep_with_next = True
            runs(p, str(v), size)
            if i == 0:
                for r in p.runs:
                    r.bold = True
                border(c, top=8, bottom=4)
            if i == len(rows) - 1:
                border(c, bottom=8)
    sp = doc.add_paragraph(); sp.paragraph_format.space_after = Pt(2)
    sp.paragraph_format.line_spacing = Pt(6)
    first[0] = True


def FIG(path, width, cap):
    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.keep_with_next = True; p.paragraph_format.space_before = Pt(6)
    p.add_run().add_picture(str(path), width=Cm(width))
    c = doc.add_paragraph(); c.alignment = WD_ALIGN_PARAGRAPH.CENTER
    c.paragraph_format.space_after = Pt(8); c.paragraph_format.space_before = Pt(3)
    runs(c, cap, 9); first[0] = True


exec((S / "paper_text.py").read_text(encoding="utf-8"))

H1("References")
for i, k in enumerate(order, 1):
    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p.paragraph_format.left_indent = Cm(0.6); p.paragraph_format.first_line_indent = Cm(-0.6)
    p.paragraph_format.space_after = Pt(1.5)
    r = p.add_run(f"{i}.  {REFS[k]}"); r.font.size = Pt(9)
unused = set(REFS) - set(order)
assert not unused, unused

ft = sec.footer.paragraphs[0]; ft.alignment = WD_ALIGN_PARAGRAPH.CENTER
for kind, txt in (("begin", None), (None, "PAGE"), ("end", None)):
    r = ft.add_run(); r.font.size = Pt(9)
    if kind:
        f = OxmlElement("w:fldChar"); f.set(qn("w:fldCharType"), kind); r._r.append(f)
    else:
        it = OxmlElement("w:instrText"); it.text = txt; r._r.append(it)
doc.core_properties.title = TITLE; doc.core_properties.author = "Lê Minh Kha, Nguyễn Đông Quân, Trương Đình Tú"; doc.core_properties.comments = ""
doc.save(OUT); print("saved", OUT, "refs", len(order))
