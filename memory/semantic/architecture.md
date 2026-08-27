# Architecture

## Layers

1. `challenge`: select only allowlisted templates.
2. `runtime`: execute canonical fixture variants and compare observable state.
3. `evidence`: normalize event results without persistence.
4. `interpretation`: map evidence to cautious qualitative statuses.
5. `visualization`: render graph state and collect explicit learner commitments.

## Module rule

Each module owns one domain behavior. Fixtures are data files; application code must not branch on fixture-specific prose or outcomes.

