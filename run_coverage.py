# run_coverage.py
"""
Run tests with coverage and generate reports.
Run: python run_coverage.py
"""

import os
import sys
import subprocess
from datetime import datetime
from pathlib import Path

def run_coverage():
    """Run tests with coverage and generate reports."""
    print("📊 Running tests with coverage...")
    
    Path("test_logs").mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    log_file = Path(f"test_logs/coverage_report_{timestamp}.txt")
    
    # Install coverage if not available
    subprocess.run([sys.executable, "-m", "pip", "install", "coverage"], capture_output=True)
    
    # Run coverage
    cmds = [
        [sys.executable, "-m", "coverage", "run", "manage.py", "test", "core.tests"],
        [sys.executable, "-m", "coverage", "report", "--include=core/*"],
        [sys.executable, "-m", "coverage", "html", "--include=core/*", "-d", "coverage_html"]
    ]
    
    with open(log_file, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write("GOODDEEDS – COVERAGE REPORT\n")
        f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("=" * 80 + "\n\n")
        
        for cmd in cmds:
            f.write(f"$ {' '.join(cmd)}\n")
            f.write("-" * 40 + "\n")
            result = subprocess.run(cmd, capture_output=True, text=True)
            f.write(result.stdout)
            if result.stderr:
                f.write("ERRORS:\n")
                f.write(result.stderr)
            f.write("\n" + "-" * 40 + "\n\n")
    
    print(f"\n📊 Coverage report saved to: {log_file}")
    print("📁 HTML coverage report available at: coverage_html/index.html")
    
    return 0

if __name__ == "__main__":
    sys.exit(run_coverage())