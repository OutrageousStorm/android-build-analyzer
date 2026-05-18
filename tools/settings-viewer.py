#!/usr/bin/env python3
"""
settings-viewer.py -- Browse and search Android system settings
View global, secure, system namespaces. Search by key or value.
Usage: python3 settings-viewer.py [--namespace secure] [--search "wifi"]
"""
import subprocess, re, argparse

def adb(cmd):
    r = subprocess.run(f"adb shell {cmd}", shell=True, capture_output=True, text=True)
    return r.stdout.strip()

def get_settings(namespace="global"):
    raw = adb(f"settings list {namespace}")
    settings = {}
    for line in raw.splitlines():
        if "=" in line:
            k, v = line.split("=", 1)
            settings[k.strip()] = v.strip()
    return settings

def search_settings(ns, keyword):
    settings = get_settings(ns)
    results = {k: v for k, v in settings.items() 
               if keyword.lower() in k.lower() or keyword.lower() in v.lower()}
    return results

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--namespace", default="global", choices=["global", "secure", "system"])
    parser.add_argument("--search", help="Search by key or value")
    parser.add_argument("--set", nargs=2, metavar=("KEY", "VALUE"), help="Set a setting")
    args = parser.parse_args()

    if args.set:
        key, val = args.set
        adb(f"settings put {args.namespace} {key} {val}")
        print(f"✓ Set {args.namespace}/{key} = {val}")
        return

    print(f"\n📋 {args.namespace.upper()} Settings")
    print("=" * 60)

    if args.search:
        results = search_settings(args.namespace, args.search)
        print(f"Found {len(results)} matches for '{args.search}'\n")
        for k, v in sorted(results.items()):
            print(f"  {k:<45} {v[:30]}")
    else:
        settings = get_settings(args.namespace)
        print(f"Total: {len(settings)} settings\n")
        for k, v in sorted(settings.items()):
            print(f"  {k:<45} {v[:30]}")

if __name__ == "__main__":
    main()
