# Vertical Split Fix for Half-Page View

## Issue Fixed
The half-page view was splitting the PDF horizontally (showing top/bottom halves) instead of vertically (left/right columns), which is what's needed for exam papers with two-column layouts.

## Changes Made

### 1. **Changed Split Direction**
- **Before**: Horizontal split (top/bottom halves)
- **After**: Vertical split (left/right columns)

### 2. **Canvas Dimensions**
- **Before**: `canvas.width = full width`, `canvas.height = half height`
- **After**: `canvas.width = half width`, `canvas.height = full height`

### 3. **Drawing Logic**
- **Before**: Used `sourceY` to select top or bottom half
- **After**: Uses `sourceX` to select left or right column

### 4. **Button Labels**
- **Before**: "Show Half Page" → "Show Bottom Half" → "Show Full Page"
- **After**: "Show Left Column" → "Show Right Column" → "Show Full Page"

### 5. **Fit to Width Enhancement**
- Added logic to properly scale half-page view when using "Fit Width"
- In half-page mode, scale is doubled to fill the container width

## How It Works Now

1. **First Click** - "Show Left Column":
   - Displays only the left half of the PDF page
   - Zooms in 1.5x for better readability
   
2. **Second Click** - "Show Right Column":
   - Switches to show only the right half
   - Maintains the zoom level
   
3. **Third Click** - "Show Full Page":
   - Returns to normal full-page view
   - Resets zoom to original level

## Benefits

- Perfect for exam papers with two-column layouts
- Each column fills the entire PDF viewer width
- Much easier to read questions and answers
- Smooth transitions between columns
- Works with all zoom controls

## Testing

1. Click "Show Left Column" to view the left side of the exam
2. Click "Show Right Column" to switch to the right side
3. Click "Show Full Page" to return to normal view
4. Try "Fit Width" while in column view for optimal sizing