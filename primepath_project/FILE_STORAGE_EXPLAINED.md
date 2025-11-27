# How PrimePath Stores Files

## Database (db.sqlite3)
Stores only **references** to files:
```
Exam Table:
- id: 123
- name: "Grade 5 Placement Test"
- pdf_file: "exams/pdfs/grade5_test_2025.pdf"  ← Just the path!
- timer_minutes: 60
```

## Actual File Storage
```
primepath_project/
├── db.sqlite3           ← Database (text data only)
├── media/              ← All uploaded files go here
│   └── exams/
│       ├── pdfs/       ← PDF files
│       │   ├── grade5_test_2025.pdf
│       │   └── grade6_test_2025.pdf
│       └── audio/      ← Audio files
│           ├── listening_part1.mp3
│           └── listening_part2.mp3
```

## Why This Way?
1. **Performance**: Database stays fast (only text)
2. **Flexibility**: Easy to backup/move files
3. **Web Standard**: How most web apps work

## To View Your Database:
1. Download "DB Browser for SQLite" (free)
2. Open db.sqlite3 file
3. You'll see all your data in tables

## File Size Limits:
- PDFs: Max 10MB (configurable)
- Audio: Max 50MB (configurable)
- Database: Can handle millions of records