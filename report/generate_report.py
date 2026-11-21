"""Build the lab report from the saved, unmodified Jenkins evidence.

Run with the document skill's bundled Python runtime (python-docx and Pillow).
Report figures are crops of full screenshots retained in screenshots/.
"""

import json
from pathlib import Path
from xml.sax.saxutils import escape

from docx import Document
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor
from PIL import Image


ROOT = Path(__file__).resolve().parent
EVIDENCE = ROOT / "evidence"
FIGURES = ROOT / "figures"
FIGURES.mkdir(exist_ok=True)
build = json.loads((EVIDENCE / "build-1.json").read_text())
manifest = json.loads((EVIDENCE / "deployment.json").read_text())
assert build["result"] == "SUCCESS" and not build["building"]

# standard_business_brief; memo_masthead opening. Named overrides:
# Title 26pt, Subtitle 11pt gray, Caption 9pt gray, Code 8.5pt Consolas.
doc = Document()
section = doc.sections[0]
section.page_width, section.page_height = Inches(8.5), Inches(11)
section.top_margin = section.bottom_margin = Inches(1)
section.left_margin = section.right_margin = Inches(1)
section.header_distance = section.footer_distance = Inches(0.492)
styles = doc.styles
for name in ("Normal", "Title", "Subtitle", "Heading 1", "Heading 2",
             "Heading 3", "Caption", "Header", "Footer"):
    style = styles[name]
    style.font.name = "Calibri"
    style.font.size = Pt(11)
    style.font.color.rgb = RGBColor.from_string("222222")
    style.paragraph_format.space_before = Pt(0)
    style.paragraph_format.space_after = Pt(6)
    style.paragraph_format.line_spacing = 1.10
for name, size, before, after, color in (
    ("Heading 1", 16, 16, 8, "2E74B5"),
    ("Heading 2", 13, 12, 6, "2E74B5"),
    ("Heading 3", 12, 8, 4, "1F4D78"),
):
    style = styles[name]
    style.font.size, style.font.bold = Pt(size), True
    style.font.color.rgb = RGBColor.from_string(color)
    style.paragraph_format.space_before = Pt(before)
    style.paragraph_format.space_after = Pt(after)
    style.paragraph_format.keep_with_next = True
styles["Title"].font.size = Pt(26)
styles["Title"].font.bold = True
styles["Title"].font.color.rgb = RGBColor.from_string("0B2545")
styles["Subtitle"].font.color.rgb = RGBColor.from_string("555555")
styles["Caption"].font.size = Pt(9)
styles["Caption"].font.color.rgb = RGBColor.from_string("555555")
styles["Caption"].paragraph_format.space_after = Pt(8)
styles["Caption"].paragraph_format.keep_with_next = False
code_style = styles.add_style("Lab Code", 1)
code_style.font.name, code_style.font.size = "Consolas", Pt(8.5)
code_style.paragraph_format.space_before = Pt(0)
code_style.paragraph_format.space_after = Pt(4)
code_style.paragraph_format.line_spacing = 1

header = section.header.paragraphs[0]
header.text = "EECE 435L  |  Lab 10  |  Joey Saade"
header.style = styles["Header"]
header.runs[0].font.size = Pt(9)
header.runs[0].font.color.rgb = RGBColor.from_string("666666")
footer = section.footer.paragraphs[0]
footer.alignment = 2
footer.add_run("Joey Saade  |  ").font.size = Pt(9)
field = OxmlElement("w:fldSimple")
field.set(qn("w:instr"), "PAGE")
footer._p.append(field)


def para(text):
    return doc.add_paragraph(text)


def figure(filename, box, caption, width=6.5):
    path = FIGURES / filename
    with Image.open(ROOT / "screenshots" / filename) as im:
        im.crop(box).save(path)
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(3)
    p.paragraph_format.keep_with_next = True
    p.add_run().add_picture(str(path), width=Inches(width))
    shape = doc.inline_shapes[-1]
    shape._inline.docPr.set("descr", caption)
    doc.add_paragraph(caption, style="Caption")


doc.add_paragraph("Lab 10: Jenkins CI/CD", style="Title")
doc.add_paragraph("Python automation, coverage, security and deployment", style="Subtitle")
para("Joey Saade  |  EECE 435L  |  21 November 2026")
para("Repository: https://github.com/JS9872/435L_Lab10")
doc.add_heading("Configuration and completed pipeline", level=1)
para("Jenkins 2.580.2 ran locally on Windows with Temurin Java 21.0.13.1, "
     "Python 3.12.6 and Git 2.47.1. Git, Pipeline and SSH Agent plugins were "
     "installed, together with Workspace Cleanup, Timestamper and Pipeline "
     "Stage View. The Python-CI-CD job uses Pipeline script from SCM, the "
     "public GitHub repository, branch */main, and script path "
     "jenkins_project/Jenkinsfile_Joey_Saade.")
para("Setup creates a virtual environment and installs pinned tools. Lint "
     "checks the application, deployment script and tests. Test runs pytest "
     "and publishes JUnit results. Coverage enforces full application coverage. "
     "Security Scan runs Bandit. Deploy creates and verifies a local release. "
     "The pipeline selects bat on Windows and sh on Linux and invokes the "
     "virtual environment's Python directly, avoiding shell activation issues.")
figure("01-jenkins-stages.png", (0, 0, 2640, 740),
       "Figure 1. Actual Jenkins build #1: all six requested stages, checkout "
       "and post actions passed.")
para("Build #1 finished SUCCESS on 21 November 2026 at 10:59 UTC "
     "(12:59 Beirut time), in approximately 87 seconds. It checked out commit "
     f"{manifest['commit'][:12]}. Full console output and Jenkins API results "
     "are retained in report/evidence. Later commits package the report and "
     "evidence; the tested application and Jenkinsfile are unchanged.")

doc.add_page_break()
doc.add_heading("Unit testing and code coverage", level=1)
para("The greeting was updated to match the lab's expected personalized "
     "output: Hello, World from Joey Saade! Four tests check the required "
     "greeting, another name, main(), and execution as a script. Jenkins "
     "recorded 4 passed, 0 failed and 0 skipped.")
figure("02-jenkins-tests.png", (700, 100, 3160, 1120),
       "Figure 2. Jenkins JUnit report for build #1: all four tests passed.")
para("The Coverage stage runs coverage run -m pytest, coverage report, "
     "coverage xml and coverage html. The .coveragerc enables branch coverage "
     "and fail_under = 100. app.py achieved 6/6 statements and 2/2 branches "
     "covered. The deployment script is security-scanned and smoke-tested "
     "separately; the reported 100% applies to app.py.")
figure("03-jenkins-coverage.png", (0, 0, 1850, 510),
       "Figure 3. Archived coverage.py HTML report: 100% application coverage.")
para("pytest, coverage and bandit were added to requirements.txt because "
     "the starter lists only flake8 while invoking additional tools. The "
     "pipeline archives XML, HTML and JSON outputs before workspace cleanup.")

doc.add_page_break()
doc.add_heading("Security scanning", level=1)
para("The Security Scan stage runs Bandit 1.8.6 against app.py and deploy.py, "
     "writes reports/bandit.json and prints a readable console report. "
     "A nonzero scan exit code fails the stage and prevents deployment. "
     "The build scanned 52 lines and reported no low, medium or high "
     "findings, no scan errors, no skipped files and no suppressed rules.")
figure("04-jenkins-security.png", (720, 380, 3140, 1650),
       "Figure 4. Actual Jenkins Bandit output: no issues identified and "
       "zero suppressed checks.")
para("Deployment runs the copied, trusted application with runpy.run_path "
     "and captures its output. This avoids building a shell command or "
     "disabling Bandit subprocess checks. The scan result is evidence of "
     "this static analysis run; it does not establish that all possible "
     "security defects are absent.")
para("Jenkins listens on 127.0.0.1:8080. Its administrator password and "
     "runtime data remain outside the public repository. The SSH Agent "
     "plugin satisfies the lab setup requirement; no SSH server is needed "
     "because the assignment permits a simple local deployment.")

doc.add_page_break()
doc.add_heading("Deployment and final build output", level=1)
para("deploy.py creates JENKINS_HOME/deployments/Python-CI-CD/build-1, "
     "copies app.py, runs that deployed file and requires the exact greeting. "
     "It records the build number, source commit, SHA-256 and smoke-test "
     "result in manifest.json. An existing release is never overwritten. "
     "The deployment survives cleanup because it is outside the workspace.")
figure("05-jenkins-deployment-success.png", (720, 330, 3140, 800),
       "Figure 5. Deployed application prints the expected greeting; "
       "deployment smoke test PASS.")
para("The deployed application's SHA-256 was independently checked against "
     "the archived deployment manifest:")
doc.add_paragraph(manifest["sha256"], style="Lab Code")
figure("06-jenkins-finished-success.png", (720, 600, 3140, 1500),
       "Figure 6. Jenkins archives artifacts, cleans the workspace and "
       "finishes with SUCCESS.")
para("Submission.txt contains the public GitHub link for Moodle. The "
     "modified Jenkinsfile, importable SCM job configuration, dependency "
     "list, screenshots, JUnit results, coverage outputs, Bandit JSON, "
     "deployment manifest and complete Jenkins console log are included "
     "in the repository. The source and report commits use Joey Saade's "
     "Git identity and were pushed to JS9872/435L_Lab10.")
para("To reproduce, follow README.md, configure Python-CI-CD using the "
     "supplied job XML or equivalent SCM settings, and choose Build Now. "
     "The implemented deployment is a local CLI release rather than a "
     "remote service; no production endpoint is required by this lab.")

doc.core_properties.author = "Joey Saade"
doc.core_properties.last_modified_by = "Joey Saade"
doc.core_properties.title = "EECE 435L Lab 10 - Jenkins CI/CD"
doc.core_properties.subject = "Successful Jenkins pipeline and execution evidence"
doc.save(ROOT / "Lab10_Report_Joey_Saade.docx")
print("Created Lab10_Report_Joey_Saade.docx")

# Render the same paragraphs and screenshot crops directly to a PDF when
# LibreOffice is unavailable. The editable DOCX is structurally checked;
# the PDF is the visually verified submission copy.
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Image as PDFImage, PageBreak, Spacer,
)

pdfmetrics.registerFont(TTFont("Calibri", "C:/Windows/Fonts/calibri.ttf"))
pdfmetrics.registerFont(TTFont("CalibriBold", "C:/Windows/Fonts/calibrib.ttf"))
pdf_styles = {
    "Normal": ParagraphStyle("Body", fontName="Calibri", fontSize=11,
                             leading=12.1, spaceAfter=6, alignment=TA_LEFT),
    "Title": ParagraphStyle("Title", fontName="CalibriBold", fontSize=26,
                            leading=29, spaceAfter=6, textColor=colors.HexColor("#0B2545")),
    "Subtitle": ParagraphStyle("Subtitle", fontName="Calibri", fontSize=11,
                               leading=12.1, spaceAfter=6, textColor=colors.HexColor("#555555")),
    "Heading 1": ParagraphStyle("H1", fontName="CalibriBold", fontSize=16,
                                leading=18, spaceBefore=16, spaceAfter=8,
                                keepWithNext=True, textColor=colors.HexColor("#2E74B5")),
    "Caption": ParagraphStyle("Caption", fontName="Calibri", fontSize=9,
                              leading=10.5, spaceAfter=8, textColor=colors.HexColor("#555555")),
    "Lab Code": ParagraphStyle("Code", fontName="Courier", fontSize=8.5,
                               leading=10, spaceAfter=4),
}
story = []
figure_index = 0
for p in doc.paragraphs:
    if p._p.xpath('.//w:br[@w:type="page"]'):
        story.append(PageBreak())
    elif p._p.xpath('.//w:drawing'):
        shape = doc.inline_shapes[figure_index]
        figure_path = FIGURES / sorted((ROOT / "screenshots").glob("*.png"))[figure_index].name
        story.append(PDFImage(str(figure_path), width=shape.width.inches * 72,
                              height=shape.height.inches * 72))
        story.append(Spacer(1, 3))
        figure_index += 1
    elif p.text:
        story.append(Paragraph(escape(p.text), pdf_styles.get(p.style.name, pdf_styles["Normal"])))


def page_furniture(canvas, document):
    canvas.saveState()
    canvas.setFont("Calibri", 9)
    canvas.setFillColor(colors.HexColor("#666666"))
    canvas.drawString(72, 756, "EECE 435L  |  Lab 10  |  Joey Saade")
    canvas.drawRightString(540, 36, f"Joey Saade  |  {document.page}")
    canvas.restoreState()


pdf = SimpleDocTemplate(str(ROOT / "Lab10_Report_Joey_Saade.pdf"),
                        pagesize=(612, 792), topMargin=72, bottomMargin=72,
                        leftMargin=72, rightMargin=72, title=doc.core_properties.title,
                        author="Joey Saade")
pdf.build(story, onFirstPage=page_furniture, onLaterPages=page_furniture)
print("Created Lab10_Report_Joey_Saade.pdf")
