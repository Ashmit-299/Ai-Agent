#!/usr/bin/env python3
"""
Performance optimization script for AI Agent routes
"""

import os
import time
import json
import sqlite3
from pathlib import Path

def optimize_database():
    """Optimize database performance"""
    print("=== Database Optimization ===")
    
    try:
        with sqlite3.connect('data.db') as conn:
            cur = conn.cursor()
            
            # Create indexes for better query performance
            indexes = [
                "CREATE INDEX IF NOT EXISTS idx_content_uploaded_at ON content(uploaded_at)",
                "CREATE INDEX IF NOT EXISTS idx_content_uploader_id ON content(uploader_id)",
                "CREATE INDEX IF NOT EXISTS idx_feedback_content_id ON feedback(content_id)",
                "CREATE INDEX IF NOT EXISTS idx_feedback_user_id ON feedback(user_id)",
                "CREATE INDEX IF NOT EXISTS idx_feedback_timestamp ON feedback(timestamp)"
            ]
            
            for index_sql in indexes:
                cur.execute(index_sql)
                print(f"[OK] Created index: {index_sql.split('idx_')[1].split(' ON')[0]}")
            
            # Analyze tables for query optimization
            cur.execute("ANALYZE")
            print("[OK] Database analysis completed")
            
            # Vacuum to reclaim space
            cur.execute("VACUUM")
            print("[OK] Database vacuum completed")
            
    except Exception as e:
        print(f"[ERROR] Database optimization failed: {e}")

def cleanup_old_files():
    """Clean up old temporary and log files"""
    print("\n=== File Cleanup ===")
    
    cleanup_dirs = [
        ('bucket/logs', 30),  # Keep logs for 30 days
        ('bucket/ratings', 90),  # Keep ratings for 90 days
        ('uploads', 7)  # Keep uploads for 7 days
    ]
    
    current_time = time.time()
    total_cleaned = 0
    
    for dir_path, days_to_keep in cleanup_dirs:
        if not os.path.exists(dir_path):
            continue
            
        cutoff_time = current_time - (days_to_keep * 24 * 3600)
        cleaned_count = 0
        
        for filename in os.listdir(dir_path):
            file_path = os.path.join(dir_path, filename)
            if os.path.isfile(file_path):
                if os.path.getmtime(file_path) < cutoff_time:
                    try:
                        os.remove(file_path)
                        cleaned_count += 1
                    except Exception as e:
                        print(f"[ERROR] Failed to remove {file_path}: {e}")
        
        print(f"[OK] Cleaned {cleaned_count} files from {dir_path}")
        total_cleaned += cleaned_count
    
    print(f"[OK] Total files cleaned: {total_cleaned}")

def optimize_config():
    """Create optimized configuration"""
    print("\n=== Configuration Optimization ===")
    
    config = {
        "database": {
            "connection_pool_size": 5,
            "query_timeout": 30,
            "enable_wal_mode": True
        },
        "file_handling": {
            "max_file_size_mb": 100,
            "allowed_extensions": [".mp4", ".mp3", ".wav", ".jpg", ".jpeg", ".png", ".txt", ".pdf"],
            "chunk_size_kb": 1024
        },
        "performance": {
            "cache_duration_seconds": 300,
            "max_concurrent_uploads": 3,
            "enable_compression": True
        },
        "monitoring": {
            "log_level": "INFO",
            "metrics_retention_days": 30,
            "enable_performance_tracking": True
        }
    }
    
    with open('config/performance.json', 'w') as f:
        json.dump(config, f, indent=2)
    
    print("[OK] Performance configuration created")

def create_monitoring_script():
    """Create a monitoring script for ongoing performance tracking"""
    monitoring_script = '''#!/usr/bin/env python3
"""
Real-time performance monitoring for AI Agent
"""

import time
import psutil
import sqlite3
import json
from datetime import datetime

def monitor_system():
    """Monitor system resources"""
    stats = {
        "timestamp": datetime.now().isoformat(),
        "cpu_percent": psutil.cpu_percent(interval=1),
        "memory_percent": psutil.virtual_memory().percent,
        "disk_usage": psutil.disk_usage('.').percent
    }
    
    # Database stats
    try:
        with sqlite3.connect('data.db') as conn:
            cur = conn.cursor()
            cur.execute('SELECT COUNT(*) FROM content')
            stats['content_count'] = cur.fetchone()[0]
            cur.execute('SELECT COUNT(*) FROM feedback')
            stats['feedback_count'] = cur.fetchone()[0]
    except Exception as e:
        stats['db_error'] = str(e)
    
    return stats

def log_performance():
    """Log performance metrics"""
    stats = monitor_system()
    
    # Save to performance log
    os.makedirs('bucket/performance', exist_ok=True)
    log_file = f'bucket/performance/perf_{int(time.time())}.json'
    
    with open(log_file, 'w') as f:
        json.dump(stats, f, indent=2)
    
    # Print summary
    print(f"CPU: {stats['cpu_percent']:.1f}% | "
          f"Memory: {stats['memory_percent']:.1f}% | "
          f"Disk: {stats['disk_usage']:.1f}%")
    
    return stats

if __name__ == "__main__":
    import os
    while True:
        try:
            log_performance()
            time.sleep(60)  # Monitor every minute
        except KeyboardInterrupt:
            print("\\nMonitoring stopped")
            break
        except Exception as e:
            print(f"Monitoring error: {e}")
            time.sleep(60)
'''
    
    with open('monitor_performance.py', 'w') as f:
        f.write(monitoring_script)
    
    print("[OK] Performance monitoring script created")

def main():
    """Run all optimization tasks"""
    print("=== AI Agent Performance Optimization ===\n")
    
    # Create necessary directories
    os.makedirs('config', exist_ok=True)
    os.makedirs('bucket/performance', exist_ok=True)
    
    optimize_database()
    cleanup_old_files()
    optimize_config()
    create_monitoring_script()
    
    print(f"\n[OK] Optimization completed at {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("\nRecommendations:")
    print("1. Run 'python monitor_performance.py' for real-time monitoring")
    print("2. Schedule this optimization script to run weekly")
    print("3. Monitor database size and consider archiving old data")
    print("4. Check logs regularly for performance bottlenecks")

if __name__ == "__main__":
    main()