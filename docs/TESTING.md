# Testing & Debugging Guide

## Application Status

✅ **Backend**: Running on http://localhost:5001
✅ **Frontend**: Served by Flask at http://localhost:5001
✅ **Comprehensive Logging**: Enabled everywhere

## Comprehensive Logging

### Backend Logs

**Location**: `logs/backend.log`

**View in real-time**:
```bash
tail -f logs/backend.log
```

**Log Levels**:
- `INFO`: Important operations (uploads, processing steps, completions)
- `DEBUG`: Detailed trace (topic analysis, formatting)
- `ERROR`: Failures with full stack traces

**What's Logged**:
- Application startup with configuration
- Every API request (upload, process, download, health)
- File operations (save, read, write)
- PDF extraction progress
- Topic identification
- Claude API calls (analyze & format)
- Processing completion
- Download requests
- All errors with full context

### Frontend Console Logs

**View**: Open browser DevTools (F12) → Console tab

**Log Prefix Format**: `[ComponentName] Message`

**What's Logged**:
- `[App]`: Application initialization, step changes
- `[FileUpload]`: File selection, upload progress, responses
- `[ProcessingStatus]`: POST requests, SSE stream chunks, progress updates
- `[ResultViewer]`: Download requests and completions

**Example Log Flow**:
```
[App] Application initialized
[FileUpload] File select event triggered
[FileUpload] File selected: pharmacy_law.pdf Size: 2048576 bytes
[FileUpload] Starting upload for: pharmacy_law.pdf
[FileUpload] Sending POST to /api/upload
[FileUpload] Upload response: {file_id: "20251016_080000", ...}
[App] File uploaded with ID: 20251016_080000
[App] Switching to processing step
[ProcessingStatus] Component mounted for file_id: 20251016_080000
[ProcessingStatus] POST request to: /api/process/20251016_080000
[ProcessingStatus] Response status: 200
[ProcessingStatus] Starting to read response stream...
[ProcessingStatus] Chunk 1: data: {"progress": 10, "message": "Extracting PDF..."}
[ProcessingStatus] Parsed data: {progress: 10, message: "Extracting PDF..."}
[ProcessingStatus] Progress update: 10%
...
[ProcessingStatus] Processing complete!
```

## Flask Hot Reload

**Answer**: Flask does **NOT** have hot reload enabled by default in production mode.

**For Development**:
- Set `DEBUG=true` environment variable to enable hot reload
- **Issue**: Current watchdog dependency incompatibility prevents this
- **Workaround**: Manually restart the server after code changes

**Current Setup**: Production mode (no auto-reload)
- Changes to backend Python files require manual restart
- Changes to frontend require rebuild + copy to static folder

**To Apply Changes**:
```bash
# Stop the app
bash stop_app.sh

# Rebuild frontend (if changed)
cd frontend && npm run build && cd ..

# Copy to backend static
cp -r frontend/dist/* backend/static/

# Restart
bash start_app.sh
```

## Error Handling & Recovery

### Frontend Features:
- **"Start Over" button** appears when processing fails
- User can return to upload screen without refreshing
- All errors logged to console for debugging

### Backend Features:
- Full error stack traces in logs
- Graceful error handling with user-friendly messages
- Processing status preserved for download retrieval

## Testing Workflow

### 1. Check Application Health
```bash
curl http://localhost:5001/api/health
```

**Expected Response**:
```json
{
  "status": "healthy",
  "claude_configured": true,
  "timestamp": "2025-10-16T12:00:00.000000"
}
```

### 2. Upload a PDF

**Browser**: http://localhost:5001
1. Drag & drop or click to upload PDF
2. Click "Process"

**Console Logs to Watch**:
- File selection confirmation
- Upload POST request
- Upload response with file_id

**Backend Logs to Watch**:
```
[INFO] File upload request received
[INFO] File received: test.pdf
[INFO] Saving file to: ./uploads/20251016_120000_test.pdf
[INFO] File saved successfully. Size: 1234567 bytes
[INFO] PDF has 50 pages
[INFO] Upload successful
```

### 3. Monitor Processing

**Browser Console**:
- Watch for SSE stream chunks
- Progress updates (10%, 30%, 50%, ..., 100%)
- Topic-by-topic processing messages

**Backend Logs**:
```
[INFO] Processing request for file_id: 20251016_120000
[INFO] Extracting 50 pages...
[INFO] Identified 10 topics
[INFO] Processing topic 1/10: Controlled Substances
[DEBUG] Analyzing topic: Controlled Substances
[DEBUG] Analysis complete for: Controlled Substances
[DEBUG] Formatting topic: Controlled Substances
...
[INFO] Processing complete for file_id: 20251016_120000
```

### 4. Download Results

Click download buttons and check:
- Browser console for download initiation
- Backend logs for file serving
- Actual file downloads in ~/Downloads

## Common Issues & Solutions

### Issue: "No progress after upload"

**Check**:
1. Browser console for POST request to `/api/process/{file_id}`
2. Backend logs for "Processing request for file_id"
3. Network tab (F12) for SSE connection status

**Solution**:
- Verify file_id matches between frontend and backend
- Check backend logs for errors
- Ensure Claude API key is configured

### Issue: "Processing stalls at X%"

**Check**:
1. Backend logs for the specific topic being processed
2. Look for Claude API errors or timeouts

**Solution**:
- Check internet connection (for Claude API)
- Verify API key is valid and has credits
- Check for PDF content issues at that specific page

### Issue: "Download fails"

**Check**:
1. Browser console for download request
2. Backend logs for file existence
3. `outputs/` folder for generated files

**Solution**:
- Verify processing completed (100%)
- Check file permissions on outputs folder
- Review backend logs for file path issues

## Debugging Tips

### Full Trace of a Request:

**Terminal 1** (Backend logs):
```bash
tail -f logs/backend.log
```

**Browser** (Console + Network tabs open):
- Console: See frontend logs
- Network: See all HTTP requests/responses

### Finding Specific Issues:

**Search backend logs**:
```bash
# Find all errors
grep ERROR logs/backend.log

# Find specific file processing
grep "file_id: 20251016" logs/backend.log

# Find Claude API calls
grep "Analyzing topic" logs/backend.log
```

**Filter console logs**:
```javascript
// In browser console
// Show only errors
console.log = () => {}
// Or filter by component
// Type "[ProcessingStatus]" in console filter box
```

## Performance Metrics

**Expected Processing Times**:
- 10-page PDF: ~30 seconds
- 50-page PDF: ~2 minutes
- 100-page PDF: ~4 minutes

**Factors Affecting Speed**:
- PDF complexity (images, tables)
- Number of topics identified
- Claude API response time
- Network latency

## Production Deployment Notes

**For Replit or Production**:
1. Set `DEBUG=false` (or don't set DEBUG env var)
2. Logs will be written to `logs/backend.log`
3. Use a production WSGI server (gunicorn)
4. Consider log rotation for long-running instances

**Recommended Production Setup**:
```bash
# Install gunicorn
pip install gunicorn

# Run with gunicorn
cd backend
gunicorn -w 4 -b 0.0.0.0:5001 app:app --access-logfile logs/access.log
```

---

**Happy Testing!** 🧪

For issues, check logs first - they contain comprehensive traces of every operation.
