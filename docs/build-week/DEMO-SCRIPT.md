# Public demo script and shot list

Target duration: approximately 2 minutes 40 seconds. Use only the public synthetic fixture.

| Time | Screen | Narration |
| --- | --- | --- |
| 0:00–0:13 | Guided Experiment challenge | “Eight synthetic tune variants. Two hidden families. There are 256 possible assignments. Which split would you expect to win?” |
| 0:13–0:40 | Click **Reveal all 256 assignments** | “The system checks every assignment, so nobody has to trust a prediction. These two outlined cells are the complement-equivalent global optima.” |
| 0:40–0:58 | Exact result | “`00001111` is the canonical representative; its complement is the same two-family split with the labels reversed. Exact enumeration is authoritative.” |
| 0:58–1:27 | Registered QAOA evidence | “In the registered p=1 local ideal simulation, 53.10 percent of 4,096 samples fell across both optima. The uniform optimum-class baseline is 0.78125 percent. This is separate from the current 256-shot quick run, is not hardware, and claims no quantum advantage.” |
| 1:27–2:12 | Evidence hierarchy and AI governance | “Exact truth governs the Qiskit comparison. Codex accelerated implementation, tests, CI diagnosis, and visual verification under Gwri’s scientific decisions. GPT-5.6 can explain only filtered, validated evidence; it cannot calculate or alter the values. Invalid or unavailable output fails closed to the complete deterministic explanation.” |
| 2:12–2:40 | Limitations | “The fixture is synthetic. This is not a demo where quantum always wins, or where the AI is always right. It is a lab where the truth is checked first, and everyone — including the machines — is held to it.” |

## Offline fallback

Record the same path with the deterministic explanation and the no-credential capability message.
Do not depend on a live API call or live Qiskit optimisation. The 256 Reveal and registered
comparison require neither optional capability. If Qiskit is unavailable, state that the exact
journey and tracked registered comparison are already complete.

For the recording, do not run live Qiskit or make a live GPT-5.6 request. Do not open optional
expanders, the 256-row table, or exports, and do not use external or copyrighted music.
