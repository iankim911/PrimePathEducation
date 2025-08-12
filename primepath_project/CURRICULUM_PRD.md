# PrimePath Curriculum Structure - Product Requirements Document

## Executive Summary
PrimePath Assessment Platform uses a hierarchical curriculum structure with 4 main programs, each containing 4 subprograms, totaling 44 distinct curriculum levels.

## Curriculum Hierarchy

### Structure Overview
```
Program (4 total)
  └── SubProgram (4 per program)
      └── Level (3 per subprogram, except PINNACLE with 2)
```

## Complete Curriculum Specification

### PRIME CORE (12 Levels)
| SubProgram | Levels | Full Names |
|------------|--------|------------|
| Phonics | 3 | CORE Phonics Level 1, CORE Phonics Level 2, CORE Phonics Level 3 |
| Sigma | 3 | CORE Sigma Level 1, CORE Sigma Level 2, CORE Sigma Level 3 |
| Elite | 3 | CORE Elite Level 1, CORE Elite Level 2, CORE Elite Level 3 |
| Pro | 3 | CORE Pro Level 1, CORE Pro Level 2, CORE Pro Level 3 |

### PRIME ASCENT (12 Levels)
| SubProgram | Levels | Full Names |
|------------|--------|------------|
| Nova | 3 | ASCENT Nova Level 1, ASCENT Nova Level 2, ASCENT Nova Level 3 |
| Drive | 3 | ASCENT Drive Level 1, ASCENT Drive Level 2, ASCENT Drive Level 3 |
| [TBD] | 3 | ASCENT [TBD] Level 1, ASCENT [TBD] Level 2, ASCENT [TBD] Level 3 |
| Pro | 3 | ASCENT Pro Level 1, ASCENT Pro Level 2, ASCENT Pro Level 3 |

*Note: One ASCENT subprogram name missing from original specification*

### PRIME EDGE (12 Levels)
| SubProgram | Levels | Full Names |
|------------|--------|------------|
| Spark | 3 | EDGE Spark Level 1, EDGE Spark Level 2, EDGE Spark Level 3 |
| Rise | 3 | EDGE Rise Level 1, EDGE Rise Level 2, EDGE Rise Level 3 |
| Pursuit | 3 | EDGE Pursuit Level 1, EDGE Pursuit Level 2, EDGE Pursuit Level 3 |
| Pro | 3 | EDGE Pro Level 1, EDGE Pro Level 2, EDGE Pro Level 3 |

### PRIME PINNACLE (8 Levels)
| SubProgram | Levels | Full Names |
|------------|--------|------------|
| Vision | 2 | PINNACLE Vision Level 1, PINNACLE Vision Level 2 |
| Endeavor | 2 | PINNACLE Endeavor Level 1, PINNACLE Endeavor Level 2 |
| Success | 2 | PINNACLE Success Level 1, PINNACLE Success Level 2 |
| Pro | 2 | PINNACLE Pro Level 1, PINNACLE Pro Level 2 |

## Naming Conventions

### Format
`[PROGRAM] [SubProgram] Level [Number]`

### Rules
1. **Always include program prefix**: "CORE Phonics" not just "Phonics"
2. **Consistent capitalization**: PROGRAM in caps, SubProgram in title case
3. **Level numbering**: Arabic numerals (1, 2, 3) not Roman numerals
4. **No standalone subprogram names**: Must always include program prefix

### Examples
✅ Correct: "CORE Phonics Level 1"
❌ Wrong: "Phonics Level 1"

✅ Correct: "PINNACLE Vision Level 1"
❌ Wrong: "PINNACLE Level 1"

## Business Rules

### Level Progression
1. **CORE, ASCENT, EDGE**: 3 levels per subprogram (beginner, intermediate, advanced)
2. **PINNACLE**: 2 levels per subprogram (advanced only - this is the mastery tier)

### Common Elements
- Every program has a "Pro" track as its highest/final subprogram
- Programs represent increasing difficulty: CORE → ASCENT → EDGE → PINNACLE
- Total of 44 unique curriculum levels

### Database Implementation
- Program: Parent entity
- SubProgram: Child of Program
- Level: Associated with SubProgram
- Each level can map to multiple exam versions (e.g., version a, b, c)

## UI Display Requirements

### Exam Mapping Page
- Display full names: "CORE Phonics Level 1" not "PHONICS Level 1"
- Group by Program (CORE, ASCENT, EDGE, PINNACLE)
- Show SubProgram and Level clearly
- Each level can map to up to 5 exam versions

### Placement Rules Page
- Use complete naming convention
- Filter out any test/QA data (prefixed with [INACTIVE] or containing "Test")

## Quality Assurance

### Data Validation
- No orphaned levels without subprograms
- No subprograms without programs
- Enforce naming convention at data entry
- Filter test data from production views

### Known Issues to Prevent
1. Truncated names showing only subprogram (e.g., "PHONICS" instead of "CORE Phonics")
2. Missing subprograms (all programs should have 4 subprograms)
3. Test data appearing in production (filter [INACTIVE] and "Test" entries)

## Summary Statistics
- **Total Programs**: 4
- **Total SubPrograms**: 16 (4 per program)
- **Total Levels**: 44
  - CORE: 12 levels
  - ASCENT: 12 levels
  - EDGE: 12 levels
  - PINNACLE: 8 levels

---
*Last Updated: August 12, 2025*
*Version: 1.0*