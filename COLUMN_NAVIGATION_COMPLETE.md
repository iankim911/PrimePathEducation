# Column-Based Navigation Implementation

## Overview
The PDF viewer now uses column-based navigation as the DEFAULT view, treating each PDF page as two separate viewing pages (left and right columns).

## Key Changes

### 1. **Virtual Page System**
- Each PDF page is split into 2 virtual pages
- PDF with 10 pages → 20 virtual pages in navigation
- Page 1 = PDF Page 1 Left Column
- Page 2 = PDF Page 1 Right Column
- Page 3 = PDF Page 2 Left Column
- And so on...

### 2. **Navigation Flow**
```
Page 1 (P1 Left) → Page 2 (P1 Right) → Page 3 (P2 Left) → Page 4 (P2 Right) → ...
```

### 3. **Page Counter Updates**
- Shows total virtual pages (actual PDF pages × 2)
- Input accepts virtual page numbers
- Column indicator shows "(Left Column)" or "(Right Column)"

### 4. **Default Behavior**
- **Column view is DEFAULT** - no button click needed
- "Show Full Page" button switches to traditional full-page view
- All zoom controls work with column view

### 5. **Mathematical Mapping**
```javascript
actualPageNum = Math.ceil(virtualPageNum / 2)
isLeftColumn = (virtualPageNum % 2) === 1
```

## User Experience

1. **On Load**: 
   - Shows Page 1 (left column of PDF page 1)
   - Auto-fits width for optimal reading
   - Page counter shows "1 of 20" (for 10-page PDF)

2. **Navigation**:
   - Next button: Goes to right column, then next page's left column
   - Previous button: Reverse navigation
   - Direct page input: Jump to any virtual page

3. **View Toggle**:
   - "Show Full Page": Switches to traditional view
   - "Show Column View": Returns to column-based navigation

## Benefits

- **Natural Reading Flow**: Matches how students read two-column exams
- **Better Readability**: Each column fills the viewer width
- **Intuitive Navigation**: Next/Previous follows reading order
- **Flexible**: Can switch to full page when needed

## Testing Guide

1. Load a PDF with two-column layout
2. Verify page 1 shows left column only
3. Click Next → should show right column (page 2)
4. Click Next → should show left column of PDF page 2 (page 3)
5. Try direct page navigation (e.g., enter "5" for page 3 left column)
6. Test "Show Full Page" toggle

The implementation ensures a seamless reading experience for two-column exam papers with natural left-to-right, top-to-bottom navigation.