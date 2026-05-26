#!/usr/bin/env python3
"""
make_figures.py — regenerate the three static SVG figures for the site.

Every number hard-coded below is a VERIFIED value taken from VERIFICATION_REPORT.md
(which in turn cites the on-cluster job logs / metrics files). No structure files or
large metrics CSVs are read; the figures are built only from these small scalars so the
provenance is auditable here. Run from the `site/` directory:

    python3 assets/figures/make_figures.py

Outputs (overwritten): assets/figures/{training_curve,repaint_sweep,design_degradation}.svg

Sources (see VERIFICATION_REPORT.md):
  - Training val_loss:  ln_train_h200_12124078.out:76 (ep0=977.76),
                        ln_train_h200_12151181.out:907 (ep48=49.913, global min),
                        12151181 (ep57=60.78, next-lowest), ...12151181.out:1490 (ep63=106.37, last).
  - RePaint sweep:      job 12329152 (r=1: 29/2500; r=5: 85/2500),
                        job 12340606 (r=10: 57/1500; r=20: 39/750).
  - Design degradation: job 14292188 (mask1=126, mask2=4),
                        job 14344725 (mask3=0; maskall=0/6300).
"""
import os

OUT = os.path.dirname(os.path.abspath(__file__))

# Shared palette
INK = "#1e293b"      # slate-800 text/axes
GRID = "#e2e8f0"     # slate-200 gridlines
BLUE = "#2563eb"     # accent
GREEN = "#16a34a"    # "works"
AMBER = "#d97706"    # working point
RED = "#dc2626"      # "fails"
MUTED = "#64748b"    # slate-500 captions

FONT = 'font-family="-apple-system,Segoe UI,Helvetica,Arial,sans-serif"'


def svg_header(w, h, title, desc):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
        f'width="{w}" height="{h}" role="img" aria-labelledby="t d">\n'
        f'  <title id="t">{title}</title>\n  <desc id="d">{desc}</desc>\n'
        f'  <rect x="0" y="0" width="{w}" height="{h}" fill="#ffffff"/>\n'
    )


# ---------------------------------------------------------------------------
# Figure 1 — training val_loss trajectory (the four recorded epochs)
# ---------------------------------------------------------------------------
def training_curve():
    W, H = 640, 380
    L, R, T, B = 72, 28, 44, 56
    x0, x1 = L, W - R
    y0, y1 = T, H - B
    EP_MAX, LOSS_MAX = 63, 1000
    # (epoch, val_loss, label) — the only epochs VERIFICATION_REPORT records individually
    pts = [(0, 977.76), (48, 49.913), (57, 60.78), (63, 106.37)]

    def px(ep):
        return x0 + (ep / EP_MAX) * (x1 - x0)

    def py(v):
        return y1 - (v / LOSS_MAX) * (y1 - y0)

    s = [svg_header(W, H, "Training validation loss",
                    "Validation loss falls from 977.8 at epoch 0 to a minimum of 49.9 at "
                    "epoch 48, then rises; early stopping fires at epoch 63.")]
    s.append(f'  <text x="{W/2:.0f}" y="24" text-anchor="middle" {FONT} '
             f'font-size="15" font-weight="600" fill="{INK}">Fine-tuning validation loss '
             f'(977.8 &#8594; 49.9, ~95% &#8595;)</text>')
    # y gridlines + ticks
    for v in (0, 250, 500, 750, 1000):
        y = py(v)
        s.append(f'  <line x1="{x0}" y1="{y:.1f}" x2="{x1}" y2="{y:.1f}" stroke="{GRID}" stroke-width="1"/>')
        s.append(f'  <text x="{x0-8}" y="{y+4:.1f}" text-anchor="end" {FONT} font-size="11" '
                 f'fill="{MUTED}">{v}</text>')
    # x ticks
    for ep in (0, 16, 32, 48, 63):
        x = px(ep)
        s.append(f'  <line x1="{x:.1f}" y1="{y1}" x2="{x:.1f}" y2="{y1+5}" stroke="{MUTED}" stroke-width="1"/>')
        s.append(f'  <text x="{x:.1f}" y="{y1+20}" text-anchor="middle" {FONT} font-size="11" '
                 f'fill="{MUTED}">{ep}</text>')
    # axis labels
    s.append(f'  <text x="{(x0+x1)/2:.0f}" y="{H-10}" text-anchor="middle" {FONT} '
             f'font-size="12" fill="{INK}">epoch</text>')
    s.append(f'  <text x="16" y="{(y0+y1)/2:.0f}" text-anchor="middle" {FONT} font-size="12" '
             f'fill="{INK}" transform="rotate(-90 16 {(y0+y1)/2:.0f})">validation loss</text>')
    # trajectory line through the recorded epochs (dashed: intermediate epochs not individually logged)
    path = " ".join(f"{px(ep):.1f},{py(v):.1f}" for ep, v in pts)
    s.append(f'  <polyline points="{path}" fill="none" stroke="{BLUE}" stroke-width="2" '
             f'stroke-dasharray="5 4" opacity="0.7"/>')
    # markers
    for ep, v in pts:
        best = (ep == 48)
        col = GREEN if best else BLUE
        rad = 6 if best else 4.5
        s.append(f'  <circle cx="{px(ep):.1f}" cy="{py(v):.1f}" r="{rad}" fill="{col}" '
                 f'stroke="#fff" stroke-width="1.5"/>')
    # annotations
    s.append(f'  <text x="{px(0)+8:.1f}" y="{py(977.76)+4:.1f}" {FONT} font-size="11.5" '
             f'fill="{INK}">epoch 0: 977.8</text>')
    s.append(f'  <text x="{px(48):.1f}" y="{py(49.913)+22:.1f}" text-anchor="middle" {FONT} '
             f'font-size="11.5" font-weight="600" fill="{GREEN}">epoch 48: 49.9 (best)</text>')
    s.append(f'  <text x="{px(63)-4:.1f}" y="{py(106.37)-10:.1f}" text-anchor="end" {FONT} '
             f'font-size="11" fill="{MUTED}">ep 63: 106.4 (early-stop)</text>')
    s.append('</svg>\n')
    return "\n".join(s)


# ---------------------------------------------------------------------------
# Figure 2 — RePaint resample sweep (yield % by r)
# ---------------------------------------------------------------------------
def repaint_sweep():
    W, H = 640, 380
    L, R, T, B = 60, 28, 46, 66
    x0, x1 = L, W - R
    y0, y1 = T, H - B
    YMAX = 6.0
    # (label, valid, attempts, yield%, is_working_point)
    bars = [("r=1", 29, 2500, 1.16, False),
            ("r=5", 85, 2500, 3.40, True),
            ("r=10", 57, 1500, 3.80, False),
            ("r=20", 39, 750, 5.20, False)]

    def py(v):
        return y1 - (v / YMAX) * (y1 - y0)

    n = len(bars)
    slot = (x1 - x0) / n
    bw = slot * 0.5

    s = [svg_header(W, H, "RePaint resample sweep",
                    "Valid-complex yield rises monotonically from 1.16% at r=1 to 5.20% at "
                    "r=20; r=5 is the chosen working point.")]
    s.append(f'  <text x="{W/2:.0f}" y="24" text-anchor="middle" {FONT} font-size="15" '
             f'font-weight="600" fill="{INK}">RePaint sweep: valid-complex yield vs resampling r</text>')
    for v in (0, 1, 2, 3, 4, 5, 6):
        y = py(v)
        s.append(f'  <line x1="{x0}" y1="{y:.1f}" x2="{x1}" y2="{y:.1f}" stroke="{GRID}" stroke-width="1"/>')
        s.append(f'  <text x="{x0-8}" y="{y+4:.1f}" text-anchor="end" {FONT} font-size="11" '
                 f'fill="{MUTED}">{v}%</text>')
    for i, (lab, valid, att, yld, wp) in enumerate(bars):
        cx = x0 + slot * i + slot / 2
        bx = cx - bw / 2
        by = py(yld)
        h = y1 - by
        col = AMBER if wp else BLUE
        s.append(f'  <rect x="{bx:.1f}" y="{by:.1f}" width="{bw:.1f}" height="{h:.1f}" '
                 f'rx="3" fill="{col}"/>')
        s.append(f'  <text x="{cx:.1f}" y="{by-18:.1f}" text-anchor="middle" {FONT} '
                 f'font-size="12.5" font-weight="600" fill="{INK}">{yld:.2f}%</text>')
        s.append(f'  <text x="{cx:.1f}" y="{by-4:.1f}" text-anchor="middle" {FONT} '
                 f'font-size="10.5" fill="{MUTED}">{valid}/{att}</text>')
        s.append(f'  <text x="{cx:.1f}" y="{y1+18:.1f}" text-anchor="middle" {FONT} '
                 f'font-size="12" fill="{INK}">{lab}</text>')
        if wp:
            s.append(f'  <text x="{cx:.1f}" y="{y1+34:.1f}" text-anchor="middle" {FONT} '
                     f'font-size="10.5" font-weight="600" fill="{AMBER}">working point</text>')
    s.append(f'  <text x="16" y="{(y0+y1)/2:.0f}" text-anchor="middle" {FONT} font-size="12" '
             f'fill="{INK}" transform="rotate(-90 16 {(y0+y1)/2:.0f})">valid / attempts</text>')
    s.append('</svg>\n')
    return "\n".join(s)


# ---------------------------------------------------------------------------
# Figure 3 — de-novo degradation (valid count collapses as context shrinks)
# ---------------------------------------------------------------------------
def design_degradation():
    W, H = 640, 380
    L, R, T, B = 60, 28, 46, 72
    x0, x1 = L, W - R
    y0, y1 = T, H - B
    YMAX = 130
    # (label, sublabel, valid, color)
    bars = [("mask 1", "4/5 context", 126, GREEN),
            ("mask 2", "3/5 context", 4, AMBER),
            ("mask 3", "2/5 context", 0, RED),
            ("mask all", "0/5 — bare Eu", 0, RED)]

    def py(v):
        return y1 - (v / YMAX) * (y1 - y0)

    n = len(bars)
    slot = (x1 - x0) / n
    bw = slot * 0.5

    s = [svg_header(W, H, "De-novo design degradation",
                    "Valid structures collapse from 126 (mask 1, completion) to 4 (mask 2) "
                    "to 0 (mask 3 and mask all) as context is removed.")]
    s.append(f'  <text x="{W/2:.0f}" y="24" text-anchor="middle" {FONT} font-size="15" '
             f'font-weight="600" fill="{INK}">Validity collapses as context shrinks</text>')
    for v in (0, 25, 50, 75, 100, 125):
        y = py(v)
        s.append(f'  <line x1="{x0}" y1="{y:.1f}" x2="{x1}" y2="{y:.1f}" stroke="{GRID}" stroke-width="1"/>')
        s.append(f'  <text x="{x0-8}" y="{y+4:.1f}" text-anchor="end" {FONT} font-size="11" '
                 f'fill="{MUTED}">{v}</text>')
    for i, (lab, sub, valid, col) in enumerate(bars):
        cx = x0 + slot * i + slot / 2
        bx = cx - bw / 2
        if valid > 0:
            by = py(valid)
            h = y1 - by
            s.append(f'  <rect x="{bx:.1f}" y="{by:.1f}" width="{bw:.1f}" height="{h:.1f}" '
                     f'rx="3" fill="{col}"/>')
            s.append(f'  <text x="{cx:.1f}" y="{by-6:.1f}" text-anchor="middle" {FONT} '
                     f'font-size="12.5" font-weight="600" fill="{INK}">{valid}</text>')
        else:
            # zero bar: baseline tick + bold "0"
            s.append(f'  <line x1="{bx:.1f}" y1="{y1}" x2="{bx+bw:.1f}" y2="{y1}" '
                     f'stroke="{col}" stroke-width="3"/>')
            s.append(f'  <text x="{cx:.1f}" y="{y1-8:.1f}" text-anchor="middle" {FONT} '
                     f'font-size="12.5" font-weight="700" fill="{col}">0</text>')
        s.append(f'  <text x="{cx:.1f}" y="{y1+18:.1f}" text-anchor="middle" {FONT} '
                 f'font-size="12" fill="{INK}">{lab}</text>')
        s.append(f'  <text x="{cx:.1f}" y="{y1+34:.1f}" text-anchor="middle" {FONT} '
                 f'font-size="10" fill="{MUTED}">{sub}</text>')
    # callout: mask all attempts
    s.append(f'  <text x="{x0 + slot*3 + slot/2:.1f}" y="{y1+50:.1f}" text-anchor="middle" '
             f'{FONT} font-size="10.5" font-weight="600" fill="{RED}">0 valid / 6,300</text>')
    s.append(f'  <text x="16" y="{(y0+y1)/2:.0f}" text-anchor="middle" {FONT} font-size="12" '
             f'fill="{INK}" transform="rotate(-90 16 {(y0+y1)/2:.0f})">valid structures</text>')
    s.append('</svg>\n')
    return "\n".join(s)


def main():
    figs = {
        "training_curve.svg": training_curve(),
        "repaint_sweep.svg": repaint_sweep(),
        "design_degradation.svg": design_degradation(),
    }
    for name, body in figs.items():
        path = os.path.join(OUT, name)
        with open(path, "w") as f:
            f.write(body)
        print(f"wrote {path} ({len(body)} bytes)")


if __name__ == "__main__":
    main()
