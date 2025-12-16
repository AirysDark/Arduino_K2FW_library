#!/usr/bin/env python3
import sys, re
from pathlib import Path
from _common import iter_files, is_probably_text, read_text_loose, dump_json

PORT_RE = re.compile(r"(?:(?:0\.0\.0\.0|127\.0\.0\.1|localhost)[: ](\d{2,5})|\bport\s*[=:]\s*(\d{2,5})\b)", re.I)
URL_RE  = re.compile(r"(https?://[^\s'\"]+)", re.I)

def main():
    if len(sys.argv) < 3:
        print("usage: extract_services.py <dump_root> <out_json>")
        return 2
    dump_root = Path(sys.argv[1]).resolve()
    out_json  = Path(sys.argv[2]).resolve()

    services = {}
    evidence = {}

    for f in iter_files(dump_root):
        rel = "/" + f.relative_to(dump_root).as_posix()
        rl = rel.lower()
        if not any(x in rl for x in ("/etc/systemd", "/lib/systemd", "/etc/init.d", "/etc/rc", "/etc", "/usr/lib/systemd")):
            continue
        if not is_probably_text(f):
            continue
        try:
            txt = read_text_loose(f, limit_bytes=600_000)
        except Exception:
            continue

        if rel.endswith(".service") or "/init.d/" in rl or "systemd" in rl:
            name = Path(rel).name
            key = "SVC_" + re.sub(r"[^A-Za-z0-9]+","_", name).upper()[:60]
            entry = services.get(key, {"name": name, "path": rel, "ports": [], "urls": [], "exec": []})

            for m in PORT_RE.findall(txt):
                for g in m:
                    if g:
                        try:
                            p = int(g)
                            if 1 <= p <= 65535 and p not in entry["ports"]:
                                entry["ports"].append(p)
                        except Exception:
                            pass

            for u in URL_RE.findall(txt):
                if u not in entry["urls"] and len(entry["urls"]) < 20:
                    entry["urls"].append(u)

            for line in txt.splitlines():
                if "ExecStart" in line or line.strip().startswith(("exec","/usr","/bin","/sbin")):
                    line2 = line.strip()
                    if line2 and line2 not in entry["exec"] and len(entry["exec"]) < 10:
                        entry["exec"].append(line2[:200])

            services[key] = entry
            evidence[key] = rel

        if len(services) >= 300:
            break

    out = {"meta": {"dump_root": str(dump_root)}, "services": services, "evidence": evidence}
    dump_json(out_json, out)
    print(f"Wrote {out_json} ({len(services)} services)")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
