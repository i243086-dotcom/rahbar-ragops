FROM python:3.12-slim-bookworm
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY eval/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY eval/ ./eval/
COPY scripts/phase4_summary.py ./scripts/phase4_summary.py
# The evaluation writes the generated human-label packet after both measured
# runs.  Make that checked-in packet writable for the non-root Job user.
RUN chmod -R a+rwX /app/eval/human_inputs
USER 10001:10001
ENTRYPOINT ["python", "eval/phase4_eval.py"]

