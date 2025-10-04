#!/usr/bin/env python3
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
            print("\nMonitoring stopped")
            break
        except Exception as e:
            print(f"Monitoring error: {e}")
            time.sleep(60)
