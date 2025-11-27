# PrimePath Agent Workflow Guide

## How to Work with Your Configured Agent

### Starting a New Session

1. **Always start with context**:
   ```
   "I need to work on [specific feature/issue] for my PrimePath educational platform. 
   Please read the CLAUDE.md file first to understand the project."
   ```

2. **Be specific about the problem**:
   ```
   "The dropdown menus in the Students page have invisible text. 
   Users can't read the options in the Grade and Status filters."
   ```

### Agent Communication Pattern

#### ✅ **Good Requests**
- "Fix the dropdown text visibility while keeping all existing features working"
- "Add a new vocabulary test feature that matches our monochromatic design"
- "Show me what the button will look like before you implement it"

#### ❌ **Avoid These**
- "Make it better" (too vague)
- "Add authentication" (too complex for single session)
- "Rewrite everything" (breaks safety rules)

### Expected Agent Response Pattern

Your agent should always:

1. **Acknowledge the request**
   - "I'll fix the dropdown text visibility issue"
   - "I understand you need dark, readable text in all dropdown components"

2. **SCAN THE CODEBASE FIRST**
   - "Let me scan for all Select components across the entire platform"
   - "I found dropdown issues in: Students page, Add Student modal, Add Class modal, Enrollment modal"

3. **Explain the comprehensive approach**
   - "This is a systemic issue affecting all Select components"
   - "I'll apply the standard fix pattern to all instances: bg-white + text-gray-900"

4. **Show comprehensive fix plan**
   - "I'll fix all 8 Select components found across 4 files"
   - "Each will get: SelectContent className='bg-white' and SelectItem className='text-gray-900'"
   - "This ensures consistent dropdown readability across your entire platform"

5. **Implement systematically**
   - Fix one file at a time
   - Test each component after changes
   - Verify all dropdowns are readable
   - Document what was changed

6. **Verify comprehensive completion**
   - "All dropdown text across the platform is now clearly visible"
   - "Please test: Students filters, Add Student form, Add Class form, Enrollment form"

### Failsafe Mechanisms

#### **Before Every Change**
- ✅ Agent reads current code
- ✅ Agent explains planned changes
- ✅ Agent identifies potential risks
- ✅ Agent asks for confirmation if major changes needed

#### **During Implementation**
- ✅ Make one small change at a time
- ✅ Test immediately after each change
- ✅ Preserve all existing functionality
- ✅ Follow established code patterns

#### **After Changes**
- ✅ Verify visual appearance
- ✅ Test all related functionality
- ✅ Confirm nothing else broke
- ✅ Document what was changed and why

### Quality Checkpoints

#### **Visual Verification**
- Text is dark and readable
- Buttons are clearly clickable
- Colors match monochromatic scheme
- Mobile responsive design maintained

#### **Functional Verification**
- All CRUD operations work
- Search and filters function correctly
- Navigation works properly
- No JavaScript errors in console

#### **Code Quality**
- TypeScript types are correct
- Components follow existing patterns
- Code is commented appropriately
- No hard-coded values (use design system)

### Emergency Procedures

#### **If Something Breaks**
1. **Don't panic** - everything is in git
2. **Tell the agent immediately**: "The [feature] stopped working"
3. **Agent should**: Identify the issue and fix it
4. **If agent can't fix**: Use git to revert changes

#### **If Agent Suggests Major Changes**
1. **Stop and ask for clarification**
2. **Ask agent to explain risks**
3. **Request smaller incremental approach**
4. **Consider if it's worth it for MVP**

### Session Management

#### **One Goal Per Session**
- ✅ "Fix dropdown text visibility"
- ✅ "Add vocabulary test interface"
- ❌ "Fix dropdowns and add tests and improve performance"

#### **Use /clear When**
- Starting a completely different feature
- Previous conversation got confusing
- Agent seems to have wrong context

### Documentation for Developer Handoff

Your agent should automatically:
- Comment complex code decisions
- Explain business logic reasoning
- Document any technical debt created
- Note areas needing professional review

### Success Metrics

#### **Good Session Outcome**
- Specific problem solved
- All existing features still work
- Code is readable and maintainable
- Change is documented

#### **Red Flags**
- Agent wants to "rewrite everything"
- Multiple files changed at once
- Existing features stop working
- Agent can't explain the changes

### Example Perfect Workflow

```
You: "The Grade filter dropdown text is invisible. Fix this."

Agent: "I can see the issue. The SelectItem components are using light CSS variables that make text nearly transparent. I'll add explicit text-gray-900 classes to make dropdown items readable while maintaining your monochromatic design. This will require small changes to the Students page Select components."

You: "Sounds good, do it."

Agent: [Makes focused changes to dropdown styling]

Agent: "Fixed! The dropdown items now use dark text (text-gray-900) and should be clearly readable. Please test the Grade and Status filters to confirm the text is visible."

You: [Tests and confirms] "Perfect, thanks!"
```

This workflow ensures safe, predictable development while building your educational platform MVP.