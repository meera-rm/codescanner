---
created_at: 2026-06-12T18:16:43Z
title: Upload Refactor Plan
source: claude-code
project: codescanner
---

# Browse & Upload Code Refactoring Plan

## Current Issues
1. **Scattered handlers** — `handleBrowseFolder`, `handleDrag`, `handleDrop` are separate and don't share logic
2. **Limited path detection** — Only searches common locations, doesn't handle deeply nested paths
3. **No GitHub support** — Can't scan GitHub repos directly
4. **No ZIP support** — Drag & drop doesn't handle ZIP files
5. **No validation** — Doesn't check if path is readable/accessible before scanning

## Proposed Architecture

### 1. Unified Upload Handler (`useUploadManager` Hook)
```typescript
const uploadManager = useUploadManager({
  onPathDetected: (path) => setDirectoryPath(path),
  onError: (err) => setError(err),
  onProgress: (msg) => setError(msg)
});
```

### 2. Smart Path Detection
- **Local paths**: Search recursively through Documents (up to 5 levels deep)
- **GitHub repos**: Parse GitHub URLs → clone/download → scan
- **ZIP files**: Extract to temp → scan → cleanup
- **Absolute paths**: Validate permissions, then scan

### 3. Upload Methods Supported
| Method | Implementation |
|--------|-----------------|
| **Browse Folder** | `webkitdirectory` + auto-detect full path |
| **Browse File** | Single/multiple files + detect language |
| **Drag & Drop Folder** | Extract from DataTransfer + search for full path |
| **Drag & Drop Files** | Accept `.py`, `.js`, `.sql`, `.zip` |
| **Drag & Drop ZIP** | Extract temp folder → scan → cleanup |
| **GitHub URL** | Parse → Download → Extract → Scan |
| **Text Input** | Validate path → search → scan |

### 4. File Structure
```
frontend/src/hooks/
├── useUploadManager.ts          # Unified upload logic
├── usePathDetection.ts           # Smart path searching
└── useGitHubDownloader.ts        # GitHub repo handling

frontend/src/components/
├── UploadZone.tsx               # Drag & drop component
└── UploadInputs.tsx             # Browse/text/GitHub inputs
```

### 5. Enhanced Features
- ✓ Progress indication during upload
- ✓ File validation (check before scan)
- ✓ Multiple format support (.zip, .tar, .tar.gz)
- ✓ Directory size check (warn if > 100MB)
- ✓ Recent paths history
- ✓ Favorites/bookmarks

### 6. Error Handling
- Path not found → Search suggestions (top 5 matches)
- Permission denied → Request elevated access
- ZIP corrupt → Show extract error
- GitHub invalid → Suggest valid format
- Size too large → Offer chunked upload

### 7. Implementation Priority
1. **Phase 1** (High Priority)
   - Consolidate handlers into `useUploadManager`
   - Improve path detection (5 levels deep)
   - Add ZIP support

2. **Phase 2** (Medium Priority)
   - GitHub URL support
   - Directory validation
   - Recent paths history

3. **Phase 3** (Low Priority)
   - Multiple file upload
   - Chunked upload for large files
   - Cloud integration (S3, GCS)

## Code Examples

### Before (Current)
```typescript
const handleBrowseFolder = () => { ... }
const handleDirectorySelect = (e) => { ... }
const handleDrag = (e) => { ... }
const handleDrop = (e) => { ... }
// Scattered, lots of duplication
```

### After (Proposed)
```typescript
const uploadManager = useUploadManager({
  onPathSelected: async (path) => {
    const resolved = await uploadManager.detectPath(path);
    setDirectoryPath(resolved);
  }
});

return (
  <UploadZone
    onBrowse={() => uploadManager.browse('folder')}
    onDrop={(files) => uploadManager.handleDrop(files)}
    onTextInput={(text) => uploadManager.parseInput(text)}
  />
);
```

## Benefits
✓ **Cleaner code** — All upload logic in one place
✓ **Better UX** — Smarter path detection, GitHub support
✓ **More formats** — ZIP, TAR, GitHub repos
✓ **Error messages** — Helpful suggestions instead of vague errors
✓ **Extensible** — Easy to add new upload sources

---

## Notes
- Keep backward compatibility with existing path detection
- All paths should resolve to absolute paths before sending to backend
- ZIP extraction should use temp directory that auto-cleans
- GitHub integration should be optional (can be added later)
