---
logical_name: forecasting_agent
google_drive_file_id: 19-COg8J9CWO10fwIjglT1bnOAiay_EytziwFm5L0SJE
source_title: Forecasting Agent - Complete System Design
sync_timestamp: '2026-09-19T14:11:19Z'
source_type: google_doc
---

# Forecasting Agent — Complete System Design (With RAG Knowledge Layer as Pre-Training Pipeline Parallel)

## Overview

The Forecasting Agent sits between the KDP forecasting platform and the planning team. The platform produces forecasts — the agent makes them actionable. It monitors every forecast cycle, diagnoses problems when they occur, and either acts autonomously or routes recommendations to the right human depending on the stakes involved.

**User Problems — Forecasting Agent**

1. Planners manually reviewed thousands of SKUs every cycle to find where the forecast looked wrong — taking 4 hours/week of work that should have been automatic \- almost 4 HC spent in just manual work.  
2. Once exceptions were found, planners had no structured guidance on what to do — 50% of forecasts were overridden or suppressed based on judgment calls with no suggested action or justification \- it drove overstock or stockouts. 5 Million in inventory cost.  
3. When accuracy dropped, planners and DS had to dig across multiple systems — data quality reports, model evaluation logs, pipeline dashboards — with no single structured diagnosis. DS had no systematic way to decide whether degradation needed a quick override or a full retrain — every decision was manual, inconsistent, and time-consuming  
4. There was no institutional memory — when a known failure pattern like a feed outage recurred, the investigation started from scratch every time. Override and retrain outcomes were never captured — the system couldn't learn from its own past decisions  
5. The feedback loop was calendar-driven, not signal-driven — degradation compounded across multiple cycles before anyone caught and acted on it

**The business impact:** DS and planner adoption suffered, trust in the platform eroded, and this was directly threatening Keystone's relationship with Hershey's — our flagship client. The problem wasn't forecast accuracy. The forecast was already 20% better than the incumbent. **The platform wasn't actionable at the speed the business needed.**

The agent has two layers:

**Action Layer** — three primary agents that monitor, diagnose, and recommend: Exception Triage, RCA Diagnostic, Retrain/Override Recommendation.

**Domain Adapted Knowledge Layer** — the RAG Knowledge Agent that provides institutional memory to every primary agent. This is where the pre-training pipeline parallel lives. The knowledge layer is not a static document store — it is a continuously maintained, multi-modal, domain-adapted corpus with an ingestion pipeline, embedding layer, retrieval architecture, eval feedback loop, and capacity model that mirrors how LLM pre-training pipelines are designed and operated.

Multi-modal documents are documents with different modalities including text, image, video, audio, structured/tabular, time-series.

The JD asks for someone who can define strategy for training pipelines, handle multi-modal documents, build feedback loops and evaluation systems, and plan capacity. Every one of those requirements maps to a specific design decision in this knowledge layer.

## Part 1: The Knowledge Layer — Built as a Pre-Training Pipeline

### Stage 1: Data Collection/Ingestion — Web Crawl Parallel

In LLM pre-training, data collection means: crawl the web, ingest books, pull code repositories, collect domain-specific corpora. Each source has different collection mechanics, update frequencies, and quality characteristics.

In the Forecasting Agent knowledge layer, data collection means: continuously ingest documents from every system in the KDP stack. Five source types, each with different collection mechanics:

**Source 1: Incident Records** Human-written narratives of data quality issues, root causes, and resolutions. Collected from the incident management system via event-driven trigger — every incident closure pushes a new document to the ingestion queue. These are the highest-value documents in the knowledge base: they encode the diagnostic reasoning that senior data scientists have developed over years. Without them, every Root Cause Agent starts from zero.

**Source 2: Data Readiness Reports** Structured JSON outputs from the Data Readiness Agent — validation verdicts, flagged dimensions, affected SKUs, confidence scores, recommended actions. Collected automatically after every validation run. Event-driven.

**Source 3: Model Evaluation Logs** wMAPE, bias, and accuracy metrics by segment, SKU tier, retailer, and time window. Collected from the ML evaluation service post-training. Event-driven.

**Source 4: Override and Retrain Decision Records** Every override decision — correction value, expiry window, rationale, outcome — and every retrain decision — config, trigger reason, expected vs. actual accuracy lift — stored as structured documents. These are the institutional memories of what humans decided and whether it worked. Collected via write hook in the approval workflow — when a planner or DS approves or rejects a recommendation, the decision is captured.

**Source 5: Reference Documents** SAP canonical schema definitions, retailer data contracts, trade calendars, item master snapshots, promo event registries. These are not generated by the pipeline — they are authored by humans or sourced from external systems. Collection is manual-trigger on change: when a retailer contract is updated or a new promo calendar is published, an ingestion job is triggered.

**Pre-training parallel:** Just as a pre-training pipeline pulls from Common Crawl (high volume, variable quality), Books (lower volume, high quality), and GitHub (domain-specific, structured), the knowledge layer pulls from five sources with different volume, quality, and update frequency profiles. The collection architecture — event-driven for high-frequency sources, manual-trigger for reference documents — mirrors how pre-training pipelines manage data freshness across heterogeneous sources.

**JD mapping:** *"Create strategies for collecting training data for next generation documents."* The collection strategy here is not "dump everything into a database." It is a deliberate architecture decision: which sources, at what frequency, with what collection trigger, and with what quality gate at the point of ingestion.

### Stage 2: Data Preparation — Pre-Training Filtering Parallel

In LLM pre-training, filtering means: remove duplicates, filter low-quality pages by perplexity, remove toxic content, apply domain quality scores, deduplicate near-identical documents.

In the knowledge layer, each source type has its own cleaning logic applied before any document enters the index.

**Deduplication:** Incident records from re-opened or re-escalated incidents get linked to the canonical incident document rather than ingested as duplicates. A new closure note on incident \#89 updates the existing document rather than creating a new one. This preserves the causal narrative across a multi-day incident without fragmenting it across multiple documents.

Pre-training parallel: near-duplicate removal in Common Crawl. The same web page scraped from 40 different domains is one document in the training corpus, not 40\.

**Quality filtering:** Pipeline logs that contain only success confirmations like "job completed, 0 errors" — are dropped. They have zero information density. Only logs that contain warnings, failures, retries, or anomalies are retained.

Data readiness reports with APPROVED verdicts and no flagged dimensions are summarized to a single-line metadata record rather than stored in full. A full report with no findings wastes index space and retrieves as noise when an agent is looking for problems.

Pre-training parallel: perplexity-based quality filtering. Pages with low information density — templated content, boilerplate, repetitive text — are filtered out before training.

**Normalization:** All client names normalized to canonical IDs: HERSHEYS, CORNING, MICHELIN. Prevents retrieval fragmentation where "Hershey's," "Hersheys," "HSY," and "The Hershey Company" all retrieve differently despite referring to the same entity.

All training run IDs normalized to a consistent format. All timestamps to ISO 8601\. All SKU identifiers to the canonical item master format.

Pre-training parallel: text normalization, unicode cleaning, encoding standardization. The goal in both cases is consistency of representation — the model or retrieval system should not treat surface variants of the same entity as semantically different.

**Confidentiality scrubbing:** Commercial volume data, revenue figures, and contract terms are masked before ingestion. The knowledge base is multi-tenant — Hershey's incident records must never surface to a Corning analyst. Masking happens at ingestion, not at retrieval, because defense at the retrieval layer alone is insufficient for a compliance-by-design system.

Pre-training parallel: PII removal from web crawl data. Compliance is built into the data pipeline, not handled as a retrieval-time filter.

**JD mapping:** *"Partner with Legal, Privacy, Security, HR, and Compliance teams to ensure platforms are compliant-by-design."* Compliance-by-design means the data pipeline enforces data boundaries before documents enter the index. It is not a retrieval-time access control layer bolted on afterward.

### Stage 3: Multi-Modal Document Handling (Parsing, which is part of data ingestion step)

The JD explicitly calls out: *"understanding models that are multi-modal and non-HTML like PDF."*

This is a real and specific challenge in the knowledge layer. Not all source documents are clean structured JSON. Three document types require non-trivial parsing:

**Type 1: SAP Schema Documentation — Layout-Heavy PDFs**

SAP schema docs arrive as PDFs with tables, nested hierarchies, field definitions in columns, and cross-references between pages. A naive PDF-to-text extraction loses the table structure entirely and produces sequences like: "Field Name Type Description VBELN CHAR Sales Document" \- three columns collapsed into a flat string with no separator semantics.

The parsing approach: layout-aware PDF extraction identifies table boundaries, preserves row-column relationships as structured key-value pairs, identifies section headers and uses them as chunk boundaries, and extracts cross-references as metadata links between chunks.

The PM decision: investing in layout-aware parsing for SAP schema docs was a deliberate scope call made after testing raw extraction. Raw extraction produced retrieval precision below 50% on schema questions — an agent asking "what is the VBELN field?" was retrieving random page fragments rather than the field definition chunk. Layout-aware parsing raised precision above 85% on schema queries.

**Type 2: Retailer Data Contracts — Legal PDFs**

Retailer contracts have clause numbering, defined terms, schedules, and annexes. The semantic structure — clause 4.2 modifies clause 3.1, Schedule A defines terms used in Section 2 — is encoded in layout and cross-reference, not in text flow.

The parsing approach: clause-level chunking using numbered headings as boundaries, defined terms extracted as a separate glossary chunk, cross-references preserved as metadata links so retrieval of clause 3.1 surfaces the modifying language in clause 4.2 as related context.

**Type 3: Trade Calendar and Promo Event Data — Semi-Structured Tables**

Promo calendars arrive as Excel exports or structured CSVs with event name, date range, retailer, SKU scope, and expected lift range. These are not prose documents — they are tabular data that needs to be queryable as structured retrieval ("what promo events are registered for Hershey's in Q1 2024?") and as semantic retrieval ("what promotional activity preceded the March forecast spike?").

The approach: each promo event row is converted to a document with structured metadata (date, retailer, SKU scope) plus a natural language description generated from the row values. This dual representation enables both metadata-filtered lookup and semantic search on the same event.

**Pre-training parallel:** This is exactly the JD requirement: building pipelines that handle multi-modal, non-HTML documents. In LLM pre-training, the analogous challenge is ingesting PDFs, scanned documents, code files, and structured data alongside web text — each requiring a different parsing strategy to extract the semantic content that makes the document useful for training. The PM decision in both cases is the same: you cannot treat all document types identically. Each format requires a parsing strategy matched to how its semantic structure is encoded

### Stage 4: Chunking Strategy — Tokenization Parallel

Chunking is the most direct PM-level parallel to tokenization decisions in pre-training. In pre-training, the decision is: what is the unit of learning — what token sequence does the model see at each training step, and at what context length? In RAG, the decision is: what is the unit of retrieval — what chunk does the system return in response to a query, and at what granularity?

The core tension in both cases is identical: too large and the unit contains irrelevant content alongside relevant content. Too small and the unit loses surrounding context needed to interpret it.

**Per-source chunking decisions:**

**Incident records → single document per incident** Never split. An incident narrative is a causal story: symptom, investigation, root cause, resolution. Splitting it creates chunks that contain the problem without the solution, or the solution without the context. An agent retrieving a split incident chunk and generating an RCA recommendation from the symptom-only fragment would produce a diagnosis without a resolution path.

PM decision rationale: I pushed back on the default engineering recommendation to chunk everything at 512 tokens uniformly. The cost of preserving incident records as single documents is slightly larger chunk size. The cost of splitting them is retrieval that surfaces half a story and generates a confidently wrong recommendation. The PM decision is asymmetric: the downside of splitting is much worse than the cost of larger chunks.

**Data readiness reports → chunked by validation dimension** Each of the seven validation dimensions becomes its own chunk, with shared metadata linking all chunks to the parent run ID. An agent asking about schema validation results for run v47 retrieves the schema dimension chunk, not the full report including temporal integrity, feature readiness, and hierarchy coherence results it doesn't need.

Rationale: agents ask dimension-specific questions. A chunk containing all seven dimensions is too large and retrieves dimensions the agent didn't ask about, adding noise to the context.

**Model evaluation logs → chunked by segment and time window** One chunk per SKU tier per evaluation cycle. Fast movers, slow movers, and new items are separate chunks even within the same evaluation run.

Rationale: degradation questions are almost always segment-specific. A chunk that mixes fast-mover and slow-mover wMAPE makes it impossible to retrieve targeted segment performance without pulling irrelevant comparison data.

**Pipeline logs → sliding window with overlap** 500-token chunks with 100-token overlap between adjacent chunks.

Rationale: pipeline logs are sequential and causal. A job failure in step 3 is explained by the output of step 2\. Overlap preserves continuity at chunk boundaries so the retrieval system can surface the context that explains an error, not just the error message itself.

Pre-training parallel: sliding window attention with overlap is used in pre-training to handle long documents — each training example overlaps with adjacent examples to preserve sequential context. The chunking logic here applies the same principle to retrieval.

**Reference documents → entity-level or clause-level** SAP schema docs chunked by entity type. Retailer contracts chunked by clause. Trade calendars chunked by event.

Rationale: reference queries are entity-specific or clause-specific. Retrieval at a higher granularity wastes context window on irrelevant entity or clause content.

### Stage 5: Embedding and Domain Adaptation — Domain-Adaptive Pre-Training Parallel

**What embedding does:** Converts each chunk into a dense vector capturing semantic meaning. Retrieval finds chunks whose vectors are closest to the query vector. The quality of retrieval is directly determined by the quality of embeddings — if the embedding model doesn't represent domain vocabulary correctly, retrieval fails regardless of how well everything else is built.

**The problem with general-purpose embeddings:**

General-purpose embedding models are trained on general web text. They have no exposure to supply chain ML vocabulary. Three concrete failure modes observed in baseline testing:

Failure 1: "SKU-location" as a hierarchy level and "SKU-location" as a data quality dimension produce identical embeddings. The model treats them as the same concept because the surface form is the same. An agent asking about hierarchy coherence issues at the SKU-location level retrieves data quality dimension chunks alongside hierarchy chunks — noise in the context.

Failure 2: "wMAPE" is unknown or loosely associated with "error metric." Queries about forecast accuracy degradation retrieve generic ML accuracy content rather than Keystone-specific evaluation logs.

Failure 3: "CONDITIONAL verdict" in a readiness report has no meaning to a general model. Queries about CONDITIONAL findings retrieve anything containing the word "conditional" — including contract clauses with conditional terms.

**The solution: domain-adaptive embedding fine-tuning**

This is the closest legitimate parallel to domain-adaptive pre-training in LLM pipelines. Domain-adaptive pre-training continues training a base LLM on domain-specific text to shift its internal representations toward the target domain before task-specific fine-tuning. The goal is the same: adapt the representation layer so that domain-specific terminology is represented with the correct semantic relationships.

**Step 1: Build the fine-tuning corpus** Collect question-chunk pairs from real agent usage:

* Questions ML engineers and planners actually asked  
* The chunks that correctly answered those questions — positive pairs  
* Chunks that were retrieved but were irrelevant — hard negative pairs

Hard negatives are critical: they teach the model to distinguish between chunks that are superficially similar (both contain "SKU-location") but semantically different (one is about hierarchy, one is about data quality). Without hard negatives, the model learns to retrieve relevant content generally but fails on the domain-specific disambiguation cases that matter most.

**Step 2: Fine-tune using contrastive learning** The embedding model is fine-tuned to minimize distance between positive query-chunk pairs and maximize distance between query and hard negative pairs. After fine-tuning, "wMAPE degradation Hershey's Q3" retrieves close to "forecast accuracy Q3 Hershey's chocolate seasonal wMAPE \+3.6 points" and far from "mean absolute percentage error general definition."

**Step 3: Evaluate on held-out retrieval pairs** Measure retrieval precision@5 before and after fine-tuning on a held-out set of known question-answer pairs. In baseline testing, precision@5 on domain-specific queries was 0.58 with a general model. Post fine-tuning: 0.87. That improvement is the justification for the investment — not a general best practice.

**Step 4: Refresh cadence** The embedding model is re-fine-tuned quarterly or when retrieval precision on the eval set drops below 0.80 — whichever comes first. New source types or significant vocabulary additions trigger an out-of-cycle refresh.

***Pre-training parallel articulation for interview:** "Domain-adaptive pre-training continues training a base LLM on domain-specific text before task fine-tuning — the goal is to shift the model's internal representations toward the target domain so that downstream tasks benefit from better-initialized weights. Embedding fine-tuning does the same thing for the retrieval layer. The decision logic is identical: when does the base model's representations diverge enough from your domain that the adaptation investment is justified? In our case, 58% precision on domain queries with the base model and 87% after fine-tuning answered that question clearly."*

### Stage 6: Metadata Tagging — Data Provenance Parallel

In pre-training pipelines, every document is tagged with: source domain, quality score, date, language, content type, deduplication hash. These tags enable filtered sampling, quality-weighted training, and retroactive exclusion when a source is found to be problematic.

In the knowledge layer, every chunk is tagged with metadata that enables filtered retrieval, compliance enforcement, and system management.

**Complete metadata schema:**

json  
{  
  "chunk\_id": "unique identifier",  
  "client\_id": "HERSHEYS / CORNING / MICHELIN",  
  "source\_type": "incident\_record / readiness\_report / eval\_log / override\_decision retrain\_decision / reference\_doc /  pipeline\_log",  
  "run\_id": "links related chunks to parent training run",  
  "incident\_id": "links to parent incident if applicable",  
  "date": "ISO 8601 — enables time-scoped retrieval",  
  "sku\_scope": \["list of SKU IDs in scope"\],  
  "retailer\_scope": \["WALMART", "TARGET", "KROGER", "COSTCO"\],  
  "segment": "chocolate\_seasonal / industrial / etc.",  
  "verdict": "APPROVED / CONDITIONAL / BLOCKED",  
  "severity": "tier\_1 / tier\_2 / tier\_3",  
  "root\_cause\_layer": "data / feature / model / external",  
  "freshness\_timestamp": "last updated",  
  "ingestion\_version": "tracks chunking strategy version",  
  "quality\_score": "0.0-1.0 — from cleaning pipeline",  
  "embedding\_model\_version": "tracks which fine-tuned model produced this vector",  
  "confidentiality\_level": "standard / masked / restricted"  
}

**How metadata is applied in retrieval:**

The retrieval pipeline uses a three-stage pattern: pre-filter → semantic search → re-rank.

Pre-filter uses metadata to narrow the search space before any vector computation. A query scoped to Hershey's incident records from Q3 2023 filters from 15,000 total chunks to 340 relevant chunks in milliseconds using an index scan — no embedding computation required at this stage.

Semantic search runs vector similarity within the filtered subset. Returns top-20 by cosine similarity.

Re-rank runs a cross-encoder model that reads the full query and each candidate chunk together — more expensive but significantly more precise than embedding similarity alone. Reduces top-20 to top-5 for the calling agent.

**Why metadata fields are PM decisions, not engineering defaults:**

Each metadata field was added to solve a specific retrieval failure:

`root_cause_layer` was added after the RCA agent started retrieving feature drift chunks when the query was about data pipeline failures — both contain "degradation" and "model accuracy" language. Filtering by `root_cause_layer = data` before semantic search eliminated the cross-layer retrieval noise.

`ingestion_version` was added after a chunking strategy change left the index with a mix of old and new chunk formats for the same source type. Without this field, there was no way to identify which chunks needed re-ingestion after a strategy change.

`embedding_model_version` was added to enable targeted re-embedding — when the fine-tuned embedding model is updated, only chunks embedded with the prior version need to be re-processed, not the entire index.

**Pre-training parallel:** In pre-training, document-level metadata enables quality-weighted sampling — you can up-weight high-quality sources and down-weight noisy ones without removing them. The `quality_score` metadata field serves the same purpose in retrieval: lower-quality chunks are not excluded but are de-prioritized in re-ranking.

### Stage 7: Retrieval architecture

The retrieval pipeline uses a three-stage pattern: pre-filter → semantic search → re-rank.

Pre-filter uses metadata to narrow the search space before any vector computation. A query scoped to Hershey's incident records from Q3 2023 filters from 15,000 total chunks to 340 relevant chunks in milliseconds using an index scan — no embedding computation required at this stage.

Semantic search runs vector similarity within the filtered subset. Returns top-20 by cosine similarity.

Re-rank runs a cross-encoder model that reads the full query and each candidate chunk together — more expensive but significantly more precise than embedding similarity alone. Reduces top-20 to top-5 for the calling agent.

### Stage 8: Vector Index and Capacity Planning — Infrastructure Parallel

**JD requirement:** *"Plan, size, and continuously optimize capacity (compute, storage, data throughput, and cost) to build, scale, and operate training pipelines reliably."*

**Index architecture:** The vector index is partitioned by the client. Three partitions: HERSHEYS, CORNING, MICHELIN. Partitioning serves two purposes: compliance isolation (Hershey's chunks are physically separated from Corning chunks, not just filtered at query time) and retrieval efficiency (pre-filter narrows search space within a partition before semantic search). Each partition is sized based on: document volume per client, expected query rate, and target retrieval latency. Hershey's is the largest client — larger partition, more replicas for query throughput.

**Storage tiers:** Three tiers with different cost and access profiles:

Raw documents retained in cold storage (Azure Blob). Purpose: re-ingestion when chunking strategy changes. Access frequency: low. Cost: minimal.

Chunk vectors stored in warm storage (vector database — Qdrant on Azure). Purpose: retrieval. Must be queryable within 500ms. Cost: higher — sized to query throughput requirements.

Eval logs and query logs stored in structured storage (Databricks Delta). Purpose: feedback pipeline, weekly health reports, embedding model refresh triggering. Cost: moderate.

**Embedding batch pipeline:**

New documents don't get embedded one at a time. They queue in a staging layer and are processed in batches by the embedding model on Azure Databricks. Batch size is tuned to balance ingestion latency (how quickly new documents become searchable) against compute cost (larger batches are more efficient but delay individual documents).

For event-driven sources (incidents, readiness reports, eval logs): target ingestion latency is under 2 hours — a new incident record should be searchable before the next RCA cycle runs.

For reference documents: ingestion latency target is 24 hours — these change infrequently and the latency is acceptable.

**Capacity sizing model:**

The PM-level capacity question is: as the client base grows from 3 to 10 clients, how does the system scale without degrading per-client retrieval quality or exceeding cost targets?

The answer is in the partitioning model: each new client gets its own partition. The vector database scales horizontally — new partitions don't affect existing partition query performance. Embedding batch pipeline scales by adding Databricks workers. The cost model is per-client: onboarding a new client adds a predictable incremental cost based on their document volume and query rate.

**Pre-training parallel:** Pre-training capacity planning involves: how many GPUs for training, how much storage for the corpus, what data throughput is needed to feed the training pipeline without GPU starvation. The decision framework is the same: size each component to the bottleneck, plan for scale horizontally not vertically, and model cost per unit of output (tokens trained, documents indexed).

# Part 2: Agent Design

## Agent Scope

The agent sits between the Deep Enterprise platform and the planning team. The platform produces forecasts — the agent makes them actionable. It monitors every forecast cycle, diagnoses problems when they occur, and either acts autonomously or routes recommendations to the right human depending on the stakes involved.

Three use cases, one agent architecture:

* **Use Case 1:** Proactive exception triage — runs after every forecast cycle \- Automatically scans every forecast after each generation cycle, ranks the SKUs that look wrong, and hands the planner a prioritized list with a diagnosis and recommended action — replacing hours of manual planner review.  
* **Use Case 2:** Forecast degradation RCA — triggered by accuracy threshold breach \- When forecast accuracy drops, the agent investigates autonomously across data, model, and signal layers, and produces a narrated explanation of what went wrong and why — replacing ad hoc DS investigation.  
* **Use Case 3:** Retraining and override recommendation loop — triggered by sustained degradation or structural demand shift \-  When sustained degradation is detected, the agent decides whether a quick statistical correction or a full model retrain is warranted, and either applies the fix or submits a pre-filled recommendation for approval.

> **The agent has a defined action library. It doesn't invent actions. Intelligence is in the reasoning. Guardrails are in the tool definitions.**

Every action the agent can take is pre-classified into one of three tiers:

**Agent guardrails:**

- Actions are tiered and only low risk, reversible actions are autonomous e.g., publishing an exception queue, raising a ticket to engineering, suppressing a segment  
- Confidence thresholding \- autonomous actions can only be taken if the issue crosses a certain threshold. Below the threshold, the action is a recommendation and human in the loop needs to approve.  
- Evaluation as the independent check \- every RCA and recommendation is scored independently by the evaluation agent on three dimensions:  
  - Faithfulness  
  - Layer sequence compliance  
  - Tier classification accuracy

| Tier | Label | When Used | Examples |
| ----- | ----- | ----- | ----- |
| 1 | Autonomous | High confidence, reversible, low stakes | Publish exception queue, suppress low-confidence segments, tag RCA metadata |
| 2 | Recommend \+ Approve | Medium confidence, or moderate stakes | Pre-fill override recommendation, submit retraining job request |
| 3 | Surface Only | Low confidence, or irreversible/high stakes | Flag data contract violation, recommend architecture change |

## Agent Workflow

Forecast Generation Cycle Completes  
            │  
            ▼  
    ┌──────────────────┐  
    │  Trigger Router                     │       ← determines which use case(s) to activate  
    └────────┬─────────┘  
                           │  
    ┌────────┼───────────────────┐  
    ▼                   ▼                                                 ▼  
\[Exception       \[RCA                           \[Retrain/Override  
 Triage         Diagnostic                         Recommendation  
 Agent\]            Agent\]                                           Agent\]  
    │        │                   │  
    └────────┴───────────────────┘  
                            │  
            ┌───────▼────────┐  
            │  Action                              │  
            │  Dispatcher                       │  ← applies tier classification  
            └───────┬────────┘  
                    │  
        ┌───────────┼───────────────┐  
        ▼                          ▼                                     ▼  
   Tier 1:                        Tier 2:                             Tier 3:  
   Execute                    Route to                       Surface to  
   Autonomously        approval queue        engineering/DS

## Agent 1: Trigger Router

1. Role: Runs immediately after every forecast generation cycle completes. Reads the forecast output, checks threshold conditions, and decides which downstream agents to activate. Does not diagnose anything — purely routes.  
2. Prompt:   
   1. You are the Trigger Router for the Forecasting Agent at Keystone.ai.  
   2. You run after every forecast generation cycle. Your job is to read the forecast output summary and decide which agents to activate.  
   3. You have no tools. You reason over the inputs provided and return a routing decision.  
   4. Activation rules:  
      1. EXCEPTION TRIAGE AGENT — activate if ANY of:  
         1. Any SKU/location forecast delta \> configured\_threshold vs prior cycle  
         2. Any SKU/location bias score outside \[-0.15, \+0.15\] for 2+ consecutive cycles  
         3. Data quality signal below 0.7 for any segment in scope  
      2. RCA DIAGNOSTIC AGENT — activate if ANY of:  
         1. Accuracy metric (wMAPE or bias) crosses degradation\_threshold for any segment  
         2. Planner has manually escalated an anomaly (escalation\_flag \= true)  
         3. Exception triage finds exception\_type \= "model\_issue" on a high-velocity SKU  
      3. RETRAIN/OVERRIDE AGENT — activate if ANY of:  
         1. RCA Diagnostic Agent concludes root cause is NOT a data issue  
         2. Sustained degradation over N consecutive cycles (N defined in config)  
         3. Structural demand shift detected: new product launch, customer loss, or macro event flag in trade calendar  
   5. Multiple agents can be activated in the same cycle.  
   6. Exception Triage always runs first.  
   7. RCA and Retrain/Override can run in parallel after triage completes.

   8. Return:  
   9. {  
   10.   "cycle\_id": string,  
   11.   "client\_id": string,  
   12.   "agents\_activated": \[list\],  
   13.   "activation\_rationale": {per agent: why activated},  
   14.   "priority\_segments": \[SKU/location combos requiring attention\],  
   15.   "escalation\_flag": true/false,  
   16.   "cycle\_summary": "2-sentence plain English summary of   
   17.     what triggered activation"  
   18. }

   19. Forecast output summary: {forecast\_summary}  
   20. Config thresholds: {config}  
   21. Escalation flag: {escalation\_flag}  
   22. Prior cycle accuracy: {prior\_accuracy}  
3. Input:   
   1. {  
   2.   "forecast\_summary": {  
   3.     "cycle\_id": "hersheys\_cycle\_47",  
   4.     "client\_id": "HERSHEYS",  
   5.     "total\_skus": 2400,  
   6.     "skus\_with\_delta\_above\_threshold": 23,  
   7.     "segments\_with\_accuracy\_breach": \[  
   8.       {  
   9.         "segment": "chocolate\_seasonal",  
   10.         "wMAPE\_prior": 11.2,  
   11.         "wMAPE\_current": 14.8,  
   12.         "bias": 0.21  
   13.       }  
   14.     \],  
   15.     "data\_quality\_flags": 2,  
   16.     "trade\_calendar\_events": \["Valentine's Day promo week 6"\]  
   17.   },  
   18.   "config": {  
   19.     "delta\_threshold": 0.15,  
   20.     "bias\_threshold": 0.15,  
   21.     "degradation\_threshold\_wMAPE": 2.0,  
   22.     "sustained\_degradation\_cycles": 3  
   23.   },  
   24.   "escalation\_flag": false,  
   25.   "prior\_accuracy": {"wMAPE": 11.2, "bias": 0.08}  
   26. }  
4. Output:  
   1. {  
   2.   "cycle\_id": "hersheys\_cycle\_47",  
   3.   "client\_id": "HERSHEYS",  
   4.   "agents\_activated": \[  
   5.     "exception\_triage\_agent",  
   6.     "rca\_diagnostic\_agent"  
   7.   \],  
   8.   "activation\_rationale": {  
   9.     "exception\_triage\_agent": "23 SKUs exceed delta threshold.   
   10.       2 data quality flags present.",  
   11.     "rca\_diagnostic\_agent": "chocolate\_seasonal segment wMAPE   
   12.       degraded 3.6 points — above 2.0 threshold. Bias at 0.21   
   13.       outside acceptable range."  
   14.   },  
   15.   "priority\_segments": \["chocolate\_seasonal"\],  
   16.   "escalation\_flag": false,  
   17.   "cycle\_summary": "Cycle 47 shows meaningful accuracy degradation   
   18.     in chocolate seasonal SKUs and 23 exceptions above threshold.   
   19.     Exception triage and RCA activated in sequence."  
   20. }  
5. Decision Logic After Output  
   1. exception\_triage\_agent always runs first  
   2. rca\_diagnostic\_agent activates in parallel once triage completes  
   3. retrain\_override\_agent activates only if RCA concludes   
   4. root cause requires it

## Agent 2: Exception Triage Agent

1. Role: Runs post every forecast cycle. Scores each SKU/location by exception severity, classifies the exception type, generates a ranked exception queue with a one-line diagnosis per item, and takes or recommends actions by tier. Actions include:  
   1. Tier 1 (autonomous):   
      1. Scores every SKU by how wrong the forecast looks, ranks them by severity, and publishes the prioritized list to the planner UI  
      2. Suppresses low-confidence SKUs from flowing into downstream systems like ERP or replenishment (autonomous)  
      3. Publishes ranked exception queue to the planner UI; suppresses low-confidence forecast segments from downstream publishing  
   2. Tier 2 (recommend \+ approve): Recommends how much to override a forecast with justification  
   3. Tier 3 (surfaces only): Flags a potential data contract violation for engineering review  
2. Prompt:  
   1. You are the Exception Triage Agent for the Forecasting Agent at Keystone.ai.  
   2. Your job is to review every SKU/location in the current forecast cycle, identify exceptions, classify them, and produce a ranked exception queue with tier-classified actions.  
   3. You have access to these tools:  
      1. \- get\_forecast\_delta(sku\_id, location\_id, cycle\_id) → returns current vs prior forecast delta  
      2. get\_bias\_history(sku\_id, location\_id, n\_cycles) → returns bias scores for last N cycles  
      3. get\_data\_quality\_score(sku\_id, location\_id, cycle\_id) → returns data quality signal 0.0-1.0  
      4. get\_rag\_context(query, client\_id) → retrieves relevant prior incidents or override history  
      5. publish\_exception\_queue(queue)   
         1. → Tier 1 action: publishes ranked queue to planner UI  
      6. \- suppress\_segment(sku\_id, location\_id, reason)   
         1. → Tier 1 action: suppresses segment from downstream publishing  
   4. Exception classification rules:  
      1. data\_issue: data quality score \< 0.7 OR known feed outage in pipeline logs  
      2. odel\_issue: data quality score \>= 0.7 AND bias outside threshold for 2+ cycles AND no external demand signal explains the delta  
      3. demand\_signal: external event in trade calendar explains the delta (promo, holiday, macro)  
   5. Severity scoring (0-10):  
      1. forecast\_delta\_score: delta magnitude normalized 0-10  
      2. bias\_persistence\_score: number of consecutive out-of-range bias cycles, capped at 10  
      3. data\_quality\_penalty: (1 \- data\_quality\_score) \* 10  
      4. final\_severity \= weighted average: 0.4 \* forecast\_delta \+ 0.4 \* bias\_persistence \+ 0.2 \* data\_quality\_penalty  
   6. Tier classification per exception:  
      1. Tier 1 (autonomous): severity \< 4 OR exception\_type \= demand\_signal with known calendar event  
      2. Tier 2 (recommend \+ approve): severity 4-7 OR exception\_type \= model\_issue on non-top-20-velocity SKU  
      3. Tier 3 (surface only): severity \> 7 OR exception\_type \= data\_issue with no known root cause OR exception\_type \= model\_issue on top-20-velocity SKU  
   7. For each exception produce:  
   8. {  
   9.   "sku\_id": string,  
   10.   "location\_id": string,  
   11.   "severity\_score": float,  
   12.   "exception\_type": "data\_issue"/"model\_issue"/"demand\_signal",  
   13.   "one\_line\_diagnosis": string,  
   14.   "tier": 1/2/3,  
   15.   "recommended\_action": string,  
   16.   "evidence": \[list of supporting signals\]  
   17. }  
   18. After scoring all exceptions:  
       1. Execute all Tier 1 actions autonomously  
       2. Queue all Tier 2 items for planner approval  
       3. Route all Tier 3 items to engineering or DS review  
   19. Client: {client\_id}  
   20. Cycle: {cycle\_id}  
   21. Priority segments: {priority\_segments}  
   22. SKU scope: {sku\_scope}  
3. ReAct Trace — Example for Chocolate Seasonal Segment  
   1. Thought: Start with the priority segment flagged by Trigger Router — chocolate\_seasonal. Get forecast delta and bias history.  
   2. Action: get\_forecast\_delta(sku\_id="choc\_seasonal\_group",  location\_id="ALL", cycle\_id="hersheys\_cycle\_47")  
   3. Observation: Average delta \+22% vs prior cycle across 18 SKUs.   
      1. Range: \+14% to \+31%.  
   4. Action: get\_bias\_history(sku\_id="choc\_seasonal\_group",   location\_id="ALL", n\_cycles=3)  
   5. Observation: Bias cycle 45: \+0.09. Cycle 46: \+0.18.   
   6.   Cycle 47: \+0.21. Trending positive, crossed threshold cycle 46\.  
   7. Action: get\_data\_quality\_score(sku\_id="choc\_seasonal\_group", location\_id="ALL", cycle\_id="hersheys\_cycle\_47")  
   8. Observation: Data quality score: 0.83. Above threshold.  No active feed flags.  
   9. Thought: Data quality is clean. Bias is persistent and worsening across 2 cycles. Delta is significant. No data issue. Check trade calendar before classifying as model\_issue.  
   10. Action: get\_rag\_context(query="chocolate seasonal Valentine's Day promo week 6 Hershey's", client\_id="HERSHEYS")  
   11. Observation: Trade calendar shows Valentine's Day promo registered for week 6\. Prior year uplift on chocolate seasonal: \+18-24%.  
   12. Thought: The \+22% delta is consistent with the Valentine's Day promo range from prior year. This is a demand\_signal exception, not a model\_issue. However, bias trending positively for 2 cycles is a separate concern — model may be systematically underforecasting this segment independent of the promo event.  
   13. Severity scoring:  
   14.   forecast\_delta\_score: 22% delta → 7.0  
   15.   bias\_persistence\_score: 2 cycles → 4.0  
   16.   data\_quality\_penalty: (1-0.83)\*10 → 1.7  
   17.   final\_severity: 0.4\*7.0 \+ 0.4\*4.0 \+ 0.2\*1.7 \= 2.8+1.6+0.34 \= 4.74  
   18. Exception type: demand\_signal (calendar event explains delta). But bias persistence is secondary concern → Tier 2 flag alongside  
   19. Tier: 2 (severity 4.74, demand\_signal but persistent bias warrants planner review)  
4. Output:  
   1. {  
   2.   "sku\_id": "choc\_seasonal\_group",  
   3.   "location\_id": "ALL",  
   4.   "severity\_score": 4.74,  
   5.   "exception\_type": "demand\_signal",  
   6.   "one\_line\_diagnosis": "Delta \+22% consistent with Valentine's Day   
   7.     promo (prior year range \+18-24%). Secondary concern: bias   
   8.     trending positive for 2 consecutive cycles — model may be   
   9.     systematically underforecasting this segment.",  
   10.   "tier": 2,  
   11.   "recommended\_action": "Review planner override for Valentine's   
   12.     promo week. Separately flag persistent bias for DS review   
   13.     — potential model recalibration needed.",  
   14.   "evidence": \[  
   15.     "forecast\_delta: \+22% cycle 47",  
   16.     "bias: \+0.09, \+0.18, \+0.21 cycles 45-47",  
   17.     "data\_quality\_score: 0.83 — clean",  
   18.     "trade\_calendar: Valentine's Day promo week 6,   
   19.       prior year uplift \+18-24%"  
   20.   \]  
   21. }  
5. Tier 1 Actions Executed Autonomously:  
   1. publish\_exception\_queue(ranked\_queue) → planner UI updated  
   2. suppress\_segment(sku\_id="low\_confidence\_group\_3",   
   3.   reason="data\_quality\_score 0.41, below 0.7 threshold")   
   4.   → 3 SKUs suppressed from downstream publishing

## Agent 3: RCA Diagnostic Agent

1. Role: Runs when accuracy metric crosses the degradation threshold or a planner escalates. Executes a structured diagnostic sequence — data pipeline first, then feature drift, then model performance, then external signals.   
   1. Tier 1 (Autonomous): Logs the incident with explanations and evidence  
   2. Tier 2 (Recommend \+ Approve): Pre-fills a backfill or statistical correction request for Data Scientist or planner approval (recommend \+ approve)  
   3. Tier 3 (Only recommends): Creates a pre-filled engineering ticket for data feed failures or infrastructure issues  
2. Prompt:  
   1. You are the RCA Diagnostic Agent for the Forecasting Agent at [Keystone.ai](http://Keystone.ai).  
   2. You run a structured diagnostic sequence to identify the root cause of forecast accuracy degradation. You must always follow this sequence — do not skip layers:  
   3. Layer 1: DATA PIPELINE HEALTH \- Check before anything else. Most degradation is data, not model.  
      1. Check feed freshness for all retailers in scope  
      2. Check for pipeline failures or data gaps in training window  
      3. Check data quality scores for degraded segment

   4. Layer 2: FEATURE DRIFT-  Only if Layer 1 is clean.  
      1. Check input feature distributions vs prior training window  
      2. Check promo flag consistency, price data, ACV data  
      3. Identify any features with distribution shift \> threshold

   5. Layer 3: MODEL PERFORMANCE \- Only if Layers 1 and 2 are clean.  
      1. Check model version and last training date  
      2. Check if degraded segment was in training scope  
      3. Check bias history trend

   6. Layer 4: EXTERNAL SIGNALS \- Run in parallel with Layers 2 and 3\.  
      1. Check trade calendar for unregistered events  
      2. Check macro signal flags  
      3. Check for known competitor or retailer actions

   7. You have access to:  
      1. check\_feed\_freshness(retailer\_id, client\_id) → returns last successful feed timestamp  
      2. check\_pipeline\_logs(segment, date\_range) → returns any failures or gaps  
      3. get\_data\_quality\_score(segment, cycle\_id) → returns quality score  
      4. check\_feature\_drift(feature\_name, segment, window\_current, window\_prior) → returns distribution shift score  
      5. get\_model\_metadata(model\_id) → returns version, training date, training scope  
      6. get\_rag\_context(query, client\_id) → retrieves prior incidents, override history, similar past degradation events  
      7. tag\_incident(segment, rca\_summary, evidence) → Tier 1: logs incident with evidence  
      8. prefill\_retraining\_request(config) → Tier 2: submits retraining job for DS approval  
      9. create\_engineering\_ticket(issue, evidence) → Tier 3: creates structured incident ticket for engineering review

   8. Stop at the layer where you find the root cause. If multiple causes are found, rank by contribution.

   9. After completing the diagnostic sequence, produce:  
      1. {  
      2.   "segment": string,  
      3.   "degradation\_magnitude": string,  
      4.   "root\_cause\_layer": "data"/"feature"/"model"/"external",  
      5.   "root\_cause\_summary": string (the narrated RCA —   
      6.     plain English, evidence-cited, 2-4 sentences),  
      7.   "evidence": \[list of supporting findings\],  
      8.   "contributing\_factors": \[secondary causes if any\],  
      9.   "confidence": 0.0-1.0,  
      10.  "tier\_actions": {  
          1. "tier\_1": \[autonomous actions taken\],  
          2. "tier\_2": \[recommendations queued for approval\],  
          3. "tier\_3": \[items surfaced for engineering/DS review\]  
          4. },  
      11. "downstream\_trigger": "retrain"/"override"/"monitor"/"none",  
      12. "downstream\_rationale": string  
   10. }

   11. Client: {client\_id}  
   12. Segment: {degraded\_segment}  
   13. Degradation: {degradation\_summary}  
   14. Cycle: {cycle\_id}

6. Full ReAct Trace — Hershey's Chocolate Seasonal RCA  
   1. Thought: Start with Layer 1 — data pipeline health.   
      1. Check all four retailers for Hershey's.  
   2. Action: check\_feed\_freshness(retailer\_id="WALMART", client\_id="HERSHEYS")  
   3. Observation: Last successful feed: 2 hours ago. Fresh.  
   4. Action: check\_feed\_freshness(retailer\_id="TARGET",  client\_id="HERSHEYS")  
   5. Observation: Last successful feed: 3 hours ago. Fresh.  
   6. Action: check\_feed\_freshness(retailer\_id="KROGER", client\_id="HERSHEYS")  
   7. Observation: Last successful feed: 11 days ago.   
      1. STALE — feed failure on \[date\].

      

   8. Thought: Kroger feed is 11 days stale. This is significant.   
      1. Check what Kroger's share of the chocolate seasonal segment looks like and whether pipeline logs show a failure.  
   9. Action: check\_pipeline\_logs(segment="chocolate\_seasonal", date\_range="last\_14\_days")  
   10. Observation: Argo job failure logged \[date-11\].   
       1. Kroger POS ingestion job failed — connection timeout.   
       2. No retry was successful. 18 chocolate seasonal SKUs at Kroger affected.

   

   11. Thought: Found root cause at Layer 1\. Kroger feed failure 11 days ago. 18 chocolate seasonal SKUs missing 11 days of actuals. Model trained on incomplete actuals — no need to check Layers 2 or 3\. Check Layer 4 in parallel to confirm no external confound.  
   12. Action: get\_rag\_context(query="Kroger feed failure chocolate seasonal Hershey's prior incidents", client\_id="HERSHEYS")  
   13. Observation: Prior incident \#89 (8 months ago): same Kroger feed failure pattern. Resolution: manual actuals backfill from Kroger portal. wMAPE recovered within 1 cycle after backfill.

   14. Thought: Prior incident confirms this is a known failure mode with a known resolution. Confidence high. Root cause is data — Kroger feed outage. Resolution path is clear: backfill actuals, suppress affected segments until backfill complete.

   15. Severity \+ tier:  
       1. Root cause: data pipeline — Layer 1  
       2. Known failure mode with prior resolution → high confidence  
       3. Engineering action needed for feed repair → Tier 3  
       4. Actuals backfill → Tier 2 (DS approval)  
       5. Segment suppression → Tier 1 (autonomous)  
7. Output:  
   1. {  
   2.   "segment": "chocolate\_seasonal",  
   3.   "degradation\_magnitude": "wMAPE \+3.6 points, bias \+0.21",  
   4.   "root\_cause\_layer": "data",  
   5.  "root\_cause\_summary": "Forecast accuracy on Hershey's chocolate  seasonal SKUs dropped 3.6 wMAPE points this cycle. Root cause: Kroger POS feed has been stale for 11 days due to an Argo job failure. 18 chocolate seasonal SKUs are missing 11 days of actuals. The model trained on incomplete actuals and produced a systematically biased forecast for this segment. No structural demand shift detected. Prior incident \#89 confirms this is a known failure mode — manual backfill from Kroger portal resolved it within one cycle.",  
   6.   "evidence": \[  
   7.     "Kroger feed last successful: 11 days ago",  
   8.     "Argo job failure logged \[date\]: connection timeout, no retry",  
   9.     "18 chocolate seasonal SKUs affected at Kroger",  
   10.     "Prior incident \#89: identical pattern,   
   11.       resolved via manual backfill"  
   12.   \],  
   13.   "contributing\_factors": \[  
   14.     "Bias was already trending positive for 2 prior cycles   
   15.       — possible pre-existing model drift independent of   
   16.       this data issue"  
   17.   \],  
   18.   "confidence": 0.94,  
   19.   "tier\_actions": {  
   20.     "tier\_1": \[  
   21.       "tag\_incident(segment='chocolate\_seasonal',   
   22.         rca='Kroger feed failure 11 days',   
   23.         evidence=\[...\])"  \],

   24.     "tier\_2": \[  
   25.       "Recommend: manual actuals backfill from Kroger portal for affected 18 SKUs. Pre-filled backfill request queued for DS approval.",  
   26.       "Recommend: suppress chocolate\_seasonal segment from  downstream publishing until backfill confirmed — queued for planner approval"   \],

   27.     "tier\_3": \[  
   28.       "Engineering ticket pre-filled: Kroger POS ingestion job failure — connection timeout. Retry logic review needed.Alert threshold: flag if feed stale \> 48 hours."  
   29.     \]  
   30.   },  
   31.   "downstream\_trigger": "monitor",  
   32.   "downstream\_rationale": "Root cause is data, not model.   
   33.     Retrain not required. Monitor accuracy after backfill —   
   34.     if bias persists beyond 1 cycle post-resolution,   
   35.     activate Retrain/Override Agent for the pre-existing   
   36.     drift concern."  
   37. }

## Agent 4: Retrain / Override Recommendation Agent

1. Role: Activated when RCA concludes degradation is not a data issue, or when sustained degradation has persisted over N cycles, or a structural demand shift is detected. Evaluates whether the fix is a statistical override (fast, targeted) or a full retrain (expensive, comprehensive).   
   1. Tier 1 (Autonomous): Applies a statistical override on small, high confidence segments   
   2. Tier 2 (Recommend \+ Approve): Submits a pre-filled retraining job with full configuration for DS approval   
   3. Tier 3 (Surface): Flags model architecture or feature pipeline gaps for DS and PM alignment before any action  
2. Prompt:  
   1. You are the Retrain/Override Recommendation Agent for the Forecasting Agent at [Keystone.ai](http://Keystone.ai).

   2. You are activated when forecast degradation cannot be resolved by fixing the data pipeline and requires either:  
      1. a statistical override — a targeted correction applied to a specific segment for a defined time window, or  
      2. a model retrain — a full or partial retraining of the forecasting model with updated data or features

   3. Your job is to:  
      1. Evaluate whether the degradation pattern warrants override or retrain  
      2. Compute the correction value for override path, or the training config for retrain path  
      3. Produce a pre-filled recommendation with full rationale  
      4. Never execute a retrain or override without approval — all actions in this agent are Tier 2 or Tier 

   4. Decision rules:  
      1. OVERRIDE is appropriate when:  
         1.   
         2. Degradation is segment-specific (\< 15% of total SKU scope)  
         3. Root cause is identifiable and time-bounded  (e.g., missed promo event, temporary demand shift)  
         4. Drift magnitude is correctable with a scalar adjustment  
         5. Degradation duration \< 3 cycles  
      2. RETRAIN is appropriate when:  
         1. Degradation is broad (\> 15% of SKU scope)  
         2. Root cause is structural: distribution shift in key features, new product mix, lost customer, macro regime change  
         3. Bias is persistent and worsening across 3+ cycles  
         4. Model training data no longer represents current demand regime

   5. You have access to:  
      1. \- get\_degradation\_history(segment, n\_cycles) → bias and wMAPE trend over N cycles  
      2. \- get\_feature\_drift\_report(segment) → distribution shift scores per feature  
      3. \- compute\_override\_value(segment, method) → computes correction scalar with confidence interval  
      4. \- get\_training\_config(model\_id) → returns current training window, features, SKU scope  
      5. \- get\_rag\_context(query, client\_id) → retrieves prior override decisions and outcomes,  prior retrain decisions and accuracy lift  
      6. \- prefill\_override\_request(segment, value, expiry\_window, rationale)   
   6.   	→ Tier 2: queues override for planner/DS approval  
      1. \- prefill\_retraining\_request(config, rationale) → Tier 2: queues retraining job for DS approval  
      2. \- flag\_architecture\_review(issue, evidence) → Tier 3: flags for DS \+ PM alignment

   7. Produce:  
      1. {  
      2. "recommendation\_type": "override"/"retrain"/"both",  
      3. "decision\_rationale": string,  
      4.  "override\_config": {if applicable},  
      5. "retrain\_config": {if applicable},  
      6. "expected\_accuracy\_lift": string,  
      7. "confidence": 0.0-1.0,  
      8. "prior\_precedent": string,  
      9. "tier\_actions": {...},  
      10. "expiry\_or\_review\_date": string  
      11. }

   8. Client: {client\_id}  
   9. RCA output: {rca\_output}  
   10. Degradation history: {degradation\_history}

3. ReAct Trace — Scenario: Sustained Bias on Corning Industrial SKUs  
   1. Thought: RCA concluded feature drift — no data issue. Check degradation history to see if this is segment-specific or broad, and how many cycles it has persisted.  
   2. Action: get\_degradation\_history(segment="industrial\_sku\_group",   n\_cycles=4)  
   3. Observation: wMAPE cycle 44: 9.1, 45: 10.3, 46: 11.8, 47: 13.2. Bias: \+0.11, \+0.14, \+0.19, \+0.23. Monotonically worsening. 4 consecutive cycles.Segment represents 28% of Corning SKU scope.  
   4. Thought: Degradation is broad (28% scope) and sustained (4 cycles, worsening). This rules out override — a scalar correction can't fix a monotonically drifting segment across 28% of SKUs. This is a retrain case. Check feature drift to understand what's driving it.  
   5. Action: get\_feature\_drift\_report(segment="industrial\_sku\_group")  
   6. Observation: ACV weighted distribution: drift score 0.81 — significant. Distribution data was last refreshed 6 months ago. Current in-store distribution for Corning industrial products has shifted materially since last training.  
   7. Thought: ACV distribution is the primary drift driver. Model was trained on a distribution reality that is now 6 months stale. Check prior retrain decisions  for this client for precedent.  
   8. Action: get\_rag\_context(query="Corning retrain ACV distribution drift prior decision", client\_id="CORNING")  
   9. Observation: Retrain decision 14 months ago — same driver: ACV distribution staleness. Resolution: refreshed ACV data, retrained with 18-month window. wMAPE improvement: 2.1 points within 2 cycles.  
   10. Thought: Strong precedent. Same root cause, same resolution path. Retrain recommendation is clear. Compute training config.  
   11. Action: get\_training\_config(model\_id="corning\_autogluon\_v12")  
   12. Observation: Current training window: 24 months. ACV feature last refreshed: 6 months ago. SKU scope: all industrial SKUs.  
4. Output:  
   1. {  
   2.   "recommendation\_type": "retrain",  
   3.   "decision\_rationale": "Degradation is broad (28% of SKU scope), sustained across 4 consecutive cycles with monotonically worsening wMAPE and bias. Root cause is ACV distribution staleness — current in-store distribution for Corning industrial products has shifted materially since the last data refresh 6 months ago. A scalar override cannot correct a structural feature drift of this magnitude. Prior retrain for same root cause (14 months ago) produced 2.1 point wMAPE improvement within 2 cycles.",  
   4.   "override\_config": null,  
   5.   "retrain\_config": {  
      1. "model\_id": "corning\_autogluon\_v12",  
      2. "trigger\_reason": "ACV distribution drift — feature staleness",  
      3. "recommended\_training\_window": "18 months",  
      4. "feature\_refresh\_required": \["acv\_weighted\_distribution"\],  
      5. "sku\_scope": "industrial\_sku\_group",  
      6. "expected\_duration": "6-8 hours compute"  
      7.   },  
   6. "expected\_accuracy\_lift": "1.8-2.3 wMAPE points based on prior retrain precedent",  
   7. "confidence": 0.89,  
   8. "prior\_precedent": "Retrain cycle 14 months ago — identical ACV staleness driver, 2.1 point wMAPE improvement within 2 cycles",   
   9. "tier\_actions": {  
      1. "tier\_1": \[\],  
      2. "tier\_2": \[ "Retraining job request pre-filled with above config.    Queued for DS approval. DS to review feature refreshscope and  approve compute allocation."\],  
      3. "tier\_3": \["Flag for PM: ACV distribution data has a 6-month refresh lag. Consider building an automated ACV freshness check into the Data Readiness Agent to catch this earlier — before degradation accumulates over 4 cycles."\]  
      4. },  
   10. "expiry\_or\_review\_date": "Review accuracy 2 cycles post-retrain completion"  
   11. }

## Agent 5: RAG Knowledge Agent (Supporting)

1. Role: Called by any primary agent via `get_rag_context()`. Retrieves relevant historical context — prior incidents, override decisions, retrain outcomes, trade calendar events. This is the institutional memory layer. Sits behind a single tool interface so the primary agents don't need to know how retrieval works.  
2. Prompt:  
   1. You are the RAG Knowledge Agent. You are called by other agents via get\_rag\_context(query, client\_id).

   2. You retrieve relevant historical context from the Keystone knowledge base to inform the calling agent's reasoning.

   3. Knowledge base contents:  
      1. \- Incident records: past data quality issues and resolutions  
      2. \- Override history: past override decisions,  correction values, outcomes  
      3. \- Retrain history: past retrain decisions, configs, accuracy lift achieved  
      4. \- Trade calendar: promo events, holidays, macro flags  
      5. \- Data readiness reports: past validation run findings  
      6. \- Model evaluation logs: wMAPE/bias history per segment

   4. For each get\_rag\_context() call:  
      1. Apply client\_id filter to scope retrieval  
      2. Run semantic search on the query  
      3. Re-rank top results  
      4. Return the 3 most relevant items with full content and source metadata  
   5. Return:  
   6. {  
      1. "results": \[  
   7.     {  
   8.       "source\_type": string,  
   9.       "date": string,  
   10.       "content": string,  
   11.       "relevance\_score": float,  
   12.       "source\_id": string  
   13.     }\],  
   14.   "retrieval\_confidence": float,  
   15.   "gaps": string (what relevant context was NOT found)  
   16. }

## Agent 6: Eval Agent

1. Role: Runs asynchronously after every RCA and recommendation produced by the primary agents. Scores diagnosis quality and feeds findings back into agent improvement.  
   1. Scores every RCA and recommendation on three dimensions: is every claim supported by evidence, was the diagnostic sequence followed correctly, and were actions classified into the right tier  
   2. Flags outputs that fall below threshold for human review,   
   3. Feeds findings back into the agent prompt refinement and knowledge base improvement  
2. Prompt:  
   1. You are the Eval Agent for the Forecasting Agent at [Keystone.ai](http://Keystone.ai). You evaluate the quality of diagnoses and recommendations produced by the RCA Diagnostic Agent and the Retrain/Override Recommendation Agent.

   2. For each output you evaluate, score on three dimensions:

   3. DIMENSION 1: DIAGNOSTIC FAITHFULNESS  
      1. Are all claims in the RCA or recommendation directly supported by the evidence listed? Are there any conclusions that go beyond what the evidence shows?  
      2. Score 1.0 \= every claim has explicit evidence support  
      3. Score 0.0 \= conclusions drawn without evidence

   4. DIMENSION 2: LAYER SEQUENCE COMPLIANCE  
      1. Did the RCA Diagnostic Agent follow the required sequence:   
      2. data → feature → model → external?  
      3. Did it stop at the layer where root cause was found?  
      4. Score 1.0 \= sequence followed correctly  
      5. Score 0.0 \= layers skipped or wrong sequence

   5. DIMENSION 3: TIER CLASSIFICATION ACCURACY  
      1. Were actions correctly classified as Tier 1/2/3 based on reversibility and stakes?  
      2. Score 1.0 \= all tier classifications correct  
      3. Score 0.0 \= autonomous action taken on irreversible decision

   6. Return:  
      1. {  
      2.   "diagnostic\_faithfulness": {score, rationale,   unsupported\_claims},  
      3.   "layer\_sequence\_compliance": {score, rationale},  
      4.   "tier\_classification\_accuracy": {score, rationale, misclassified\_actions},  
      5.   "overall\_score": float,  
      6.   "action\_required": "none"/"flag\_for\_review"/"agent\_prompt\_review",  
      7.   "improvement\_note": string  
      8. }  
   7. Threshold:   
   8.   tier\_classification\_accuracy \< 0.9 → agent\_prompt\_review  
   9.   Any Tier 1 action taken on irreversible decision →   immediate flag, human review

## Complete End-to-End Flow — One Cycle

Forecast cycle 47 completes for Hershey's  
          │  
          ▼  
    Trigger Router  
    → Activates: Exception Triage \+ RCA Diagnostic  
    → Priority segment: chocolate\_seasonal  
                    │  
    ┌─────┴──────────────────────┐  
    ▼                                                                       ▼  
Exception Triage Agent      RCA Diagnostic Agent  
→ Scores 23 exceptions      → Layer 1: Kroger feed   
→ Chocolate seasonal:         stale 11 days  
  Tier 2, demand\_signal     → Layer 4: no external  
  \+ bias concern              confound  
→ Tier 1: publishes         → Confidence: 0.94  
  exception queue           → Root cause: data  
→ Tier 1: suppresses        → Tier 1: tag incident  
  3 low-quality segments    → Tier 2: backfill request  
→ Tier 2: pre-fills           queued for DS approval  
  override rec for          → Tier 3: engineering  
  planner review              ticket created  
    │                            │  
    └────────────┬───────────────┘  
                                     ▼  
          Eval Agent (async)  
          → Scores both outputs  
          → All dimensions \> 0.9  
          → No action required  
                 │  
                 ▼  
    downstream\_trigger \= "monitor"  
    Retrain/Override Agent NOT activated  
    Review scheduled: post-backfill cycle 48

# Part 3: Eval Feedback Loop — Pre-Training Parallel

**In a pre-training pipeline:** Benchmark evaluation identifies weak categories → trace to training data → collect more domain data or re-weight the mix → retrain → re-evaluate.

**In the Forecasting Agent:** Eval Agent scores RCA quality → low retrieval completeness traced to knowledge base gaps → KB review ticket opened → ML engineer adds missing source type, re-chunks affected documents, or triggers embedding model refresh → re-index → retrieval quality improves.

The feedback loop:

Weekly aggregation on eval\_log Delta table:  
    
  retrieval\_completeness \< 0.75 on \> 20% of queries for a source\_type  
  → KB review ticket: re-chunk or add source type

  faithfulness \< 0.70 on any RCA  
  → Immediate human review: was a wrong diagnosis acted on?

  tier\_classification\_accuracy \< 0.90  
  → Agent prompt review: tier classification rules need refinement

  embedding\_precision on eval set drops below 0.80  
  → Trigger embedding model fine-tuning refresh

  Any Tier 1 irreversible action flagged  
  → Immediate escalation to PM \+ engineering

**Who acts on it:** The Eval Agent surfaces findings in a weekly KB health report. An ML engineer reviews and decides: re-chunk, re-ingest, add source type, or trigger fine-tuning. In a more mature system, re-chunking and re-ingestion of low-quality source types can be triggered automatically — the embedding fine-tuning refresh always requires human approval because it affects the entire retrieval layer.

# Part 4: Metrics Throughout the Architecture

**JD requirement:** *"Define success criteria, OKRs, and KPIs across multiple product surfaces."*

| Layer | Metric | Target | Why |
| ----- | ----- | ----- | ----- |
| Ingestion | Documents ingested per day | SLA by source type | Are new incidents searchable before the next RCA cycle? |
| Ingestion | Ingestion lag by source type | \< 2hr event-driven, \< 24hr reference | Freshness requirement per source |
| Cleaning | Deduplication rate | \< 5% duplicates in index | Index quality |
| Chunking | Chunk size distribution | Within target range per source type | Retrieval precision proxy |
| Embedding | Retrieval precision@5 on eval set | \> 0.85 | Primary embedding quality metric |
| Retrieval | Recall@5 | \> 0.85 | Is the right context being found? |
| Retrieval | Retrieval latency p50/p95 | \< 500ms p95 | Within latency budget for RCA cycle |
| RCA Agent | Layer sequence compliance | \> 0.95 | Is the diagnostic logic being followed? |
| RCA Agent | Diagnostic faithfulness | \> 0.90 | Are RCAs evidence-grounded? |
| Tier classification | Tier 1 irreversible action rate | 0 | Critical guardrail metric |
| Business | Planner exception triage time | \< 30min per cycle | Was 2-3 hours manually |
| Business | DS RCA investigation time | \< 1 cycle | Was 4-6 hours |
| Business | Retrain trigger accuracy | \> 80% retrains justified | Are we triggering retrains that improve accuracy? |
| Feedback loop | KB review tickets opened per week | Tracked | Signal for KB health |
| Feedback loop | Time to resolve KB gap | \< 2 weeks | Is the feedback loop actually closing? |
