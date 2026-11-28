# Teammate tasks

These tasks must be completed by `m-shaheer-shoaib` from his own GitHub account. Do not use his identity or add co-author trailers on his behalf.

## Phase 0 (about 10 minutes)

1. Accept the GitHub collaborator invitation for `i243086-dotcom/rahbar-ragops` when it arrives.
2. Clone the new repository, configure your own Git identity, and inspect `docs/A02-AUDIT.md`.
3. Review and approve the Phase 0 PR only after reading its verification output. If something is wrong, request changes rather than approving.

## Remaining-phase handoff

The complete ordered handoff, clone commands, human-input protocol, screenshot commands, and
review responsibilities are in [SHAHEER-REMAINING-PHASES.md](SHAHEER-REMAINING-PHASES.md).

## Reserved later tasks (about 35–50 minutes total)

- Write some of the human golden questions in your own words and commit them on your own branch (10 minutes).
- Fill synthetic accept/edit/reject verdicts and commit them (10 minutes).
- Label at least part of the answer-agreement sheet and commit it (15 minutes).
- Make one small independent Batch B or README correction (5 minutes).
- Review each phase PR from your account (2–5 minutes each).

Phase 4 files are now ready:

1. Write at least four entries in `eval/human_inputs/human_questions.yaml` using only your own
   wording and the verified prompts in `WRITE_QUESTIONS.md`.
2. Review `syn01` through `syn04` and enter genuine decisions in `synthetic_reviews.yaml`.
3. After a real evaluation, label at least four rows in `answer_labels.yaml` using the generated
   `LABEL_ANSWERS.md` context packet.
4. Run `python eval/phase4_inputs.py` and the Phase 4 unit tests before committing.

A task is not marked complete until the teammate's commit/review is visible on GitHub.

