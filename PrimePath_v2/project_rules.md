# PrimePath LMS - Project Rules

## Tech Stack

- **Framework:** Next.js 15 (App Router)
- **Language:** TypeScript
- **Styling:** Tailwind CSS
- **Database:** Supabase
- **Icons:** Lucide-React
- **Package Manager:** npm

## Architecture

- Multi-tenancy system with academy_id in all tables
- Server-side rendering with Next.js App Router
- Type-safe development with TypeScript
- Component-based UI architecture
- Responsive design with Tailwind CSS utilities
- Service layer pattern for all data access

## Code Architecture (src/ structure)

### Folder Structure

- `src/app` - Next.js App Router pages and API routes
- `src/components` - UI components (layout + feature-specific)
- `src/lib` - Shared utilities and service layer
  - `src/lib/supabaseClient.ts` - Single Supabase client instance
  - `src/lib/services/` - Domain logic and data access functions
- `src/types` - TypeScript type definitions
- `db/` - Database schemas and migrations
- `public/` - Static assets

### Key Patterns

1. **Single Supabase Client**: Only created in `src/lib/supabaseClient.ts`
2. **Service Layer**: All data access goes through service functions in `src/lib/services/`
3. **Type Safety**: TypeScript interfaces match database schemas
4. **Multi-tenancy**: Every query includes `academy_id` for data isolation
5. **Soft Deletes**: Use `deleted_at` timestamp instead of hard deletes

### Import Alias

- Use `@/*` to import from the `src/` folder
- Example: `import { supabase } from '@/lib/supabaseClient'`

## Code Architecture Pattern (v1)

### Data Access Layer
- **Database access lives in:** `src/lib/services/*`
  - Each entity (students, users, classes) gets its own service file
  - Service functions handle all Supabase queries
  - Services export TypeScript interfaces matching database tables
  - All queries include `academy_id` for multi-tenancy

### API Routes
- **Location:** `src/app/api/*`
- **Pattern:** API routes must be "thin"
  - Only handle HTTP concerns (request/response)
  - Always call service-layer functions for business logic
  - Never talk to Supabase directly
  - Return JSON responses with proper error handling

### Dashboard Pages
- **Location:** `src/app/(dashboard)/*`
- **Pattern:**
  - Server components by default (no "use client" unless needed)
  - Fetch data via API routes or directly from services
  - Delegate rendering to UI components
  - Handle loading and error states

### UI Components Organization
- **Layout components:** `src/components/layout/*`
  - Shared layout elements (DashboardShell, navigation, headers)
  - Used across multiple pages
  - No data fetching, only presentational
  
- **Feature components:** `src/components/features/<featureName>/*`
  - Feature-specific UI components (StudentsTable, StudentForm)
  - Receive data via props
  - No direct data fetching
  - Focused on presentation and user interactions

### Adding a New Feature (Example: Classes)
1. **Database:** Add table schema in `db/schema.sql`
2. **Service:** Create `src/lib/services/classes.ts` with CRUD operations
3. **API:** Create `src/app/api/classes/route.ts` calling the service
4. **UI Component:** Create `src/components/features/classes/ClassesTable.tsx`
5. **Page:** Create `src/app/(dashboard)/classes/page.tsx` using the component
6. **Follow existing patterns:** Look at students implementation as reference

## Development Communication Rules

### Plain English Explanations
After every coding iteration or technical step, provide a plain English explanation that covers:
1. **What just happened** - In non-technical terms
2. **Why it matters** - How it affects the user's product
3. **What the user can now do** - Practical outcomes
4. **Next steps** - What comes next in simple terms

### Example Format:
```
## ✅ What Just Happened (Plain English)

**What we did:** Connected your app to the cloud database
**In simple terms:** Like plugging your app into a filing cabinet in the cloud
**What you can do now:** Store and retrieve student data permanently
**Next step:** Build the form to add students
```

### Key Principles:
- Avoid technical jargon unless necessary
- Use analogies to explain complex concepts
- Focus on practical outcomes, not technical details
- Always relate back to the user's business needs (running an academy)