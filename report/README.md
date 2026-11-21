# Report and execution evidence

Use `Lab10_Report_Joey_Saade.pdf` as the submission report. It contains four
pages and six screenshots from the successful Jenkins build #1. The DOCX
contains the same text and screenshot crops as an editable companion.

`screenshots/` retains the full original browser captures. `figures/` contains
the crops used in the report; only cropping was applied. `evidence/` retains
the original Jenkins console log, build and stage API responses, plugin
versions, JUnit XML, coverage XML/HTML, Bandit JSON and deployment manifest.

The verified build checked out commit
`c6ec5f334265396d28fad3777beb60ea32734bc6`. Subsequent commits add the report,
evidence and documentation; they do not change the tested Python project or
Jenkinsfile.

`generate_report.py` rebuilds both reports using python-docx, Pillow and
ReportLab from the document skill's bundled runtime. It uses Windows Calibri
fonts. These report-authoring tools are separate from the lab application's
Jenkins requirements.

PDF quality assurance: rendered all four pages with Poppler and inspected
every page for clipping, overlap and screenshot readability. The DOCX was
structurally checked for six images, expected text, author and page geometry.
LibreOffice is absent and Microsoft Word rendering stalled, so DOCX visual
rendering was not completed. The PDF is the visually verified version.
