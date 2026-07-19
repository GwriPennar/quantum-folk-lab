# Public demo script and shot list

Target duration: 2 minutes 50 seconds. Use only the public synthetic fixture.

| Time | Screen | Narration |
| --- | --- | --- |
| 0:00–0:15 | Guided Experiment challenge | “Eight synthetic tune variants. Two hidden families. There are 256 possible assignments. Before the system reveals the answer, which split would you expect to win?” |
| 0:15–0:45 | Click **Reveal all 256 assignments** | “We made the problem small enough that nobody has to trust a prediction. The system checks every possible assignment. These are all 256 possibilities, and these two cells are the complement-equivalent global optima.” |
| 0:45–1:05 | Exact result | “`00001111` is the canonical representative. Its complement represents the same two-family split with the labels reversed.” |
| 1:05–1:35 | Registered QAOA evidence | “In the registered p=1 local ideal-simulator experiment, 53.10 percent of 4,096 samples fell across the two equivalent optima. A uniform random assignment places 0.78125 percent of its probability on that optimum class. Exact enumeration remains authoritative.” |
| 1:35–2:05 | Evidence hierarchy | “The quantum result is measured against truth established first. GPT-5.6 then explains that validated evidence, but it cannot calculate or alter the scientific values.” |
| 2:05–2:25 | Deterministic fallback | “If the AI response fails schema, grounding, numerical or claim checks, the system fails closed to a deterministic explanation with identical science.” |
| 2:25–2:37 | Codex contribution | “Codex helped implement and test the release under human-defined scientific contracts.” |
| 2:37–2:50 | Limitations | “This is not a demo where quantum always wins, or where the AI is always right. It is a lab where the truth is checked first, and everyone — including the machines — is held to it.” |

## Offline fallback

Record the same path with the deterministic explanation and the no-credential capability message.
Do not depend on a live API call or live Qiskit optimisation. The 256 Reveal and registered
comparison require neither optional capability. If Qiskit is unavailable, state that the exact
journey and tracked registered comparison are already complete.
