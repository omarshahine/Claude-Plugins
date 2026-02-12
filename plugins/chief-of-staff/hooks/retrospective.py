#!/usr/bin/env python3
"""Post-triage retrospective hook for chief-of-staff.

Fires via SubagentStop when the batch-processor completes.
Reads batch-state.yaml and decision-history.yaml to check for:
  - Failed actions (suggest retry)
  - Low success rate
  - Learning opportunities (enough sessions to retrain rules)

Surfaces findings via systemMessage (shown to the user).
Does NOT block the subagent from stopping.
"""
import json
import re
import sys
from pathlib import Path


def main():
    try:
        input_data = json.load(sys.stdin)
    except Exception:
        sys.exit(0)

    # Prevent infinite loops: if already triggered by a stop hook, allow stop
    if input_data.get('stop_hook_active', False):
        sys.exit(0)

    data_dir = Path.home() / '.claude' / 'data' / 'chief-of-staff'
    findings = []

    # --- Check batch-state.yaml for failures ---
    batch_state = data_dir / 'batch-state.yaml'
    try:
        if batch_state.exists():
            content = batch_state.read_text()

            # Count failure entries (lines with "- emailId:" under "failures:" section)
            failures_match = re.search(
                r'^failures:\s*\n((?:[ \t]+.*\n)*)', content, re.MULTILINE
            )
            if failures_match:
                failure_entries = re.findall(
                    r'- emailId:', failures_match.group(1)
                )
                if failure_entries:
                    findings.append(
                        f"{len(failure_entries)} action(s) failed"
                        " - run `/chief-of-staff:batch --retry`"
                    )

            # Check overall success rate from top-level results fields
            # Use ^ anchor + 2-space indent to match only the top-level keys,
            # not nested byAction entries like "archive: { attempted: 10 }"
            results_match = re.search(
                r'^results:\s*\n((?:[ \t]+.*\n)*)', content, re.MULTILINE
            )
            if results_match:
                results_text = results_match.group(1)
                total_m = re.search(r'^  total:\s*(\d+)', results_text, re.MULTILINE)
                failed_m = re.search(r'^  failed:\s*(\d+)', results_text, re.MULTILINE)
                if total_m and failed_m:
                    total, failed = int(total_m.group(1)), int(failed_m.group(1))
                    if total > 5 and failed / total > 0.15:
                        rate = 100 * (total - failed) // total
                        findings.append(
                            f"Success rate is {rate}% ({failed}/{total} failed)"
                        )
    except Exception:
        pass  # Don't let batch-state errors prevent decision-history check

    # --- Check decision-history.yaml for learning opportunities ---
    history_file = data_dir / 'decision-history.yaml'
    try:
        if history_file.exists():
            content = history_file.read_text()

            sessions_m = re.search(r'total_sessions:\s*(\d+)', content)
            decisions_m = re.search(r'total_decisions:\s*(\d+)', content)
            accepted_m = re.search(r'suggestions_accepted:\s*(\d+)', content)

            if sessions_m and decisions_m:
                sessions = int(sessions_m.group(1))
                decisions = int(decisions_m.group(1))
                # Suggest learning after every 5 sessions
                if sessions > 0 and sessions % 5 == 0:
                    findings.append(
                        f"{decisions} decisions across {sessions} sessions"
                        " - good time to run `/chief-of-staff:learn`"
                    )

            # Compute acceptance rate from raw counts (the acceptance_rate
            # field may be stale since batch-processor doesn't update it)
            if accepted_m and decisions_m:
                accepted = int(accepted_m.group(1))
                total_dec = int(decisions_m.group(1))
                if total_dec > 0:
                    rate = accepted / total_dec
                    if rate < 0.5:
                        findings.append(
                            f"Suggestion acceptance is {rate:.0%}"
                            " - `/chief-of-staff:learn` may improve accuracy"
                        )
    except Exception:
        pass  # Don't let history errors prevent output of batch-state findings

    # --- Output findings ---
    if findings:
        msg = "Triage Retrospective:\n" + "\n".join(
            f"  - {f}" for f in findings
        )
        print(json.dumps({"systemMessage": msg}))

    sys.exit(0)


if __name__ == '__main__':
    main()
