"""
Script to fix Pydantic v2 compatibility issues in schema files.

This script automatically updates:
- @validator to @field_validator with @classmethod
- @root_validator to @model_validator
- validator imports to field_validator, model_validator
"""

import os
import re

def fix_pydantic_v2_file(filepath):
    """Fix Pydantic v2 compatibility issues in a single file."""
    print(f"Processing {filepath}...")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # Fix imports
    content = re.sub(
        r'from pydantic import ([^,\n]*,\s*)?validator([,\s][^,\n]*)?',
        lambda m: f"from pydantic import {m.group(1) or ''}field_validator{m.group(2) or ''}",
        content
    )
    
    content = re.sub(
        r'from pydantic import ([^,\n]*,\s*)?root_validator([,\s][^,\n]*)?',
        lambda m: f"from pydantic import {m.group(1) or ''}model_validator{m.group(2) or ''}",
        content
    )
    
    # Add missing imports if needed
    if '@field_validator' in content and 'field_validator' not in content:
        content = re.sub(
            r'from pydantic import ([^\n]+)',
            r'from pydantic import \1, field_validator',
            content,
            count=1
        )
    
    if '@model_validator' in content and 'model_validator' not in content:
        content = re.sub(
            r'from pydantic import ([^\n]+)',
            r'from pydantic import \1, model_validator',
            content,
            count=1
        )
    
    # Fix @validator decorators
    content = re.sub(
        r'(\s+)@validator\(([^)]+)\)\s*\n(\s+)def (\w+)\(cls, v\):',
        r'\1@field_validator(\2)\n\1@classmethod\n\3def \4(cls, v):',
        content
    )
    
    # Fix @root_validator decorators
    content = re.sub(
        r'(\s+)@root_validator\s*\n(\s+)def (\w+)\(cls, values\):',
        r'\1@model_validator(mode=\'after\')\n\2def \3(self):',
        content
    )
    
    # Fix root validator method bodies to use self instead of values
    def fix_root_validator_body(match):
        indent = match.group(1)
        method_name = match.group(2)
        body = match.group(3)
        
        # Replace values.get() with self.attribute
        body = re.sub(r'values\.get\([\'"](\w+)[\'"]\)', r'self.\1', body)
        
        # Replace return values with return self
        body = re.sub(r'return values\b', 'return self', body)
        
        return f'{indent}@model_validator(mode=\'after\')\n{indent}def {method_name}(self):{body}'
    
    # More comprehensive root validator fix
    content = re.sub(
        r'(\s+)@model_validator\(mode=\'after\'\)\s*\n(\s+)def (\w+)\(self\):(.*?)(?=\n\s+(?:@|\w+\s*=|\w+\s*:|\s*$))',
        fix_root_validator_body,
        content,
        flags=re.DOTALL
    )
    
    if content != original_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✓ Updated {filepath}")
        return True
    else:
        print(f"- No changes needed for {filepath}")
        return False

def main():
    """Fix all schema files."""
    schema_dir = "schemas"
    
    if not os.path.exists(schema_dir):
        print(f"Schema directory {schema_dir} not found!")
        return
    
    files_updated = 0
    
    for filename in os.listdir(schema_dir):
        if filename.endswith('.py') and filename != '__init__.py':
            filepath = os.path.join(schema_dir, filename)
            if fix_pydantic_v2_file(filepath):
                files_updated += 1
    
    print(f"\nCompleted! Updated {files_updated} files.")

if __name__ == "__main__":
    main()