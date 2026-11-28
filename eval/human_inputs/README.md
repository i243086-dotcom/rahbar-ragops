# Phase 4 human checkpoint

These files separate genuine human work from generated evaluation data. Do not copy generated
wording into the human files and do not enter another person's name, date, verdict, or label.

1. Read `WRITE_QUESTIONS.md` and write questions in `human_questions.yaml` in your own words.
2. Read `synthetic_candidates.yaml`, then record at least eight genuine decisions in
   `synthetic_reviews.yaml` (Shaheer is assigned `syn01` through `syn04`).
3. Run `python eval/phase4_inputs.py`. It writes `eval/golden.jsonl` only when the required
   8 human questions and 8 synthetic reviews are valid.
4. Run `python eval/phase4_eval.py ...`. It creates a timestamped result and refreshes
   `LABEL_ANSWERS.md` with real answers and retrieved context.
5. Label at least eight rows in `answer_labels.yaml`, then rerun the evaluator with `--labels`.

The assignment requires 25 questions: 15 answerable, 5 abstain, and 5 hard. The generated set
contributes 11 answerable, 3 abstain, and 3 hard questions. The human file must therefore contain
exactly the remaining minimum mix: 4 answerable, 2 abstain, and 2 hard questions.

