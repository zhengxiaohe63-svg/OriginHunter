import argparse
from core.collector import collect_candidate_ips
from core.analyzer import build_baseline, analyze_candidate
from core.scorer import sort_results
from core.reporter import build_report, print_console_report, write_json_report

SAFE_SUFFIXES = (".local", ".test", ".internal", ".example")

def is_lab_domain(domain: str) -> bool:
    if domain == "localhost":
        return True
    return domain.endswith(SAFE_SUFFIXES)

def main():
    parser = argparse.ArgumentParser(description="OriginHunter Phase1 MVP (Lab Edition)")
    parser.add_argument("--target", required=True, help="Target domain")
    parser.add_argument("--candidates", help="Comma separated candidate IPs")
    parser.add_argument("--candidates-file", help="Candidate IP file, one per line")
    parser.add_argument("--subdomains", action="store_true", help="Collect current DNS + common subdomains")
    parser.add_argument("--historical", help="Local historical DNS JSON file")
    parser.add_argument("--geo", action="store_true", help="Reserved for future use")
    parser.add_argument("--json-out", help="Write JSON report")
    parser.add_argument("--top", type=int, default=10)
    parser.add_argument("--timeout", type=int, default=6)
    parser.add_argument("--only-collect", action="store_true")
    parser.add_argument("--only-score", action="store_true")
    args = parser.parse_args()

    #if not is_lab_domain(args.target):
        #raise SystemExit(
            #"This MVP is restricted to local or authorized lab domains such as "
            #".local, .test, .internal, .example, or localhost."
        #)

    collected = []

    if args.candidates:
        ips = [x.strip() for x in args.candidates.split(",") if x.strip()]
        collected = [{"ip": ip, "sources": ["manual"], "duration_days": 0} for ip in ips]
    else:
        collected = collect_candidate_ips(
            args.target,
            subdomains=args.subdomains,
            historical_file=args.historical,
        )

    if args.candidates_file:
        with open(args.candidates_file, "r", encoding="utf-8") as f:
            for line in f:
                ip = line.strip()
                if ip:
                    collected.append({
                        "ip": ip,
                        "sources": ["manual_file"],
                        "duration_days": 0,
                    })

    # merge by ip
    merged = {}
    for item in collected:
        ip = item["ip"]
        if ip not in merged:
            merged[ip] = {
                "ip": ip,
                "sources": [],
                "duration_days": item.get("duration_days", 0),
                "first_seen": item.get("first_seen"),
                "last_seen": item.get("last_seen"),
            }
        merged[ip]["sources"].extend(item.get("sources", []))
        merged[ip]["duration_days"] = max(
            merged[ip].get("duration_days", 0),
            item.get("duration_days", 0),
        )

    collected = list(merged.values())

    baseline = build_baseline(args.target, timeout=args.timeout)

    if args.only_collect:
        print("Collected Candidates:")
        for item in collected:
            print(f"  - {item['ip']} | sources={','.join(item.get('sources', []))}")
        return

    results = []
    for candidate in collected:
        r = analyze_candidate(args.target, candidate, baseline, timeout=args.timeout)
        results.append(r)

    sort_results(results)

    print_console_report(args.target, baseline, results, top_n=args.top)

    report = build_report(args.target, baseline, results)

    if args.json_out:
        write_json_report(args.json_out, report)
        print(f"\nJSON report written to: {args.json_out}")

if __name__ == "__main__":
    main()