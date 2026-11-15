# GigBid Portfolio MCP Server

Official Model Context Protocol (MCP) server for freelancers and technical contractors. Exposes verified case studies, past proposals, and skill inventories through standardized read-only MCP tools, resources, and prompt templates.

## 1. Quick Installation & Running

### Using `uvx` (Instant execution):
```bash
uvx gigbid-portfolio-mcp
```

### Using `pip` & Python:
```bash
pip install gigbid-portfolio-mcp
python -m mcp_servers.portfolio.server
```

### Connecting to Claude Desktop or Cursor:
Add to your `claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "gigbid-portfolio": {
      "command": "uvx",
      "args": ["gigbid-portfolio-mcp"]
    }
  }
}
```

## 2. Exposed Tools & Resources
- **Tools**:
  - `search_evidence(requirement, k, filters)`: Semantic search over case studies and past proposals.
  - `get_case_study(id)`: Fetch complete architectural problem, approach, and verified metrics.
  - `list_skills(persona_id)`: Enumerate verified competencies and floor rates.
- **Resources**:
  - `portfolio://case/{id}`
  - `portfolio://proposal/{id}`
- **Prompt Templates**:
  - `screening_question_answer`: Ground answers to client screening questions in portfolio evidence.
