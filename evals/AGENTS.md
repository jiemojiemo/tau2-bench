# Airline Level 1 evals

The LangSmith dataset `tau2-airline-zh-level1-v1` contains pre-booking checks,
confirmed bookings, flight searches, reservation cancellations, reservation
changes, refunds and compensation. Each case has a unique `case_id`, a `feature`
and a `scenario`. The case files are in `airline_level1/`.

The feature labels are `预定航班` (including flight searches), `修改航班`,
`取消航班` and `退款与补偿`. Use the feature label with `--filter` to select the
whole group.

Run from the repository root.

```bash
# List the available cases without running the model
uv run --frozen --extra langsmith python -m evals.airline_level1.eval --list

# Run the whole dataset and upload scores and traces
uv run --frozen --extra langsmith python -m evals.airline_level1.eval --upload

# Preview a filter, then run only the matching cases
uv run --frozen --extra langsmith python -m evals.airline_level1.eval --filter 'BOOK-*' --list
uv run --frozen --extra langsmith python -m evals.airline_level1.eval --filter 'BOOK-*' --upload

# Run specific cases together in one experiment
uv run --frozen --extra langsmith python -m evals.airline_level1.eval --filter BOOK-06 --filter FLIGHT-04 --upload

# Run the cancellation cases
uv run --frozen --extra langsmith python -m evals.airline_level1.eval --filter 'CANCEL-*' --upload

# Run the reservation change cases
uv run --frozen --extra langsmith python -m evals.airline_level1.eval --filter 'CHANGE-*' --upload

# Run the refund and compensation cases
uv run --frozen --extra langsmith python -m evals.airline_level1.eval --filter 'COMP-*' --upload
```

`--filter` matches the case ID, feature or scenario. Quote patterns containing
`*` or `?`. Repeat `--filter` to select cases matching any of those patterns.
Omit `--upload` to run locally. Running cases needs model credentials, and
`--upload` also needs LangSmith credentials. Upload syncs the full dataset and
adds scores and traces for the selected cases to the experiment.

The default model is Luna Low. Use `case_pass` for the overall score and
`db_match` for the final database assertion. Cases with only `db_actions` in
their expected outputs are scored solely by `db_match`. When multiple
`db_actions` are expected, every action must succeed in a later tool-call step
than the preceding action. A lookup with `before` must succeed before the named
write action is attempted.
