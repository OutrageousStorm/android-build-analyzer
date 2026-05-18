#!/usr/bin/env python3
"""
analyze.py -- Gradle build log analyzer
Parses Gradle output and identifies bottlenecks, slow tasks, and optimization opportunities
Usage: python3 analyze.py build.log [--json] [--top N]
"""
import re, sys, json, argparse
from collections import defaultdict
from datetime import datetime

class GradleAnalyzer:
    def __init__(self, logfile):
        self.logfile = logfile
        self.tasks = []
        self.total_time = 0
        self.warnings = []
        
    def parse(self):
        with open(self.logfile) as f:
            content = f.read()
        
        # Extract task execution times
        # Pattern: ":app:compileDebugKotlin 4.5s"
        pattern = r':[\w:]+\s+([\d.]+)s'
        for match in re.finditer(pattern, content):
            time_str = match.group(1)
            try:
                seconds = float(time_str)
                task_name = match.group(0).split()[0]
                self.tasks.append({
                    'name': task_name,
                    'time': seconds,
                    'percentage': 0
                })
            except ValueError:
                pass
        
        # Extract total build time
        total_match = re.search(r'BUILD SUCCESSFUL.*?(\d+[ms\.]+)', content)
        if total_match:
            time_str = total_match.group(1)
            self.total_time = self._parse_time(time_str)
        
        # Look for warnings
        if 'warning' in content.lower():
            self.warnings = re.findall(r'warning:(.+)', content, re.IGNORECASE)
        
        # Calculate percentages
        total = sum(t['time'] for t in self.tasks)
        for task in self.tasks:
            task['percentage'] = round((task['time'] / total * 100), 1) if total else 0
        
        # Sort by time
        self.tasks.sort(key=lambda x: x['time'], reverse=True)
    
    def _parse_time(self, s):
        s = s.lower()
        if 'm' in s: return int(s.split('m')[0]) * 60
        if 's' in s: return float(s.split('s')[0])
        return 0
    
    def print_report(self, top=10):
        print('\n📊 Gradle Build Analysis')
        print('─' * 60)
        print(f'Total build time: {self.total_time:.1f}s')
        print(f'Total tasks: {len(self.tasks)}')
        if self.warnings:
            print(f'Warnings: {len(self.warnings)}')
        
        print(f'\nTop {min(top, len(self.tasks))} slowest tasks:')
        for i, task in enumerate(self.tasks[:top]):
            bar = '█' * int(task['percentage'] / 5) + '░' * (20 - int(task['percentage'] / 5))
            print(f"  {bar} {task['name']:<40} {task['time']:6.2f}s ({task['percentage']:5.1f}%)")
        
        if self.warnings:
            print(f'\nWarnings:')
            for w in self.warnings[:5]:
                print(f"  ⚠️  {w[:80]}")
    
    def to_json(self):
        return json.dumps({
            'total_time': self.total_time,
            'task_count': len(self.tasks),
            'top_tasks': self.tasks[:10],
            'warnings': len(self.warnings)
        }, indent=2)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('logfile', help='Gradle build log file')
    parser.add_argument('--json', action='store_true', help='Output as JSON')
    parser.add_argument('--top', type=int, default=10, help='Show top N tasks')
    args = parser.parse_args()
    
    try:
        analyzer = GradleAnalyzer(args.logfile)
        analyzer.parse()
        if args.json:
            print(analyzer.to_json())
        else:
            analyzer.print_report(args.top)
    except FileNotFoundError:
        print(f'File not found: {args.logfile}')
        sys.exit(1)

if __name__ == '__main__':
    main()
