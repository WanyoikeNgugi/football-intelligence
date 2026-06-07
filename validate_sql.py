import sqlglot
import sys
import pathlib

files = [f for f in sys.argv[1:] if f.endswith(".sql")]
errors = []

for f in files:
    content = pathlib.Path(f).read_text()
    # skip dbt models that use Jinja templating
    if "{{" in content:
        continue
    try:
        sqlglot.parse(content, error_level=sqlglot.ErrorLevel.RAISE)
    except Exception as e:
        errors.append(f"{f}: {e}")

if errors:
    print("\n".join(errors))
    sys.exit(1)
