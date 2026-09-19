---
logical_name: deep_enterprise
google_drive_file_id: 1UxvPfz4zS5x4HWYBPc4Lgh67C7zQ0x2rBeb8m4NchAU
source_title: Deep Enterprise Product Strategy
sync_timestamp: '2026-09-19T14:11:15Z'
source_type: google_doc
---

# Deep Enterprise Product Strategy

## Customer Problem(s):

1. Global supply chain disruptions cost companies an average 45% of one year’s profits over a decade \- McKinsey Global institute.   
2. Traditional supply chain organizations are facing a planning and intelligence crisis driven by increasing complexity, volatile demand, and outdated forecasting methodologies. Key problems \-   
   1. Inventory is rising, not moving, costing money: US manufacturers are holding $800 B in excess inventory annually. 90% is tied up in raw materials & finished goods, which is a symptom of broken planning and not execution. SKU proliferation, re-shoring and shorter production runs have driven inventory up.  
   2. Stockouts bleed revenue and lose customers: Retailers and CPG manufacturers lose $1.75 trillion in revenue from stockouts (Netstock). It costs customer relationship, market share and retailer trust.  
   3. Operational firefighting \- Incorrect demand plans lead to high cost of fixing the plans in real-time (retroactively). Wrong forecasts trigger emergency production runs, air freight expediting, and last-minute procurement at spot prices — all at significant premium.  
   4. Poor financial planning \- At the enterprise level, supply chain planning feeds directly into financial forecasting. CFOs and CEOs operating with broken demand signals cannot commit confidently to revenue targets, production investment decisions, or capacity expansion plans.   
   5. Forecasting methodologies have not evolved in decades: According to a PwC survey, CPG companies face 25%-35% error annually in their demand forecast. Traditional forecasting systems are not even designed to support real-world decision making in complex, uncertain and dynamic supply chains. This forecast error does not stay in the demand planning spreadsheet. It propagates and amplifies \- across all downstream decisions \- wrong inventory targets, wrong production schedules, wrong labor plans, wrong procurement commitments, wrong customer commitments.  
   6. In the world where AI is advancing at a rapid scale, traditional organizations are unable to keep up with that pace. They lack internal AI capability and infrastructure \- business teams want outputs not models, but science teams have limited ability to deploy and iterate  
   7. AI capability gap in traditional organizations is wide \-   
      1. Just 23% of supply chain leaders report having a formal supply chain AI strategy in place.   
      2. Most CSCOs are focused on "project-by-project" short-term wins rather than a defined investment strategy — an unstructured approach that often results in complex, layered architectures that hinder scalability.  
      3. Some 90% of supply chain leaders in a McKinsey survey say their companies lack sufficient talent and skills to meet their digitization goals.  
      4. Business teams want decisions, not models. Data science teams can build models but cannot deploy them into production. IT owns the data but not the planning problem.   
      5. No single owner bridges AI capability and operational execution — resulting in proof-of-concept purgatory.  
3. **Why forecasting as the starting point for deep enterprise:**   
   1. Forecasting sits at the apex of supply chain decision-making.   
   2. It is the root cause of supply chain costs \- Every downstream function \- inventory, labor, production, procurement \- is derivative of demand forecast.  
   3. It is where AI delivers the most measurable, fast ROI. The delta is large, measurable, and directly translatable to financial outcomes.  
   4. Without improving forecast optimization layers like OR would amplify rather than create value.  
   5. It’s where Amazon started.  
   6. Wedge into broader platform \- Forecasting win creates organizational trust. Once planners see better numbers, they ask for better inventory recommendations. Then better production plans. Then better scenario tools. Forecasting is not just the entry point — it is the beachhead for full AI-managed supply chain planning.  
4. **Common problems observed at customers around forecasting which led to deep enterprise platform features:**  
   1. Traditional forecasting models have a hard accuracy ceiling: The forecasting models embedded in most enterprise planning systems today — Holt-Winters, ARIMA, Croston's — were not designed for the complexity of modern supply chains. They were developed for stable, low-SKU, low-volatility environments. Applying them to complex supply chains — with thousands of SKUs, heavy promotional dynamics, and retailer-level demand variability — is not a configuration challenge. **It is a mathematical mismatch.** These models share four structural constraints that no vendor implementation or parameter tuning can overcome:  
      1. **Univariate by design.** They model demand against its own history — making them structurally blind to the external forces that actually move demand: promotions, pricing, competitor activity, and market signals. For promotion-heavy CPG businesses, this is not a minor gap.  
      2. **Stability assumption.** They assign decaying weights to historical observations, implicitly assuming the recent past reliably predicts the near future. When demand patterns shift structurally — a new retail partner, a category disruption, a consumption shift — these models smooth over the change with a lag, producing systematically wrong forecasts during the periods that matter most.  
      3. **No uncertainty quantification.** The output is a single point forecast — one number, no range, no confidence interval. Planners make inventory, production, and procurement commitments against a figure that carries no acknowledgment of its own reliability. Uncertainty is never surfaced — it is deferred until it materializes as a stockout or write-down.  
      4. **The consequence is a hard accuracy ceiling.** No matter how well these models are tuned, parameterized, or implemented, they cannot exceed what their mathematics allow. For companies like Hershey's operating in high-complexity, high-volatility, promotion-driven environments, that ceiling is simply not good enough.  
   2. High forecast inaccuracy at the lowest grain, which is a key decision grain \- At the granular level where decisions are actually made, forecast error is materially higher — and directly translates into wrong inventory positions, missed service levels, and poor production plans.  
   3. Planners “override” models with intuition:   
      1. It is a trust failure  
      2. Even companies that adopt ERP, APS, or dedicated demand planning tools often resort to manual adjustments — symptomatic of planning systems that cannot absorb market nuances, context, or unexpected signals  
      3. Demand planners spend the majority of their time massaging data, not driving insights. [Netstock](https://www.netstock.com/research/inventory-management-report/)  
      4. The override problem is self-reinforcing: models produce numbers planners don't trust → planners override → overrides introduce human bias → model accuracy degrades further → trust erodes more.  
   4. Lagging & Batch oriented systems \- Forecasts updates weekly or monthly. But demand signals change daily and even real time. As a result, decisions are based on stale data. By the time the plan reflects reality, the window to act has often closed.  
   5. Inconsistent forecasts across hierarchies \- Forecasts are required at different hierarchies for different business decisions. But these forecasts do not reconcile with each other which leads to weeks-months of reconciliation effort.

## Keystone Problem(s): A consulting business hitting its structural ceiling 

1. Long deployment cycle with low reusability:   
   1. Every client engagement required months of setup — data pipelines built from scratch, models developed and evaluated independently, deployment logic written anew.  
   2. Despite solving the same core problems repeatedly across clients, there were no shared platform components, no reusable modules, no common infrastructure.  
   3. Each project reinvented the wheel  
2. A hard product to sell:   
   1. Clients increasingly wanted tangible, demoable capabilities with visible product interfaces before committing a budget.  
   2. A consulting pitch requires trust built over time; a product can demonstrate value in a single session. Keystone was losing deals not because of capability gaps, but because of packaging gaps.  
3. Revenue tied to headcount, not scale \-   
   1. Consulting economics are linear: more revenue requires more people, more projects, more delivery capacity. The business could not scale without scaling its cost base at the same rate.   
   2. A product-led model was the only path to non-linear growth.  
4. Mismatch between client expectations and delivery:  
   1. Clients were used to and expected product-like experiences — minimal internal resource commitment, ready to use product, fast onboarding, deployment within their own environments, and intuitive interfaces.   
   2. What they received was a long engagement, a system operated externally by Keystone, significant time investment from their own teams, and a dependency on Keystone's continued involvement to sustain outcomes.   
   3. This expectation gap created adoption friction, delayed time-to-value, and made renewal conversations harder.

## Product Strategy:

1. **Product Vision:**   
   1. Deep Enterprise™ is an AI-managed services platform designed to help **traditional supply-chain-driven enterprises transition into AI-first organizations**  
   2. Starting with forecasting as the entry point and expanding into end-to-end decision intelligence.  
2. **Product features:**  
   1. **Data layer:**  
      1. SAP data schema standardization — order headers, line items, delivery data normalized into a common schema  
      2. Ingestion pipelines for ERP, POS (Circana), retailer EDI, and external feeds  
      3. Feature engineering logic — promotional flags, seasonality patterns, causal factor encoding  
      4. Bronze / Silver / Gold transformation architecture with schema registry and validation  
   2. **Modeling Layer**  
      1. Forecasting pipeline — training, inference, evaluation as reusable modules  
      2. Multi-model strategy: Statistical (ETS, ARIMA), ML (XGBoost, LightGBM), Deep Learning (DeepAR), Transformer (TFT), and advanced models (DeepFM, PCC, BVAR) — model selection driven by SKU complexity, data availability, and volatility profile  
      3. Model registry with versioning and retraining triggers  
   3. **Evaluation & Monitoring Layer**  
      1. Standardized evaluation framework — WAPE, MAPE, bias metrics at multiple hierarchy levels  
      2. Drift detection and model performance monitoring  
      3. Data quality triggers and validation rules as reusable Great Expectations components  
   4. **User-Facing Layer:**  
      1. Forecast UI — planner-facing dashboard for review, override tracking, and reconciliation  
      2. Consumption APIs for downstream integration into client planning workflows  
      3. Explainability layer — model confidence, feature contribution visibility for planner trust  
3. **Platform architecture:** Micro-service architecture (intentional design choice)  
   1. Data Platform Services: ingestion service, transformation service, schema registry, validation service, DP API Service, Coreai-IO service, core infrastructure \- pipelines (Glue, Athena, dbt)  
   2. Model Execution Service \- training pipelines, inference pipelines, model registry, versioning  
   3. Forecast Data Service \- forecast store, Dashboard APIs, Reconciliation engine   
   4. Monitoring & Observability service \- data quality triggers, model performance triggers, drift detection  
   5. Infrastructure \- Glue, Athena, dbt, multi-cloud: AWS, Azure  
   6. **Why modular mattered strategically:**  
      1. A client that only needed the forecasting pipeline could deploy without the full stack  
      2. New model types could be added to the Model Execution Service without touching data pipelines  
      3. The monitoring service could be upgraded independently as model complexity grew  
      4. Each service boundary became a natural expansion point for future product capabilities  
4. **Deployment strategy: Client environment first**  
   1. Deep Enterprise deploys inside the client's cloud environment, not as an externally hosted SaaS  
   2. This addressed three enterprise requirements that incumbent vendors consistently failed on:  
      1. **Data sovereignty** — enterprise data never left the client's environment, resolving security and compliance objections that blocked SaaS deployments  
      2. **Integration fidelity** — models ran against live client data pipelines, not replicated or sampled data  
      3. **IT trust** — deployment within existing AWS or Azure tenants meant IT teams could govern, audit, and control the platform through their own tooling  
   3. Multi-cloud support (AWS and Azure) was a go-to-market requirement, not just a technical one — different enterprise clients had committed to different cloud providers, and a single-cloud strategy would have excluded a significant portion of the addressable market.  
5. **Go-To-Market Strategy: Forecasting as the Beachhead**  
   1. **High impact, fast measurable ROI.** Forecast accuracy improvement translates directly and quickly into inventory reduction and service level improvement — both of which are tracked, reported, and owned by named executives. This creates internal champions fast.  
   2. **Low organizational resistance.** Forecasting improvement does not require re-engineering existing workflows on day one — it augments them. Planners see better numbers in familiar interfaces. The change management burden is lower than, say, re-architecting production planning.  
   3. **Organizational trust as currency.** A forecasting win creates the credibility to expand. Once planners trust the model, they ask for inventory recommendations. Once supply chain leaders see the platform working, they fund the next module. The expansion path is pull-driven, not push-driven.  
   4. **Hershey's as the proof-of-concept archetype.** Hershey's represented the hardest version of the forecasting problem — high SKU complexity, extreme seasonal concentration, retailer-level granularity, promotion-heavy demand. Solving it there created a referenceable proof point that was immediately credible to any CPG manufacturer facing the same dynamics.

6. ## **Expansion Roadmap:** From Forecasting to Decision Intelligence Forecasting was the entry point, not the destination. The platform roadmap was sequenced deliberately:

   1. Phase 1 — Forecasting Foundation: Demand forecasting · Causal modeling · Probabilistic outputs · Hierarchy reconciliation  
   2. Phase 2 — Inventory Intelligence: Safety stock optimization · Reorder point recommendations · Excess & obsolescence detection  
   3. Phase 3 — Supply Planning: Production schedule optimization · Procurement signal generation · Capacity planning inputs  
   4. Phase 4 — Decision Intelligence: Scenario planning · What-if simulation · Promotion optimization · Pricing-demand elasticity  
7. Strategic shift:   
   1. From: Bespoke consulting delivery, one-off models, custom pipelines per client   
   2. To: Managed AI platform, Reusable modules, configurable deployments, continuous improvement  
8. Modeling strategy:  
   1. Multi-model platform: Includes Statistical (ETS, ARIMA), ML (XGBoost, LightGBM), Deep Learning (DeepAR), Transformer (TFT), DeepFM / PCC / BVAR (for advanced use-cases)  
9. **Pricing Model:**   
   1.   
5. Impact:  
   1. Clients:   
      1. Forecast accuracy \- measured reduction in WAPE across SKU portfolio vs. baseline  
      2. Reconciliation effort \- weeks reduced through hierarchy consistent forecasting  
      3. AI-first transformation: shifted from vendor dependent to AI-first planning infrastructure  
   2. Keystone:   
      1. Delivery velocity \- months to weeks  
      2. Revenue \-   
      3. Scalability \- platform components reused across deployments, breaking headcount-revenue link

## Key Challenges:

### Scope creep due to long-range forecast

**Situation:** 

- During the implementation of Keystone’s forecasting platform at Hershey’s, the client requested for a 3-year forecast.  
- This requirement was outside the scope of current platform capability, which was focused on forecast at a certain grain and certain time-horizon

**Why important:** This was a difficult situation because developing the real solution was a significant effort and outside the scope of work. But not solving the problem would impact client’s trust.  
**Actions:**

- I dived into the data to understand if it was even feasible to develop this forecast. I learnt that we only had 2 years of history which was not feasible to generate a 3 year forecast.  
- As the most important outcome of a forecast is the business decision, I then inquired about the business decision from this forecast. I learnt that it was only required to maintain technical pipelines.  
- Given these 2 aspects, I collaborated with my data science team to see if there could be a simpler solution and we identified an empirical approach.  
- I then aligned my executive leadership to solve it as a one off problem using an empirical approach to maintain long-term customer relationship. While the actual topline forecast solution was planned for integration at a later stage.  
- Finally, I discussed this approach with Hershey’s, educated them about their data limitation.  
- Then we developed and implemented this solution.

**Impact:**

- Launched a forecast with accuracy better than incumbent  
- Client trust and long-term relationship  
- Leadership trust

**Learning:** In enterprise and AI product development, sometimes we need to come up with simpler solution to meet customer needs

### Change Management and Org Complexity

**Situation:** 

- While implementing Keystone’s AI-based forecasting platform at Hershey’s, one key challenge was to drive alignment across stakeholders from demand, commercial, sales planning, senior leadership, data scientists, and engineering.  
- It was important because a lack of alignment or trust across these stakeholders would directly impact the adoption of our product and long-term relationship with Hershey’s.

**Task:** My role was to setup scalable mechanisms so that we could align our solution, enable implementation and drive adoption.  
**Actions:**

1. Project kick-off:Since it was a key organizational transformation initiative, I requested Hershey’s Chief Supply Chain officer along with senior leaders to kick-off the project between Hershey’s SMEs and Keystone.  
2. Single POC: I also requested for a Single POC to help with project management which was to maintain track of all activities required at Hershey’s, involve the right people, hold them accountable, and provide required details to Keystone.  
3. Weekly reviews: I established bi-weekly performance reviews with Hershey’s key stakeholders and Keystone ML and Engineering team to review the model WAPE metrics, performance across different hierarchies, align on model performance, resolve data requirements, and answer any questions.  
4. C-suite reviews: I also owned bi-weekly reviews between Keystone’s and Hershey’s C-suite leadership. I used this forum to present our findings, share project status, challenges or any support needed from Hershey’s team. The C-suite was the champion of our project and it was important to keep them onboard.

**Impact:**

- Improved Hershey’s forecast WAPE by 21%  
- Reduced project completion time by 1 month vs. previous deployments  
- Adoption of the solution by 15+ stakeholders across demand planners, data science and engineering  
- Hershey’s data science team even added new features into the model

**Learnings:** Enterprise AI deployments are change management initiatives. At this level, PM has to design the operating model \- roles, cadence, decision rights, and metrics \- with the same rigor as system architecture.

### Managed Services Operational Trap 

As Deep Enterprise scaled beyond the first deployments, our managed-services model created a trap: the same DS/engineering team responsible for platform innovation was spending more and more time on operational support—drift investigations, manual retraining coordination, and ‘why did this forecast change?’ escalations. Support load was scaling roughly linearly with clients, and roadmap velocity was slowing.

I reframed it: these weren’t ‘services we must provide’—they were product gaps. If routine reliability work required Keystone, the platform wasn’t self-sufficient.

So I paused \[X\] roadmap work for \[Y\] weeks and invested in three platform capabilities:

1. Automated performance monitoring and drift alerts at SKU level so degradation was detected proactively, not via escalations  
2. Drift-based retraining triggers plus configurable retraining cadence so retraining became a platform behavior, not a manual process  
3. Forecast change alerts with a root-cause summary (including top drivers) so planners got answers before they asked

The strategic shift was: managed services means owning model strategy and platform evolution—not doing repetitive ops that software should automate.

Result: support effort per client dropped from \[A\] to \[B\] hours/week (or tickets down \[X%\]), we reclaimed \~\[Y\] FTE back to the roadmap, and accelerated Phase 2 inventory optimization by \[Z\]. Client trust improved because the platform surfaced issues proactively, and commercially we moved from ‘operational dependency’ to ‘strategic partnership.’

Learning: in managed-services AI, every recurring operational touchpoint is a product gap—and closing those gaps is a business model requirement.”

## Key trade-offs:

1. ### Managed Services vs. pure SaaS

**Situation:** As Keystone transitioned from consulting to product, the strategic question was what type of company we were building. Most investors and executives pushed for SaaS platform as it is centrally hosted, scalable and high margin. I pushed back because it didn’t match how our target customers actually bought.  
**Trade-off and Stakes:**

- Based on my customer research, I understood that our target customers were Fortune 500 supply chain enterprises. Their operations data was sensitive information. Their legal and IT teams had hard requirements around data residency and environment control.  
- If we led with a centralized multi-tenant architecture, it would trigger long security reviews, limited access to production-grade signals, and slower time to value.  
- The real trade-off was margin and scale upfront vs. immediate enterprise adoption and trust.  
- I chose enterprise trust.

**Actions:**

- I led the decision to launch as a managed AI service deployed inside client’s environment.   
- The client retained ownership of data and runtime boundaries, while Keystone owned model performance with clear SLAs.   
- To avoid becoming bespoke services I productized delivery: we standardized deployment through Infrastructure as code, built repeatable runbooks for upgrades and incident response  
- To align the leadership: I had to convince stakeholders that narrowing our GTM to a segment where we had structural advantage was better than chasing a broader SaaS market with a misaligned architecture.

**Impact:**

- Reduced deployment time from 3 months to 3 weeks  
- Launched Deep Enterprise at Hershey’s driving $2Million contract for Deep Enterprise  
- turned Keystone’s managed-service relationship into a durable product moat

2. ### Multi-model vs. single algorithm

3. ### Client cloud deployment vs. hosted

**Situation:** 

- When I was leading Keystone’s transition from consulting to product, I had to make a key trade-off decision: build a fully managed SaaS platform deployed in Keystone’s environment vs. deploy the platform in each client’s cloud environment 

**Why important:** It was a critical decision because it determined the platform's commercial viability, not just scalability. If we got it wrong, procurement would block us from any conversation around product value.   
**Trade-offs:**

- **SaaS Platform:**  
  - SaaS product was faster to build and faster to market, which was critical given Keystone’s pressure to ship  
  - It also meant true platform economics \- one upgrade cycle, non-linear scaling  
- **Multi-cloud managed services deployment:**  
  - During discovery with procurement, security, and supply chain leaders, we confirmed a hard constraint: forecasting demand data could not leave the customer’s cloud boundary due to data-classification policy.   
  - For our flagship target, Hershey, that also meant Azure-first.   
  - No amount of SOC2, encryption, or contractual language would get us through procurement with a SaaS-first approach.  
  - Hershey’s \- our first target customer was also on Azure, which made multi-cloud support a market access requirement

**Decision criteria:**

- Will this unlock enterprise client adoption?  
- Can we enable scalable economics?

**Solution:** 

- We chose customer-cloud deployment as MVP to win the market, but I structured it to avoid bespoke consulting   
- I also partnered with engineering and ML Ops to ship a standardized architecture: using infra-as-code, automated provisioning, repeatable deployment playbook  
- To keep long-term economics, I aligned the executives on a hybrid model \- customer-hosted data plane, and a centralized control plane for orchestration and release management   
- It ensured model deployment, monitoring, and rollback could be managed consistently across customers

**Impact:**

- Successfully deployed in Hershey’s Azure environment, contributing $2Million in Revenue  
- Reduced procurement cycle time by 5 weeks  
- Unlocked new clients like Michelin on Azure worth $3 Million

**Learning:**

- Good product discovery doesn't just validate your strategy — it can expose a direct conflict between customer constraints and your business model.   
- The PM's job is to surface that conflict early, make the trade-off explicit, and design a path that resolves it over time.

4. ### Microservice vs. Monolith architecture:

**Situation:** 

- When Keystone transitioned from consulting to product, we were under immense commercial pressure \- every month without a deployed product was burning runway.   
- In this situation, I had to make a trade-off decision between monolith service architecture to go to market faster vs. invest upfront in a micro-service architecture which was longer initially but will scale to enterprise customers.

**Actions:**

- I decided to build modular services based on three criteria that I validated with our target customers: independent deployability based on scope, reliability, cost of change over time.  
- Independent deployability — Fortune 500 procurement and security teams wanted to deploy only what was contractually approved. A monolith is all-or-nothing; you can't selectively deploy a forecasting module without also deploying the training pipeline.   
- Reliability — a memory leak in the training pipeline should not degrade planner-facing forecast APIs. Service isolation wasn’t an architectural preference; it was a requirement for production credibility.  
- Cost of change over time — our roadmap was forecasting first, then inventory optimization, then supply planning. Modularizing a large monolith with production clients already on it — would be a 10x rewrite vs. paying the modularity tax upfront.  
- Engineering pushed back on the timeline. I reframed the conversation: this wasn't a technical debt debate, it was a business risk decision. The cost of refactoring post-launch with a live enterprise client on the system far exceeded six weeks of upfront investment. That landed.  
- To protect speed, I de-risked delivery by scoping an MVP with clear service boundaries and standardized deployment templates. I aligned engineering and security on the interface contracts early, so we didn’t discover deployment blockers at the end.

**Impact:**

- Deployment time reduced from 3 months to 3 weeks  
- Cleared Hershey’s Security review and deployed within slated timeline  
- When Michelin came in six months later with a different module scope, we onboarded them without a single refactor — the architecture absorbed it exactly as designed.  
- Now building Inventory optimization on top of forecasting

5. ### Probabilistic output vs. point forecasts

6. ### Model sophistication vs. adoption

**Situation:** During the rollout of Keystone’s enterprise forecasting platform at Hershey’s, I had to make a difficult trade-off: keep a highly accurate but complex ensemble model or simplify the modeling approach to improve explainability and stability.  
**Why important:** 

- The stakes were high. Hershey’s was our flagship client and a commercial proof point. Losing their trust wouldn't just cost us the engagement; it would undermine our ability to close Michelin, Corning, and every enterprise conversation that followed.  
- Volatility: Forecast changed week over week in ways planners couldn’t explain, and they were overriding the model at a 50% rate.  
- Explainability gaps: Demand planners were overriding the forecast due to inability to explain changes to the stakeholders  
- So the real trade-off wasn’t accuracy versus simplicity; it was accuracy versus trust, and if we lost trust we’d lose the customer regardless of model performance.

**Actions:**

- I set two guardrails: we would not materially degrade accuracy, and we would make forecast changes explainable and operationally stable.   
- I evaluated two options: replace the ensemble with a simpler model for interpretability, or keep the ensemble and build the missing product layer to make it more usable. I chose the second path because it preserved performance while solving the adoption blockers.  
- I shipped two explainability features:   
  - I introduced feature-level explainability using SHAP values to understand top business contributors;   
  - For the data science team, I built a feature displaying the top two model weights per SKU week over week, giving scientists visibility into ensemble behavior without requiring them to inspect model internals.  
- On volatility, I identified that the root cause was frequent retraining. So, I made the call to move from weekly retraining to quarterly retraining with on-demand triggering as per business needs. It reduced unexpected changes while retaining freshness when the data shifted.  
- I productized both explainability and retraining configuration as platform features — not one-off fixes for Hershey's, but capabilities that would scale to every subsequent client deployment.

**Impact:**

- Reduced planner override rate from 50% to 20%, restoring trust in model output  
- Scalable explainability features for new clients

**Learning:** Adoption failure is rarely about model complexity — it's about the gap between what the model knows and what the user can verify. The PM's job is to close that gap through product design, not by compromising the model. Explainability is a product problem, not just an ML problem.

## Conflicts

1. CEO conflict \- UX philosophy

**Situation:**

- CEO pushed for exposing raw event-stream data  
- belief: transparency → trust

**Your stance:**

* business users need:  
  * simplified narratives

  * not raw data complexity

**Resolution:**

* layered UX:  
  * summary → drill-down

2. Scope conflict

Situation: pressure to include full planning stack vs. MVP of shipment forecast

Decision: focused entry point

## Interview answers

### **Context**

Keystone was solving enterprise forecasting problems through bespoke consulting-heavy engagements.

### **Observation**

Across Hershey and adjacent client learnings, the same bottlenecks kept recurring:

* fragmented planning workflows  
* inconsistent data foundations  
* bespoke feature engineering  
* low model trust  
* repeated deployment / monitoring problems  
* poor reusability across clients

### **Strategic insight**

These were not one-off project issues. They were product problems.

### **Response**

You helped define Deep Enterprise as the answer:

* reusable data foundation  
* reusable science / deployment workflows  
* reusable monitoring  
* configurable client-specific logic  
* product-led platform instead of reinventing every engagement

### **Flagship proof point**

Hershey became the first flagship proof point of that direction. Your resume already reflects that you led the flagship Hershey deployment and helped define the Deep Enterprise platform direction. 
