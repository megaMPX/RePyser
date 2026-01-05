import dis
import html
from .constants import SUSPICIOUS_KEYWORDS

def collect_suspicious(codeobj, file_path):
    res = []
    for i, ins in enumerate(dis.get_instructions(codeobj)):
        if ins.opname in {"LOAD_NAME", "LOAD_GLOBAL", "IMPORT_NAME"}:
            if ins.argval in SUSPICIOUS_KEYWORDS:
                res.append({
                    "file": file_path,
                    "line": i + 1,
                    "offset": ins.offset,
                    "keyword": ins.argval,
                    "instruction": f"{ins.opname} {ins.argrepr}"
                })
    return res


def export_txt(report, out):
    with open(out, "w", encoding="utf-8") as f:
        for r in report:
            f.write(f"{r['file']}\n")
            f.write(f"line {r['line']} offset {r['offset']}\n")
            f.write(f"trigger: {r['keyword']}\n")
            f.write(f"{r['instruction']}\n")
            f.write("-" * 40 + "\n")


def export_html(report, out):
    with open(out, "w", encoding="utf-8") as f:
        f.write("<html><body><h1>Security report</h1>")
        for r in report:
            f.write("<div style='border:1px solid #444;margin:10px;padding:10px'>")
            f.write(f"<b>File:</b> {html.escape(r['file'])}<br>")
            f.write(f"<b>Line:</b> {r['line']} offset {r['offset']}<br>")
            f.write(f"<b>Trigger:</b> {r['keyword']}<br>")
            f.write(f"<code>{html.escape(r['instruction'])}</code>")
            f.write("</div>")
        f.write("</body></html>")
