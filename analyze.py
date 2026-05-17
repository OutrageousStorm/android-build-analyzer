#!/usr/bin/env python3
"""
analyze.py -- Analyze Android Gradle build profiles
Requires: ./gradlew build --profile (generates build/reports/profile/profile-<timestamp>.html)
Usage: python3 analyze.py [profile.html] [--top 20]
"""
import sys, re, json, argparse
from pathlib import Path

def find_profile():
    """Find latest profile report"""
    p = Path("build/reports/profile")
    if not p.exists(): return None
    profiles = sorted(p.glob("profile-*.html"), key=lambda x: x.stat().st_mtime, reverse=True)
    return profiles[0] if profiles else None

def parse_html_profile(html_file):
    """Extract task timing from Gradle profile HTML"""
    with open(html_file) as f:
        content = f.read()
    
    tasks = []
    # Look for task rows: <td>task_name</td> <td>duration_ms</td>
    pattern = r'<td[^>]*>([^<]+)</td>\s*<td[^>]*>(\d+)ms</td>'
    for match in re.finditer(pattern, content):
        task = match.group(1).strip()
        duration = int(match.group(2))
        tasks.append((task, duration))
    
    return sorted(tasks, key=lambda x: x[1], reverse=True)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("profile", nargs='?', help="Path to profile HTML")
    parser.add_argument("--top", type=int, default=20)
    parser.add_argument("--json", action="store_true", help="Output JSON")
    args = parser.parse_args()

    profile_path = args.profile and Path(args.profile) or find_profile()
    if not profile_path or not profile_path.exists():
        print("❌ No profile found. Run: ./gradlew build --profile")
        sys.exit(1)

    print(f"📊 Analyzing: {profile_path.name}\n")
    tasks = parse_html_profile(str(profile_path))
    
    if not tasks:
        print("⚠️  No tasks found in profile.")
        return

    total_ms = sum(t[1] for t in tasks)
    print(f"Total build time: {total_ms/1000:.1f}s\n")
    print(f"{'Rank':<5} {'Task':<50} {'Time':<10} {'%'}")
    print("─" * 75)

    for i, (task, duration) in enumerate(tasks[:args.top], 1):
        pct = (duration / total_ms * 100) if total_ms else 0
        bar = "▓" * int(pct / 2)
        print(f"{i:<5} {task[:49]:<50} {duration/1000:>6.2f}s {bar}")

    slow_threshold = total_ms * 0.1  # Tasks taking >10% of total time
    slow = [t for t in tasks if t[1] > slow_threshold]
    if slow:
        print(f"\n⚠️  {len(slow)} tasks take >10% of build time:")
        for task, duration in slow:
            print(f"  • {task} ({duration/1000:.2f}s)")

    if args.json:
        out = {"total_ms": total_ms, "tasks": [{"name": t[0], "duration_ms": t[1]} for t in tasks]}
        print(json.dumps(out, indent=2))

if __name__ == "__main__":
    main()
