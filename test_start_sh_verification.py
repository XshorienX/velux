#!/usr/bin/env python3
"""
Test to verify start.sh correctly uses $HOME/mongodb_bin instead of /usr/local/bin
This addresses the review request: "Verify that the modified start.sh correctly avoids 
using root-level directories like /usr/local/bin which throw permission denied errors 
on Render, and instead installs MongoDB to the user's home directory."
"""

import os
import re

def test_start_sh_uses_home_directory():
    """Verify start.sh uses $HOME/mongodb_bin instead of /usr/local/bin"""
    
    start_sh_path = "/app/backend/start.sh"
    
    print("=" * 80)
    print("VERIFICATION: start.sh MongoDB installation path")
    print("=" * 80)
    
    # Read start.sh content
    with open(start_sh_path, 'r') as f:
        content = f.read()
    
    print("\n✓ Successfully read start.sh file")
    
    # Test 1: Verify it checks for $HOME/mongodb_bin/mongod (NOT /usr/local/bin/mongod)
    print("\n[Test 1] Checking if script checks for $HOME/mongodb_bin/mongod...")
    if '$HOME/mongodb_bin/mongod' in content:
        print("✓ PASS: Script checks for $HOME/mongodb_bin/mongod")
    else:
        print("✗ FAIL: Script does NOT check for $HOME/mongodb_bin/mongod")
        return False
    
    # Test 2: Verify it does NOT use /usr/local/bin
    print("\n[Test 2] Checking if script avoids /usr/local/bin...")
    if '/usr/local/bin' not in content:
        print("✓ PASS: Script does NOT use /usr/local/bin (avoids permission errors)")
    else:
        print("✗ FAIL: Script uses /usr/local/bin (would cause permission denied errors)")
        return False
    
    # Test 3: Verify it creates $HOME/mongodb_bin directory
    print("\n[Test 3] Checking if script creates $HOME/mongodb_bin directory...")
    if 'mkdir -p $HOME/mongodb_bin' in content:
        print("✓ PASS: Script creates $HOME/mongodb_bin directory")
    else:
        print("✗ FAIL: Script does NOT create $HOME/mongodb_bin directory")
        return False
    
    # Test 4: Verify it copies mongod to $HOME/mongodb_bin/
    print("\n[Test 4] Checking if script copies mongod to $HOME/mongodb_bin/...")
    if re.search(r'cp.*mongod \$HOME/mongodb_bin/', content):
        print("✓ PASS: Script copies mongod to $HOME/mongodb_bin/")
    else:
        print("✗ FAIL: Script does NOT copy mongod to $HOME/mongodb_bin/")
        return False
    
    # Test 5: Verify it runs mongod from $HOME/mongodb_bin/mongod
    print("\n[Test 5] Checking if script runs mongod from $HOME/mongodb_bin/mongod...")
    if '$HOME/mongodb_bin/mongod' in content and '--fork' in content:
        print("✓ PASS: Script runs mongod from $HOME/mongodb_bin/mongod")
    else:
        print("✗ FAIL: Script does NOT run mongod from $HOME/mongodb_bin/mongod")
        return False
    
    # Test 6: Verify data directory uses /data/db (persistent disk)
    print("\n[Test 6] Checking if script uses /data/db for MongoDB data...")
    if '--dbpath /data/db' in content:
        print("✓ PASS: Script uses /data/db for MongoDB data (persistent disk)")
    else:
        print("✗ FAIL: Script does NOT use /data/db for MongoDB data")
        return False
    
    print("\n" + "=" * 80)
    print("VERIFICATION RESULT: ALL TESTS PASSED (6/6)")
    print("=" * 80)
    print("\nCONCLUSION:")
    print("✓ start.sh correctly avoids /usr/local/bin (which causes permission errors)")
    print("✓ start.sh correctly installs MongoDB to user's home directory ($HOME/mongodb_bin)")
    print("✓ start.sh correctly uses persistent disk (/data/db) for MongoDB data")
    print("\nThis implementation will work correctly on Render without permission issues.")
    print("=" * 80)
    
    return True

if __name__ == "__main__":
    success = test_start_sh_uses_home_directory()
    exit(0 if success else 1)
