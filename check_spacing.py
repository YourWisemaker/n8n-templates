#!/usr/bin/env python3
import re
import json
import os

# Define minimum spacing requirements
MIN_HORIZONTAL = 240
MIN_VERTICAL = 200

def analyze_positions(file_path):
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        nodes = data.get('nodes', [])
        positions = []
        
        for node in nodes:
            if 'position' in node:
                x, y = node['position']
                name = node.get('name', 'Unnamed')
                positions.append((x, y, name, file_path))
        
        return positions
    except Exception as e:
        return []

def find_close_nodes(all_positions):
    issues = []
    
    # Group by file
    files = {}
    for pos in all_positions:
        file_path = pos[3]
        if file_path not in files:
            files[file_path] = []
        files[file_path].append(pos)
    
    for file_path, positions in files.items():
        for i, (x1, y1, name1, _) in enumerate(positions):
            for j, (x2, y2, name2, _) in enumerate(positions[i+1:], i+1):
                dx = abs(x2 - x1)
                dy = abs(y2 - y1)
                
                # Check if nodes are too close horizontally or vertically
                too_close_horizontal = dx < MIN_HORIZONTAL and dy == 0
                too_close_vertical = dy < MIN_VERTICAL and dx == 0
                too_close_diagonal = dx < MIN_HORIZONTAL and dy < MIN_VERTICAL and dx > 0 and dy > 0
                
                if too_close_horizontal or too_close_vertical or too_close_diagonal:
                    issues.append({
                        'file': file_path.split('/')[-1],
                        'node1': f'{name1} [{x1}, {y1}]',
                        'node2': f'{name2} [{x2}, {y2}]',
                        'distance': f'dx={dx}, dy={dy}',
                        'type': 'horizontal' if too_close_horizontal else 'vertical' if too_close_vertical else 'diagonal'
                    })
    
    return issues

def main():
    # Scan all JSON files
    all_positions = []
    template_dir = '/Users/wisemaker/n8n-templates/templates/'
    
    for root, dirs, files in os.walk(template_dir):
        for file in files:
            if file.endswith('.json'):
                file_path = os.path.join(root, file)
                positions = analyze_positions(file_path)
                all_positions.extend(positions)
    
    # Find issues
    issues = find_close_nodes(all_positions)
    
    print(f'Node Spacing Analysis Results:')
    print(f'==============================')
    print(f'Minimum horizontal spacing: {MIN_HORIZONTAL}px')
    print(f'Minimum vertical spacing: {MIN_VERTICAL}px')
    print(f'Total templates scanned: {len(set(pos[3] for pos in all_positions))}')
    print(f'Total nodes analyzed: {len(all_positions)}')
    print(f'Spacing issues found: {len(issues)}')
    print()
    
    if issues:
        # Group issues by file
        files_with_issues = {}
        for issue in issues:
            file_name = issue['file']
            if file_name not in files_with_issues:
                files_with_issues[file_name] = []
            files_with_issues[file_name].append(issue)
        
        for file_name, file_issues in files_with_issues.items():
            print(f'📄 {file_name} ({len(file_issues)} issues):')
            for issue in file_issues:
                print(f'  ⚠️  {issue["type"].upper()} spacing issue:')
                print(f'      {issue["node1"]} <-> {issue["node2"]}')
                print(f'      Distance: {issue["distance"]}')
                print()
    else:
        print('✅ No spacing issues found! All nodes meet the minimum spacing requirements.')
        print('\nAll templates follow the spacing guidelines:')
        print(f'- Horizontal spacing ≥ {MIN_HORIZONTAL}px')
        print(f'- Vertical spacing ≥ {MIN_VERTICAL}px')

if __name__ == '__main__':
    main()