#!/usr/bin/env python3
"""
Force SQLite Mode - Disable Supabase completely
"""

import os

def force_sqlite():
    print("🔧 Forcing SQLite Mode")
    print("=" * 30)
    
    # Read .env
    env_content = ""
    if os.path.exists('.env'):
        with open('.env', 'r') as f:
            env_content = f.read()
    
    # Comment out all Supabase variables
    lines = env_content.split('\n')
    new_lines = []
    
    for line in lines:
        if any(line.startswith(prefix) for prefix in [
            'DATABASE_URL=postgresql://',
            'SUPABASE_URL=',
            'SUPABASE_ANON_KEY=',
            'SUPABASE_DB_PASSWORD='
        ]):
            new_lines.append(f"# {line}")
        else:
            new_lines.append(line)
    
    # Add SQLite configuration
    new_lines.extend([
        "",
        "# SQLite Configuration (Forced)",
        "DATABASE_URL=sqlite:///./ai_agent.db",
        "USE_SUPABASE_STORAGE=false",
        "BHIV_STORAGE_BACKEND=local"
    ])
    
    # Write back
    with open('.env', 'w') as f:
        f.write('\n'.join(new_lines))
    
    print("✅ Supabase disabled")
    print("✅ SQLite enabled")
    print("✅ Local storage enabled")
    
    return True

if __name__ == "__main__":
    force_sqlite()