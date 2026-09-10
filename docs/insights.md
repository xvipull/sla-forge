# Business insights and recommendations

## Evidence from the synthetic portfolio run

- The governed population contains 720 tickets and 1,189 assignment events, with 469 derived transfers reconciled exactly.
- Infrastructure and Business Apps are the first queues to inspect because queue-level SLA attainment is below the 90% target while handoff and risk measures remain material.
- Priority is the strongest explainable model driver: P1/P2 features increase breach odds, while P3/P4 reduce them. Transfer count also increases breach odds.
- The chronological holdout AUC is 0.7701 versus 0.7176 for the operational rule baseline. This is engineering evidence on synthetic data, not a production accuracy claim.

## Recommended operating actions

1. Start a weekly queue review for the lowest-attaining queue, pairing aged-backlog count with average transfers and reopen rate.
2. Add an early handoff checkpoint for P1/P2 tickets before the response target is at risk.
3. Route recurring high-breach categories to problem management; validate taxonomy before changing staffing or policy.
4. Use the risk worklist as a human-reviewed intervention queue and record whether interventions change outcomes.
5. Before contractual use, implement business calendars and pause rules, calibrate thresholds to intervention capacity, and monitor drift and subgroup performance.
