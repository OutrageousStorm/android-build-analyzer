# ⏱️ Android Build Analyzer

Analyze Gradle build times — find slow tasks, module dependencies, and bottlenecks.

## Usage

```bash
./gradlew build --profile
python3 analyze.py  # auto-finds profile
```

## Output

- 📊 Total build time breakdown
- 🐢 Slowest tasks ranked
- 🔗 Module dependency graph
- 💡 Optimization suggestions
