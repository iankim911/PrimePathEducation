# MCP Best Practices for PrimePath Project

## Your Context
- **Role**: Non-technical founder building MVP
- **Goal**: Create proof-of-concept for developer handoff
- **Project**: Educational platform with Test Management module
- **Stack**: Next.js, TypeScript, SQLite, Prisma

## Recommended MCP Configuration

### 1. Current Setup (Good Foundation)
```json
{
  "mcpServers": {
    "vscode": {
      "command": "node",
      "args": ["/Users/ian/.vscode/extensions/anthropic.claude-code-1.0.70/mcp/dist/index.js"],
      "env": {}
    },
    "puppeteer": {
      "command": "npx",
      "args": ["-y", "puppeteer-mcp-server@latest"],
      "env": {}
    }
  }
}
```

### 2. Why This Setup Makes Sense for You

#### VS Code MCP Server ✅
**Purpose**: Real-time code quality checks
- Catches TypeScript errors before they break your app
- Identifies unused imports and variables
- Ensures code consistency

**Best Practice**: Use `mcp__ide__getDiagnostics` after major changes to catch issues early

#### Puppeteer MCP Server ✅  
**Purpose**: Automated testing without manual clicking
- Tests your Test Management module features
- Verifies PDF upload functionality works
- Ensures forms submit correctly
- Checks navigation doesn't break

**Best Practice**: Run Puppeteer tests after implementing new features, especially:
- After adding new forms or buttons
- After changing navigation
- Before git commits

### 3. Recommended Workflow

#### For Feature Development:
1. **Build Feature** → Make the changes
2. **Check Diagnostics** → `mcp__ide__getDiagnostics` to catch TypeScript errors
3. **Test with Puppeteer** → Automated UI testing
4. **Manual Verification** → Quick check at localhost:3000
5. **Git Commit** → Save working state

#### For Testing Test Management Module:
```javascript
// Example Puppeteer test flow
1. Navigate to /exams/create
2. Upload a PDF file
3. Add audio files
4. Configure questions
5. Save exam
6. Verify it appears in /exams list
```

### 4. What You DON'T Need (Avoiding Over-Engineering)

❌ **Database MCP servers** - SQLite with Prisma is simple enough
❌ **Cloud/AWS MCP servers** - You're building locally for MVP
❌ **Complex monitoring** - Keep it simple for proof-of-concept
❌ **Multiple environment configs** - Just development for now

### 5. Security Best Practices for Your Setup

✅ **DO**:
- Keep MCP config in ~/.claude/ide/ (not in project repo)
- Use Puppeteer only on localhost:3000
- Let Claude handle file operations through built-in tools

⚠️ **AVOID**:
- Don't add production credentials to MCP config
- Don't expose real student data during testing
- Don't commit MCP config to git

### 6. Practical Tips for Non-Technical Founder

1. **When MCP helps most**:
   - Finding TypeScript errors you can't see
   - Testing multi-step workflows (like exam creation)
   - Checking if recent changes broke anything

2. **When to skip MCP**:
   - Simple text changes
   - CSS/styling updates
   - Adding static content

3. **If MCP fails**:
   - Usually just needs restart: Close and reopen Claude Code
   - Check if VS Code is running
   - Puppeteer may need Chrome/Chromium installed

### 7. Future Considerations

When you hand off to developers, they might add:
- **GitHub MCP** - For automated PR creation
- **Database MCP** - For complex migrations
- **Monitoring MCP** - For production error tracking

But for MVP development, your current setup is ideal.

## Quick Reference Commands

```bash
# Check if MCP is working
mcp__ide__getDiagnostics

# Test with Puppeteer (example)
mcp__puppeteer__navigate to http://localhost:3000
mcp__puppeteer__screenshot

# When to restart MCP
# If you see "MCP server failed" - restart Claude Code
```

## Summary

Your MCP setup is **correctly configured** for MVP development. The VS Code integration catches code issues, and Puppeteer enables automated testing - exactly what you need for building and validating features before developer handoff.

Keep it simple, test the important paths, and don't over-engineer the tooling.