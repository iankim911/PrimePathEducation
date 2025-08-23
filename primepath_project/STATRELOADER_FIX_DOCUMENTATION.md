# StatReloader Fix Documentation

## Problem: "StatReloader exited unexpectedly"

This error occurs frequently in Django development servers, especially on macOS, due to:
1. **File descriptor limits too low** (default 256 on macOS)
2. **Too many files being watched** by Django's auto-reload system
3. **System resource constraints**
4. **File system events overwhelming the watcher**

## Solutions Implemented

### 1. 🚀 Quick Start Options

#### Option A: Use Stable Server Starter (RECOMMENDED)
```bash
cd /Users/ian/Desktop/VIBECODE/PrimePath/primepath_project
./start_server.sh
```
**Features:**
- Auto-restarts on crash
- Colored output
- Port conflict resolution
- File limit management

#### Option B: Python Auto-Restart Runner
```bash
cd /Users/ian/Desktop/VIBECODE/PrimePath/primepath_project
../venv/bin/python run_server_stable.py
```
**Features:**
- Python-based auto-restart
- Detailed error handling
- Crash recovery

#### Option C: Manual with --noreload (Most Stable)
```bash
cd /Users/ian/Desktop/VIBECODE/PrimePath/primepath_project
../venv/bin/python manage.py runserver 127.0.0.1:8000 --settings=primepath_project.settings_sqlite --noreload
```
**Note:** Auto-reload disabled, must restart manually for code changes

### 2. 🔧 System Configuration Fixes

#### File Limits Increased
- **Before:** 256 files (macOS default)
- **After:** 10,240 files
- **Location:** Added to `~/.zshrc`

```bash
# Added to shell profile
ulimit -n 10240
```

#### Django Configuration
- **File:** `primepath_project/statreloader_config.py`
- **Import:** Added to `settings_sqlite.py`
- **Effect:** Configures Django to handle file watching better

### 3. 📁 Files Created

| File | Purpose |
|------|---------|
| `start_server.sh` | Bash script with auto-restart and monitoring |
| `run_server_stable.py` | Python script with crash recovery |
| `fix_statreloader.py` | One-time setup utility |
| `statreloader_config.py` | Django configuration module |
| `run_with_watchman.py` | Alternative using Watchman (if installed) |

### 4. 🎯 How Each Solution Works

#### start_server.sh
1. Increases file limits for session
2. Cleans up any stuck processes
3. Runs Django with `--noreload` flag
4. Monitors for crashes
5. Auto-restarts up to 10 times
6. Colored output for easy reading

#### run_server_stable.py
1. Python-based monitoring
2. Detects rapid restart loops
3. Port conflict resolution
4. Subprocess management
5. Graceful shutdown handling

#### statreloader_config.py
1. Sets autoreload type to 'stat' (more stable)
2. Increases resource limits programmatically
3. Optional Watchman integration
4. Platform-specific optimizations

## Troubleshooting

### If Still Getting Errors

1. **Check current limits:**
   ```bash
   ulimit -n
   ```
   Should show 10240 or higher

2. **Kill stuck processes:**
   ```bash
   pkill -f "manage.py runserver"
   lsof -ti:8000 | xargs kill -9
   ```

3. **Restart terminal** to apply new limits

4. **Use --noreload flag** as last resort

### Port Already in Use

```bash
# Find what's using port 8000
lsof -i :8000

# Kill it
kill -9 <PID>
```

### For Permanent System Fix (Requires Admin)

```bash
# Run with sudo to create system configuration
sudo python fix_statreloader.py
```

## Best Practices

1. **For Development:** Use `./start_server.sh` - handles everything automatically
2. **For Testing:** Use `--noreload` flag for maximum stability
3. **For Production:** Never use development server; use Gunicorn/uWSGI

## Quick Commands Reference

```bash
# Start with auto-restart
./start_server.sh

# Manual stable start
../venv/bin/python manage.py runserver --noreload

# Check if server is running
lsof -i :8000

# Kill all Django processes
pkill -f "manage.py runserver"

# Check file limits
ulimit -n
```

## Why This Happens

Django's StatReloader watches all Python files in your project for changes. With a large codebase:
- Hundreds of `.py` files
- Virtual environment files
- Static files
- Media files
- Git files

This quickly exceeds macOS's default 256 file descriptor limit, causing the watcher to crash.

## The Fix Explained

1. **Increased Limits:** From 256 to 10,240 file descriptors
2. **Disabled Auto-reload:** Using `--noreload` flag prevents watching
3. **Auto-restart:** Scripts detect crashes and restart automatically
4. **Process Cleanup:** Ensures no zombie processes block the port

---

**Last Updated:** August 23, 2025
**Tested On:** macOS with Django 5.0.1