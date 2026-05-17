# 📊 Android Build Analyzer

Visualize Android project build times and dependency graphs.

## Features
- Parse Gradle build logs
- Identify slowest modules
- Visualize dependency tree
- Generate HTML reports
- Suggest optimization targets

## Usage
```bash
pip install -r requirements.txt

# Analyze a build log
python3 analyze.py --log build.log --output report.html

# Visualize module deps
python3 visualize_deps.py app/build.gradle --format svg
```
