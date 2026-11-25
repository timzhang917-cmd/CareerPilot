import re
from io import BytesIO
from pathlib import Path
from xml.sax.saxutils import escape

from django.utils import formats, timezone
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    CondPageBreak, KeepTogether, Paragraph, SimpleDocTemplate, Table, TableStyle,
)


FONT_NAME = "CareerPilotReportSans"
FONT_PATH = Path(__file__).with_name("fonts") / "CareerPilotReportSans.ttf"
pdfmetrics.registerFont(TTFont(FONT_NAME, str(FONT_PATH)))

INK = colors.HexColor("#222222")
MUTED = colors.HexColor("#515B54")
ACCENT = colors.HexColor("#315D3F")
RULE = colors.HexColor("#D9E1DB")
SCORE_BACKGROUND = colors.HexColor("#EEF4EC")
MARGIN = 46
CJK_TEXT = re.compile(r"[\u3000-\u9fff\uf900-\ufaff\U00020000-\U000323af]")

BODY = ParagraphStyle(
    "Body", fontName=FONT_NAME, fontSize=10.5, leading=16, textColor=INK, spaceAfter=5,
)
CJK_BODY = ParagraphStyle("CJK Body", parent=BODY, wordWrap="CJK")
TITLE = ParagraphStyle(
    "Title", parent=BODY, fontName="Helvetica-Bold", fontSize=27, leading=32,
    spaceAfter=10, keepWithNext=True,
)
JOB = ParagraphStyle(
    "Job", parent=BODY, fontSize=16, leading=22, spaceAfter=3, keepWithNext=True,
)
CJK_JOB = ParagraphStyle("CJK Job", parent=JOB, wordWrap="CJK")
METADATA = ParagraphStyle(
    "Date", parent=BODY, fontSize=9, leading=13, textColor=MUTED, spaceAfter=15,
    keepWithNext=True,
)
SECTION = ParagraphStyle(
    "Section", parent=BODY, fontName="Helvetica-Bold", fontSize=15, leading=20,
    textColor=ACCENT, spaceBefore=15, spaceAfter=5,
)
ITEM = ParagraphStyle(
    "Item", parent=BODY, fontSize=11, leading=17, textColor=ACCENT, spaceBefore=5,
)
CJK_ITEM = ParagraphStyle("CJK Item", parent=ITEM, wordWrap="CJK")
SCORE_LABEL = ParagraphStyle(
    "Score Label", parent=BODY, fontName="Helvetica", fontSize=8.5, leading=11,
    textColor=MUTED, alignment=TA_CENTER,
)
SCORE_VALUE = ParagraphStyle(
    "Score Value", parent=SCORE_LABEL, fontName="Helvetica-Bold", fontSize=17,
    leading=21, textColor=ACCENT,
)

SCORES = (
    ("Hard Skills", "hard_skills"),
    ("Soft Skills", "soft_skills"),
    ("Experience", "experience"),
    ("Education", "education"),
)
DETAIL_SECTIONS = (
    ("Job Requirement Comparison", "requirements", "requirement", (
        ("Candidate Evidence", "evidence"), ("Assessment", "assessment"),
    )),
    ("Must-fix Issues", "must_fix_issues", "problem", (
        ("Location", "location"), ("Why it matters", "why_it_matters"),
        ("Suggested correction", "suggested_correction"),
    )),
    ("Advanced Suggestions", "suggestions", "recommendation", (
        ("Priority", "priority"), ("Target section", "target_section"),
        ("Why this helps", "reason"),
    )),
)


def report_paragraph(text, style=BODY, cjk_style=CJK_BODY):
    # Paragraph supports markup, so content from the analysis must be escaped.
    return Paragraph(
        "<br/>".join(escape(line) for line in text.splitlines()),
        cjk_style if CJK_TEXT.search(text) else style,
    )


def text_value(value):
    return value.strip() if isinstance(value, str) else ""


def result_list(result, key):
    values = result.get(key)
    return values if isinstance(values, list) else []


def score_text(value):
    if type(value) in (int, float):
        return f"{value}%" if 0 <= value <= 100 else "-"
    if isinstance(value, str) and re.fullmatch(r"\d+(?:\.\d+)?", value.strip(), re.ASCII):
        return f"{value.strip()}%" if 0 <= float(value) <= 100 else "-"
    return "-"


def score_table(overall, categories, width):
    scores = [("Overall Match", overall.get("score"))]
    scores.extend((label, categories.get(key)) for label, key in SCORES)
    table = Table(
        [[Paragraph(label, SCORE_LABEL) for label, _ in scores],
         [Paragraph(score_text(value), SCORE_VALUE) for _, value in scores]],
        colWidths=[width / len(scores)] * len(scores),
    )
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), SCORE_BACKGROUND),
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#DCEBE0")),
        ("TOPPADDING", (0, 0), (-1, 0), 11),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 2),
        ("BOTTOMPADDING", (0, 1), (-1, 1), 11),
    ]))
    return table


def add_section_heading(story, title):
    # Reserve room for the start of the section while allowing its body to split.
    height = SECTION.spaceBefore + SECTION.leading + SECTION.spaceAfter
    height += 2 * BODY.leading
    story.extend([CondPageBreak(height), Paragraph(title, SECTION)])


def add_detail_section(story, title, records, heading_key, fields, width):
    section_heading = [Paragraph(title, SECTION)]
    for record in records:
        if not isinstance(record, dict):
            continue

        heading = text_value(record.get(heading_key))
        entry = [report_paragraph(heading, ITEM, CJK_ITEM)] if heading else []
        for label, key in fields:
            value = text_value(record.get(key))
            if value:
                entry.append(report_paragraph(f"{label}: {value}"))
        if not entry:
            continue

        entry = section_heading + entry
        section_heading = []
        heights = [paragraph.wrap(width, 0)[1] for paragraph in entry]
        spacing = [paragraph.getSpaceBefore() + paragraph.getSpaceAfter() for paragraph in entry]
        if sum(heights) + sum(spacing) <= 130:
            story.append(KeepTogether(entry))
        else:
            # Keep short entries intact and let longer entries start on the current page.
            opening = sum(
                min(height, 2 * paragraph.style.leading) + gap
                for paragraph, height, gap in zip(entry[:3], heights, spacing)
            )
            story.append(CondPageBreak(opening))
            story.extend(entry)

    if section_heading:
        story.append(KeepTogether(section_heading + [report_paragraph("No entries recorded.")]))


def draw_page(canvas, document):
    width, height = document.pagesize
    canvas.saveState()
    canvas.setStrokeColor(RULE)
    canvas.line(MARGIN, height - 45, width - MARGIN, height - 45)
    canvas.line(MARGIN, 42, width - MARGIN, 42)
    canvas.setFillColor(ACCENT)
    canvas.setFont("Helvetica-Bold", 10)
    canvas.drawString(MARGIN, height - 34, "CareerPilot")
    canvas.setFillColor(MUTED)
    canvas.setFont("Helvetica", 9)
    canvas.drawRightString(width - MARGIN, 29, f"Page {document.page}")
    canvas.restoreState()


def build_analysis_pdf(analysis):
    result = analysis.result_data
    overall = result.get("overall")
    if not isinstance(overall, dict):
        overall = {}
    categories = result.get("category_scores")
    if not isinstance(categories, dict):
        categories = {}

    buffer = BytesIO()
    document = SimpleDocTemplate(
        buffer, pagesize=A4, title="CV Analysis Report", author="CareerPilot",
        leftMargin=MARGIN, rightMargin=MARGIN, topMargin=63, bottomMargin=57,
    )
    date = formats.date_format(timezone.template_localtime(analysis.created_at), "M j, Y")
    width = document.width - 12  # SimpleDocTemplate's frame applies 6 pt padding on each side.
    story = [
        Paragraph("CV Analysis Report", TITLE),
        report_paragraph(analysis.job_description.job_title, JOB, CJK_JOB),
        Paragraph(f"Analyzed {escape(date)}", METADATA),
        score_table(overall, categories, width),
    ]
    add_section_heading(story, "Overall Summary")
    summary = [text_value(overall.get(key)) for key in ("level", "summary")]
    story.append(report_paragraph("\n".join(filter(None, summary)) or "No summary recorded."))

    for title, key in (("Key Strengths", "strengths"), ("Main Gaps", "gaps")):
        add_section_heading(story, title)
        items = [text_value(item) for item in result_list(result, key)]
        story.extend(report_paragraph(f"• {item}") for item in items if item)
        if not any(items):
            story.append(report_paragraph("No entries recorded."))

    for title, key, heading_key, fields in DETAIL_SECTIONS:
        add_detail_section(story, title, result_list(result, key), heading_key, fields, width)

    document.build(story, onFirstPage=draw_page, onLaterPages=draw_page)
    buffer.seek(0)
    return buffer
