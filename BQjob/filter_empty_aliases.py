#!/usr/bin/env python3
"""
Filter out records where both original_aliases and filtered_aliases are empty.
"""

import json
import sys
from pathlib import Path

def filter_empty_aliases(input_file, output_file):
    """
    Filter out records where both original_aliases and filtered_aliases are empty.
    
    Args:
        input_file (str): Path to input JSONL file
        output_file (str): Path to output JSONL file
    """
    input_path = Path(input_file)
    output_path = Path(output_file)
    
    if not input_path.exists():
        print(f"Error: Input file {input_file} does not exist")
        return
    
    total_records = 0
    filtered_records = 0
    kept_records = 0
    
    print(f"Processing {input_file}...")
    
    with open(input_path, 'r', encoding='utf-8') as infile, \
         open(output_path, 'w', encoding='utf-8') as outfile:
        
        for line_num, line in enumerate(infile, 1):
            line = line.strip()
            if not line:
                continue
                
            try:
                record = json.loads(line)
                total_records += 1
                
                # Check if both aliases are empty
                original_aliases = record.get('original_aliases', [])
                filtered_aliases = record.get('filtered_aliases', [])
                
                # Keep record if at least one alias list has content
                if original_aliases or filtered_aliases:
                    outfile.write(line + '\n')
                    kept_records += 1
                else:
                    filtered_records += 1
                    
            except json.JSONDecodeError as e:
                print(f"Warning: Invalid JSON on line {line_num}: {e}")
                continue
    
    print(f"\nFiltering complete!")
    print(f"Total records processed: {total_records}")
    print(f"Records with empty aliases (filtered out): {filtered_records}")
    print(f"Records kept: {kept_records}")
    print(f"Output saved to: {output_file}")

def main():
    if len(sys.argv) != 3:
        print("Usage: python filter_empty_aliases.py <input_file> <output_file>")
        print("Example: python filter_empty_aliases.py filtered_aliases_result_fixed_records.jsonl filtered_aliases_with_content.jsonl")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    
    filter_empty_aliases(input_file, output_file)

if __name__ == "__main__":
    main()
