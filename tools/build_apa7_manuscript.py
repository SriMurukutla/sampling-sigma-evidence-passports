#!/usr/bin/env python3
from __future__ import annotations

import copy
import re
import sys
from pathlib import Path

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT, WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt


TITLE = "Scope-Bound Cybersecurity Evidence Passports With Independent Review and Living Assurance Lineage"
SHORT_TITLE = "CYBERSECURITY EVIDENCE PASSPORTS"


def field_page(run):
    begin = OxmlElement("w:fldChar"); begin.set(qn("w:fldCharType"), "begin")
    instr = OxmlElement("w:instrText"); instr.set(qn("xml:space"), "preserve"); instr.text = " PAGE "
    end = OxmlElement("w:fldChar"); end.set(qn("w:fldCharType"), "end")
    run._r.extend([begin, instr, end])


def set_cell_margins(cell, top=80, start=100, bottom=80, end=100):
    tc_pr = cell._tc.get_or_add_tcPr()
    tc_mar = tc_pr.first_child_found_in("w:tcMar")
    if tc_mar is None:
        tc_mar = OxmlElement("w:tcMar"); tc_pr.append(tc_mar)
    for key, value in (("top", top), ("start", start), ("bottom", bottom), ("end", end)):
        node = tc_mar.find(qn(f"w:{key}"))
        if node is None: node = OxmlElement(f"w:{key}"); tc_mar.append(node)
        node.set(qn("w:w"), str(value)); node.set(qn("w:type"), "dxa")


def set_cell_border(cell, **edges):
    tc_pr = cell._tc.get_or_add_tcPr()
    borders = tc_pr.first_child_found_in("w:tcBorders")
    if borders is None:
        borders = OxmlElement("w:tcBorders"); tc_pr.append(borders)
    for edge, spec in edges.items():
        node = borders.find(qn(f"w:{edge}"))
        if node is None: node = OxmlElement(f"w:{edge}"); borders.append(node)
        for k, v in spec.items(): node.set(qn(f"w:{k}"), str(v))


def add_p(doc, text="", *, indent=True, align=None, italic=False, bold=False, keep=False):
    p = doc.add_paragraph()
    p.paragraph_format.line_spacing = 2
    # APA 7 requires double spacing without extra space before or after
    # paragraphs. Keep this explicit so later Word style changes cannot add it.
    p.paragraph_format.space_after = Pt(0)
    p.paragraph_format.space_before = Pt(0)
    if indent: p.paragraph_format.first_line_indent = Inches(0.5)
    if align is not None: p.alignment = align
    if keep: p.paragraph_format.keep_with_next = True
    r = p.add_run(text); r.italic = italic; r.bold = bold
    return p


def heading(doc, text, level=1):
    p = doc.add_paragraph()
    p.paragraph_format.line_spacing = 2
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(0)
    p.paragraph_format.keep_with_next = True
    if level == 1:
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(text); r.bold = True
    elif level == 2:
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        r = p.add_run(text); r.bold = True
    else:
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        r = p.add_run(text); r.bold = True; r.italic = True
    return p


def add_list(doc, text):
    p = doc.add_paragraph(style=None)
    p.paragraph_format.left_indent = Inches(0.5)
    p.paragraph_format.first_line_indent = Inches(-0.25)
    p.paragraph_format.line_spacing = 2
    p.paragraph_format.space_after = Pt(0)
    p.add_run("•\t" + text)
    return p


def add_equation(doc, text, number):
    t = doc.add_table(rows=1, cols=2)
    t.autofit = False; t.alignment = WD_TABLE_ALIGNMENT.CENTER
    t.columns[0].width = Inches(5.9); t.columns[1].width = Inches(0.6)
    for c in t.rows[0].cells:
        set_cell_border(c, top={"val":"nil"}, bottom={"val":"nil"}, start={"val":"nil"}, end={"val":"nil"})
        set_cell_margins(c, 0, 0, 0, 0)
    p = t.cell(0,0).paragraphs[0]; p.alignment = WD_ALIGN_PARAGRAPH.CENTER; p.paragraph_format.line_spacing = 2
    r=p.add_run(text); r.italic=True
    p=t.cell(0,1).paragraphs[0]; p.alignment=WD_ALIGN_PARAGRAPH.RIGHT; p.paragraph_format.line_spacing=2; p.add_run(f"({number})")


def add_table(doc, number, title, source_table):
    p=doc.add_paragraph(); p.paragraph_format.keep_with_next=True; p.paragraph_format.line_spacing=2; p.paragraph_format.space_before=Pt(0); p.paragraph_format.space_after=Pt(0)
    p.add_run(f"Table {number}").bold=True
    p=doc.add_paragraph(); p.paragraph_format.keep_with_next=True; p.paragraph_format.line_spacing=2; p.paragraph_format.space_after=Pt(0)
    p.add_run(title).italic=True
    rows, cols = len(source_table.rows), len(source_table.columns)
    t=doc.add_table(rows=rows, cols=cols); t.alignment=WD_TABLE_ALIGNMENT.CENTER; t.autofit=True
    for ri, row in enumerate(source_table.rows):
        for ci, sc in enumerate(row.cells):
            c=t.cell(ri,ci); c.text=sc.text; c.vertical_alignment=WD_CELL_VERTICAL_ALIGNMENT.CENTER
            set_cell_margins(c)
            edges={"start":{"val":"nil"},"end":{"val":"nil"},"insideV":{"val":"nil"},"insideH":{"val":"nil"}}
            if ri==0: edges.update(top={"val":"single","sz":"8","color":"000000"},bottom={"val":"single","sz":"8","color":"000000"})
            if ri==rows-1: edges.update(bottom={"val":"single","sz":"8","color":"000000"})
            set_cell_border(c, **edges)
            for p2 in c.paragraphs:
                p2.paragraph_format.line_spacing=1; p2.paragraph_format.space_after=Pt(0)
                for r in p2.runs:
                    r.font.name="Times New Roman"; r.font.size=Pt(12); r.bold=(ri==0)
        if ri==0:
            tr_pr=row._tr.get_or_add_trPr(); repeat=OxmlElement("w:tblHeader"); repeat.set(qn("w:val"),"true"); tr_pr.append(repeat)
    return t


def add_reference(doc, parts):
    """Add one APA reference entry with a hanging indent and rich typography."""
    p = doc.add_paragraph()
    p.paragraph_format.line_spacing = 2
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(0)
    p.paragraph_format.left_indent = Inches(0.5)
    p.paragraph_format.first_line_indent = Inches(-0.5)
    for text, italic in parts:
        run = p.add_run(text)
        run.italic = italic
    return p


def apa_text(text):
    for roman, arabic in (("VII","7"),("VI","6"),("V","5"),("IV","4"),("III","3"),("II","2"),("I","1")):
        text = text.replace(f"Table {roman}", f"Table {arabic}")
    text = text.replace("Tables IV and V", "Tables 4 and 5")
    text = text.replace("[1]", "(Haber & Stornetta, 1991)")
    text = text.replace("[2]", "(Torres-Arias et al., 2019)")
    text = text.replace("[3]", "(World Wide Web Consortium [W3C], 2025)")
    text = text.replace("[4]", "(National Institute of Standards and Technology [NIST], 2022a)")
    text = text.replace("[5]", "(Supply-chain Levels for Software Artifacts [SLSA], n.d.)")
    text = text.replace("[6]", "(Coalition for Content Provenance and Authenticity [C2PA], n.d.)")
    text = text.replace("[7]", "(Hevner et al., 2004)")
    text = text.replace("[8]", "(NIST, 2022b)")
    text = text.replace("[9]", "(OpenZeppelin, n.d.)")
    text = text.replace("[10]", "(IEEE Access, n.d.)")
    text = text.replace("[11]", "(NIST, 2015)")
    text = text.replace("[12]", "(Rundgren et al., 2020)")
    text = text.replace("[13]", "(OpenAI, 2026a)")
    text = text.replace("[14]", "(OpenAI, 2026b)")
    text = text.replace("Haber and Stornetta established tamper-evident document timestamping (Haber & Stornetta, 1991).", "Haber and Stornetta (1991) established tamper-evident document timestamping.")
    text = text.replace("described by Hevner et al. (Hevner et al., 2004):", "described by Hevner et al. (2004):")
    text = text.replace("described by Hevner et al. (Hevner et al., 2004),", "described by Hevner et al. (2004),")
    text = text.replace("(World Wide Web Consortium [W3C], 2025)-(Coalition for Content Provenance and Authenticity [C2PA], n.d.), (NIST, 2022b)", "(W3C, 2025; NIST, 2022a; SLSA, n.d.; C2PA, n.d.; NIST, 2022b)")
    text = re.sub(r"\s+", " ", text).strip()
    return text


def build(source: Path, output: Path):
    src=Document(source); doc=Document()
    sec=doc.sections[0]; sec.top_margin=sec.bottom_margin=sec.left_margin=sec.right_margin=Inches(1)
    styles=doc.styles
    normal=styles["Normal"]; normal.font.name="Times New Roman"; normal.font.size=Pt(12)
    normal.paragraph_format.line_spacing = 2
    normal.paragraph_format.space_before = Pt(0)
    normal.paragraph_format.space_after = Pt(0)
    normal._element.rPr.rFonts.set(qn("w:eastAsia"), "Times New Roman")
    for s in styles:
        if hasattr(s,"font"):
            s.font.name="Times New Roman"; s._element.get_or_add_rPr().rFonts.set(qn("w:eastAsia"),"Times New Roman")
    header=sec.header
    header.paragraphs[0].text=""
    ht=header.add_table(rows=1, cols=2, width=Inches(6.5)); ht.autofit=False
    ht.columns[0].width=Inches(5.8); ht.columns[1].width=Inches(0.7)
    for c in ht.rows[0].cells:
        set_cell_border(c, top={"val":"nil"}, bottom={"val":"nil"}, start={"val":"nil"}, end={"val":"nil"}, insideH={"val":"nil"}, insideV={"val":"nil"})
        set_cell_margins(c,0,0,0,0)
        c.paragraphs[0].paragraph_format.line_spacing=1
    ht.cell(0,0).paragraphs[0].add_run(SHORT_TITLE)
    hp=ht.cell(0,1).paragraphs[0]; hp.alignment=WD_ALIGN_PARAGRAPH.RIGHT; field_page(hp.add_run())

    # Professional title page.
    for _ in range(3): doc.add_paragraph()
    p=add_p(doc,TITLE,indent=False,align=WD_ALIGN_PARAGRAPH.CENTER,bold=True); p.paragraph_format.keep_with_next=True
    add_p(doc,"Sri Sai Lakshmi Ganesh Murukutla",indent=False,align=WD_ALIGN_PARAGRAPH.CENTER)
    add_p(doc,"Murukutla Group LLC",indent=False,align=WD_ALIGN_PARAGRAPH.CENTER)
    add_p(doc,"Austin, Texas, United States",indent=False,align=WD_ALIGN_PARAGRAPH.CENTER)
    doc.add_paragraph()
    heading(doc,"Author Note",1)
    add_p(doc,"ORCID: https://orcid.org/0009-0001-5057-7399",indent=False)
    add_p(doc,"This research received no external funding. The author declares no conflict of interest related to the prototype evaluation reported in this manuscript.",indent=False)
    add_p(doc,"OpenAI ChatGPT (OpenAI, 2026a) and Codex (OpenAI, 2026b) supported editorial restructuring, software development, preparation of the reproducible evaluation harness, and document formatting. The author reviewed the manuscript, source code, citations, experiments, and submission statements and independently executed the reported tests.",indent=False)
    add_p(doc,"Correspondence concerning this article should be addressed to Sri Sai Lakshmi Ganesh Murukutla, Murukutla Group LLC, Austin, TX, USA. Email: murukutlassl@gmail.com",indent=False)
    doc.add_page_break()

    heading(doc,"Abstract",1)
    abstract=re.sub(r"^ABSTRACT\s+","",src.paragraphs[7].text)
    add_p(doc,abstract,indent=False)
    p=add_p(doc,"",indent=False); p.add_run("Keywords: ").italic=True; p.add_run(re.sub(r"^INDEX TERMS\s+","",src.paragraphs[8].text))
    doc.add_page_break()
    heading(doc,TITLE,1)

    table_map={25:(1,"Design Requirements and Protected Failure Modes",0),29:(2,"Evidence Passport Field Groups",1),36:(3,"Threats, Mitigations, and Residual Risks",4),49:(4,"Observed Prototype Measurements",6),52:(5,"Contract Suite Composition",8),56:(6,"Planned Primary Outcomes and Analysis",9),86:(7,"Reproducibility Artifacts",10)}
    # APA papers begin the body with the paper title; an "Introduction"
    # heading is not used. Subsequent major divisions use Level 1 headings.
    h1={14:"Research Questions and Related Work",23:"Design Science Method",26:"Architecture and Data Model",35:"Threat Model",37:"Prototype Implementation",45:"Measured Prototype Results",54:"Comparative Evaluation Protocol",58:"Prospective Results and Decision Rules",65:"Validity Ethics and Reproducibility",72:"Governance and Economic Separation",74:"Limitations",80:"Conclusion",82:"Acknowledgments",84:"Data Availability",86:"Appendix A Reproducibility Artifacts"}
    h2={15:"Research Questions",21:"Research Gap",27:"Assurance Planes",31:"Formal Commitments and Decision Predicate",38:"Smart Contract",40:"Verification Algorithm",43:"Reproducibility Package",46:"Experimental Setup",48:"Observed Results",66:"Validity",68:"Ethics and Privacy",70:"Reproducibility"}
    skip={0,1,2,3,4,5,6,7,8,10,25,29,36,49,52,56,82,84,86,87,89,90,91,92,93,94,95,96,97,98,99,100,101,102,103,104}
    for i in range(10,89):
        if i in table_map:
            if i == 86:
                doc.add_page_break()
                heading(doc,"Appendix A Reproducibility Artifacts",1)
            n,title,ti=table_map[i]; add_table(doc,n,title,src.tables[ti]); continue
        if i in h1: heading(doc,h1[i],1); continue
        if i in h2: heading(doc,h2[i],2); continue
        if i in skip: continue
        if i==32:
            add_p(doc,apa_text(src.paragraphs[i].text)); add_equation(doc,"C(x) = SHA-256(JCS(x))",1); continue
        if i==33:
            add_p(doc,apa_text(src.paragraphs[i].text)); add_equation(doc,"V = H ∧ S ∧ C ∧ R ∧ T ∧ Q",2); continue
        if i==41:
            p=add_p(doc,"Algorithm 1",indent=False,bold=True); p.paragraph_format.keep_with_next=True
            add_p(doc,"Local Passport Verification",indent=False,italic=True,keep=True)
            code=src.tables[5].cell(0,0).text
            p=add_p(doc,code,indent=False); p.paragraph_format.line_spacing=1
            for r in p.runs: r.font.name="Courier New"; r.font.size=Pt(10)
            continue
        if i==50:
            add_p(doc,apa_text(src.paragraphs[i].text)); add_equation(doc,"L95 = 0.025^(1/5000) = 0.999263",3); continue
        text=src.paragraphs[i].text.strip()
        if text.startswith("•"):
            add_list(doc,apa_text(text[1:].strip()))
        elif text:
            add_p(doc,apa_text(text))

    doc.add_page_break(); heading(doc,"References",1)
    refs=[
      [("Coalition for Content Provenance and Authenticity. (n.d.). ",False),("Content credentials technical specification (Version 2.5)",True),(". https://spec.c2pa.org/specifications/specifications/2.5/index.html",False)],
      [("Haber, S., & Stornetta, W. S. (1991). How to time-stamp a digital document. ",False),("Journal of Cryptology, 3",True),(", 99–111. https://doi.org/10.1007/BF00196791",False)],
      [("Hevner, A. R., March, S. T., Park, J., & Ram, S. (2004). Design science in information systems research. ",False),("MIS Quarterly, 28",True),("(1), 75–105. https://doi.org/10.2307/25148625",False)],
      [("IEEE Access. (n.d.). ",False),("Preparing your article",True),(". https://ieeeaccess.ieee.org/authors/preparing-your-article/",False)],
      [("National Institute of Standards and Technology. (2015). ",False),("Secure hash standard (FIPS PUB 180-4)",True),(". U.S. Department of Commerce. https://doi.org/10.6028/NIST.FIPS.180-4",False)],
      [("National Institute of Standards and Technology. (2022a). ",False),("Assessing security and privacy controls in information systems and organizations (NIST SP 800-53A Rev. 5)",True),(". U.S. Department of Commerce. https://doi.org/10.6028/NIST.SP.800-53Ar5",False)],
      [("National Institute of Standards and Technology. (2022b). ",False),("Secure software development framework (SSDF) version 1.1 (NIST SP 800-218)",True),(". U.S. Department of Commerce. https://doi.org/10.6028/NIST.SP.800-218",False)],
      [("OpenAI. (2026a). ",False),("ChatGPT",True),(" [Large language model]. https://chatgpt.com/",False)],
      [("OpenAI. (2026b). ",False),("Codex",True),(" [AI coding agent]. https://openai.com/codex/",False)],
      [("OpenZeppelin. (n.d.). ",False),("OpenZeppelin contracts documentation",True),(". https://docs.openzeppelin.com/contracts/",False)],
      [("Rundgren, A., Jordan, B., & Erdtman, S. (2020). ",False),("JSON canonicalization scheme (JCS) (RFC 8785)",True),(". Internet Engineering Task Force. https://doi.org/10.17487/RFC8785",False)],
      [("Supply-chain Levels for Software Artifacts. (n.d.). ",False),("SLSA specification version 1.2",True),(". https://slsa.dev/spec/v1.2/",False)],
      [("Torres-Arias, S., Afzali, H., Kuppusamy, T. K., Curtmola, R., & Cappos, J. (2019). in-toto: Providing farm-to-table guarantees for bits and bytes. In ",False),("28th USENIX Security Symposium (USENIX Security 19)",True),(" (pp. 1393–1410). USENIX Association. https://www.usenix.org/conference/usenixsecurity19/presentation/torres-arias",False)],
      [("World Wide Web Consortium. (2025). ",False),("Verifiable credentials data model v2.0",True),(". https://www.w3.org/TR/vc-data-model-2.0/",False)],
    ]
    for ref in refs:
        add_reference(doc,ref)
    output.parent.mkdir(parents=True,exist_ok=True); doc.save(output)


if __name__=="__main__":
    if len(sys.argv)!=3: raise SystemExit("usage: build_apa7_manuscript.py SOURCE.docx OUTPUT.docx")
    build(Path(sys.argv[1]),Path(sys.argv[2]))
