---
logical_name: data_platform
google_drive_file_id: 11QBYF-j3RYKq_82bu465oumOUh3u5inSeWATLgftQqI
source_title: Data Platform Product Strategy
sync_timestamp: '2026-09-19T14:05:28Z'
source_type: google_doc
---

# Data Platform Product Strategy

## Problems

1. ### Root problem \- There was no shared mental model of how enterprise supply chain data works

   1. Across clients (Hershey, Corning, Michelin):  
      1. Data existed in:  
         1. SAP tables (cryptic, normalized, business-encoded)  
         2. Spreadsheets (business logic)  
         3. Data warehouses (Snowflake)  
         4. Ad-hoc extracts  
      2. No one had a **connected understanding of:**  
         1. What is an *order* vs *shipment*  
         2. Which table is source of truth  
         3. How dates relate (order\_date vs shipment\_date vs requested\_delivery\_date)  
         4. How entities join (order\_line, schedule\_line, shipment\_line)  
   2. So every new client required: **Weeks of data discovery \+ reverse engineering SAP**

2. ### Fragmented & Untrusted Data Foundation across Keystone

   1. Data extracted from client environment was scattered across:  
      1. Multiple S3 buckets in different AWS accounts  
      2. Box / SharePoint  
      3. Individual laptops  
      4. Notebooks  
   2. No visibility into: What datasets exist, Which version is correct, What each dataset represents  
   3. Scientists couldn’t reliably find or reuse datasets  
   4. No clear governance which could lead to an enterprise trust issue  
   5. Blocked cross-client learning and reuse  
   6. No auditability

3. ### No standardized ingestion layer: Every client required custom ingestion pipelines

   1. No reusable ingestion framework  
   2. Data onboarding required: Custom scripts, Manual mapping  
   3. Highly engineering-dependent  
   4. Onboarding took months  
   5. High cost per client  
   6. Slowed sales \+ deployment velocity

4. ### Transformation pipelines rebuilt from scratch: 

   1. Each client had: Custom ETL logic, Logic locked inside their environment  
   2. Keystone couldn’t reuse or extend pipelines  
   3. Couldn’t process new data snapshots independently  
   4. Slowed iteration cycles

5. ### No Canonical Data Model (SAP Learnings Not Leveraged)

   1. No learning or reuse from common SAP schemas  
   2. Most clients used: Orders, Shipments, Promotions, Pricing, Item master, customer master, location master  
   3. But:  
      1. No standard schema abstraction  
      2. No reusable transformation logic  
   4. Repeated schema understanding effort  
   5. Inconsistent outputs across clients  
   6. Lost opportunity to build domain advantage

6. ### Data quality handled inconsistently:

   1. Quality checks existed: Only in client pipelines  
   2. Scientists: Created custom datasets locally where no validation applied  
   3. Rework across scientists in every project  
   4. Silent data issues in experimentation  
   5. Model performance inconsistency  
   6. Trust erosion

7. ### No Standardized Data Access for Scientists:

   1. Scientists: Pulled data manually, Used different tools  
   2. No standardized interface  
   3. It Slowed experimentation  
   4. Increased onboarding time for new scientists  
   5. Inconsistent data usage

8. ### Feature encoding logic inconsistent and hard to reuse:

   1. Feature engineering: Built per project, Not standardized  
   2. No reuse of encoders across science models, logic siloed to specific models  
   3. Scientists could not setup encoders in data pipelines  
   4. Repeated effort  
   5. Inconsistent model inputs  
   6. Slowed experimentation

9. ### Data not structured for UI consumption:

   1. Forecast UI required: Fast APIs, Clean datasets  
   2. Data pipelines not designed for UX  
   3. Slowed product development  
   4. Poor user experience

10. ### Lack of End-to-End Platform Thinking:

    1. No unified platform  
    2. Each layer evolved independently  
    3. Integration complexity  
    4. Slower product evolution  
    5. Poor scalability

11. ### No Standardized Infrastructure Deployment Across Client: Every client deployment required:

    1. Manual infra setup: Glue, Athena, dbt pipelines, APIs  
    2. Differences across: AWS vs Azure environments  
    3. Slow onboarding  
    4. Inconsistent environments 

12. ### Lack of Standardized Model Input Interface

    1. Models consumed data in: Different formats, Different schemas  
    2. Each model required: Custom preprocessing 

## Product Strategy

1. ### Schema Registry \+ Data understanding layer:

   1. Entity-level understanding  
      1. Orders (intent)  
      2. Shipments (execution)  
      3. Reconciliation (mismatch between intent vs execution)  
   2. Date semantics (VERY important IP you built)  
      1. Order date  
      2. Requested delivery date  
      3. Scheduled date  
      4. Shipment date  
      5. Delivery date

2. ### Centralized Data Platform \+ governed storage layer:

   1. Standardized data storage in: S3 \+ Glue catalog  
   2. Dataset registration

3. ### Data Connectors: Built ingestion services for:

   1. SAP  
   2. Snowflake  
   3. POS systems  
   4. Impact:  
      1. Reduced onboarding time significantly  
      2. Enabled repeatable deployments  
      3. Decoupled ingestion from client-specific implementations

4. ### Standardized transformation system (dbt \+ layered architecture)

   1. Layered architecture:   
      1. Raw: raw client data  
      2. Bronze: Corrected data types  
      3. Silver: Master and transactional datasets (dim\_product, dim\_customers, dim\_locations, fact\_orders, fact\_shipments)  
      4. Gold:   
         1. Transactional datasets enriched with master information (fact\_orders\_enriched, fact\_shipments\_enriched)  
         2. Datasets aggregated to specific hierarchies (e.g., product\_id, ship\_to\_region)  
      5. Platinum  architecture: Model ready in forecast input schema (primary\_key, timestamp, time-variant, time invariant features)  
   2. Built reusable transformation logic using: dbt pipelines  
   3. Externalized transformation logic from client environments  
   4. Impact:  
      1. Reusable transformation components  
      2. Keystone regained control over data pipelines  
      3. Faster iteration on new data snapshots

5. ### Schema Registry \+ Canonical Models

   1. Built canonical schema aligned to: SAP structures, Supply chain entities  
   2. Captured: Entity definitions, Relationships, Standard transformations  
   3. Impact:  
      1. Enabled cross-client reuse  
      2. Built Keystone’s data moat in supply chain domain  
      3. Reduced onboarding \+ alignment time

6. ### Centralized validation framework

   1. Built validation pipelines using: Great Expectations  
   2. Applied across: Ingestion, Transformation, Consumption layers  
   3. Standardized checks: schema validation, null checks, business rules  
   4. Impact:  
      1. Proactive issue detection  
      2. Consistent data quality across environments  
      3. Improved model reliability

7. ### Controlled access patterns: Built CoreAI-IO client:

   1. Programmatic data access exposed by Glue and Athena  
   2. Pre-signed URL support  
   3. Supported:  
      1. Pandas (by default)  
      2. Polars (for large-scale data like Michelin)  
   4. Enabled access via: Science workbench notebooks  
   5. Impact:  
      1. Standardized data access across all scientists and production environments  
      2. Enabled large-scale data processing  
      3. Faster experimentation cycles  
      4. Reduced friction for scientists

8. ### Feature Encoding Service: 

   1. Encoder registry: Central repository of reusable encoders  
      1. Time-based encoders:  
         1. Day\_of\_week  
         2. Month  
         3. Day\_of\_year  
         4. cyclical encodings (sin/cos)  
      2. Business calendar encoders:  
         1. workday / holiday flags  
         2. workdays per month  
      3. Demand behavior encoders:  
         1. Dominant\_day\_of\_week  
         2. inter-arrival time  
         3. order frequency  
      4. Sequence / lifecycle encoders:  
         1. event sequence features  
         2. lifecycle duration  
      5. Causal encoders:  
         1. next\_quantity (expanding mean / smoothing)  
         2. lag-based features   
   2. Feature pipelines: Ability to chain encoders into workflows  
   3. Support for:  
      1. Time-based encodings  
      2. Behavioral encodings  
      3. Aggregations  
   4. Impact:  
      1. Standardized feature engineering  
      2. Reduced duplication of effort  
      3. Enabled reusable ML pipelines

9. ### Data Platform API Service: 

   1. Built APIs for: Dataset access, Forecast consumption  
   2. Designed datasets aligned to: UX needs  
   3. Key API endpoints enabled \-   
      1. Time-series API \- Returns demand/forecast series  
      2. Event behavior API \-   
         1. Order patterns \- day of week, order quantity, order number  
         2. Shipment patterns  
      3. Product master API \- product attributes  
      4. Customer master API \- customer attributes  
      5. Event stream API  
   4. Impact:  
      1. Enabled scalable UI interfaces  
      2. Improved planner experience

10. ### End-to-end Data Platform architecture:

    1. Integrated: Ingestion, Transformation, Validation, Access, APIs  
    2. Impact:  
       1. Unified platform foundation  
       2. Enabled Deep Enterprise to scale  
       3. Shifted Keystone from: “project-based delivery” → “platform-based delivery”

11. ### Metadata layer:

    1. Dataset inventory across: Bronze / Silver / Gold / Platinum layers  
    2. Dataset properties: Primary key, Timestamp columns  
    3. Semantic classification: Forecast input vs output  
    4. Impact:  
       1. Enabled **dataset discoverability**  
       2. Introduced **governance \+ auditability**  
       3. Became the backbone for: Data access (CoreAI-IO), APIs (DP API Service), Transformation pipelines

12. ### Standardized Infra via Pulumi (Multi-Cloud Deployment Layer)

    1. Pulumi-based infrastructure-as-code framework to deploy:   
       1. S3/ADLS  
       2. Glue catalog  
       3. Athena query layer,   
       4. dbt transformation pipelines,  
       5. Argo/scheduled pipelines  
       6. Containerized execution  
       7. Data Platform API Service  
       8. Coreai-IO  
       9. Great expectations  
    2. Designed for: AWS \+ Azure compatibility  
    3. Standardized: IAM roles, Networking, Environment configs  
    4. Impact:  
       1. Reduced environment setup time drastically  
       2. Enabled **repeatable, production-grade deployments**  
       3. Ensured **consistency across clients**  
       4. Critical enabler for **scaling platform beyond 1–2 clients**

13. ### Standard Forecasting Input Schema:

    1. defined a canonical modeling contract: Primary key, Timestamp, Time-variant features, Time-invariant features   
    2. Impact:  
       1. Standardized model ingestion  
       2. Reduced model-specific data prep  
       3. Enabled:  
          1. Plug-and-play modeling pipelines  
          2. Multi-model experimentation

14. ### Data Platform UX:

    1. Capabilities:  
       1. View datasets  
       2. View schema  
       3. View sample data  
       4. View AWS location  
       5. View dbt transformation logic  
       6. View lineage (end-to-end)  
    2. Enabled:  
       1. Scientists  
       2. PMs  
       3. Business users

15. ### Event Stream architecture:

    1. Core Philosophy (Why Event Stream Exists): At its core, the **event\_stream** model transforms enterprise data from:  
       1. static tables (orders, shipments) → into immutable, time-aware business events  
       2. Immutability (no updates, only new events)  
       3. Dual time semantics:  
          1. Business time (`event_time`)  
          2. System time (`system_ts`)  
       4. Idempotency (same input → same event\_id)  
    2. High-Level Architecture:  
       1. Source Systems (SAP, ERP, Spreadsheets, DW)  
       2. Bronze Layer (raw ingestion)  
       3. Silver Layer (normalized tables)  
       4. Event Stream Builder (core logic)  
       5. Gold Layer:  
          1. Event\_stream  
          2. Event\_stream\_enriched  
    3. Core Data Model:  
       1. event\_stream (Canonical Event Table):  
          1. Grain: 1 row \= 1 event  
          2. Event\_id \= Deterministic unique ID \= hash(tenant, source\_table, source\_primary\_key, event\_type, event\_time)  
             1. Same inputs → same event\_id (idempotent)  
             2. Any change → new event\_id  
             3. No overwrites ever  
          3. Source\_table \= orders / shipments  
          4. Source\_pk \= Source primary key  
          5. Event\_type \=   
             1. Order\_created \= order\_date  
             2. Order\_requested\_delivery \= requested\_delivery\_date  
             3. Scheduled\_date \= scheduled\_date  
             4. Order\_reserved \= reserved\_date  
             5. Original\_promise \= original\_promise\_date  
             6. New\_promise \= new\_promise\_date  
             7. Goods\_movement \= shipment\_date  
             8. Delivery\_arrived \= delivery\_date  
          6. Event\_time \= When event actually occurred Example: shipment\_date, order\_date  
          7. System\_ts \= When the system observed the event. Enables Late-arriving data tracking, Replay, Audit trails  
          8. Event\_category \=   
             1. order \= Intent (demand)  
             2. Shipment \= Execution (fulfillment)  
             3. reconciliation \= Conflict resolution when orders and shipments disagree.   
          9. Event\_form \=   
             1. created \= First occurrence  
             2. Updated \= Attribute change  
             3. Cancelled \= Logical deletion  
             4. status\_update \= Only status changed  
             5. Split shipment \= One order → multiple shipments  
          10. Event\_class \= business / reconciliation  
       2. Event\_stream\_enriched: Extends event\_stream with:  
          1. Measures (qty, revenue)  
          2. Static attributes (product, customer)  
          3. Derived features  
          4. Measures are attached ONLY from Source-of-Record (SoR) to avoid leakage/double counting  
    4. Primary Key Strategy (Multi-Tenant Complexity): Event model decouples from source PK inconsistencies  
       1. Hershey:   
          1. Orders: (sales\_document, item\_id)  
          2. Shipments: (shipment\_id, shipment\_item\_id)  
       2. Corning:  
          1. Orders: (order\_no, line\_no, schedule\_line\_nbr, product\_id)  
          2. Shipments: (order\_no, line\_no, schedule\_line\_nbr, invoice, product\_id, pom)  
    5. Data Quality & Real-World Challenges:  
       1. 97% overlap between orders and shipments  
       2. Some orphan shipments exist  
       3. Missing product\_id / customer\_id issues  
       4. Schedule line complexity creates duplicates  
    6. Benefits:  
       1. **Lifecycle visibility:** Enables delay attribution, SLA measurement  
       2. **Auditability:** Full history of changes  
       3. Compare event\_time vs system\_ts, which allows for model updated when an event changes in real-time  
          1. New order → trigger forecast update  
          2. Shipment delay → trigger inventory reallocation  
          3. Promise date change → trigger customer risk alert  
       4. **ML Feature Generation:**   
          1. Lifecycle features:  
             1. Time between order → shipment  
             2. Delivery delays  
             3. Order lifecycle stages  
             4. Dominant ordering day  
             5. Next quantity prediction  
          2. Time-based encodings  
       5. A Universal Event Abstraction Layer for Enterprise Data \-   
          1. abstracting SAP complexity  
       6. Multi-tenant standardization:  
          1. Across Hershey, Corning, Michelin: Different schemas, Different PKs, Different data quality  
          2. Event stream: Created canonical abstraction layer  
          3. Standardized event definitions across clients  
    7. Integration with Deep Enterprise Platform: Used by:  
       1. Forecasting models  
       2. Feature engineering pipelines  
       3. User Experience

16. ### coAI Agent \- Data Readiness Agent for Forecasting

    1. Use-case: validates a dataset before model training for forecasting  
       1. scientist provides input dataset  
       2. Agent fetches data from data platform  
       3. Runs all the required validations for a forecasting model  
       4. Provides an output report for the scientist to understand data quality before model training  
    2. User: Scientist within Keystone working on forecasting models  
    3. Trigger: scientists initiated, through a chat prompt  
    4. **Why an agent, not just code:**   
       1. Data readiness for forecasting requires contextual judgment, not just rule execution. Whether zero inflation is a blocker depends on the demand pattern. Whether a column like `next_delivery_date` is a leakage risk depends on what it semantically means in a supply chain context. Whether the dataset has enough history depends on the forecast horizon. None of that is deterministic — it requires reasoning over the scientist's modeling context. So I designed the agent as a thin reasoning layer on top of deterministic tooling: Great Expectations handles the measurement layer, the agent handles the judgment and communication layer — severity classification, leakage detection, and scientist-friendly explanations of *why* each issue matters for forecasting quality.  
       2. The agent is designed as a **ReAct reasoning layer**, the agent handles the judgment and communication layer — deciding *which* check to run next, *whether* a prior finding changes the severity of the current one, and *when* enough evidence exists to stop. This is the key upgrade from a sequential pipeline: the agent can short-circuit after a confirmed blocker, fetch schema it doesn't have before making assumptions, and reason about leakage based on column names observed earlier in the same loop.  
    5. Input:   
       1. CDP dataset details: Scientist name an input CDP dataset as a prompt  
          1. Database Name: hershey\_gold.   
          2. Dataset name: fact\_orders\_enriched or fact\_orders\_aggregated\_product\_id\_ship\_to\_region  
          3. Snapshot\_id:   
          4. Frequency: weekly  
       2. Forecasting context:  
          1. Hierarchy: product\_id, ship\_to\_region, dc, sales\_org  
          2. Time\_horizon: 52 weeks ahead  
          3. Model: Auto Gluon  
          4. Timestamp column: request\_date  
          5. Target column: quantity  
          6. Primary\_key column: product\_id, ship\_to\_region, dc, sales\_org  
    6. Prompt:  
       1. Role: You are a data readiness agent for forecasting. You validate datasets before model training using a strict Thought → Action → Observation loop. You do not produce a report until the loop is complete.  
       2. *Loop format:* At every step you must output your reasoning before calling a tool:  
          1. **Thought:** Reason about what you know so far, what the most important unknown is, and whether skipping this check risks a wrong final verdict.  
          2. **Action:** Call exactly one tool. Never call multiple tools in a single step.  
          3. **Observation:** Receive the tool result, update your internal findings, and loop again.  
       3. Mandatory tool sequence:  
          1. `fetch_schema` — always first; never assume column names or types  
          2. `run_structural_check` — if required columns are missing, stop immediately (blocker; do not call further tools)  
          3. `check_grain` — duplicate entity-time rows, join explosion  
          4. `profile_time_series` — history length, gaps, zero inflation vs forecast horizon  
          5. `check_target_quality` — nulls, negatives, outliers, spikes, variance  
          6. `detect_leakage` — flag future-information columns (`next_delivery_date` is always suspicious)  
          7. `fetch_feature_profile` — only if non-key, non-target feature columns exist  
       4. *Stopping rules:*  
          1. After step 2: if `run_structural_check` returns `blocker=true` → emit final report immediately with `status=not_ready`. Do not call further tools.  
          2. After any step: if a critical blocker is confirmed and no further check can change the final verdict, stop early.  
          3. Normal exit: all applicable tools have been called and the model returns `end_turn`  
       5. *You must:*  
          1. gather dataset metadata via `fetch_schema` before making any assumptions  
          2. run forecasting-specific validations using the tool sequence above  
          3. reason explicitly in each Thought about whether the prior observation changes severity of the next check  
          4. distinguish clearly between blockers and warnings  
          5. explain every issue in scientist-friendly language  
          6. return a structured readiness report only after the loop ends  
       6. *You must not:*  
          1. train a model  
          2. mutate production data  
          3. invent schema details  
          4. declare a dataset ready if critical checks fail  
          5. ignore uncertainty when required inputs are missing  
          6. call more than one tool per step  
       7. *Severity classification:*  
          1. Blockers (prevent safe training): missing required columns, duplicate entity-time rows, high leakage risk columns present in feature set, infeasible train/validation split.  
          2. Warnings (important but not hard blockers): short series for some entities, missing time buckets, zero inflation, small count of negative target values, outliers/spikes, high-cardinality features needing encoding.  
       8. **Validations** *(unchanged — all 7 validation categories remain as specified)*  
       9. ***Output policy**:*  
          1. *The agent produces its report only after the ReAct loop exits (either via a stopping rule or after all applicable tools have been called). The report is assembled from the accumulated observations across all loop iterations — not from a single model pass. The structured report format is unchanged:*  
          2. *Executive Summary → Dataset Overview → Blockers → Warnings → Detailed Validation Results → Recommended Actions → Final Decision*  
       10.   
           1. Run forecasting-specific readiness checks  
              1. Structural validations:  
                 1. Required columns exist:  
                    1. target column  
                    2. timestamp column  
                    3. entity key columns  
                 2. Timestamp is parseable as a date/time  
                 3. Target is numeric  
                 4. No duplicate column names  
                 5. Dataset can be read successfully  
              2. Entity-grain validations: Checks whether the dataset actually matches the intended modeling grain.  
                 1. Validate uniqueness of primary key \+ timestamp  
                 2. Flag duplicate entity-time rows  
                 3. Flag grain mismatch across rows  
                 4. Flag one-to-many join explosion evidence  
              3. Critical field quality  
                 1. Null rates for:  
                    1. Target  
                    2. Timestamp  
                    3. entity keys  
                 2. Identify rows with missing required values  
              4. Time-series validations: Checks whether time series are healthy enough for forecasting.  
                 1. Provide Min and max timestamp  
                 2. Provide History length by entity  
                 3. Provide Missing time buckets for the declared frequency  
                 4. Flag Irregular cadence  
                 5. flag Short series  
                 6. Flag Sparse or intermittent demand patterns  
                 7. Flag Excess zero inflation  
              5. Target validations: Checks the target variable.  
                 1. Flag Negative values if invalid for shipment forecasting  
                 2. Flag Extreme outliers  
                 3. Flag Constant or near-constant series  
                 4. Flag Very low variance  
                 5. Flag Heavy spikes that may require investigation  
              6. Feature validations: If feature columns are provided, check:  
                 1. missingness  
                 2. constant columns  
                 3. suspicious high-cardinality columns  
                 4. whether features appear usable for forecasting  
              7. Leakage detection: Flag likely leakage, such as:  
                 1. columns that appear to contain future information  
                 2. post-outcome fields like future delivery dates used as model features  
                 3. obviously target-derived future fields  
                 4. Treat columns like next\_delivery\_date as suspicious for forecasting unless explicitly justified.  
              8. Modeling readiness validation: Assess whether the dataset appears trainable for forecasting:  
                 1. enough observations overall  
                 2. enough observations per entity  
                 3. train/validation split appears feasible  
                 4. dataset is better suited for current grain or should be aggregated  
           2. Output policy: Return a structured report with exactly these sections:  
              1. Executive Summary:  
                 1. readiness status: ready / ready\_with\_warnings / not\_ready  
                 2. overall summary in 2–4 sentences  
              2. Dataset Overview:  
                 1. row count  
                 2. date range  
                 3. target column  
                 4. timestamp column  
                 5. entity keys  
                 6. detected frequency if possible  
              3. Blockers:  
                 1. bullet list of critical issues preventing safe model training  
                 2. if none, say “No critical blockers found.”  
              4. Warnings:  
                 1. bullet list of non-blocking but important issues  
                 2. if none, say “No major warnings found.”  
              5. Detailed Validation Results:  
                 1. Include short subsections for:  
                    1. Structural Validation  
                    2. Grain Validation  
                    3. Time-Series Health  
                    4. Target Quality  
                    5. Feature and Leakage Risks  
                 2. Recommended Actions: Give specific next steps, ordered by priority.  
              6. Final Decision:One line:  
                 1. Proceed to model training  
                 2. Proceed after fixes  
                 3. Do not proceed  
           3. Style policy:  
              1. Be concise, diagnostic, and scientist-friendly.  
              2. Do not be generic.  
              3. Explain why each issue matters for forecasting quality.  
              4. If the dataset looks synthetic or partial, mention that the assessment is based only on the provided sample.  
       11. Guardrails:  
           1. never silently assume correctness if required information is missing

17. ### AI Eval for Data Readiness Agent for Forecasting:

    1. Role: You are an expert evaluator for a data readiness agent for forecasting. You need to assess if the validation report is correct, complete and appropriately prioritized.  
    2. Inputs you will receive:   
       1. The original user input that was sent to the data readiness agent, which may include inline dataset content and modeling instructions.  
       2. A computed dataset fact sheet derived from the dataset. Treat this fact sheet as the primary source of truth for objective checks.  
       3. The agent-generated validation report.  
       4. Optional reference examples showing how similar reports should be scored.  
    3. What to evaluate:   
       1. **Executive Summary Accuracy**  
          1. Is the readiness status (`ready`, `ready_with_warnings`, `not_ready`) supported by the evidence?  
          2. Is the summary factually correct and consistent with the detailed findings?  
       2. **Dataset Overview Correctness**  
          1. Are row count, date range, target column, timestamp column, entity keys, and detected frequency correctly stated if inferable?  
          2. Does the report avoid inventing metadata that is not provided?  
       3. **Structural Validation Correctness**  
          1. Did the report correctly assess required columns, timestamp parseability, numeric target, duplicate column names, and dataset readability?  
       4. **Grain Validation Correctness**  
          1. Did the report correctly identify duplicate entity-time rows, grain mismatch, or one-to-many join explosion evidence when present?  
          2. Did it avoid falsely claiming grain issues when none are supported?  
       5. **Time-Series Health Correctness**  
          1. Did the report correctly assess date range, history length by entity, missing time buckets, irregular cadence, short series, sparsity, and zero inflation?  
       6. **Target Quality Correctness**  
          1. Did the report correctly identify nulls, invalid negative values, extreme outliers, constant series, low variance, and suspicious spikes?  
       7. **Feature and Leakage Risk Correctness**  
          1. If feature columns are present, did the report correctly assess missingness, constant columns, high-cardinality risks, and usability?  
          2. Did it correctly flag likely leakage or suspicious future-derived fields?  
       8. **Severity Classification Quality**  
          1. Were issues correctly classified into **Blockers** vs **Warnings**?  
          2. Critical issues that prevent safe training must appear under Blockers.  
          3. Non-critical but important issues should appear under Warnings.  
       9. **Recommended Actions Quality**  
          1. Are actions specific, prioritized, and directly tied to the identified problems?  
          2. Do they explain what should be fixed before training?  
       10. **Final Decision Correctness**  
           1. Is the final decision correct?  
              1. `Proceed to model training`  
              2. `Proceed after fixes`  
              3. `Do not proceed`  
    4. Scoring Rubric: For each dimension, assign:  
       1. **2 \= Correct**  
       2. **1 \= Partially correct / incomplete / minor issue**  
       3. **0 \= Incorrect / missing / misleading**  
       4. **Critical evaluation rules:**  
          1. Do not reward plausible language if the conclusions are unsupported by the data.  
          2. Penalize hallucinated schema details or invented findings.  
          3. Penalize failure to state uncertainty when required inputs are missing.  
          4. Penalize any case where the report declares the dataset ready despite critical blockers.  
          5. Be especially strict about blocker vs warning classification and the final decision.   
    5. Output format: Return exactly these sections  
       1. **Evaluation Summary:**   
          1. overall verdict: pass / borderline / fail  
          2. 2–4 sentence summary of whether the readiness report is trustworthy  
       2. **Dimension Scores:**  
          1. Executive Summary Accuracy: score/2 — short justification  
          2. Dataset Overview Correctness: score/2 — short justification  
          3. Structural Validation Correctness: score/2 — short justification  
          4. Grain Validation Correctness: score/2 — short justification  
          5. Time-Series Health Correctness: score/2 — short justification  
          6. Target Quality Correctness: score/2 — short justification  
          7. Feature and Leakage Risk Correctness: score/2 — short justification  
          8. Severity Classification Quality: score/2 — short justification  
          9. Recommended Actions Quality: score/2 — short justification  
          10. Final Decision Correctness: score/2 — short justification  
       3. **Critical Errors:**  
          1. Bullet list of serious mistakes, if any  
          2. If none, say: `No critical errors found.`  
       4. **Missed Issues:**  
          1. Bullet list of important issues that should have been reported but were omitted  
          2. If none, say: `No important missed issues found.`  
       5. **Overcalled Issues:**  
          1. Bullet list of issues that were incorrectly flagged or overstated  
          2. If none, say: `No overcalled issues found.`  
    6. **Final Verdict:**  
       1. One line:   
          1. `Pass`  
          2. `Borderline – needs review`  
          3. `Fail`  
    7. Suggested Pass/Fail policy  
       1. Fail if any of these occur:  
          1. final decision is wrong  
          2. readiness status is wrong  
          3. critical blocker missed  
          4. critical issue wrongly downgraded to warning  
          5. invented schema/facts  
          6. leakage missed when obvious  
       2. Borderline if:  
          1. final decision is acceptable but report misses secondary issues  
          2. explanations are too generic  
          3. recommendations are weak  
       3. Pass if:  
          1. key findings are correct  
          2. severity is correct  
          3. final decision is correct  
          4. no hallucinations  
          5. explanations are scientist-friendly and actionable   
    8. Example:  
       1. Example agent-generated readiness report  
          1. Executive Summary: readiness status: ready\_with\_warnings  
              This dataset appears mostly usable for weekly shipment forecasting, but there are some data quality issues that should be reviewed before training. The overall structure is valid and the data has enough history to support model development.  
          2. Dataset Overview:  
              row count: 12  
              date range: 2024-01-01 to 2024-02-05  
              target column: shipment\_qty  
              timestamp column: week\_start  
              entity keys: item\_id, customer\_id  
              detected frequency: weekly  
          3. Blockers: No critical blockers found.  
          4. Warnings:  
             1. One duplicate entity-time row exists for item A and customer C1 on 2024-01-08.  
             2. Some rows have missing required values in the timestamp and target fields.  
             3. There are some gaps in weekly history for certain entities.  
             4. One negative shipment quantity was found.  
             5. One unusually high shipment spike was found and should be reviewed.  
             6. Column next\_delivery\_date may contain future information and should be reviewed for leakage.  
          5. Detailed Validation Results:  
             1. Structural Validation  
                 The dataset can be read successfully, required columns are present, and the target is numeric. There are minor missing values in the timestamp and target columns.  
             2. Grain Validation  
                 The dataset is mostly aligned to the intended grain, with one duplicate entity-week row that should be deduplicated.  
             3. Time-Series Health  
                 The dataset spans from 2024-01-01 to 2024-02-05 and appears to follow a weekly cadence overall. Some missing weeks exist for some entities, but the cadence is still broadly usable. Sparse demand is present for entity B-C2.  
             4. Target Quality  
                 The target is numeric. One negative value and one large spike were detected. These should be reviewed before modeling.  
             5. Feature and Leakage Risks  
                 promo\_flag appears usable. next\_delivery\_date may represent future information and should likely be excluded unless justified.  
             6. Recommended Actions:  
                1. Remove duplicate entity-week records.  
                2. Impute or remove rows with missing target or timestamp.  
                3. Review negative values and outliers.  
                4. Exclude next\_delivery\_date unless the feature is justified.  
                5. Proceed with training after these fixes.  
             7. Final Decision: Proceed after fixes  
       2. Reference evaluation  
       3. Evaluation Summary:  
          1.  verdict: fail  
              The report is reasonably structured and identifies several real issues, but it materially understates dataset severity. It incorrectly classifies critical readiness issues as warnings and reaches an overly permissive final status. Based on the fact sheet, this dataset is not ready for safe forecasting model training.  
          2. Dimension Scores:  
             1. Executive Summary Accuracy: 0/2 — The report says the dataset is mostly usable and has enough history, which is not supported. The fact sheet shows insufficient observations per entity and infeasible train/validation split.  
             2. Dataset Overview Correctness: 2/2 — Row count, date range, target, timestamp, entity keys, and frequency are mostly stated correctly.  
             3. Structural Validation Correctness: 1/2 — Missing required values are mentioned, but the report does not clearly reflect that timestamp parseability is not fully clean due to missing timestamp values.  
             4. Grain Validation Correctness: 2/2 — Duplicate entity-time row is correctly identified.  
             5. Time-Series Health Correctness: 0/2 — The report understates irregular cadence, short series, and infeasible history. Saying the cadence is broadly usable is misleading.  
             6. Target Quality Correctness: 2/2 — Negative value and outlier are correctly identified.  
             7. Feature and Leakage Risk Correctness: 2/2 — next\_delivery\_date is correctly flagged as suspicious leakage risk.  
             8. Blocker vs Warning Classification: 0/2 — Duplicate entity-time rows, missing required fields, insufficient observations per entity, and infeasible train/validation split should be blockers for safe training in this sample.  
             9. Recommended Actions Quality: 1/2 — Actions are directionally correct, but they miss the need to aggregate the data or collect more history before training.  
             10. Final Decision Correctness: 0/2 — “Proceed after fixes” is too lenient. The correct decision is “Do not proceed” based on the current sample.  
          3. Critical Errors:  
             1. Incorrectly states that the dataset has enough history to support model development.  
             2. Fails to classify insufficient observations per entity as a blocker.  
             3. Fails to classify infeasible train/validation split as a blocker.  
             4. Uses readiness status `ready_with_warnings` when `not_ready` is more appropriate.  
          4. Missed Issues:  
             1. Short series by entity  
             2. Feasibility problem for train/validation split  
             3. Recommendation to aggregate grain or collect more history  
             4. Explicit mention that assessment is based only on a partial sample  
          5. Overcalled Issues: No overcalled issues found.  
          6. Final Verdict: Fail  
       4. What the correct data readiness answer should have been  
          1. For completeness, the correct report should be roughly:  
             1. **readiness status:** `not_ready`  
             2. **Blockers:**  
                1. duplicate entity-time rows  
                2. missing required timestamp/target values  
                3. insufficient observations per entity  
                4. infeasible train/validation split  
             3. **Warnings:**  
                1. irregular cadence / missing buckets  
                2. sparse demand / zero inflation  
                3. negative value  
                4. Outlier  
                5. leakage risk in `next_delivery_date`  
                6. partial sample caveat  
             4. **Final Decision:** `Do not proceed`

## Trade-offs

### Storage vs Accuracy

* Events duplicate info → higher storage  
* But enable audit \+ ML

### Complexity vs Usability

* Harder to design  
* Much more powerful downstream

### Immutability vs Simplicity

* No updates → more rows  
* But guarantees consistency

## Conflicts

1. ### Launch Event Stream early in Data Platform

**Situation:** During early stages of Data Platform’s strategy development, the CEO wanted us to build an event\_stream architecture of orders and shipment datasets in the next 3 weeks.  
**The conflict:** The conflict was that Data Platform wasn’t mature and building an end-to-end event stream required foundational cloud infrastructure and transformation pipelines. Along with the right foundational architecture, it required minimum 3 months to launch the event stream capability.   
**Action:**

1. So I met in a 1:1 with the CEO to understand the urgency of the request. I learnt that it was important to create features for forecasting models. It was also important to show it as a key innovation in a planned customer demo 3-4 weeks ahead. I also understood what is the success criteria and what was his vision for the demo.  
2. I reframed the debate from yes/no to how we achieve the customer outcome \- better forecasting features and a credible demo.  
3. I partnered with Engineering VP and outlined the trade-offs:  
   1. Develop the full event-stream along with foundational Data Platform capabilities \- which was 3 months of effort  
   2. Or build the MVP of foundational capabilities along with minimal event stream which could be implemented in 3 weeks with required engineering support  
4. I chose the 2nd option, clarified v1 requirements   
5. We also set decision rights: Eng owned feasibility, I owned scope trade-offs, and CEO owned demo narrative \- so we stayed aligned under pressure.  
6. Eventually, I got the right engineering resources to complete the implementation.

**Results:**

1. Reduced event\_stream launched timelines from 3months to 3 weeks  
2. Launched foundational Data Platform capabilities which were extensible without material tech debt  
3. Event stream unlocked new features for forecasting models like time between orders/shipments, delayed shipments, orders per week  
4. CEO did the client demo within timelines, the customer is now a paying customer for Keystone  
5. Earn Trust

**Learning:**

2. ### Canonical SAP Schema Registry vs. client-native schema

**Situation:** When I was shaping Data Platform’s strategy, the CEO strongly wanted us to maintain a canonical SAP schema registry as a core platform capability. The idea was strategically sound: if we standardized all client data into one internal canonical schema, we could create and reuse across clients like Hershey, Corning, and Michelin.  
**Conflict:** 

- I was not aligned with this platform capability because based on my research, I knew that customers did not maintain standard SAP schemas  
- Forcing a Keystone schema would take weeks of mapping effort and create translation friction in client conversations

**Stakes:** It was a critical decision because on one side the CEO had a strong belief on this idea and on other side it would directly impact the client onboarding time, engineering development time, and consumption of the data by downstream models.  
**Actions:**

1. I first aligned the use-cases for canonical SAP schema with my CEO \- it was mainly internal education of scientists, ease of future client onboarding and downstream science consumption.  
2. I quantified ingestion/transformation burden across existing clients and showed canonical enforcement would add 4 weeks per onboarding before reaching value.  
3. I agreed with my CEO’s use-cases and I created solutions for those \-   
   1. SAP schema education was brought through documentation which was also mapped to existing client’s data schema  
   2. For ease of future client onboarding we documented specific data requirements from clients based on our forecasting models  
   3. For downstream science consumption, I standardized the model input contract \- primary\_key, timestamp, time variant features, time invariant features. It was aligned as a contract with the science team.  
4. I aligned the CEO, engineering and science with this approach and implemented these as platform capabilities.

**Results:**

- Reduced client onboarding time by 2 weeks as our data ask became very specific  
- Standardizing data contract for forecasting models saved 2 weeks/model for data wrangling

3. ### Managing SME overload and scientist confusion during Hershey’s data understanding

**Situation:** Early in the Data Platform work at Hershey, one scientist was the SME on the client’s data ecosystem—SAP tables, spreadsheets, and warehouse feeds.   
**Conflict:**

- I needed a structured, sequential deep-dive with the SME to convert client’s tribal data knowledge into reusable platform assets,   
- At the same time, 4 different scientists from modeling team needed rapid ad hoc answers to unblock experiments — and both streams were competing for the same SME’s time

**Stakes:**

- If we didn’t fix this problem it would burnout the SME,   
- slow both platform and modeling work   
- And fail to convert tribal knowledge into reusable platform work

**Actions:**

- I reset trust with the SME and aligned on the goal: reduce repeated questions by turning her knowledge into artifacts.   
- Second, I established a simple operating model: a single intake channel for questions, a shared backlog to dedupe them, and a weekly office-hours cadence for clarifications—no more random pings.   
- Third, I converted answers into reusable assets: a Hershey data understanding doc, mappings of key entities, and a gold-layer join blueprint that teams had to consult first before escalating.

**Results:**

- Reduced SME time spent on this from 4 hrs/day to 4 hrs/week  
- Shortened data discovery for next client from 4 weeks to 2 weeks  
- Forecasting model development due to accurate data understanding  
- Data Platform strategy development and deployment

## Challenges

### 

### Immutability vs Simplicity

**The problem:** Hershey's core transactional data lived in SAP. Extracting order headers, line items, and delivery data in a clean, consistent, and schedulable format required navigating SAP's data extraction architecture — a technically complex process that involved SAP BASIS administrators, custom extraction logic, and data pipeline scheduling that sat outside Deep Enterprise's direct control.

**The conflict:** The data pipeline was a shared dependency between Hershey's IT, Hershey's SAP team, and Deep Enterprise's engineering team. Delays in SAP extraction — which happened frequently in early deployment — blocked model training and inference on the Deep Enterprise side. The PM decision was to build explicit data availability monitoring into the platform — alerting when expected data feeds were late or malformed — and to establish clear SLA agreements with Hershey's IT on data delivery schedules.
