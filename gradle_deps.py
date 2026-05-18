#!/usr/bin/env python3
"""
gradle_deps.py -- Analyze and visualize Android Gradle dependencies
Shows dependency tree, identifies heavy libraries, detects version conflicts.
Usage: python3 gradle_deps.py --tree
       python3 gradle_deps.py --sizes
       python3 gradle_deps.py --conflicts
"""
import subprocess, json, sys, argparse, re

def get_deps_tree():
    """Run gradle dependencies task"""
    result = subprocess.run(
        ['./gradlew', 'dependencies', '--configuration=releaseRuntimeClasspath'],
        capture_output=True, text=True
    )
    return result.stdout

def parse_tree(output):
    """Parse gradle dependency output"""
    lines = output.splitlines()
    deps = {}
    stack = []
    
    for line in lines:
        # Count leading spaces to determine depth
        stripped = line.lstrip()
        depth = (len(line) - len(stripped)) // 4
        
        # Match dependency format: +--- or \--- or |
        match = re.search(r'[+|\\].*?(\S+):(\S+):(\S+)', stripped)
        if not match:
            continue
        
        group, artifact, version = match.groups()
        key = f"{group}:{artifact}"
        
        if key not in deps:
            deps[key] = {'versions': set(), 'depth': depth}
        deps[key]['versions'].add(version)
    
    return deps

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--tree', action='store_true', help='Show dependency tree')
    parser.add_argument('--sizes', action='store_true', help='Show largest libraries')
    parser.add_argument('--conflicts', action='store_true', help='Show version conflicts')
    args = parser.parse_args()

    tree_out = get_deps_tree()
    deps = parse_tree(tree_out)

    if args.conflicts or (not args.tree and not args.sizes):
        conflicts = {k: v['versions'] for k, v in deps.items() if len(v['versions']) > 1}
        if conflicts:
            print("⚠️  Version Conflicts:\n")
            for k, versions in sorted(conflicts.items()):
                print(f"  {k}: {', '.join(sorted(versions))}")
        else:
            print("✅ No version conflicts detected")

    if args.tree:
        print("\n📦 Dependency Tree:\n")
        for k, v in sorted(deps.items()):
            indent = "  " * v['depth']
            print(f"{indent}{k} ({', '.join(v['versions'])})")

    if args.sizes:
        print("\n💾 Largest Dependencies (by artifact name length as proxy):\n")
        by_size = sorted(deps.items(), key=lambda x: len(x[0]), reverse=True)
        for k, _ in by_size[:20]:
            print(f"  {k}")

if __name__ == "__main__":
    main()
