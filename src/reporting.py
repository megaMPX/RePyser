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


def format_report_text(report):
    lines = []
    for r in report:
        lines.append(f"{r['file']}")
        lines.append(f"line {r['line']} offset {r['offset']}")
        lines.append(f"trigger: {r['keyword']}")
        lines.append(f"{r['instruction']}")
        lines.append("-" * 40)
    return "\n".join(lines)


