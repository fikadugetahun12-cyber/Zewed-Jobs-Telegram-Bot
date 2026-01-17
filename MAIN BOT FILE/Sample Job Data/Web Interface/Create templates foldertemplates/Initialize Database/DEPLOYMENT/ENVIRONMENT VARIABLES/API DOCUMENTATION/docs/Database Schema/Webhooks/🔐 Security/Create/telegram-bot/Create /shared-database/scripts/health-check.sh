#!/bin/bash

# Health check script for ZewedJobs system

echo "🔍 ZewedJobs System Health Check"
echo "================================="

check_service() {
    local name=$1
    local url=$2
    local command=$3
    
    echo -n "Checking $name... "
    
    if [ ! -z "$command" ]; then
        if eval "$command" > /dev/null 2>&1; then
            echo "✅ OK"
            return 0
        else
            echo "❌ FAILED"
            return 1
        fi
    elif [ ! -z "$url" ]; then
        if curl -s -f "$url" > /dev/null 2>&1; then
            echo "✅ OK"
            return 0
        else
            echo "❌ FAILED"
            return 1
        fi
    else
        echo "⚠️  No check defined"
        return 2
    fi
}

check_database() {
    echo -n "Checking database connection... "
    
    if python3 -c "
import mysql.connector
from config import Config
try:
    conn = mysql.connector.connect(
        host=Config.DB_HOST,
        user=Config.DB_USER,
        password=Config.DB_PASS,
        database=Config.DB_NAME
    )
    print('✅ OK')
    conn.close()
except Exception as e:
    print(f'❌ FAILED: {e}')
    exit(1)
" 2>/dev/null; then
        return 0
    else
        return 1
    fi
}

check_telegram_bot() {
    echo -n "Checking Telegram bot token... "
    
    if [ -f "telegram-bot/.env" ]; then
        if grep -q "BOT_TOKEN=" telegram-bot/.env; then
            token=$(grep "BOT_TOKEN=" telegram-bot/.env | cut -d= -f2)
            if [ ${#token} -gt 20 ]; then
                echo "✅ OK"
                return 0
            else
                echo "❌ Invalid token length"
                return 1
            fi
        else
            echo "❌ Token not found"
            return 1
        fi
    else
        echo "❌ .env file not found"
        return 1
    fi
}

check_disk_space() {
    echo -n "Checking disk space... "
    
    local usage=$(df -h . | awk 'NR==2 {print $5}' | sed 's/%//')
    
    if [ $usage -lt 90 ]; then
        echo "✅ OK ($usage% used)"
        return 0
    else
        echo "⚠️  WARNING ($usage% used)"
        return 1
    fi
}

check_memory() {
    echo -n "Checking memory... "
    
    if free -h | grep -q "Mem:"; then
        memory=$(free -h | grep "Mem:" | awk '{print $4}')
        echo "✅ $memory available"
        return 0
    else
        echo "⚠️  Could not check"
        return 1
    fi
}

# Run checks
echo ""
echo "📊 System Checks:"
check_disk_space
check_memory

echo ""
echo "🔧 Service Checks:"
check_database
check_telegram_bot
check_service "Admin Panel" "http://localhost:8080/admin"
check_service "Web Dashboard" "http://localhost:5000"

echo ""
echo "📁 Directory Checks:"
echo -n "Checking project structure... "
if [ -d "admin-panel" ] && [ -d "telegram-bot" ] && [ -d "shared-database" ]; then
    echo "✅ OK"
else
    echo "❌ Missing directories"
fi

echo -n "Checking required files... "
if [ -f "telegram-bot/bot.py" ] && [ -f "admin-panel/admin/index.php" ] && [ -f "shared-database/schema.sql" ]; then
    echo "✅ OK"
else
    echo "❌ Missing files"
fi

echo ""
echo "📋 Summary:"
echo "Run './start_all.sh' to start all services"
echo "Access Admin Panel: http://localhost:8080/admin"
echo "Access Dashboard: http://localhost:5000"
echo ""
echo "For more details, check the documentation in docs/"
