#!/usr/bin/env python3
"""Measure separate-chaining lookup costs at controlled load factors."""

from pathlib import Path


CAPACITY = 257
LOAD_FACTORS = tuple(step / 4 for step in range(1, 17))
OUTPUT = Path(__file__).with_name("probe_results.svg")


def _bucket_index(key: str, capacity: int) -> int:
    value = 0
    for character in key:
        value = (value * 31 + ord(character)) % capacity
    return value


def measure(load_factor: float, capacity: int = CAPACITY) -> tuple[float, float]:
    """Return observed successful and unsuccessful node comparisons."""
    if load_factor <= 0 or capacity <= 0:
        raise ValueError("load_factor and capacity must be positive")

    buckets: list[list[str]] = [[] for _ in range(capacity)]
    count = round(load_factor * capacity)
    keys = [f"key-{number}" for number in range(count)]
    for key in keys:
        buckets[_bucket_index(key, capacity)].insert(0, key)

    successful_probes = 0
    for key in keys:
        bucket = buckets[_bucket_index(key, capacity)]
        for candidate in bucket:
            successful_probes += 1
            if candidate == key:
                break

    unsuccessful_probes = 0
    for index, bucket in enumerate(buckets):
        missing_key = f"missing-{index}"
        if missing_key in keys:
            raise RuntimeError("generated unsuccessful query unexpectedly exists")
        for _candidate in bucket:
            unsuccessful_probes += 1

    successful_average = successful_probes / count if count else 0.0
    unsuccessful_average = unsuccessful_probes / capacity
    return successful_average, unsuccessful_average


def _svg(results: list[tuple[float, float, float]]) -> str:
    width, height = 800, 480
    left, right, top, bottom = 72, 24, 32, 64
    plot_width, plot_height = width - left - right, height - top - bottom
    max_y = max(4.5, max(row[3] for row in results) * 1.08)

    def point(x: float, y: float) -> tuple[float, float]:
        return left + x / 4 * plot_width, top + (1 - y / max_y) * plot_height

    observed_success = " ".join(
        f"{point(alpha, success)[0]:.1f},{point(alpha, success)[1]:.1f}"
        for alpha, success, _, _ in results
    )
    theoretical_success = " ".join(
        f"{point(alpha, expected)[0]:.1f},{point(alpha, expected)[1]:.1f}"
        for alpha, _, expected, _ in results
    )
    observed_failure = " ".join(
        f"{point(alpha, failure)[0]:.1f},{point(alpha, failure)[1]:.1f}"
        for alpha, _, _, failure in results
    )
    theoretical_failure = " ".join(
        f"{point(alpha, alpha)[0]:.1f},{point(alpha, alpha)[1]:.1f}"
        for alpha, _, _, _ in results
    )

    grid = []
    for tick in range(0, int(max_y) + 1):
        y = point(0, tick)[1]
        grid.append(
            f'<line x1="{left}" y1="{y:.1f}" x2="{width-right}" y2="{y:.1f}" '
            'stroke="#ddd"/><text x="40" y="{:.1f}" text-anchor="end">{}</text>'.format(
                y + 4, tick
            )
        )
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
<title>Separate chaining probes by load factor</title>
<rect width="100%" height="100%" fill="white"/>
{''.join(grid)}
<line x1="{left}" y1="{top+plot_height}" x2="{width-right}" y2="{top+plot_height}" stroke="black"/>
<line x1="{left}" y1="{top}" x2="{left}" y2="{top+plot_height}" stroke="black"/>
<polyline points="{observed_success}" fill="none" stroke="#1565c0" stroke-width="2"/>
<polyline points="{theoretical_success}" fill="none" stroke="#1565c0" stroke-dasharray="6 4"/>
<polyline points="{observed_failure}" fill="none" stroke="#c62828" stroke-width="2"/>
<polyline points="{theoretical_failure}" fill="none" stroke="#c62828" stroke-dasharray="6 4"/>
<text x="{width/2}" y="{height-18}" text-anchor="middle">Load factor (alpha)</text>
<text x="18" y="{height/2}" text-anchor="middle" transform="rotate(-90 18 {height/2})">Average node comparisons</text>
<text x="{left}" y="18">Solid: measured; dashed: theory. Blue: successful; red: unsuccessful</text>
{''.join(f'<text x="{point(alpha, 0)[0]:.1f}" y="{top+plot_height+22}" text-anchor="middle">{alpha:g}</text>' for alpha in (0, 1, 2, 3, 4))}
</svg>
"""


def run() -> list[tuple[float, float, float, float]]:
    results = []
    for alpha in LOAD_FACTORS:
        success, failure = measure(alpha)
        results.append((alpha, success, 1 + alpha / 2, failure))
    OUTPUT.write_text(_svg(results), encoding="utf-8")
    print("alpha  successful measured/theory  unsuccessful measured/theory")
    for alpha, success, expected_success, failure in results:
        print(
            f"{alpha:4.2f}  {success:8.3f}/{expected_success:5.3f}"
            f"                  {failure:8.3f}/{alpha:5.3f}"
        )
    print(f"\nWrote {OUTPUT}")
    return results


if __name__ == "__main__":
    run()
