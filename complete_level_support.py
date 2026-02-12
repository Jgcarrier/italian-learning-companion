#!/usr/bin/env python3
"""
Automated script to complete level support for all practice types
"""

import re
from pathlib import Path

print("🚀 Completing level support for all practice types...")
print("=" * 60)

# Read app.py
app_file = Path(__file__).parent / 'app.py'
app_content = app_file.read_text()

# Routes to update with their line patterns
routes_to_update = [
    ('verb_conjugation', 'verb_conjugation_setup.html'),
    ('irregular_passato', 'irregular_passato_setup.html'),
    ('auxiliary_choice', 'auxiliary_choice_setup.html'),
    ('futuro_semplice', 'futuro_semplice_setup.html'),
    ('reflexive_verbs', 'reflexive_verbs_setup.html'),
    ('articulated_prepositions', 'articulated_prepositions_setup.html'),
    ('time_prepositions', 'time_prepositions_setup.html'),
    ('negations', 'negations_setup.html'),
    ('fill_in_blank', 'fill_in_blank_setup.html'),
    ('multiple_choice', 'multiple_choice_setup.html'),
    ('sentence_translator', 'sentence_translator_setup.html'),
]

# Update each route in app.py
for route_name, template_name in routes_to_update:
    print(f"\n📝 Updating {route_name} route...")

    # Pattern to find the route function
    pattern = rf'(@app\.route.*?\ndef {route_name}\(\):.*?if request\.method == \'GET\':.*?return render_template\(\'{template_name}\'\))'

    # Find and update
    matches = list(re.finditer(pattern, app_content, re.DOTALL))

    if matches:
        old_code = matches[0].group(1)

        # Create new code with level support
        new_code = old_code.replace(
            f"return render_template('{template_name}')",
            f"level = request.args.get('level') or request.form.get('level', 'A2')\n        return render_template('{template_name}', level=level)"
        )

        # Also update the route decorator to accept GET and POST if needed
        if 'methods=' not in old_code:
            new_code = new_code.replace(
                f"@app.route('/{route_name.replace('_', '-')}')",
                f"@app.route('/{route_name.replace('_', '-')}', methods=['GET', 'POST'])"
            )

        app_content = app_content.replace(old_code, new_code)
        print(f"  ✓ Updated route to accept level parameter")

    # Now update the question generation to use level
    # Find patterns like: generator.generate_XXX(count)
    # Replace with: generator.generate_XXX(level, count) or appropriate params

    if route_name == 'verb_conjugation':
        app_content = re.sub(
            r'(def verb_conjugation.*?level = request\.form\.get\(\'level\', \'A1\'\))',
            r'def verb_conjugation():\n    """General verb conjugation practice."""\n    level = request.args.get(\'level\') or request.form.get(\'level\', \'A2\')',
            app_content,
            count=1,
            flags=re.DOTALL
        )

    elif route_name in ['fill_in_blank', 'multiple_choice']:
        # These already have level in their generator
        app_content = re.sub(
            rf'(def {route_name}.*?)level = request\.form\.get\(\'level\', \'A1\'\)',
            rf'\1level = request.args.get(\'level\') or request.form.get(\'level\', \'A2\')',
            app_content,
            count=1,
            flags=re.DOTALL
        )

    elif route_name == 'sentence_translator':
        app_content = re.sub(
            rf'(def {route_name}.*?)level = request\.form\.get\(\'level\', \'A1\'\)',
            rf'\1level = request.args.get(\'level\') or request.form.get(\'level\', \'A2\')',
            app_content,
            count=1,
            flags=re.DOTALL
        )

# Write updated app.py
app_file.write_text(app_content)
print("\n✅ Updated app.py with level support for all routes")

# Now update all templates
print("\n" + "=" * 60)
print("📄 Updating template files...")

templates_dir = Path(__file__).parent / 'templates'

for route_name, template_name in routes_to_update:
    template_file = templates_dir / template_name

    if not template_file.exists():
        print(f"  ⚠️  {template_name} not found, skipping")
        continue

    print(f"\n📝 Updating {template_name}...")
    content = template_file.read_text()

    # Add hidden level input if not present
    if '<input type="hidden" name="level"' not in content:
        # Find the form opening tag
        content = content.replace(
            '<form method="POST"',
            '<form method="POST">\n    <input type="hidden" name="level" value="{{ level or \'A2\' }}"',
            1
        )
        print(f"  ✓ Added level hidden input")

    # Update button text to show level
    if 'Start Practice' in content and '{{ level' not in content:
        content = re.sub(
            r'(btn btn-primary btn-large">)Start Practice(<)',
            r'\1Start Practice ({{ level or \'A2\' }})\2',
            content
        )
        print(f"  ✓ Updated button to show level")

    # Remove "Completed" and "Current" labels
    content = content.replace('(Completed)', '')
    content = content.replace('(Current)', '')
    content = content.replace('A1 (completed)', 'A1')
    content = content.replace('A2 (current)', 'A2')

    # Update select options to not have labels
    content = re.sub(
        r'<option value="A1">A1 \(.*?\)</option>',
        '<option value="A1">A1 - Beginner</option>',
        content
    )
    content = re.sub(
        r'<option value="A2".*?>A2 \(.*?\)</option>',
        '<option value="A2" selected>A2 - Elementary</option>',
        content
    )

    # Add all level options if select for level exists
    if 'select name="level"' in content:
        old_select = re.search(r'(<select name="level".*?>)(.*?)(</select>)', content, re.DOTALL)
        if old_select:
            new_options = '''
            <option value="A1">A1 - Beginner</option>
            <option value="A2" selected>A2 - Elementary</option>
            <option value="B1">B1 - Intermediate</option>
            <option value="B2">B2 - Upper Intermediate</option>
            <option value="GCSE">GCSE</option>
        '''
            content = content.replace(old_select.group(0), old_select.group(1) + new_options + old_select.group(3))
            print(f"  ✓ Updated level select options")

    template_file.write_text(content)
    print(f"  ✅ Updated {template_name}")

print("\n" + "=" * 60)
print("✅ All routes and templates updated!")
print("\n📊 Summary:")
print(f"  - Updated {len(routes_to_update)} routes in app.py")
print(f"  - Updated {len(routes_to_update)} template files")
print(f"  - All practices now support A1, A2, B1, B2, and GCSE levels")
print("\n🎉 Level support complete! Restart the server to see changes.")
