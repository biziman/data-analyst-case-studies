#!/usr/bin/env python3
"""Build the static interactive site under docs/ (GitHub Pages).

Reads one JSON config per case from scripts/cases/*.json and writes:
  docs/index.html                     landing page (all configured cases)
  docs/cases/<slug>/index.html        narrative + widget page (cases with sections)

Assets (style.css, widgets.js, theme.js, plotly.min.js) live in docs/assets/
and are not touched here. Run from the repository root:  python3 scripts/build_site.py
"""
import html
import json
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CASES_DIR = ROOT / "scripts" / "cases"
DOCS = ROOT / "docs"
REPO_URL = "https://github.com/biziman/data-analyst-case-studies"
SITE_TITLE = "Product & marketing analytics — interactive case studies"
# Same title with non-breaking spaces so the wrap never splits "analytics —
# interactive" or "case studies" across lines.
SITE_TITLE_HTML = "Product &amp; marketing analytics&nbsp;—&nbsp;interactive case&nbsp;studies"

# Runs in <head> before first paint: pick the saved theme, else the system
# preference. The toggle itself lives in TOPBAR and is wired by assets/theme.js.
THEME_INIT = """  <script>
    (function () {
      try {
        var t = localStorage.getItem("theme");
        if (t !== "light" && t !== "dark") {
          t = window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
        }
        document.documentElement.dataset.theme = t;
      } catch (e) {
        document.documentElement.dataset.theme = "light";
      }
    })();
  </script>"""

WIDGETS = {
    "cpp_chart": """
  <div class="card">
    <h3>{heading}</h3>
    <div class="key">
      <span class="item"><span class="swatch" style="--c: var(--teal)"></span> Meets the $50 screen</span>
      <span class="item"><span class="swatch" style="--c: var(--brick)"></span> Above the $50 screen</span>
    </div>
    <div id="cpp-chart" class="chart"></div>
    <div id="cpp-caption" class="live">Loading…</div>
    <div class="caption">Assessment data (anonymized): 41 daily cost rows, May 2020;
      registrations 2020-05-01 to 2020-05-31. Cost rows and payer cohorts are not aligned
      to the same dates. Screening metric only, not a budget result.</div>
  </div>""",

    "funnel_pooled": """
  <div class="card">
    <h3>{heading}</h3>
    <div class="key">
      <span class="item"><span class="swatch" style="--c: var(--teal)"></span> Meets the $50 screen</span>
      <span class="item"><span class="swatch" style="--c: var(--brick)"></span> Above the $50 screen</span>
    </div>
    <div id="cpp-funnel" class="chart"></div>
    <div id="funnel-caption" class="live">Loading…</div>
    <div class="caption">Assessment data (anonymized). Bars pool counts across the campaigns
      in their group; each bar is labeled with the cumulative share of the group's impressions
      that still converts at that stage. The smallest stages are barely visible at this scale —
      the labels carry the numbers. Descriptive — not a causal comparison.</div>
  </div>""",

    "arpu_windows": """
  <div class="card">
    <h3>{heading}</h3>
    <div class="key">
      <span class="item"><span class="line" style="--c: var(--teal)"></span> Meets the $50 screen (B, E, G)</span>
      <span class="item"><span class="line" style="--c: var(--brick)"></span> Above the screen (A, C, D, F, H)</span>
      <span class="item"><span class="line" style="--c: var(--ink)"></span> Blended ARPU across all eight campaigns (weighted)</span>
      <span class="item">letters at the line ends mark the campaign</span>
    </div>
    <div id="arpu-chart" class="chart"></div>
    <div class="callout"><b>Same metric, two rules:</b> campaign E reads
      <b>$0.75</b> under whole-day truncation and <b>$0.68</b> under a strict
      168-hour window. The window rule — not the data — explains the gap.</div>
    <div id="arpu-caption" class="live">Loading…</div>
    <div class="caption">Assessment data (anonymized). ARPU denominators are registered users
      per campaign with non-payers at zero.</div>
  </div>""",

    "eh_distribution": """
  <div class="card">
    <h3>{heading}</h3>
    <div class="key">
      <span class="item"><span class="line" style="--c: var(--teal)"></span> Campaign E</span>
      <span class="item"><span class="line" style="--c: var(--brick)"></span> Campaign H</span>
    </div>
    <div id="eh-chart" class="chart tall"></div>
    <div id="eh-caption" class="live">Loading…</div>
    <div class="caption">Assessment data (anonymized). Payments within 168 h of registration,
      summed per user; non-payers kept at 0. The curve is descriptive — the rank test is
      exploratory because the campaign pair was selected after inspecting the data.</div>
  </div>""",

    "eh_overlap": """
  <div class="card">
    <h3>{heading}</h3>
    <div class="key">
      <span class="item"><span class="line" style="--c: var(--teal)"></span> Campaign E</span>
      <span class="item"><span class="line" style="--c: var(--brick)"></span> Campaign H</span>
      <span class="item"><span class="swatch" style="--c: var(--amber)"></span> Overlap of the two shapes</span>
    </div>
    <div id="ov-chart" class="chart"></div>
    <div id="ov-caption" class="live">Loading…</div>
    <div class="caption">Assessment data (anonymized). Densities are Gaussian kernel estimates
      over log10 payment totals of paying users; the overlap is the area shared by the two
      curves. Descriptive — the rank test is exploratory because the campaign pair was
      selected after inspecting the data.</div>
  </div>""",

    "cohort_cumulative": """
  <div class="card">
    <h3>{heading}</h3>
    <div class="key">
      <span class="item"><span class="line" style="--c: var(--teal)"></span> Cumulative payment revenue (USD)</span>
    </div>
    <div id="cum-chart" class="chart"></div>
    <div id="cum-caption" class="live">Loading…</div>
    <div class="caption">Renders the notebook's exploratory SQL exactly as written — daily
      revenue is not aggregated before its cumulative sum and elapsed days are truncated to
      whole days. Its curve is not a validated LTV estimate. Assessment data (anonymized).</div>
  </div>""",

    "sample_calculator": """
  <div class="card">
    <h3>{heading}</h3>
    <div class="controls">
      <label for="calc-lift">Relative uplift</label>
      <input type="range" id="calc-lift" min="5" max="50" step="1" value="20">
      <span class="value" id="calc-lift-value">20%</span>
      <label for="calc-daily">Daily registrations</label>
      <input type="range" id="calc-daily" min="250" max="3000" step="250" value="1000">
      <span class="value" id="calc-daily-value">1,000</span>
    </div>
    <div class="readout">
      <div class="stat"><div class="num" id="calc-n">–</div><div class="lbl">users per arm</div></div>
      <div class="stat"><div class="num" id="calc-total">–</div><div class="lbl">total, both arms</div></div>
      <div class="stat"><div class="num" id="calc-days">–</div><div class="lbl">days at current traffic</div></div>
    </div>
    <div id="calc-caption" class="live">Loading…</div>
    <div class="caption">Sketch only: sample size follows the normal approximation for a
      one-sided two-sample z-test on proportions. Eligibility, exposure logging, guardrails
      and a stopping rule are not part of this calculation.</div>
  </div>""",
}

TOPBAR = """<header class="topbar">
  <a class="brand" href="{home}">Case studies</a>
  <nav>
    <a href="{home}">All cases</a>
    <a href="{repo}">Code on GitHub</a>
    <button class="theme-toggle" id="theme-toggle" type="button" aria-label="Switch to dark theme" title="Switch to dark theme" aria-pressed="false">
      <svg class="icon-moon" viewBox="0 0 24 24" aria-hidden="true"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>
      <svg class="icon-sun" viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M2 12h2M20 12h2M4.93 19.07l1.41-1.41M17.66 6.34l1.41-1.41"/></svg>
    </button>
  </nav>
</header>"""

FOOTER = """<footer class="site">
  <div class="wrap">
    <div>Synthetic and assessment data, labeled per case — not client outcomes, not evidence of professional tenure.</div>
    <div>Numbers verified against a clean notebook run; see the case README for metric contracts and limits.
      <a href="{repo}">{repo_name}</a></div>
  </div>
</footer>"""


def esc(text):
    return html.escape(str(text), quote=True)


def render_sections(sections):
    out = []
    for section in sections:
        stype = section.get("type")
        heading = esc(section.get("heading", ""))
        if stype == "prose":
            body = "".join(f"<p>{esc(p)}</p>" for p in section.get("paragraphs", []))
            if section.get("items"):
                body += "<ol class='limits'>" + "".join(f"<li>{esc(i)}</li>" for i in section["items"]) + "</ol>"
            if section.get("code"):
                body += f"<pre class='code'>{esc(section['code'])}</pre>"
            for link in section.get("links", []):
                body += f'<p><a href="{esc(link["url"])}">{esc(link["label"])} →</a></p>'
            out.append(f'<section class="band"><div class="wrap"><div class="prose"><h2>{heading}</h2>{body}</div></div></section>')
        elif stype == "table":
            head = "".join(f"<th>{esc(h)}</th>" for h in section["headers"])
            left = section.get("left")
            rows = "".join(
                "<tr>" + "".join(
                    f'<td class="num">{esc(c)}</td>' if i and not left else f"<td>{esc(c)}</td>"
                    for i, c in enumerate(row)
                ) + "</tr>"
                for row in section["rows"]
            )
            table = f'<table class="data"><thead><tr>{head}</tr></thead><tbody>{rows}</tbody></table>'
            if section.get("spoiler"):
                out.append(
                    f'<section class="band"><div class="wrap">'
                    f'<details class="spoiler"><summary>{heading}</summary>{table}</details></div></section>'
                )
            else:
                out.append(
                    f'<section class="band"><div class="wrap"><h2 class="prose">{heading}</h2>'
                    f"{table}</div></section>"
                )
        elif stype == "widget":
            intro = "".join(f"<p>{esc(p)}</p>" for p in section.get("paragraphs", []))
            block = WIDGETS[section["widget"]].format(heading=heading)
            out.append(
                f'<section class="band alt"><div class="wrap"><div class="prose"><h2>{heading}</h2>{intro}</div>'
                f"{block}</div></section>"
            )
    return "\n".join(out)


def render_case(cfg):
    slug, number = cfg["slug"], cfg["number"]
    badges = [f'<span class="badge">{esc(cfg.get("provenance", ""))}</span>']
    if cfg.get("reviewed"):
        badges.append(f'<span class="badge reviewed">Reviewed {esc(cfg["reviewed"])}</span>')
    if cfg.get("publish_date"):
        badges.append(f'<span class="badge">Published {esc(cfg["publish_date"])}</span>')
    badges_html = "".join(b for b in badges if b != '<span class="badge"></span>')

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Case {number:02d}: {esc(cfg["title"])} — interactive case study</title>
  <meta name="description" content="{esc(cfg["decision"])}">
{THEME_INIT}
  <link rel="stylesheet" href="../../assets/style.css">
  <script src="../../assets/plotly.min.js"></script>
  <script src="../../assets/widgets.js" defer></script>
  <script src="../../assets/theme.js" defer></script>
</head>
<body>
{TOPBAR.format(home="../../index.html", repo=REPO_URL)}
  <div class="hero">
    <div class="wrap">
      <div class="casenum">Case {number:02d}</div>
      <h1>{esc(cfg["title"])}</h1>
      <div class="decision">{esc(cfg["decision"])}</div>
      <div class="badges">{badges_html}</div>
    </div>
  </div>
{render_sections(cfg["sections"])}
{FOOTER.format(repo=REPO_URL, repo_name="github.com/biziman/data-analyst-case-studies")}
</body>
</html>
"""


def render_index(configs):
    cards = []
    for cfg in sorted(configs, key=lambda c: c["number"]):
        live = cfg.get("status") == "live" and cfg.get("sections")
        if live:
            status = '<span class="status"><span class="live-dot">● Live</span> · interactive walkthrough</span>'
            link = f'<a class="more" href="cases/{cfg["slug"]}/">Open the demo →</a>'
            cls = "case-card"
        else:
            when = cfg.get("publish_date", "soon")
            status = f'<span class="status"><span class="sched">Scheduled {esc(when)}</span></span>'
            link = f'<a class="more" href="{REPO_URL}/blob/main/{cfg["repo_path"]}/README.md">Read the case on GitHub →</a>'
            cls = "case-card soon"
        cards.append(
            f'<div class="{cls}"><div class="n">Case {cfg["number"]:02d}</div>'
            f'<h3>{esc(cfg["title"])}</h3>'
            f'<div class="q">{esc(cfg["decision"])}</div>'
            f"{status}{link}</div>"
        )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{esc(SITE_TITLE)}</title>
  <meta name="description" content="Interactive walkthroughs of product and marketing analytics case studies: the decision, the data, the verified numbers, and what the analysis cannot show.">
{THEME_INIT}
  <link rel="stylesheet" href="assets/style.css">
  <script src="assets/theme.js" defer></script>
</head>
<body>
{TOPBAR.format(home="index.html", repo=REPO_URL)}
  <div class="hero">
    <div class="wrap">
      <div class="casenum">Interactive portfolio</div>
      <h1>{SITE_TITLE_HTML}</h1>
      <p class="lede prose">Eleven case studies of product experiments, marketing measurement,
      forecasting and data quality. Each page walks through the decision, the data and the
      verified numbers — with charts you can manipulate. Synthetic and assessment data,
      labeled as such; never client outcomes.</p>
    </div>
  </div>
  <section class="band">
    <div class="wrap">
      <div class="grid">
{chr(10).join(cards)}
      </div>
    </div>
  </section>
{FOOTER.format(repo=REPO_URL, repo_name="github.com/biziman/data-analyst-case-studies")}
</body>
</html>
"""


def main():
    configs = []
    for path in sorted(CASES_DIR.glob("*.json")):
        configs.append(json.loads(path.read_text()))

    built = 0
    for cfg in configs:
        if cfg.get("sections"):
            out_dir = DOCS / "cases" / cfg["slug"]
            out_dir.mkdir(parents=True, exist_ok=True)
            (out_dir / "index.html").write_text(render_case(cfg))
            built += 1

    (DOCS / "index.html").write_text(render_index(configs))
    print(f"built {built} case page(s) + index from {len(configs)} config(s)")


if __name__ == "__main__":
    main()
