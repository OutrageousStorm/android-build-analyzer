#!/usr/bin/env python3
"""
analyze.py -- Parse Android Gradle build logs and identify slow tasks
Usage: ./gradlew build --profile > build.log
       python3 analyze.py build.log
"""
import sys, re, json
from collections import defaultdict
from pathlib import Path

def parse_gradle_log(filename):
    content = Path(filename).read_text()
    
    # Look for gradle profile JSON (Android Studio 4.0+)
    match = re.search(r'Build profile:\s*([^\n]+)', content)
    profile_path = match.group(1) if match else None
    
    # Parse task times from log output
    tasks = defaultdict(lambda: {'duration': 0, 'count': 0})
    
    for line in content.splitlines():
        # Match lines like: Task ':app:compileDebugJava' took 3.2s
        task_match = re.search(r"Task '([^']+)' took ([\d.]+)([sm])?", line, re.IGNORECASE)
        if task_match:
            task_name = task_match.group(1)
            duration = float(task_match.group(2))
            unit = task_match.group(3) or 's'
            if unit == 'm':
                duration *= 60
            tasks[task_name]['duration'] += duration
            tasks[task_name]['count'] += 1
    
    # Sort by duration
    sorted_tasks = sorted(tasks.items(), key=lambda x: x[1]['duration'], reverse=True)
    return sorted_tasks, profile_path

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 analyze.py <gradle_build.log>")
        sys.exit(1)
    
    filename = sys.argv[1]
    if not Path(filename).exists():
        print(f"File not found: {filename}")
        sys.exit(1)
    
    tasks, profile = parse_gradle_log(filename)
    
    print(f"\n⏱️  Gradle Build Time Analysis\n")
    print(f"{'Task':<60} {'Time':<10} {'Count'}")
    print("─" * 80)
    
    total_time = 0
    for task, data in tasks[:20]:
        task_short = task.replace(':', '/').split('/')[-1] if ':' in task else task
        time_str = f"{data['duration']:.2f}s"
        total_time += data['duration']
        print(f"{task_short:<60} {time_str:<10} {data['count']}")
    
    if len(tasks) > 20:
        print(f"... +{len(tasks) - 20} more tasks")
    
    print(f"\n{'Total (top 20):':<60} {total_time:.2f}s")
    
    if profile:
        print(f"\nProfile report: {profile}")

if __name__ == "__main__":
    main()
