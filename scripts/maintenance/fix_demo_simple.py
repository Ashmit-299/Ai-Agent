#!/usr/bin/env python3
"""
Simple demo user fix
"""

import sqlite3
import time
from passlib.context import CryptContext

# Create password context
pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
demo_hash = pwd_context.hash('demo1234')

# Connect to database
conn = sqlite3.connect('data.db')
with conn:
    cur = conn.cursor()
    
    # Update demo user password
    cur.execute('UPDATE user SET password_hash=? WHERE username=?', (demo_hash, 'demo'))
    
    # Verify the password works
    cur.execute('SELECT password_hash FROM user WHERE username=?', ('demo',))
    result = cur.fetchone()
    
    if result and pwd_context.verify('demo1234', result[0]):
        print("SUCCESS: Demo user password updated and verified")
        print("Credentials: username=demo, password=demo1234")
    else:
        print("FAILED: Password verification failed")

conn.close()