# MongoDB Connection Retry Logic - Complete Implementation

## Overview

Your Fitness AI application now has **enterprise-grade MongoDB connection handling** with:
- ✅ Automatic retry with exponential backoff
- ✅ Runtime reconnection on connection loss
- ✅ Health checks
- ✅ Detailed logging
- ✅ Graceful error handling
- ✅ Connection pooling configuration

---

## What Was Implemented

### File Modified: `app/db.py`

### Key Features:

#### 1. **Exponential Backoff Retry Logic**
```python
# Retry schedule:
# Attempt 1: Immediate
# Attempt 2: Wait 2 seconds
# Attempt 3: Wait 4 seconds
# Attempt 4: Wait 8 seconds
# Attempt 5: Wait 16 seconds
# Max wait: 60 seconds
```

#### 2. **Connection Settings**
```python
AsyncIOMotorClient(
    settings.MONGODB_URI,
    serverSelectionTimeoutMS=5000,   # 5 second timeout
    connectTimeoutMS=10000,          # 10 second connection timeout
    socketTimeoutMS=10000,           # 10 second socket timeout
    retryWrites=True,                # Auto-retry failed writes
    retryReads=True,                 # Auto-retry failed reads
    maxPoolSize=50,                  # Max connections in pool
    minPoolSize=10,                  # Min connections to maintain
)
```

#### 3. **Error Handling**
Handles specific MongoDB errors:
- `ServerSelectionTimeoutError` - Can't reach MongoDB server
- `ConfigurationError` - Invalid MongoDB URI
- `OperationFailure` - Authentication failed
- `Exception` - Any other unexpected errors

#### 4. **Runtime Reconnection**
- `check_connection()` - Verify connection is alive
- `ensure_connection()` - Reconnect if lost
- `get_database_with_retry()` - Get DB with auto-reconnect

#### 5. **Additional Indexes**
Added performance indexes for:
- Tasks by user and completion status
- Plans by user and creation date

---

## How It Works

### Startup Connection Flow

```
Application Starts
      ↓
connect_to_mongo()
      ↓
Attempt 1 ──┐
            ├─ Success? → Create Indexes → Done ✅
            └─ Fail? → Wait 2s
      ↓
Attempt 2 ──┐
            ├─ Success? → Create Indexes → Done ✅
            └─ Fail? → Wait 4s
      ↓
Attempt 3 ──┐
            ├─ Success? → Create Indexes → Done ✅
            └─ Fail? → Wait 8s
      ↓
... (up to 5 attempts)
      ↓
All Failed? → Raise ConnectionError ❌
```

### Runtime Reconnection Flow

```
API Request
      ↓
check_connection()
      ↓
Connected? ──┐
             ├─ Yes → Proceed with request ✅
             └─ No → ensure_connection()
                         ↓
                   Reconnect → Retry request ✅
```

---

## Usage Examples

### Example 1: Basic Usage (Current - No Change Needed)

Your existing routes work as-is:
```python
@router.get("/tasks")
async def get_tasks(
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_user: User = Depends(get_current_user)
):
    tasks = await db.tasks.find({"user_id": str(current_user.id)}).to_list(100)
    return tasks
```

**What happens**:
- Connection established at startup
- If connection lost mid-operation, request fails with DB error
- Frontend shows error toast

### Example 2: With Automatic Reconnect (Recommended)

For critical routes, use `get_database_with_retry`:
```python
@router.get("/tasks")
async def get_tasks(
    db: AsyncIOMotorDatabase = Depends(get_database_with_retry),  # ← Changed
    current_user: User = Depends(get_current_user)
):
    tasks = await db.tasks.find({"user_id": str(current_user.id)}).to_list(100)
    return tasks
```

**What happens**:
- Checks connection before proceeding
- Auto-reconnects if connection was lost
- Request succeeds even if temporary connection issue

### Example 3: Manual Connection Check

For custom logic:
```python
from app.db import check_connection, ensure_connection

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    is_connected = await check_connection()

    if not is_connected:
        # Try to reconnect
        try:
            await ensure_connection()
            is_connected = True
        except Exception as e:
            return {"status": "unhealthy", "database": "disconnected", "error": str(e)}

    return {
        "status": "healthy",
        "database": "connected"
    }
```

---

## Connection States

### State 1: Initial Startup

```bash
INFO: Attempting to connect to MongoDB (Attempt 1/5)...
INFO: ✅ Successfully connected to MongoDB!
INFO: Creating database indexes...
INFO: ✅ Ensured unique email index exists for users collection
INFO: ✅ Ensured user_id and task_date index exists for tasks collection
INFO: ✅ Ensured user_id and completed index exists for tasks collection
INFO: ✅ Ensured user_id and created_at index exists for plans collection
INFO: 🎉 All indexes created successfully!
```

### State 2: Connection Failure with Retry

```bash
INFO: Attempting to connect to MongoDB (Attempt 1/5)...
WARNING: ⚠️ Connection failed. Retrying in 2 seconds...
INFO: Attempting to connect to MongoDB (Attempt 2/5)...
INFO: ✅ Successfully connected to MongoDB!
```

### State 3: All Retries Exhausted

```bash
INFO: Attempting to connect to MongoDB (Attempt 1/5)...
WARNING: ⚠️ Connection failed. Retrying in 2 seconds...
INFO: Attempting to connect to MongoDB (Attempt 2/5)...
WARNING: ⚠️ Connection failed. Retrying in 4 seconds...
INFO: Attempting to connect to MongoDB (Attempt 3/5)...
WARNING: ⚠️ Connection failed. Retrying in 8 seconds...
INFO: Attempting to connect to MongoDB (Attempt 4/5)...
WARNING: ⚠️ Connection failed. Retrying in 16 seconds...
INFO: Attempting to connect to MongoDB (Attempt 5/5)...
ERROR: ❌ Failed to connect to MongoDB after 5 attempts
ERROR: Error: [Errno 11001] getaddrinfo failed
ERROR: Please check:
ERROR:   1. MongoDB Atlas cluster is running
ERROR:   2. Network/firewall allows connections
ERROR:   3. MongoDB URI is correct
ERROR:   4. IP whitelist includes your IP
```

### State 4: Runtime Reconnection

```bash
WARNING: ⚠️ MongoDB connection check failed: Network is unreachable
WARNING: ⚠️ MongoDB connection lost. Attempting to reconnect...
INFO: Attempting to connect to MongoDB (Attempt 1/5)...
INFO: ✅ Successfully connected to MongoDB!
```

---

## Configuration Options

### Adjust Retry Attempts

In `app/db.py`:
```python
class Database:
    _max_retries: int = 5  # Change this (default: 5)
```

Or modify in `connect_to_mongo()`:
```python
max_retries = 10  # Try 10 times instead of 5
```

### Adjust Retry Delays

```python
base_delay = 2   # Start with 2 seconds
max_delay = 60   # Max 60 seconds between retries

# Custom delay strategy:
delay = base_delay * retries  # Linear: 2, 4, 6, 8...
delay = base_delay ** retries  # Exponential: 2, 4, 8, 16...
delay = min(base_delay * (2 ** retries), max_delay)  # Current (exponential with cap)
```

### Adjust Connection Timeouts

```python
AsyncIOMotorClient(
    settings.MONGODB_URI,
    serverSelectionTimeoutMS=10000,  # Increase to 10 seconds
    connectTimeoutMS=20000,          # Increase to 20 seconds
    socketTimeoutMS=20000,           # Increase to 20 seconds
)
```

### Adjust Connection Pool

```python
maxPoolSize=100,  # Increase for high traffic
minPoolSize=20,   # Keep more connections ready
```

---

## Error Messages Guide

### Error: "ServerSelectionTimeoutError"

**Meaning**: Can't reach MongoDB server

**Possible Causes**:
1. MongoDB Atlas cluster is paused/stopped
2. Network/firewall blocking connection
3. Wrong MongoDB URI
4. IP not whitelisted in Atlas

**Fix**:
1. Check MongoDB Atlas dashboard
2. Verify cluster is running
3. Add your IP to whitelist
4. Check MONGODB_URI in .env

### Error: "ConfigurationError"

**Meaning**: Invalid MongoDB URI format

**Possible Causes**:
1. Malformed connection string
2. Missing required parameters
3. Wrong protocol (mongodb:// vs mongodb+srv://)

**Fix**:
1. Check .env file
2. Verify MONGODB_URI format
3. Example: `mongodb+srv://user:pass@cluster.mongodb.net/dbname`

### Error: "OperationFailure"

**Meaning**: Authentication failed

**Possible Causes**:
1. Wrong username/password
2. User doesn't have permissions
3. Database name doesn't match

**Fix**:
1. Verify MongoDB credentials
2. Check user permissions in Atlas
3. Ensure DB_NAME matches

---

## Testing Retry Logic

### Test 1: Simulate Network Failure

```bash
# Disconnect from internet
# Start your backend
python run.py

# You should see retries:
INFO: Attempting to connect to MongoDB (Attempt 1/5)...
WARNING: ⚠️ Connection failed. Retrying in 2 seconds...
INFO: Attempting to connect to MongoDB (Attempt 2/5)...
...

# Reconnect internet
# Should eventually succeed
INFO: ✅ Successfully connected to MongoDB!
```

### Test 2: Runtime Reconnection

```python
# Add test endpoint
@router.get("/test-reconnect")
async def test_reconnect(db: AsyncIOMotorDatabase = Depends(get_database_with_retry)):
    """Test automatic reconnection"""
    # Simulate connection loss
    from app.db import db as database
    database._is_connected = False

    # This should trigger reconnection
    result = await db.users.count_documents({})
    return {"status": "success", "user_count": result}
```

### Test 3: Health Check Endpoint

```python
# Add this to your routes
@router.get("/health")
async def health_check():
    from app.db import check_connection

    db_connected = await check_connection()

    return {
        "status": "healthy" if db_connected else "unhealthy",
        "database": "connected" if db_connected else "disconnected",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
```

---

## Production Recommendations

### 1. **Use Connection with Retry for Critical Routes**

```python
# Critical routes (authentication, plan generation, etc.)
@router.post("/plans/generate")
async def generate_plan(
    db: AsyncIOMotorDatabase = Depends(get_database_with_retry),  # ← Use retry
    current_user: User = Depends(get_current_user)
):
    # Your logic
```

### 2. **Add Health Check Endpoint**

```python
@router.get("/health", tags=["Health"])
async def health_check():
    """Monitor application and database health"""
    from app.db import check_connection

    db_status = await check_connection()

    return {
        "status": "healthy" if db_status else "degraded",
        "components": {
            "database": "up" if db_status else "down",
            "api": "up"
        },
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
```

### 3. **Monitor Connection Status**

Add metrics/logging:
```python
# In app/db.py
class Database:
    _connection_count: int = 0  # Track reconnection attempts
    _last_connection_time: Optional[datetime] = None
```

### 4. **Set Up Alerts**

Monitor for:
- Frequent reconnections
- Connection failures
- Slow queries
- High connection pool usage

### 5. **Use MongoDB Atlas Monitoring**

MongoDB Atlas provides:
- Real-time connection metrics
- Query performance insights
- Alert notifications
- Connection spike detection

---

## Advantages of This Implementation

### ✅ **Automatic Recovery**
- Connection issues don't require manual restart
- Temporary network glitches handled gracefully
- App stays available during short outages

### ✅ **Better User Experience**
- Requests succeed even with temporary connection issues
- Transparent to end users
- No manual intervention needed

### ✅ **Production-Ready**
- Handles MongoDB Atlas maintenance windows
- Survives network hiccups
- Proper connection pooling for scale

### ✅ **Detailed Logging**
- Easy to diagnose connection issues
- Clear error messages
- Helpful troubleshooting hints

### ✅ **Efficient Resource Usage**
- Connection pooling (50 max, 10 min)
- Reuses connections
- Closes gracefully on shutdown

---

## Comparison: Before vs After

| Scenario | Before | After |
|----------|--------|-------|
| **Startup with network issue** | ❌ Crash immediately | ✅ Retry 5 times, succeed when network returns |
| **MongoDB Atlas maintenance** | ❌ All requests fail | ✅ Auto-reconnect, requests succeed |
| **Temporary network glitch** | ❌ App must be restarted | ✅ Auto-recovers, no restart needed |
| **Connection timeout** | ❌ Single 30s timeout | ✅ 5 attempts with exponential backoff |
| **Connection lost mid-request** | ❌ Request fails, no retry | ✅ Auto-reconnect on next request |
| **Error diagnosis** | ❌ Generic error | ✅ Detailed error with troubleshooting steps |

---

## Summary

Your MongoDB connection handling is now:
- ✅ **Resilient** - Survives temporary connection issues
- ✅ **Automatic** - Reconnects without manual intervention
- ✅ **Informative** - Clear logging for debugging
- ✅ **Efficient** - Connection pooling for performance
- ✅ **Production-Ready** - Handles real-world scenarios

**No more manual restarts needed when MongoDB connection is temporarily lost!** 🎉

---

## Quick Reference

```python
# Import in your routes
from app.db import get_database, get_database_with_retry, check_connection, ensure_connection

# Standard usage (current behavior)
db: AsyncIOMotorDatabase = Depends(get_database)

# With automatic reconnect (recommended for critical routes)
db: AsyncIOMotorDatabase = Depends(get_database_with_retry)

# Manual connection check
is_connected = await check_connection()

# Manual reconnection
await ensure_connection()
```

**Your MongoDB connection is now bulletproof!** 💪
