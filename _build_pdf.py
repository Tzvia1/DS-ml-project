import re, pathlib

md = pathlib.Path("PROJECT_STORY_v2.md").read_text(encoding="utf-8")

def md_to_html(text):
    lines = text.split("\n")
    out = []
    i = 0
    while i < len(lines):
        line = lines[i]

        # fenced code block
        if line.strip().startswith("```"):
            lang = line.strip()[3:].strip()
            i += 1
            block = []
            while i < len(lines) and not lines[i].strip().startswith("```"):
                block.append(lines[i])
                i += 1
            i += 1
            content = "\n".join(block)
            if lang == "mermaid":
                out.append(f'<div class="mermaid">{content}</div>')
            else:
                escaped = content.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")
                out.append(f'<pre><code>{escaped}</code></pre>')
            continue

        # headings
        m = re.match(r'^(#{1,4})\s+(.*)', line)
        if m:
            lvl = len(m.group(1))
            txt = inline(m.group(2))
            out.append(f"<h{lvl}>{txt}</h{lvl}>")
            i += 1; continue

        # hr
        if re.match(r'^-{3,}$', line.strip()):
            out.append("<hr>"); i += 1; continue

        # blockquote
        if line.startswith("> "):
            out.append(f"<blockquote>{inline(line[2:])}</blockquote>")
            i += 1; continue

        # table
        if line.startswith("|"):
            rows = []
            while i < len(lines) and lines[i].startswith("|"):
                cells = [c.strip() for c in lines[i].strip().strip("|").split("|")]
                rows.append(cells)
                i += 1
            rows = [r for r in rows if not all(re.match(r'^[-:]+$', c) for c in r if c)]
            html = ['<table>']
            for ri, row in enumerate(rows):
                tag = "th" if ri == 0 else "td"
                html.append("<tr>" + "".join(f"<{tag}>{inline(c)}</{tag}>" for c in row) + "</tr>")
            html.append("</table>")
            out.append("\n".join(html))
            continue

        # bullet
        m = re.match(r'^\s*[-*]\s+(.*)', line)
        if m:
            out.append(f"<li>{inline(m.group(1))}</li>")
            i += 1; continue

        # blank
        if line.strip() == "":
            out.append("<br>"); i += 1; continue

        # paragraph
        out.append(f"<p>{inline(line)}</p>")
        i += 1

    return "\n".join(out)


def inline(text):
    # bold
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    # italic
    text = re.sub(r'\*(.+?)\*', r'<em>\1</em>', text)
    # code
    text = re.sub(r'`(.+?)`', r'<code>\1</code>', text)
    return text


body = md_to_html(md)

html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Can We Predict Which Startups Win?</title>
<script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
<script>mermaid.initialize({{startOnLoad:true, theme:'default'}});</script>
<style>
  body {{
    font-family: 'Segoe UI', Calibri, sans-serif;
    max-width: 900px;
    margin: 40px auto;
    color: #1a1a2e;
    font-size: 15px;
    line-height: 1.6;
  }}
  h1 {{ color: #2e86ab; font-size: 2em; text-align: center; margin-bottom: 4px; }}
  h2 {{ color: #1a1a2e; font-size: 1.4em; border-bottom: 2px solid #2e86ab; padding-bottom: 4px; margin-top: 36px; }}
  h3 {{ color: #2e86ab; font-size: 1.1em; margin-top: 20px; }}
  h4 {{ color: #555566; font-style: italic; }}
  hr  {{ border: none; border-top: 1px solid #2e86ab; margin: 28px 0; }}
  table {{ border-collapse: collapse; width: 100%; margin: 16px 0; font-size: 14px; }}
  th {{ background: #2e86ab; color: white; padding: 8px 12px; text-align: left; }}
  td {{ padding: 7px 12px; border-bottom: 1px solid #dde; }}
  tr:nth-child(even) td {{ background: #eef4f9; }}
  pre {{ background: #f4f4f4; padding: 14px; border-radius: 6px; font-family: 'Courier New', monospace; font-size: 12px; overflow-x: auto; }}
  code {{ background: #eee; padding: 1px 4px; border-radius: 3px; font-size: 13px; }}
  blockquote {{ border-left: 4px solid #2e86ab; margin: 16px 0; padding: 8px 16px; color: #447799; font-style: italic; background: #f0f7fb; }}
  li {{ margin: 4px 0; }}
  .mermaid {{ text-align: center; margin: 20px 0; }}
  @media print {{
    body {{ margin: 20px; max-width: 100%; }}
    h2 {{ page-break-before: auto; }}
  }}
</style>
</head>
<body>
{body}
<script>
  window.onload = function() {{
    // give mermaid a moment then prompt print
    setTimeout(function() {{
      window.print();
    }}, 2000);
  }};
</script>
</body>
</html>"""

out = pathlib.Path("PROJECT_STORY_v2.html")
out.write_text(html, encoding="utf-8")
print(f"HTML written: {out.resolve()}")
print("Opening in browser — Mermaid will render, then a print dialog appears.")
print("Choose 'Save as PDF' in the print dialog.")

import subprocess, sys
subprocess.Popen(["start", "", str(out.resolve())], shell=True)
