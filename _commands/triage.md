Run the Pre-Submission Triage Gate on this finding: $ARGUMENTS

Answer each question with YES or NO and one sentence of evidence from the finding.

1. Can an attacker use this RIGHT NOW with a real HTTP request?
2. Is the impact on the program's accepted-impact list?
3. Is the asset in scope?
4. Does it work without privileged access an attacker cannot get?
5. Is this not already known or documented behavior?
6. Can impact be proved beyond "technically possible"?
7. Is this not on the program's never-submit list?

End with one of:
- GO — all 7 pass, proceed to report
- KILL — one or more failed, explain which and why
- DOWNGRADE — passes but severity is lower than claimed, state what it should be
