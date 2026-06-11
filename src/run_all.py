"""Run the full project pipeline in a reproducible order."""

from pathlib import Path
import subprocess
import sys


PIPELINE_STEPS = [
    ("Data cleaning", "data_cleaning.py"),
    ("Load to SQLite", "load_to_sqlite.py"),
    ("Feature engineering", "feature_engineering.py"),
    ("Financial metrics", "run_financial_metrics.py"),
    ("Portfolio analysis", "run_portfolio_analysis.py"),
    ("Predictive modeling", "modeling.py"),
]


def run_pipeline():
    """Run each pipeline script and stop immediately if a step fails."""
    project_root = Path(__file__).resolve().parents[1]
    src_dir = project_root / "src"

    for step_name, script_name in PIPELINE_STEPS:
        script_path = src_dir / script_name
        relative_script_path = script_path.relative_to(project_root)
        print(f"\n=== {step_name}: {relative_script_path} ===", flush=True)
        subprocess.run([sys.executable, str(script_path)], cwd=project_root, check=True)

    print("Pipeline completed successfully.")


if __name__ == "__main__":
    run_pipeline()
