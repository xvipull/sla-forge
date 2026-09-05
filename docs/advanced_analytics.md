# Advanced decision-support analytics

## Purpose and design

`explainable_logistic_breach_risk_v1` estimates the likelihood that a ticket will breach its SLA. It is a transparent logistic-regression implementation using priority, category, initial queue, and current transfer count. It deliberately excludes response time, resolution time, age, breach flags, risk score, and reopen state to avoid using outcome-derived information as features.

Tickets are ordered by creation timestamp and split chronologically: the earliest 80% train the model and the latest 20% evaluate it. This avoids evaluating on future information mixed into training data. A documented rule baseline flags P1/P2 tickets and Infrastructure tickets with at least two handoffs.

## Governed outputs

| Asset | Grain / use |
| --- | --- |
| `model_run` | One training run, feature list, assumptions, holdout metrics, and threshold. |
| `model_driver` | One model run and feature; coefficient, odds ratio, direction, and rank enable explanation. |
| `fact_breach_risk_prediction` | One model run and ticket; model and baseline scores/bands, partition, and observed outcome. |
| `v_breach_risk_decision_support` | One ticket/model-run decision worklist joined to conformed operational attributes. |
| `reports/model_evaluation.json` | Portable evaluation, baseline comparison, drivers, and limitations. |

Run `npm run analytics` after `npm run build`. The output is a prioritization aid, not an automated action, customer commitment, or employee-performance measure.

## Assumptions and limitations

- This synthetic dataset establishes engineering behavior only; it does not validate production predictive performance.
- A breach label captures association, not root cause or causal effect.
- Threshold 0.50 is a starting point; production calibration should use cost of missed breaches versus intervention capacity.
- Revalidate drift, subgroup performance, data completeness, and calibration after each source or policy change and at least quarterly.
- Human review remains required for escalation and workload decisions.
