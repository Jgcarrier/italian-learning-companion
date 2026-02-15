#!/usr/bin/env python3
"""
Add session['level'] = level to all practice routes that don't have it.
"""

import re

# Read the file
with open('app.py', 'r') as f:
    content = f.read()

# Find all places where we set start_time and add level after it
# But only if level isn't already set
lines = content.split('\n')
modified_lines = []
i = 0

while i < len(lines):
    line = lines[i]
    modified_lines.append(line)

    # Check if this line sets start_time
    if "session['start_time'] = time.time()" in line:
        # Check if the next line already sets level
        if i + 1 < len(lines) and "session['level']" in lines[i + 1]:
            # Already has level, skip
            pass
        else:
            # Add level storage
            indent = len(line) - len(line.lstrip())
            level_line = ' ' * indent + "session['level'] = level  # Store level for navigation"
            modified_lines.append(level_line)

    i += 1

# Write back
with open('app.py', 'w') as f:
    f.write('\n'.join(modified_lines))

print("✅ Added session['level'] to all practice routes")
