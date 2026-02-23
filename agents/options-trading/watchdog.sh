#!/bin/bash
# OpenClaw Options Trading Agent Watchdog
# Monitors agent health, gateway status, and trading system integrity
# Restarts components if degraded or crashed

CLI="/opt/homebrew/bin/openclaw"
WORKSPACE="/Users/sigbotti/.openclaw/workspace/agents/options-trading"
LOG_FILE="/tmp/openclaw/watchdog.log"
LOCK_FILE="/tmp/openclaw-watchdog.lock"
PID_FILE="/tmp/options-trading-agent.pid"

# Notification settings (optional)
NOTIFY_DISCORD=""
DISCORD_WEBHOOK=""

mkdir -p /tmp/openclaw

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG_FILE"
}

# Rotate log if > 1MB
if [ -f "$LOG_FILE" ] && [ "$(stat -f%z "$LOG_FILE" 2>/dev/null || echo 0)" -gt 1048576 ]; then
    mv "$LOG_FILE" "${LOG_FILE}.old"
    log "Log rotated"
fi

acquire_lock() {
    if [ -f "$LOCK_FILE" ]; then
        local old_pid
        old_pid=$(cat "$LOCK_FILE" 2>/dev/null)
        if [ -n "$old_pid" ] && kill -0 "$old_pid" 2>/dev/null; then
            log "Watchdog already running (PID: $old_pid)"
            exit 0
        fi
    fi
    echo $$ > "$LOCK_FILE"
}

release_lock() { 
    rm -f "$LOCK_FILE"
    log "Lock released"
}

trap release_lock EXIT
acquire_lock

# ============================================
# HEALTH CHECK FUNCTIONS
# ============================================

check_gateway_health() {
    local result
    result=$($CLI health 2>&1)
    local exit_code=$?
    
    if [ $exit_code -ne 0 ]; then
        echo "gateway_down"
        return 1
    fi
    
    # Check for channel issues
    if echo "$result" | grep -qi "discord.*failed\|discord.*error\|discord.*disconnected"; then
        echo "discord_down"
        return 1
    fi
    
    echo "healthy"
    return 0
}

check_agent_process() {
    if [ -f "$PID_FILE" ]; then
        local pid
        pid=$(cat "$PID_FILE")
        if kill -0 "$pid" 2>/dev/null; then
            # Check if process is actually responding
            if ps -p "$pid" -o args= | grep -q "options-trading"; then
                echo "running"
                return 0
            fi
        fi
    fi
    echo "stopped"
    return 1
}

check_disk_space() {
    local usage
    usage=$(df -h /tmp | tail -1 | awk '{print $5}' | tr -d '%')
    if [ "$usage" -gt 90 ]; then
        echo "critical"
        return 1
    elif [ "$usage" -gt 80 ]; then
        echo "warning"
        return 0
    fi
    echo "ok"
    return 0
}

check_memory_usage() {
    local usage
    usage=$(ps -o %mem= -p "$(cat "$PID_FILE" 2>/dev/null || echo 0)" 2>/dev/null | tr -d ' ')
    if [ -n "$usage" ]; then
        if (( $(echo "$usage > 50" | bc -l) )); then
            echo "high"
            return 1
        fi
    fi
    echo "normal"
    return 0
}

# ============================================
# RESTART FUNCTIONS
# ============================================

restart_gateway() {
    log "Restarting OpenClaw gateway..."
    
    $CLI gateway stop 2>/dev/null || true
    sleep 3
    
    $CLI gateway start 2>/dev/null || {
        log "Gateway service start failed, trying manual..."
        nohup $CLI gateway > /tmp/openclaw-gateway.log 2>&1 &
        sleep 5
    }
    
    # Verify
    sleep 5
    local health
    health=$(check_gateway_health)
    
    if [ "$health" = "healthy" ]; then
        log "Gateway restarted successfully"
        send_notification "✅ Gateway was down and has been restarted"
        return 0
    else
        log "Gateway restart failed: $health"
        send_notification "🚨 Gateway restart failed: $health - Manual intervention needed"
        return 1
    fi
}

restart_trading_agent() {
    log "Restarting Options Trading Agent..."
    
    # Kill existing if running
    if [ -f "$PID_FILE" ]; then
        local old_pid
        old_pid=$(cat "$PID_FILE")
        kill "$old_pid" 2>/dev/null || true
        sleep 2
    fi
    
    # Start fresh
    cd "$WORKSPACE" || exit 1
    nohup python3 main.py > /tmp/options-trading-agent.log 2>&1 &
    local new_pid=$!
    echo $new_pid > "$PID_FILE"
    
    sleep 10
    
    # Verify
    if kill -0 "$new_pid" 2>/dev/null; then
        log "Trading agent restarted (PID: $new_pid)"
        send_notification "✅ Options Trading Agent was down and has been restarted"
        return 0
    else
        log "Trading agent restart failed"
        send_notification "🚨 Trading Agent restart failed - Check logs at /tmp/options-trading-agent.log"
        return 1
    fi
}

# ============================================
# NOTIFICATION
# ============================================

send_notification() {
    local message="$1"
    
    # Discord webhook
    if [ -n "$DISCORD_WEBHOOK" ]; then
        curl -s -X POST "$DISCORD_WEBHOOK" \
            -H "Content-Type: application/json" \
            -d "{\"content\":\"$message\"}" 2>/dev/null || true
    fi
    
    # Log to file
    log "NOTIFY: $message"
}

# ============================================
# METRICS COLLECTION
# ============================================

collect_metrics() {
    local metrics_file="/tmp/openclaw/metrics.json"
    
    local gateway_status
    gateway_status=$(check_gateway_health)
    
    local agent_status
    agent_status=$(check_agent_process)
    
    local disk_status
    disk_status=$(check_disk_space)
    
    cat > "$metrics_file" << EOF
{
    "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
    "gateway": "$gateway_status",
    "trading_agent": "$agent_status",
    "disk": "$disk_status",
    "checks_performed": $CHECK_COUNT
}
EOF
}

# ============================================
# MAIN CHECK LOOP
# ============================================

CHECK_COUNT=0

check_and_fix() {
    CHECK_COUNT=$((CHECK_COUNT + 1))
    log "=== Health Check #$CHECK_COUNT ==="
    
    local needs_restart=0
    
    # Check 1: Gateway Health
    local gateway_status
    gateway_status=$(check_gateway_health)
    log "Gateway: $gateway_status"
    
    if [ "$gateway_status" != "healthy" ]; then
        log "Gateway issue detected: $gateway_status"
        restart_gateway
        needs_restart=1
    fi
    
    # Check 2: Trading Agent Process
    local agent_status
    agent_status=$(check_agent_process)
    log "Trading Agent: $agent_status"
    
    if [ "$agent_status" != "running" ]; then
        log "Trading Agent not running"
        restart_trading_agent
        needs_restart=1
    fi
    
    # Check 3: Disk Space
    local disk_status
    disk_status=$(check_disk_space)
    log "Disk: $disk_status"
    
    if [ "$disk_status" = "critical" ]; then
        log "CRITICAL: Disk space critical"
        send_notification "🚨 CRITICAL: Disk space on /tmp is over 90% - Trading may be affected"
    elif [ "$disk_status" = "warning" ]; then
        log "WARNING: Disk space over 80%"
    fi
    
    # Check 4: Memory Usage
    local mem_status
    mem_status=$(check_memory_usage)
    log "Memory: $mem_status"
    
    if [ "$mem_status" = "high" ]; then
        log "WARNING: Trading agent using high memory"
        send_notification "⚠️ Trading Agent memory usage is high - Consider restarting during off-hours"
    fi
    
    # Collect metrics
    collect_metrics
    
    log "Check complete. Issues found: $needs_restart"
}

# ============================================
# EXECUTE CHECK
# ============================================

log "Options Trading Agent Watchdog started"
log "Workspace: $WORKSPACE"
log "PID File: $PID_FILE"

# Run the check
check_and_fix

log "Watchdog check complete"
