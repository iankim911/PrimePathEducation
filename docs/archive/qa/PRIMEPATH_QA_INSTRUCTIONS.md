# PrimePath Level Test - QA Testing Instructions

## 🌐 Language Note
**Important**: This testing platform is currently in English for QA purposes. The live production version will be fully translated to Korean. Please test functionality rather than language during this QA phase.

## Overview
This document guides teachers through Quality Assurance testing of the PrimePath Level Test web application. The testing involves two main parts: uploading test materials and conducting student test sessions.

---

## 📋 Pre-Testing Setup

### Required Materials
- [ ] Monthly test PDF documents (scanned)
- [ ] Answer keys for the test
- [ ] Level mapping logic/rules document
- [ ] Word document or Google Docs for taking notes
- [ ] Screenshot tool ready (Snipping Tool on Windows, Screenshot on Mac)

### Access Information
- **URL**: [Will be provided by administrator]
- **Login Credentials**: [Will be provided by administrator]

---

## Part 1: Test Upload & Configuration

### Step 1: Upload Test Materials

1. **Navigate to Create Exam**
   - Click "Create Exam" from the main menu
   - Or go directly to `/placement/create-exam/`

2. **Fill Basic Information**
   - Enter Exam Name (e.g., "2025 January Monthly Test")
   - Add Description (optional)
   - Set Time Limit (in minutes)
   - Toggle "Is Passing Mandatory" if required

3. **Upload PDF**
   - Click "Choose File" under PDF Document
   - Select your scanned test PDF
   - Wait for upload confirmation
   - **Screenshot**: Take a screenshot of the PDF preview

### Step 2: Configure Questions & Answers

1. **Add Questions**
   - For each question in the test:
     - Enter Question Number
     - Select Question Type (Multiple Choice, Short Answer, etc.)
     - Enter Points value
     - Enter Correct Answer
   - **Screenshot**: Capture the questions list after adding 5-10 questions

2. **Set Answer Keys**
   - Review all answers are correctly entered
   - Verify point values match the actual test

### Step 3: Configure Level Mapping

1. **Set Placement Rules**
   - Define score ranges for each level
   - Example:
     - 90-100%: Advanced
     - 70-89%: Intermediate
     - 50-69%: Elementary
     - Below 50%: Beginner

2. **Save Configuration**
   - Click "Save Exam"
   - Note the confirmation message
   - **Screenshot**: Capture the success message

### ⚠️ Document Any Issues
- If upload fails, note the error message
- If PDF doesn't display correctly, capture the issue
- Note any confusing UI elements

---

## Part 2: Student Test Sessions

### Step 1: Start Test Session (Repeat 3-5 times)

1. **Navigate to Start Test**
   - Go to `/placement/start-test/`
   - Or click "Start Test" from main menu

2. **Enter Mock Student Details**
   - **Use different test scenarios**:
     - Test 1: High-performing student (aim for 90%+ score)
     - Test 2: Average student (aim for 70% score)
     - Test 3: Struggling student (aim for 40% score)
     - Test 4: Edge cases (timeout, partial completion)
     - Test 5: Technical issues test (refresh page mid-test)

3. **Fill Student Information**
   ```
   Name: Test Student [1-5]
   Email: test[1-5]@primepath.edu
   Phone: 555-0100 (increment for each test)
   Current Level: [Vary between tests]
   ```

### Step 2: Complete Test

1. **During the Test**
   - Answer questions according to your test scenario
   - Test all question types
   - Test navigation (Previous/Next buttons)
   - Test question navigation buttons (1-20)
   - Try the PDF viewer controls (zoom, page navigation)
   - Test audio players if present
   - **Screenshot**: Capture any unusual behavior

2. **Monitor Timer**
   - Note if timer displays correctly
   - Test what happens when time expires
   - **Screenshot**: Capture timer at different stages

3. **Submit Test**
   - Click "Submit Test"
   - Review the results page
   - **Screenshot**: Capture the results/level assignment

### Step 3: Document Each Session

For each test session, record:
- Student details used
- Start time
- Any errors encountered
- Features that worked well
- Features that didn't work
- Confusing elements
- End result (assigned level)

---

## 🐛 Capturing Technical Issues

### Opening Developer Console

#### Windows (Chrome/Edge)
1. Press `F12` or `Ctrl + Shift + I`
2. Click "Console" tab
3. Look for red error messages
4. **Screenshot**: Capture both the webpage AND console

#### Mac (Chrome/Safari)
1. Press `Cmd + Option + I` (Chrome) or `Cmd + Option + C` (Safari)
2. Click "Console" tab
3. Look for red error messages
4. **Screenshot**: Press `Cmd + Shift + 4` to capture both windows

### What to Capture
- ❌ Red error messages in console
- ⚠️ Yellow warning messages
- 🔄 Network errors (if page doesn't load)
- 📸 Visual glitches or layout issues

---

## 📝 Notes Template

Use this format for your Word document:

```
TEST SESSION #[1-5]
Date: [Date]
Time: [Start - End]
Tester: [Your Name]

PART 1: UPLOAD
- Upload Success: Yes/No
- Issues: [List any problems]
- Screenshots: [List screenshot numbers]

PART 2: STUDENT TEST
- Test Scenario: [High/Average/Low performer]
- Student Details: [Name, Email used]
- Issues Encountered:
  1. [Issue description + screenshot #]
  2. [Issue description + screenshot #]
- Working Features:
  1. [Feature that worked well]
  2. [Feature that worked well]
- Suggestions:
  1. [Improvement idea]
  2. [Improvement idea]

CONSOLE ERRORS: [If any]
- Error 1: [Copy error text + screenshot #]
- Error 2: [Copy error text + screenshot #]
```

---

## 🎯 Focus Areas for Testing

### Critical Functions
- [ ] PDF displays correctly
- [ ] Questions load in order
- [ ] Answer selection saves
- [ ] Navigation between questions works
- [ ] Timer counts down properly
- [ ] Submit function works
- [ ] Results calculate correctly
- [ ] Level assignment matches rules

### Edge Cases to Test
- [ ] Refresh page during test
- [ ] Use browser back button
- [ ] Submit with unanswered questions
- [ ] Let timer expire
- [ ] Test on different browsers
- [ ] Test on mobile device (if applicable)

---

## 📤 Submitting QA Report

1. **Compile all screenshots** into the Word document
2. **Organize by test session** (Session 1, Session 2, etc.)
3. **Highlight critical issues** in red
4. **Add summary** at the beginning:
   - Total tests conducted
   - Critical issues found
   - Minor issues found
   - Suggestions for improvement

5. **Send report to**: [Administrator email]

---

## ⚡ Quick Troubleshooting

| Problem | Solution |
|---------|----------|
| Page won't load | Clear browser cache (Ctrl+Shift+Del) |
| Can't see PDF | Try different browser |
| Test won't submit | Check all required fields filled |
| Timer not showing | Refresh page and try again |
| Lost progress | Note which question, take screenshot |

---

## 📞 Support

If you encounter blocking issues:
- **Technical Support**: [Contact information]
- **Emergency**: Take screenshot and continue with next test

---

**Thank you for helping improve PrimePath Level Test!**

*Document Version: 1.0*  
*Date: August 2025*