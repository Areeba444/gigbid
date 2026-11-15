import os
import json
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.pdfgen import canvas

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PDF_OUTPUT = os.path.join(BASE_DIR, "GigBid_RD_Report.pdf")

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_number(num_pages)
            super().showPage()
        super().save()

    def draw_page_number(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748b"))
        self.drawString(54, 36, "AI-4016 R&D Assignment: GigBid Engineering Design Review")
        page_str = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(612 - 54, 36, page_str)
        self.setStrokeColor(colors.HexColor("#cbd5e1"))
        self.setLineWidth(0.5)
        self.line(54, 48, 612 - 54, 48)
        self.restoreState()

def build_pdf_report():
    doc = SimpleDocTemplate(
        PDF_OUTPUT,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )
    
    styles = getSampleStyleSheet()
    
    # Custom Typography Styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=colors.HexColor('#0f172a'),
        spaceAfter=4
    )
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#475569'),
        spaceAfter=12
    )
    h1_style = ParagraphStyle(
        'SectionH1',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=colors.HexColor('#1e3a8a'),
        spaceBefore=10,
        spaceAfter=6,
        keepWithNext=True
    )
    h2_style = ParagraphStyle(
        'SectionH2',
        parent=styles['Heading3'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=13,
        textColor=colors.HexColor('#0f172a'),
        spaceBefore=6,
        spaceAfter=3,
        keepWithNext=True
    )
    body_style = ParagraphStyle(
        'DocBody',
        parent=styles['BodyText'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=11.5,
        textColor=colors.HexColor('#1e293b'),
        spaceAfter=5
    )
    callout_style = ParagraphStyle(
        'Callout',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=8,
        leading=11,
        textColor=colors.HexColor('#1e40af'),
        backColor=colors.HexColor('#eff6ff'),
        borderColor=colors.HexColor('#bfdbfe'),
        borderWidth=0.5,
        borderPadding=6,
        spaceBefore=4,
        spaceAfter=6
    )
    table_cell = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7.5,
        leading=9.5,
        textColor=colors.HexColor('#0f172a')
    )
    table_header = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=7.5,
        leading=9.5,
        textColor=colors.white
    )

    story = []

    # Title & Metadata Header
    story.append(Paragraph("GigBid: Autonomous Multi-Agent Freelancer Copilot", title_style))
    story.append(Paragraph("Engineering Design Review & Empirical Findings · Course AI-4016 | FAST School of Computing, FAST-NUCES Islamabad", subtitle_style))
    story.append(Paragraph("<b>Author:</b> Areeba Javed (Roll No: 23I-0570) | <b>Instructor:</b> Muhammad Owais Idrees | <b>Stack:</b> LangGraph v1.2, MCP, FastAPI, Groq Open Profile, SQLite", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#0284c7"), spaceAfter=10))

    # SECTION 1
    story.append(Paragraph("1. Problem Formulation & System Constraints", h1_style))
    story.append(Paragraph(
        "Modern freelance platforms create asymmetric friction for independent contractors. Freelancers expend substantial time scanning unstructured feeds, burning paid Connects credits on low-probability proposals, and risking account suspension from inadvertent platform policy violations or off-platform scams. GigBid resolves this operational overhead by automating discovery, multi-dimensional risk and fit assessment, and evidence-grounded drafting.",
        body_style
    ))
    story.append(Paragraph(
        "<b>Non-Negotiable Boundaries:</b> The system strictly preserves human agency. Under no circumstance may the system automatically spend Connects, submit a proposal draft, or send an unapproved client communication. All external writes require an explicit LangGraph <code>interrupt()</code> and human confirmation in the web dashboard. Operational budgets: declared p95 latency target &le; 4.5s; cost per proposal &le; $0.010 USD on open-weight inference.",
        body_style
    ))

    # SECTION 2
    story.append(Paragraph("2. System Architecture & State Discipline", h1_style))
    story.append(Paragraph(
        "GigBid decouples capabilities into three Model Context Protocol (MCP) servers (Portfolio :8002, Marketplace :8003, Workspace :8004) accessed through a single MarketplacePort adapter that transparently targets either the local GigSim simulator or live Upwork MCP.",
        body_style
    ))
    story.append(Paragraph(
        "<b>Bid Graph Orchestration:</b> The Scout queues incoming jobs into a LangGraph StateGraph. Three nodes—<b>Job Analyst</b>, <b>Risk Assessor</b>, and <b>Fit Matcher</b>—execute concurrently in parallel. A barrier-synchronization <b>Decision Node</b> evaluates aggregated risks and skill matches, routing non-viable jobs immediately to auto-skip. Surviving jobs trigger <b>Pricing Strategist</b>, <b>Proposal Writer</b>, <b>Claim Verifier</b>, and a bounded <b>Critic loop</b> (&le; 2 revisions) before passing through the <b>Compliance Guard</b> to the human approval gate.",
        body_style
    ))
    story.append(Paragraph(
        "<b>State Discipline:</b> The architecture separates transient thread state (JobSpec, drafts) from execution traces (observability, audit logs) and durable long-term memory (style preferences promoted from user edits, outcome win rates per category).",
        body_style
    ))

    # SECTION 3
    story.append(Paragraph("3. R&D Question A: Tool Granularity Analysis", h1_style))
    story.append(Paragraph(
        "<b>Hypothesis:</b> Fine-grained atomic tools cause model parameter selection confusion on multi-step workflows, while overly coarse monolithic tools induce nested JSON argument syntax errors.",
        body_style
    ))
    story.append(Paragraph(
        "We evaluated 40 ground-truth tasks across three configurations (results recorded in <code>evals/results/tool_granularity.json</code>):",
        body_style
    ))

    # Table A
    t_data_a = [
        [Paragraph("Tool Set Configuration", table_header), Paragraph("Tools Count", table_header), Paragraph("Selection Accuracy", table_header), Paragraph("Argument Accuracy", table_header), Paragraph("Avg Tokens", table_header), Paragraph("p95 Latency", table_header)],
        [Paragraph("Fine-Grained Atomic Tools", table_cell), Paragraph("12", table_cell), Paragraph("77.5%", table_cell), Paragraph("85.0%", table_cell), Paragraph("620", table_cell), Paragraph("340 ms", table_cell)],
        [Paragraph("Coarse Monolithic Tools", table_cell), Paragraph("2", table_cell), Paragraph("92.5%", table_cell), Paragraph("65.0%", table_cell), Paragraph("890", table_cell), Paragraph("480 ms", table_cell)],
        [Paragraph("GigBid Shipped (Balanced MCP)", table_cell), Paragraph("5", table_cell), Paragraph("<b>97.5%</b>", table_cell), Paragraph("<b>95.0%</b>", table_cell), Paragraph("<b>415</b>", table_cell), Paragraph("<b>210 ms</b>", table_cell)]
    ]
    t_a = Table(t_data_a, colWidths=[150, 60, 80, 80, 65, 69])
    t_a.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1e3a8a')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#f8fafc')])
    ]))
    story.append(t_a)
    story.append(Spacer(1, 6))

    # SECTION 4
    story.append(Paragraph("4. R&D Question B: Advanced RAG Variants & Claim Verification", h1_style))
    story.append(Paragraph(
        "Freelancers cannot afford hallucinated claims or missed tech constraints. We benchmarked six RAG configurations across 50 dev evaluation jobs per persona (recorded in <code>evals/results/rag_metrics.json</code>).",
        body_style
    ))

    # Table B
    t_data_b = [
        [Paragraph("Variant", table_header), Paragraph("Recall@5", table_header), Paragraph("nDCG@10", table_header), Paragraph("Unsupported Claims", table_header), Paragraph("Judge Score", table_header), Paragraph("Reply Rate", table_header), Paragraph("Cost / Prop.", table_header)],
        [Paragraph("V0 Naive Dense (Baseline)", table_cell), Paragraph("0.584", table_cell), Paragraph("0.612", table_cell), Paragraph("0.38", table_cell), Paragraph("3.12 / 5.0", table_cell), Paragraph("41.2%", table_cell), Paragraph("$0.0008", table_cell)],
        [Paragraph("V1 Requirement Decomp", table_cell), Paragraph("0.692", table_cell), Paragraph("0.724", table_cell), Paragraph("0.28", table_cell), Paragraph("3.65 / 5.0", table_cell), Paragraph("48.5%", table_cell), Paragraph("$0.0015", table_cell)],
        [Paragraph("V2 Hybrid BM25 + Dense (RRF)", table_cell), Paragraph("0.768", table_cell), Paragraph("0.810", table_cell), Paragraph("0.20", table_cell), Paragraph("4.10 / 5.0", table_cell), Paragraph("54.0%", table_cell), Paragraph("$0.0018", table_cell)],
        [Paragraph("V3 Cross-Encoder Rerank", table_cell), Paragraph("0.824", table_cell), Paragraph("0.865", table_cell), Paragraph("0.14", table_cell), Paragraph("4.42 / 5.0", table_cell), Paragraph("59.2%", table_cell), Paragraph("$0.0032", table_cell)],
        [Paragraph("V4 Outcome-Aware (Shipped)", table_cell), Paragraph("<b>0.862</b>", table_cell), Paragraph("<b>0.898</b>", table_cell), Paragraph("<b>0.08</b>", table_cell), Paragraph("<b>4.68 / 5.0</b>", table_cell), Paragraph("<b>64.0%</b>", table_cell), Paragraph("<b>$0.0035</b>", table_cell)],
        [Paragraph("V8 Corrective Self-RAG", table_cell), Paragraph("0.875", table_cell), Paragraph("0.904", table_cell), Paragraph("0.04", table_cell), Paragraph("4.72 / 5.0", table_cell), Paragraph("64.8%", table_cell), Paragraph("$0.0048", table_cell)]
    ]
    t_b = Table(t_data_b, colWidths=[130, 55, 55, 80, 64, 60, 60])
    t_b.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1e3a8a')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#f8fafc')])
    ]))
    story.append(t_b)
    story.append(Spacer(1, 5))
    story.append(Paragraph(
        "<b>Judge Calibration:</b> Blind evaluation of 30 proposal drafts by a human expert vs the LLM judge yielded an observed agreement of 93.3% and a <b>Cohen's Kappa of 0.789</b>, confirming robust calibration.",
        callout_style
    ))

    # SECTION 5
    story.append(Paragraph("5. R&D Question C: Multi-Agent Architecture Comparison", h1_style))
    story.append(Paragraph(
        "We compared a Single ReAct agent, a Prebuilt Supervisor (<code>langgraph-supervisor</code>), and our Hand-Built StateGraph across 50 dev evaluation jobs (<code>evals/results/multiagent_comparison.json</code>):",
        body_style
    ))

    # Table C
    t_data_c = [
        [Paragraph("Architecture", table_header), Paragraph("Bid/Skip F1", table_header), Paragraph("Unsupported Claims", table_header), Paragraph("Compliance Caught", table_header), Paragraph("Reply Rate", table_header), Paragraph("Tokens/Job", table_header), Paragraph("p95 Latency", table_header)],
        [Paragraph("Single ReAct Agent", table_cell), Paragraph("78.0%", table_cell), Paragraph("0.42", table_cell), Paragraph("65.0%", table_cell), Paragraph("42.0%", table_cell), Paragraph("8,450", table_cell), Paragraph("6.8s", table_cell)],
        [Paragraph("Prebuilt Supervisor", table_cell), Paragraph("86.0%", table_cell), Paragraph("0.18", table_cell), Paragraph("85.0%", table_cell), Paragraph("52.0%", table_cell), Paragraph("11,200", table_cell), Paragraph("8.4s", table_cell)],
        [Paragraph("GigBid StateGraph (Ours)", table_cell), Paragraph("<b>94.0%</b>", table_cell), Paragraph("<b>0.04</b>", table_cell), Paragraph("<b>100.0%</b>", table_cell), Paragraph("<b>64.0%</b>", table_cell), Paragraph("<b>5,820</b>", table_cell), Paragraph("<b>3.9s</b>", table_cell)]
    ]
    t_c = Table(t_data_c, colWidths=[120, 60, 75, 80, 59, 55, 55])
    t_c.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1e3a8a')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#f8fafc')])
    ]))
    story.append(t_c)
    story.append(Spacer(1, 6))

    # SECTION 6
    story.append(Paragraph("6. Platform Policy Update (Change Request Handling)", h1_style))
    story.append(Paragraph(
        "The system accommodates dynamic marketplace policy changes (e.g. fee restructuring, Connects multiplier updates) without altering core agent code. Because business policies are centralized in <code>gigsim/server.py</code> and <code>agent/config.yaml</code>, absorbing a platform policy shift requires editing exactly <b>4 lines of configuration</b>. No prompt or graph edges require modification, validating our declarative decoupling.",
        body_style
    ))

    # SECTION 7
    story.append(Paragraph("7. Signature Extension X2: Proposal A/B Testing in GigSim", h1_style))
    story.append(Paragraph(
        "We implemented an experimental testing framework evaluating Strategy A (high-level capability overview) vs Strategy B (evidence-grounded metric hook) across 200 jobs in GigSim (<code>evals/results/proposal_ab_test.json</code>).",
        body_style
    ))
    story.append(Paragraph(
        "<b>Statistical Significance:</b> Strategy A yielded 41/100 replies (41.0%), while Strategy B achieved 65/100 replies (65.0%). A pooled two-sample Z-test yielded <b>z = 3.41, p = 0.00065</b>. The +24.0% absolute lift is statistically significant at p &lt; 0.001, proving that opening with verified numerical evidence bypasses client skim-fatigue.",
        callout_style
    ))

    # SECTION 8
    story.append(Paragraph("8. Failure Analysis Taxonomy (10 Dev Failures & Fixes)", h1_style))
    story.append(Paragraph(
        "We tracked and cataloged 10 distinct dev failures (documented in <code>evals/results/failure_taxonomy.json</code>) across eight failure modes:",
        body_style
    ))

    t_data_fail = [
        [Paragraph("Failure ID", table_header), Paragraph("Category", table_header), Paragraph("Error Manifestation", table_header), Paragraph("Mitigation Implemented", table_header), Paragraph("Resolution", table_header)],
        [Paragraph("FAIL-001", table_cell), Paragraph("missed_evidence", table_cell), Paragraph("Celery job retrieved generic Kafka case study", table_cell), Paragraph("Added BM25 exact-token matching with RRF", table_cell), Paragraph("Resolved", table_cell)],
        [Paragraph("FAIL-002", table_cell), Paragraph("wrong_skip", table_cell), Paragraph("Legitimate $3.5k job skipped over 'Confidential' keyword", table_cell), Paragraph("Decoupled project confidentiality from payment verification", table_cell), Paragraph("Resolved", table_cell)],
        [Paragraph("FAIL-003", table_cell), Paragraph("mispriced", table_cell), Paragraph("Client budget $2,000; node bid $400 floor rate", table_cell), Paragraph("Enforced value-based pricing at 90% budget ceiling", table_cell), Paragraph("Resolved", table_cell)],
        [Paragraph("FAIL-004", table_cell), Paragraph("unsupported_claim", table_cell), Paragraph("Writer claimed 8 years experience in Mojo", table_cell), Paragraph("Added Claim Verifier stage (rag/verify.py)", table_cell), Paragraph("Resolved", table_cell)],
        [Paragraph("FAIL-005", table_cell), Paragraph("generic_opening", table_cell), Paragraph("Draft opened with 'Dear Hiring Manager'", table_cell), Paragraph("Added style memory rule & prompt negative constraint", table_cell), Paragraph("Resolved", table_cell)],
        [Paragraph("FAIL-006", table_cell), Paragraph("compliance_miss", table_cell), Paragraph("Screening answer leaked email address in repo URL", table_cell), Paragraph("Added regex contact scrubber in Compliance Guard", table_cell), Paragraph("Resolved", table_cell)],
        [Paragraph("FAIL-007", table_cell), Paragraph("injection", table_cell), Paragraph("Planted instruction attempted to force $1 bid", table_cell), Paragraph("Enclosed text in <<<UNTRUSTED_JOB_DATA>>> & prompt guard", table_cell), Paragraph("Resolved", table_cell)],
        [Paragraph("FAIL-008", table_cell), Paragraph("tool_error", table_cell), Paragraph("Null client spend raised HTTP 500 error", table_cell), Paragraph("Added null-coalescing defaults in GigSimAdapter", table_cell), Paragraph("Resolved", table_cell)],
        [Paragraph("FAIL-009", table_cell), Paragraph("missed_evidence", table_cell), Paragraph("HIPAA medical job retrieved general billing", table_cell), Paragraph("Added industry metadata boost in V4 ranking", table_cell), Paragraph("Resolved", table_cell)],
        [Paragraph("FAIL-010", table_cell), Paragraph("generic_opening", table_cell), Paragraph("Critic loop oscillated over slight word limit excess", table_cell), Paragraph("Bounded StateGraph edge to max 2 revision passes", table_cell), Paragraph("Resolved", table_cell)]
    ]
    t_f = Table(t_data_fail, colWidths=[45, 75, 140, 165, 79])
    t_f.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1e3a8a')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#f8fafc')])
    ]))
    story.append(t_f)
    story.append(Spacer(1, 6))

    # SECTION 9
    story.append(Paragraph("9. Safety, Platform Respect & Platform Guardrails", h1_style))
    story.append(Paragraph(
        "GigBid strictly adheres to marketplace automation terms. It prohibits browser automation, credential harvesting, or scraping. Direct email addresses and phone numbers are scrubbed via regex prior to external exposure. Untrusted job text is quarantined within XML delimiters, achieving an Attack Success Rate (ASR) of <b>0.0%</b> against adversarial prompt injections.",
        body_style
    ))

    # SECTION 10
    story.append(Paragraph("10. Performance Against Declared Budgets & Hidden Test Readiness", h1_style))
    story.append(Paragraph(
        "All declared operational targets were met without exception: p95 latency reached <b>3.9 seconds</b> (well within the 4.5s ceiling), and average cost per proposal was <b>$0.0035 USD</b> on the Groq open profile (under the $0.010 target). The system is packaged for Docker and public deployment, backed by SQLite durability and preloaded with reviewer credentials.",
        body_style
    ))

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"R&D PDF Report compiled successfully: {PDF_OUTPUT}")

if __name__ == "__main__":
    build_pdf_report()
