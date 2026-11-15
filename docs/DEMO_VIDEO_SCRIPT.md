# GigBid 3-Minute Demo Video Walkthrough & Script

**Student**: Areeba Javed (Roll No: 23I-0570)  
**Duration**: Exactly 3 minutes (180 seconds)  
**Live Deployed URL**: [https://gigbid-rx4j.onrender.com](https://gigbid-rx4j.onrender.com)  
**Deliverable**: Public Video Link for Google Classroom Submission

---

### [0:00 – 0:30] Scene 1: Problem & System Onboarding
- **Visual**: Show browser at `https://gigbid-rx4j.onrender.com` with Reviewer mode preloaded (`reviewer@gigbid.ai`).
- **Narration**: *"Hi, I am Areeba Javed (Roll No: 23I-0570). Welcome to GigBid, an autonomous multi-agent freelancer copilot built with LangGraph, Model Context Protocol, and outcome-aware RAG. When freelancers scan platforms like Upwork, they waste hours parsing posts, burning Connects, and dodging scams. GigBid automates discovery, assessment, and drafting, while keeping the human in control of every single external action."*
- **Action**: Highlight the Reviewer Mode badge, the 120 available Connects, and the persona selector set to Alex Morgan (Senior AI/ML Engineer).

---

### [0:30 – 1:15] Scene 2: Discovery to Approved Proposal
- **Visual**: Point to the first recommended job (*"Fine-tune Llama 3 on Domain Dataset"* with 92% fit). Click **Launch Copilot**.
- **Narration**: *"Watch the live Agent Run stream. In parallel, Job Analyst, Risk Assessor, and Fit Matcher evaluate the job post in under 2 seconds. The Decision node confirms a 92% fit, passing the job to Pricing and the Proposal Writer. The Claim Verifier audits every sentence against our verified portfolio case studies before the Critic checks grounding."*
- **Visual**: LangGraph hits the `approval_gate` interrupt. The Proposal Studio modal pops up.
- **Action**: Hover over the green underlined cover letter text to demonstrate **Evidence on Hover**, showing the verified case study tooltip.
- **Visual**: Point out the dry-run submission preview ($1,800 bid, 8 Connects, Will Succeed).
- **Action**: Click **Approve & Submit to Marketplace**. Show the confirmation notification.

---

### [1:15 – 1:50] Scene 3: Scam Caught & Prompt Injection Defeated
- **Visual**: Return to Inbox and click the **"Auto-Skipped / Scams"** filter button.
- **Narration**: *"Now let's test adversarial safety. Prohibited scam jobs attempting to solicit unpaid work or off-platform communication on Telegram/WhatsApp are automatically flagged by our Risk Assessor with a high risk score, routing them directly to Auto-Skip to protect our Connects wallet."*
- **Visual**: Click **Inspect Spec** on a flagged job. Show the Risk Report with 88% risk score and policy violation tags.
- **Narration**: *"Even when a job post contains planted prompt injections attempting to override system directives, our XML-delimited parser and prompt guard quarantine the attack with zero instruction leakage."*

---

### [1:50 – 2:30] Scene 4: Client Reply & Calendar Hold
- **Visual**: Navigate to **Client Messages** on the left sidebar. Show incoming message from client Sarah Jenkins asking for a technical sync.
- **Narration**: *"When an interested client replies, our Conversation Graph's Client Liaison classifies the intent as an interview request. It queries the Workspace MCP server for free calendar slots and automatically drafts a professional reply offering Thursday at 2:00 PM EST or Friday at 10:00 AM EST."*
- **Action**: Click **Approve & Send**. Show the tentative calendar hold created.

---

### [2:30 – 3:00] Scene 5: Pipeline, Memory, & Wrap-Up
- **Visual**: Click **Pipeline Board** (Kanban showing proposals across submitted, viewed, replied, hired).
- **Visual**: Click **Settings & Memory** to show learned Style Memory rules and the interactive delete button.
- **Narration**: *"Every user edit updates our durable style memory store. GigBid is fully observable, deployed live on Render, and ready for evaluation. Thank you!"*
