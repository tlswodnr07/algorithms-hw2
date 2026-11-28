#!/usr/bin/env python3
"""Compare separate chaining and linear probing on identical key sets."""

import csv
from pathlib import Path
from random import Random

from src.hash_table import HashTable
from src.linear_probe_hash_table import LinearProbeHashTable


CAPACITY = 997
LOAD_FACTORS = tuple(step / 10 for step in range(1, 10))
SVG_OUTPUT = Path(__file__).with_name("linear_probe_comparison.svg")
PDF_OUTPUT = Path(__file__).with_name("linear_probe_report.pdf")
CSV_OUTPUT = Path(__file__).with_name("results.csv")
CSV_COLUMNS = (
    "load_factor",
    "chain_successful_measured",
    "chain_unsuccessful_measured",
    "linear_successful_measured",
    "linear_unsuccessful_measured",
    "chain_successful_theory",
    "chain_unsuccessful_theory",
    "linear_successful_theory",
    "linear_unsuccessful_theory",
)


def _missing_key_for_start(table, start: int) -> str:
    prefix = f"absent-{start}-"
    code_point = (start - 31 * table._hash(prefix)) % table.capacity
    if code_point > 0x10FFFF:
        raise ValueError("capacity is too large to construct a probe key")
    return prefix + chr(code_point)


def measure_comparison(
    load_factor: float, capacity: int = CAPACITY
) -> tuple[float, float, float, float]:
    """Return chain-success, chain-miss, linear-success, and linear-miss probes."""
    if not 0 < load_factor < 1:
        raise ValueError("load_factor must be between 0 and 1")
    if capacity < 2:
        raise ValueError("capacity must be at least 2")

    chaining = HashTable[str](capacity, max_load_factor=None)
    linear = LinearProbeHashTable[str](capacity, max_load_factor=None)
    sample = Random(2026).sample(
        range(1_000_000_000), round(0.9 * capacity)
    )
    keys = [f"key-{number}" for number in sample[:round(load_factor * capacity)]]
    for key in keys:
        chaining[key] = key
        linear[key] = key

    if keys:
        chaining_success = sum(len(chaining.probe_trace(key)) for key in keys) / len(keys)
        linear_success = sum(len(linear.probe_trace(key)) for key in keys) / len(keys)
    else:
        chaining_success = linear_success = 0.0
    chaining_miss = sum(
        len(chaining.probe_trace(_missing_key_for_start(chaining, start)))
        for start in range(capacity)
    ) / capacity
    linear_miss = sum(
        len(linear.probe_trace(_missing_key_for_start(linear, start)))
        for start in range(capacity)
    ) / capacity
    return chaining_success, chaining_miss, linear_success, linear_miss


def _theory(alpha: float) -> tuple[float, float, float, float]:
    return (
        1 + alpha / 2,
        alpha,
        (1 + 1 / (1 - alpha)) / 2,
        (1 + 1 / (1 - alpha) ** 2) / 2,
    )


def _svg(results: list[tuple[float, ...]]) -> str:
    width, height = 900, 520
    left, right, top, bottom = 80, 28, 38, 72
    plot_width, plot_height = width - left - right, height - top - bottom
    maximum = max(max(row[1:]) for row in results) * 1.08

    def point(alpha: float, cost: float) -> tuple[float, float]:
        return left + alpha * plot_width, top + (1 - cost / maximum) * plot_height

    series = (
        ("Chain successful", 1, "#1565c0", False),
        ("Chain unsuccessful", 2, "#c62828", False),
        ("Linear successful", 3, "#2e7d32", False),
        ("Linear unsuccessful", 4, "#6a1b9a", False),
        ("Chain successful theory", 5, "#1565c0", True),
        ("Chain unsuccessful theory", 6, "#c62828", True),
        ("Linear successful theory", 7, "#2e7d32", True),
        ("Linear unsuccessful theory", 8, "#6a1b9a", True),
    )
    lines = []
    for label, column, color, dashed in series:
        points = " ".join(
            f"{point(row[0], row[column])[0]:.1f},{point(row[0], row[column])[1]:.1f}"
            for row in results
        )
        dash = ' stroke-dasharray="6 4"' if dashed else ""
        lines.append(
            f'<polyline points="{points}" fill="none" stroke="{color}" '
            f'stroke-width="2"{dash}><title>{label}</title></polyline>'
        )

    grid = []
    for tick in range(0, int(maximum) + 1, max(1, int(maximum // 10))):
        y = point(0, tick)[1]
        grid.append(
            f'<line x1="{left}" y1="{y:.1f}" x2="{width-right}" y2="{y:.1f}" '
            f'stroke="#ddd"/><text x="{left-10}" y="{y+4:.1f}" '
            f'text-anchor="end">{tick}</text>'
        )
    legend = []
    for position, (label, _, color, dashed) in enumerate(series):
        x = left + (position % 2) * 365
        y = height - 42 + (position // 2) * 16
        dash = ' stroke-dasharray="5 3"' if dashed else ""
        legend.append(
            f'<line x1="{x}" y1="{y-4}" x2="{x+25}" y2="{y-4}" '
            f'stroke="{color}"{dash}/><text x="{x+32}" y="{y}">{label}</text>'
        )
    ticks = "".join(
        f'<text x="{point(alpha, 0)[0]:.1f}" y="{top+plot_height+20}" '
        f'text-anchor="middle">{alpha:.1f}</text>'
        for alpha in (0.1, 0.3, 0.5, 0.7, 0.9)
    )
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
<title>Hash table collision strategy comparison</title><rect width="100%" height="100%" fill="white"/>
{''.join(grid)}
<line x1="{left}" y1="{top+plot_height}" x2="{width-right}" y2="{top+plot_height}" stroke="black"/>
<line x1="{left}" y1="{top}" x2="{left}" y2="{top+plot_height}" stroke="black"/>
{''.join(lines)}{ticks}
<text x="{width/2}" y="{top+plot_height+42}" text-anchor="middle">Load factor (alpha)</text>
<text x="20" y="{height/2}" text-anchor="middle" transform="rotate(-90 20 {height/2})">Average probes</text>
{''.join(legend)}</svg>
"""


def _write_pdf(lines: list[str]) -> None:
    commands = ["BT", "/F1 10 Tf", "50 750 Td", "14 TL"]
    for index, line in enumerate(lines):
        if index:
            commands.append("T*")
        escaped = line.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
        commands.append(f"({escaped}) Tj")
    commands.append("ET")
    stream = "\n".join(commands).encode("ascii")
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
        b"<< /Length " + str(len(stream)).encode("ascii") + b" >>\nstream\n" + stream + b"\nendstream",
    ]
    pdf = bytearray(b"%PDF-1.4\n")
    offsets = [0]
    for number, body in enumerate(objects, start=1):
        offsets.append(len(pdf))
        pdf.extend(f"{number} 0 obj\n".encode("ascii"))
        pdf.extend(body)
        pdf.extend(b"\nendobj\n")
    xref_offset = len(pdf)
    pdf.extend(f"xref\n0 {len(offsets)}\n".encode("ascii"))
    pdf.extend(b"0000000000 65535 f \n")
    for offset in offsets[1:]:
        pdf.extend(f"{offset:010d} 00000 n \n".encode("ascii"))
    pdf.extend(
        f"trailer\n<< /Size {len(offsets)} /Root 1 0 R >>\n"
        f"startxref\n{xref_offset}\n%%EOF\n".encode("ascii")
    )
    PDF_OUTPUT.write_bytes(pdf)


def _write_csv(results: list[tuple[float, ...]], output: Path = CSV_OUTPUT) -> None:
    with output.open("w", encoding="utf-8", newline="") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(CSV_COLUMNS)
        writer.writerows(results)


def run() -> list[tuple[float, ...]]:
    results = []
    for alpha in LOAD_FACTORS:
        observed = measure_comparison(alpha)
        results.append((alpha, *observed, *_theory(alpha)))
    SVG_OUTPUT.write_text(_svg(results), encoding="utf-8")
    _write_csv(results)

    report_lines = [
        "Hash Table Collision Strategies: Probe Comparison",
        "Same Horner hash, key sequence, and capacity (997); one measurement per load factor.",
        "Separate chaining theory: successful 1 + alpha/2; unsuccessful alpha.",
        "Linear probing theory (uniform hashing approximation): successful (1+1/(1-alpha))/2;",
        "unsuccessful (1+1/(1-alpha)^2)/2. Clustering can increase observed costs.",
        "",
        "alpha | chain S/U | linear S/U | theory chain S/U | theory linear S/U",
    ]
    for row in results:
        alpha, chain_s, chain_u, linear_s, linear_u, theory_cs, theory_cu, theory_ls, theory_lu = row
        report_lines.append(
            f"{alpha:.1f} | {chain_s:.2f}/{chain_u:.2f} | {linear_s:.2f}/{linear_u:.2f} | "
            f"{theory_cs:.2f}/{theory_cu:.2f} | {theory_ls:.2f}/{theory_lu:.2f}"
        )
    report_lines.extend(
        [
            "",
            "Interpretation: chaining unsuccessful searches track alpha because they inspect",
            "the selected bucket only. Linear probing forms contiguous clusters; unsuccessful",
            "searches rise sharply near full occupancy. The seeded key permutation is",
            "reproducible; at high loads its clustering and finite capacity differ from the",
            "uniform-hashing approximation. See linear_probe_comparison.svg for both curves.",
        ]
    )
    _write_pdf(report_lines)

    print("alpha | chain successful/unsuccessful | linear successful/unsuccessful")
    for row in results:
        print(f"{row[0]:.1f}   | {row[1]:.3f}/{row[2]:.3f}                    | {row[3]:.3f}/{row[4]:.3f}")
    print(f"\nWrote {SVG_OUTPUT}\nWrote {CSV_OUTPUT}\nWrote {PDF_OUTPUT}")
    return results


if __name__ == "__main__":
    run()
