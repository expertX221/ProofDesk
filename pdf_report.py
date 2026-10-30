"""Readable PDF exports, generated in memory without storing user reports."""
from io import BytesIO
from xml.sax.saxutils import escape


def create_report_pdf(report):
    try:
        from reportlab.lib import colors
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.enums import TA_LEFT
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, KeepTogether
    except ImportError:
        raise ValueError('PDF export needs reportlab. Run: pip install -r requirements.txt') from None
    if not isinstance(report.get('checks'), list) or not report['checks']:
        raise ValueError('No review checks to export.')
    buffer = BytesIO()
    ink, green = colors.HexColor('#182b2a'), colors.HexColor('#286757')
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='PDTitle', fontName='Helvetica-Bold', fontSize=28, leading=34, textColor=ink, spaceAfter=8))
    styles.add(ParagraphStyle(name='PDSection', fontName='Helvetica-Bold', fontSize=14, leading=19, textColor=green, spaceBefore=15, spaceAfter=8))
    styles.add(ParagraphStyle(name='PDBody', fontName='Helvetica', fontSize=10, leading=15, textColor=ink, spaceAfter=9, splitLongWords=True))
    styles.add(ParagraphStyle(name='PDMeta', fontName='Helvetica', fontSize=8, leading=12, textColor=colors.HexColor('#63716a'), spaceAfter=7))
    styles.add(ParagraphStyle(name='PDCheck', parent=styles['PDBody'], fontName='Helvetica-Bold', fontSize=11, leading=16, spaceAfter=7))
    def para(value, style='PDBody', limit=18000):
        value = str(value or '')[:limit].replace('\u2011', '-').replace('\u2013', '-').replace('\u2014', '-')
        return Paragraph(escape(value).replace('\n', '<br/>'), styles[style])
    story = [para('ProofDesk', 'PDTitle'), para('SUBMISSION READINESS REVIEW', 'PDMeta')]
    mode = str(report.get('mode', 'unknown'))
    story.append(para('ILLUSTRATIVE SAMPLE - no live inference' if mode == 'sample' else 'LIVE REVIEW - NVIDIA Nemotron on Nebius Token Factory', 'PDCheck'))
    for field, label in [('repository', 'Repository'), ('created_at', 'Review time (UTC)'), ('model', 'Model'), ('seconds', 'Inference seconds')]:
        if report.get(field) is not None:
            story.append(para(f'{label}: {report[field]}', 'PDMeta'))
    usage = report.get('usage') or {}
    if isinstance(usage, dict) and usage.get('total_tokens') is not None:
        story.append(para(f"Reported token usage: {usage['total_tokens']} total", 'PDMeta'))
    checks = [c for c in report['checks'][:30] if isinstance(c, dict)]
    counts = {s: sum(c.get('status') == s for c in checks) for s in ['verified', 'needs_review', 'missing']}
    story.extend([Spacer(1, 10), para('  |  '.join(f'{n} {s.replace("_", " ")}' for s, n in counts.items()), 'PDCheck'), para(report.get('summary')), para('Requirement checks', 'PDSection')])
    evidence = {str(e.get('id')): e for e in report.get('evidence', [])[:20] if isinstance(e, dict)}
    cited = []
    for i, c in enumerate(checks, 1):
        status = str(c.get('status', 'needs_review')).replace('_', ' ').upper()
        story.append(KeepTogether([para(f'{i:02d} / {status}', 'PDMeta'), para(c.get('requirement', 'Requirement'), 'PDCheck')]))
        story.append(para(c.get('reason')))
        if c.get('action'):
            story.append(para('Next action: ' + str(c['action'])))
        ids = c.get('evidence_ids', [])
        if isinstance(ids, list):
            for identifier in ids:
                if not isinstance(identifier, str):
                    continue
                e = evidence.get(identifier)
                if e:
                    story.append(para(f"Source [{identifier}]: {e.get('path', '')}", 'PDMeta'))
                    if identifier not in cited:
                        cited.append(identifier)
        story.append(Spacer(1, 7))
    for field, heading in [('description', 'Submission description draft'), ('demo_script', 'Demo outline draft')]:
        if report.get(field):
            story.extend([para(heading, 'PDSection'), para(report[field])])
    if cited:
        story.append(para('Evidence references', 'PDSection'))
        for identifier in cited:
            e = evidence[identifier]
            story.extend([para(f"[{identifier}] {e.get('path', '')}", 'PDCheck'), para(e.get('url') or 'User-provided context; not independently verified.', 'PDMeta')])
    story.extend([para('Review limits', 'PDSection'), para('This is a bounded static evidence review. Verified means supported by inspected text; it does not establish successful execution, eligibility, ownership, or formal compliance. Missing means absent from inspected evidence. Demo links and video visibility/duration require separate verification. Model-generated drafts and judgments need human review.', 'PDMeta')])
    def page(canvas, doc):
        canvas.setStrokeColor(colors.HexColor('#dce3dd'))
        canvas.line(45, 42, 550, 42)
        canvas.setFont('Helvetica', 8)
        canvas.setFillColor(green)
        canvas.drawString(45, 29, 'ProofDesk | Evidence first. Always.')
        canvas.drawRightString(550, 29, f'Page {doc.page}')
    SimpleDocTemplate(buffer, pagesize=(595, 842), rightMargin=45, leftMargin=45, topMargin=45, bottomMargin=57, title='ProofDesk submission review', author='ProofDesk').build(story, onFirstPage=page, onLaterPages=page)
    return buffer.getvalue()
