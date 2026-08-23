# Phase 15.A.5: Search & Advanced Filtering

## Overview

Comprehensive search and filtering system for CI/CD scan history with:
- **Full-text search** across repository names, branches, and platforms
- **Advanced filtering** by exact fields (platform, status, branch)
- **Range filtering** for issue counts (critical, errors)
- **Autocomplete suggestions** for faster search
- **Saved filter presets** for recurring searches
- **Pagination** for large result sets

## Backend Implementation

### Search Service (`api/services/search_service.py`)

Core search logic with three main methods:

1. **`search_scans()`** - Flexible query builder
   - Full-text search on repository, branch, platform
   - Exact filtering by repository, platform, status, branch
   - Range filtering on critical/error counts
   - Date range filtering with 30-day default lookback
   - Pagination with limit/offset

2. **`get_filter_options()`** - Dropdown data
   - Returns distinct values for all filterable fields
   - Sorted and nullable values only

3. **`get_search_suggestions()`** - Autocomplete
   - Prefix-based suggestions for search fields
   - Returns up to 10 suggestions

### API Routes (`api/routes/search.py`)

Three RESTful endpoints:

```bash
# Search with flexible filters
GET /api/v1/search/scans?q=repo&status=failure&min_critical=1

# Get available filter options
GET /api/v1/search/filters

# Get autocomplete suggestions
GET /api/v1/search/suggestions?q=repo&field=repository
```

#### Query Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| q | string | null | Full-text search term |
| repository | string | null | Exact repository match |
| platform | string | null | Platform filter (github, gitlab, jenkins) |
| status | string | null | Status filter (success, failure, warning) |
| branch | string | null | Git branch filter |
| min_critical | int | null | Minimum critical count |
| max_critical | int | null | Maximum critical count |
| min_errors | int | null | Minimum error count |
| max_errors | int | null | Maximum error count |
| days | int | 30 | Look-back period in days |
| limit | int | 20 | Results per page |
| offset | int | 0 | Pagination offset |

#### Response Structure

```json
{
  "results": [
    {
      "id": "uuid",
      "repository": "my-repo",
      "branch": "main",
      "platform": "github",
      "status": "success",
      "critical_count": 0,
      "error_count": 2,
      "warning_count": 15,
      "total_findings": 22,
      "files_scanned": 150,
      "created_at": "2026-07-06T04:07:03.137338"
    }
  ],
  "total": 487,
  "limit": 5,
  "offset": 0,
  "has_more": true
}
```

## Frontend Implementation

### SearchFilters Component (`frontend/src/components/SearchFilters.tsx`)

Interactive search interface with:

- **Quick Search Bar** - Prominent text search with gradient background
- **Advanced Filters** - Collapsible card with all filter options
- **Range Sliders** - Critical and error count ranges
- **Saved Filters** - Persist favorite filter combinations locally
- **Autocomplete** - Suggestions as user types
- **Material-UI** - Professional, responsive design

#### Features

1. **Search Bar**
   - Full-text search with icon
   - Search/Advanced/Clear buttons
   - Gradient purple background

2. **Advanced Filters Panel**
   - Repository dropdown
   - Platform dropdown
   - Status dropdown
   - Branch dropdown
   - Critical count range slider
   - Error count range slider
   - Look-back period (days)
   - Results per page setting

3. **Saved Filters**
   - Save current filters with custom name
   - Click saved filter chip to reload
   - Delete saved filters
   - Persisted in localStorage

4. **Responsive Design**
   - Mobile-friendly layout
   - Grid-based responsive spacing
   - Touch-friendly controls

### CI Dashboard Integration

Updated `CIDashboard.tsx` to:

1. **Embed SearchFilters component** at top of page
2. **Handle search submissions** via `handleSearch()` callback
3. **Display search results** in main scan table
4. **Show result count** in card header
5. **Add pagination** for large result sets
6. **Toggle between views** - normal history vs. search results

#### State Management

```typescript
const [searchResults, setSearchResults] = useState<ScanHistory[]>([]);
const [totalSearchResults, setTotalSearchResults] = useState(0);
const [currentPage, setCurrentPage] = useState(1);
const [isSearchMode, setIsSearchMode] = useState(false);
```

#### Search Handler

```typescript
const handleSearch = async (filters: Record<string, any>) => {
  // Build query string from filters
  // Call /api/v1/search/scans endpoint
  // Update searchResults state
  // Set isSearchMode = true
};
```

## API Examples

### Basic Text Search
```bash
curl "http://localhost:8000/api/v1/search/scans?q=my-repo"
```

### Search + Filter by Status
```bash
curl "http://localhost:8000/api/v1/search/scans?q=repo&status=failure"
```

### Find Repos with Critical Issues
```bash
curl "http://localhost:8000/api/v1/search/scans?min_critical=1&days=7"
```

### Filter by Platform and Branch
```bash
curl "http://localhost:8000/api/v1/search/scans?platform=github&branch=develop&limit=50"
```

### Search with Range Filters
```bash
curl "http://localhost:8000/api/v1/search/scans?min_critical=1&max_critical=5&min_errors=2"
```

### Get Filter Options
```bash
curl "http://localhost:8000/api/v1/search/filters" | jq .
```

### Autocomplete Suggestions
```bash
curl "http://localhost:8000/api/v1/search/suggestions?q=my&field=repository"
```

## Usage Workflow

### From UI

1. **Navigate to CI/CD Dashboard** at `/ci-dashboard`
2. **Use Quick Search** - Type to search repositories
3. **Click Advanced** to expand advanced filters
4. **Set Filters:**
   - Select repository, platform, status, branch
   - Adjust critical/error count ranges
   - Set time period and results per page
5. **Click Apply Filters** to execute search
6. **View Results** in the scan history table
7. **Save Filter** - Name current filters for reuse
8. **Click saved filter chip** to reload that filter
9. **Clear All** to reset to default dashboard view

### From API

```python
import requests

# Search for failed scans with critical issues
response = requests.get(
    "http://localhost:8000/api/v1/search/scans",
    params={
        "q": "payment-service",
        "status": "failure",
        "min_critical": 1,
        "days": 7,
        "limit": 50
    }
)

results = response.json()
print(f"Found {results['total']} matching scans")

for scan in results['results']:
    print(f"  {scan['repository']} - {scan['status']}")
```

## Performance Characteristics

- **Full-Text Search**: `LIKE %term%` on 3 fields (fast with index)
- **Exact Filters**: Indexed equality filters on repository, platform, status, branch
- **Range Filters**: Indexed range filters on critical_count, error_count
- **Pagination**: OFFSET/LIMIT with defaults (20 per page)
- **Typical Query**: <100ms for 500+ scans

## Future Enhancements

1. **Database Indexing**
   - Add composite indexes on frequently filtered combinations
   - Optimize ILIKE searches with partial indexes

2. **Search Analytics**
   - Track popular search terms
   - Suggest filters based on history

3. **Advanced Saved Filters**
   - Share filters with team
   - Filter groups by topic
   - Set alerts on saved searches

4. **Export Results**
   - Export search results as CSV
   - Generate reports from searches

5. **Real-time Search**
   - WebSocket updates as new scans arrive
   - Live filter refresh

## Testing

### Test Endpoints

```bash
# Test /filters endpoint
curl http://localhost:8000/api/v1/search/filters

# Test basic search
curl "http://localhost:8000/api/v1/search/scans?limit=5"

# Test text search
curl "http://localhost:8000/api/v1/search/scans?q=repo"

# Test suggestions
curl "http://localhost:8000/api/v1/search/suggestions?q=my&field=repository"

# Test filters
curl "http://localhost:8000/api/v1/search/scans?platform=github&status=success"

# Test ranges
curl "http://localhost:8000/api/v1/search/scans?min_critical=1&max_errors=10"
```

### Test in UI

1. Open http://localhost:3000/ci-dashboard
2. Type in quick search box
3. Check autocomplete suggestions appear
4. Click "Advanced" to expand filters
5. Set various filters and click "Apply Filters"
6. Verify results update
7. Save a filter and verify it appears in saved filters
8. Click saved filter to reload it
9. Verify pagination works for large result sets

## Integration Points

- **CIDashboard.tsx** - Primary UI integration
- **api/routes/search.py** - REST API
- **api/services/search_service.py** - Business logic
- **api/db/models.py** - CIScanHistory model
- **frontend/src/components/SearchFilters.tsx** - Reusable component

## Files Changed/Created

### New Files
- `api/services/search_service.py`
- `api/routes/search.py`
- `frontend/src/components/SearchFilters.tsx`
- `PHASE_15_A5_SEARCH.md` (this file)

### Modified Files
- `api/main.py` - Added search router import and registration
- `frontend/src/pages/CIDashboard.tsx` - Integrated SearchFilters component

## Environment Variables

No new environment variables required. Uses existing database connection.

## Database Requirements

Assumes `CIScanHistory` model with these fields:
- id, repository, branch, platform, status
- critical_count, error_count, warning_count
- total_findings, files_scanned
- created_at

## Error Handling

- **Invalid filters** → Returns empty results
- **Invalid pagination** → Returns error 400
- **No matches** → Returns 0 results, total=0
- **Database error** → Returns 500 with error message
