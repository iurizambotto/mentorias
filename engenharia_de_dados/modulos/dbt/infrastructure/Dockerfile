# Pinned on purpose: the apostila states the versions it was verified against,
# and a floating tag would silently break that claim.
FROM python:3.11-slim

# dbt deps clones packages over git, and dbt debug fails the check without it.
RUN apt-get update \
    && apt-get install --no-install-recommends -y git \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir \
    "dbt-core==1.12.0" \
    "dbt-duckdb==1.10.1"

WORKDIR /projeto

# dbt looks for profiles.yml here instead of ~/.dbt, so the project stays
# self contained and nothing needs to be written to the mentee's home.
ENV DBT_PROFILES_DIR=/projeto

ENTRYPOINT ["dbt"]
CMD ["--version"]
