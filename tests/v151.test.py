from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = (ROOT / "app.js").read_text(encoding="utf-8")
CSS = (ROOT / "styles.css").read_text(encoding="utf-8")

assert "data-chart-kind=\"cash\"" in APP
assert "data-chart-kind=\"investment\"" in APP
assert "function bindInteractiveCharts" in APP
assert "chart-tooltip" in CSS
assert "chart-readout" in CSS
assert "chart-crosshair" in CSS
assert "ArrowLeft" in APP and "ArrowRight" in APP
assert "Home" in APP and "End" in APP
print("v1.5.1 interactive chart source checks passed")
