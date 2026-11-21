"""Create and smoke-test a versioned local deployment outside the workspace."""

import argparse
from contextlib import redirect_stdout
import hashlib
import io
import json
from pathlib import Path
import runpy
import shutil


def deploy(destination, build_number, commit):
    """Copy the app to a new release and verify the actual deployed file."""
    source = Path(__file__).resolve().parent / "app.py"
    release = Path(destination).resolve() / f"build-{build_number}"
    release.mkdir(parents=True, exist_ok=False)
    target = release / "app.py"
    shutil.copy2(source, target)
    output = io.StringIO()
    with redirect_stdout(output):
        runpy.run_path(str(target), run_name="__main__")
    expected = "Hello, World from Joey Saade!"
    if output.getvalue().strip() != expected:
        raise RuntimeError("Deployed application failed the smoke test")
    manifest = {
        "build_number": str(build_number), "commit": commit,
        "sha256": hashlib.sha256(target.read_bytes()).hexdigest(),
        "output": output.getvalue().strip(), "smoke_test": "PASS",
    }
    (release / "manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8",
    )
    reports = source.parent / "reports"
    reports.mkdir(exist_ok=True)
    shutil.copy2(release / "manifest.json", reports / "deployment.json")
    print(f"Deployed to {release}")
    print(output.getvalue(), end="")
    print("Deployment smoke test: PASS")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--destination", required=True)
    parser.add_argument("--build-number", required=True)
    parser.add_argument("--commit", required=True)
    args = parser.parse_args()
    deploy(args.destination, args.build_number, args.commit)
