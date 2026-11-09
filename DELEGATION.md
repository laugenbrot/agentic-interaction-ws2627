# DELEGATION.md
## Delegation boundary

| # | Action | Decision | Justification |
|---|--------|----------|---------------|
| 1 | Read the appointments of a day | alone | Read-only, no external effects, wrong guesses cost nothing. Asking permission before every lookup is exactly the slowness an agent should remove. |
| 2 | Look up the weather | alone | Read-only and uncertain in content, not in effect: the forecast can be wrong, but nobody outside the system is harmed by a good-faith lookup. |
| 3 | Search train connections | alone | Pure search over published schedules, read-only. Announcing the result is enough; the user decides what to do with it — until the agent starts booking (see 7). |
| 4 | Read notes | alone | Read-only on personal data. Reading changes nothing, so the risk lies only in what is done with the contents. |
| 5 | Create a personal block in the calendar (e.g. travel time, no other attendees) | alone | It writes, but only into my own calendar, with no attendees and no notifications sent to anyone. Blocking my own time is low-risk and easily reversible, and requiring approval for every self-block would defeat the speed the delegation is meant to create. |
| 6 | Reschedule an appointment with other attendees | approval | Affects people outside the interaction: attendees get moved and see changes they did not initiate. A time pushed without consent destroys trust much faster than a wrong read. |
| 7 | Book a train ticket | approval | Binds the wallet and, through the booked time, the whole rest of the day. One wrong connection and every dependent step is wrong. Money plus irreversible commitment mean the slot stays with the human. |
| 8 | Send a message to third parties | approval | Once sent, it exercises my social obligations without my voice being checked — unattributable, irreversible. The agent may draft, but the send is mine. |
| 9 | Create a note | alone | Writes only into my own notes — no one outside the interaction is affected. A wrong note costs a quick correction, and gating every capture would break the low-friction flow that makes note-taking useful in the first place. |
| 10 | Delete a note | approval | Destroys information that was trusted enough to be kept — irreversibly. The tidiest agent cleanup must not decide which of my memories stays. |

## Rule

I decide by who bears the consequence: **Everything that only reads is delegated to the agent, and so are writes that touch only my own space and are easily reversible (notes, self-blocks); everything that reaches outside the conversation — other people, my money, or irreversible destruction of state — the agent prepares, but does only after I say yes.**

## Observations from the role play

- **Read-only chaining needed no approvals and was fast.** While playing the agent for card A ("What's on today?"), I announced `calendar(2026-10-29)`, `weather(muenchen, 2026-10-29)`, and `read notes`, one after the other, and reported a short spoken summary each time. None of the pure lookups felt like they needed a gate, which is why actions 1–4 are "alone".
- **The write-only announcement was the tension point.** On card B/C the agent announced `create_event` for a travel-time block without asking first. I only noticed it afterwards, when the block quietly shaped the rest of the schedule — a reminder that even low-risk writes deserve a spoken announcement beforehand, and that outward-facing actions (6–8, 10) must wait for approval.
