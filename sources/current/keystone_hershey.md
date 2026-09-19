---
logical_name: keystone_hershey
google_drive_file_id: 1HsRQ3fNMs1clfNQvSwFYkjlkxSZCUSTWDg8Ca2LJuI4
source_title: Keystone Hershey's Experience
sync_timestamp: '2026-09-19T14:11:22Z'
source_type: google_doc
---

# Hershey’s Salty Snacks

## Business Process:

**Commercial Planning \-** 

- Planning levels:  
  - Sku or PPG [Leilei Zhang](mailto:lzhangisu2011@gmail.com)to verify)  
  - brand / sub-brand  
  - Franchise  
  - product line  
  - customer / channel  
  - weekly or monthly view  
- Incorporated key levers in planning:  
  - Promotions  
  - pricing changes  
  - innovation / new launches /product retirement  
  - market events  
  - distribution assumptions  
  - business growth expectations  
  - Done on manual spreadsheets, without any tech or science intervention

**Sales Planning**

- Planning levels:  
  - SKU or product-family by customer  
  - customer/channel/region combinations  
  - periodic view used for account / sales execution planning  
- Key drivers:  
  - account-level commitments  
  - retailer-specific behavior  
  - sales expectations  
  - adjustments driven by customer relationships or planned events  
  - promotion/pricing/market events/display ads

**Demand Planning:**

- Planning levels and corresponding decisions:  
  - Item/DC/ship-to customer/sales-org: Logistics planning (which DC should fulfill which customer demand)  
  - Item/ship-to customer/sales-org: Customer/account planning (what will Walmart vs. Target vs. Costco need)  
  - Item/DC/sales-org: Inventory positioning (how much stock to hold at each DC)  
  - Item: production planning, procurement  
- Primary input:   
  - Historical shipments

**Reconciliation:**

- Different teams generated different forecasts at different levels  
- All teams collaborated to adjust their forecast based on business knowledge or account expectations,  
- All of that had to be rolled up / split down consistently

## Business Problem(s):

**Fragmented planning workflows, which required months to reconcile:** Each planning process had its own forecasting logic, owners, and assumptions, so Hershey’s ended up with: 

- handoffs across mismatched grains  
- Hard to explain differences in different forecasts  
- inconsistent adjustments  
- manual spreadsheets for planning with difficult to maintain history  
- Months of effort in forecast reconciliation instead of making better decisions

**Low shipment forecast accuracy \-** Blue Yonder was used for shipment forecasting which offered a low forecast accuracy (WAPE \= xx%) due to following reasons \-

| Levels | BY base WAPE | Keystone HF WAPE | Improvement (BY-HF)/BY |
| :---- | :---- | :---- | :---- |
| Item-Customer-Location-salesOrg | 77% | 61% | 21% |
| Item-Customer-SalesOrg | 68% | 53% | 22% |
| Item-Location-SalesOrg | 67% | 52% | 23% |
| Item-SalesOrg | 57% | 42% | 26% |

- Blue Yonder used triple exponential smoothing which is an unsophisticated modelling technique:	  
  - It is a univariate model, which ignores business drivers like pricing, promotion   
  - Struggles for lumpy/intermittent patters \- with many zeroes and irregular ordering patterns  
  - Local model, no cross-learning from other time-series. Cannot leverage: similar items, similar customers, same product family behavior  
  - Assumes stable trend and seasonality, which isn’t the case with Hershey’s shipments  
  - Hershey’s has sparse demand at lowest hierarchy  
  - Uses exponential smoothing \- does not capture demand spikes, supply disruptions, one-time events  
- Did not incorporate nuanced features/drivers around promotions, pricing, innovation, events, POS  
- Relied on shipment forecast, which is not a true representation of demand. Shipment can be impacted by \- supply constraints, inventory availability. It’s partly a reflection of operational constraints and execution noise  
- Difficult to diagnose errors \- When forecast quality was poor, teams could tell the number was off, but not easily determine whether the issue came from data, model assumptions, certain SKU segments, promotions, or supply distortions.  
- Worst performance observed on the lowest forecast grain (Item/DC/ship-to/sales-org level), which is actually used for supply planning decisions  
- Unsophisticated reconciliation algorithm 

**Business impact of poor WAPE:**

- Sub-optimal supply planning decisions \- production planning, inventory positioning, safety stock decisions

	Improved shipment forecast results in reduced safety stock, which releases capital locked in the safety stock:  
	$safety\ stock\ =\ z\ \times \ \sqrt{(LT\ \times {{{\sigma }_{a\ }}^{2})}_{\ }+({\overline{D}}^{2}\times {{\sigma }_{LT}}^{2})\ }$  
	Where Z \= Z score, calculated using standard normal distribution table based on cumulative probability. Z \= 2.05 for 98% service level or case fill rate.  
LT \= Average lead time (e.x. 4 weeks)  
 ${{{\sigma }_{a\ }}^{}}_{\ }=$Standard deviation of demand forecast per week  
${\overline{D}}^{}$\= Average demand forecast over the lead time \= 4 weeks (LT) rolling forecast mean  
${{\sigma }_{LT}}^{}$\= Standard deviation of the lead time

- Commercial/go-to-market decisions impacted \- promotions planning, pricing decisions, innovation / new launch expectations, trade investment allocation, customer / retailer discussions, sales target settings  
- Financial / operational decisions impacted \- revenue outlook confidence, inventory carrying cost, service level / fill rate risk, stockout risk, obsolescence / excess inventory risk, expedite costs, wasted planner time in reconciliation cycles  
- Organizational impact   
  - Planners rely more on manual adjustments  
  - Leadership trusted numbers less  
  - Teams spent more time debating numbers than acting on them

**Hershey’s limited ability of science experimentation:**

- BY was a pre-packaged solution which limited Hershey’s ability of science experimentation, also impacting Hershey’s long-term vision to become an AI-first company

## Keystone Solution

1. **Enterprise AI-product deployment:** This was not just “build a model.” It was an enterprise AI product deployment: data integration, model pipeline, evaluation, user workflows, explainability and production adoption.  
2. **Scope:** Identified a broader planning problem, but intentionally chose a high-value, high-feasibility entry point:  
   * Shipment forecast was mission critical  
   * It had measurable baseline  
   * It affected multiple downstream decisions  
   * Used the deployment to create internal science capability and platform leverage  
   * Laid the path for future commercial/sales planning expansion  
3. Deployed an AI-powered forecasting capability with:  
   * Data integration pipelines: integrates fragmented data sources  
   * Sophisticated forecasting model: produces forecast outputs at actionable business grains  
   * Reconciliation algorithm: reconciled forecasts to make them consistent at different levels. Based on the common business metrics all 3 teams care about, we chose topdown reconciliation to best match the forecasts from different levels.   
   * Deployed in Databricks environment: can be run and consumed in production, not just analyzed offline  
4. Technical architecture:  
   1. **Data ingestion layer**  
      1. shipment history  
      2. order / planning history  
      3. pricing inputs  
      4. promotion / trade activity  
      5. product master / hierarchy data  
      6. customer / region mapping  
      7. supply or constraint-related inputs  
      8. manually maintained business inputs from spreadsheets / legacy systems  
   * **Data transformation / feature layer**  
     1. Time alignment  
     2. promotion flags  
     3. pricing and event features  
     4. hierarchy rollups  
     5. quality checks and validation \- great expectations  
   * **Modeling layer**  
     1. Hierarchical forecast model which was an ensemble of deep learning, statistical methods (AutoETS included), and transformer-based model  
        1. Statistical: Triple exponential smoothing, ARIMA AutoETS, AutoARIMA, Theta  
        2. ML: XG Boost/Light GBM, Autogluon  
        3. Deep Learning: DeepAR, Chronos  
        4. Transformer: Temporal Fusion Transformer (TFT), Chronos  
     2. Ensemble layer: Weighted combination of multiple models  
     3. Weighted Least Square (WLS) reconciliation approach which reconciled topline and base forecast, with weights tied to forecast error variance.  
     4. Hierarchical consistency  
     5. Probabilistic forecast instead of point forecast  
     6. Key advantages of hierarchical approach:  
        1. Enables both local and global learning across time-series  
        2. Transformers capture non-linearities in the dataset  
        3. Ensemble reduces both bias and variance  
        4. Captures complex patterns: promotion effects, cross-feature interactions  
        5. Handles sparsity better, especially at the lowest grain  
     7. Key innovations:  
        1. special treatment for intermittent / lumpy SKUs  
        2. Sophisticated reconciliation approach  
        3. bias/error monitoring  
        4. Extensibility \- internal science team could easily add new features and new model variants  
        5. Learnings from time-series of different DFUs  
        6. Probabilistic forecast instead of point forecast  
        7. Adding product chaining to build the map of new product development and old product retirement.  
   * **Evaluation layer**  
     1. Hierarchical forecast vs. BY WAPE for each hierarchy  
     2. Triggers for WAPE deviation beyond thresholds  
     3. Over-bias, under-bias  
     4. week-over-week forecast volatility  
     5. business review loops  
     6. Data quality triggers:  
        1. Schema drift  
        2. Null spikes  
        3. Abnormal row counts  
   * **Production / consumption layer**  
     1. Weekly triggering to re-train the model and run inference, consumed latest weekly data up to the most recent full weeks (to avoid taking partial week data) to keep model up to date  
     2. forecast outputs served into downstream planning workflows  
     3. user-facing dashboards  
     4. explainability views  
     5. retraining / refresh cadence  
     6. operational ownership model  
     7. Metrics reviews on dashboard to help demand planning team to switch smoothly to KSAI forecast (based on 4 weeks of rolling performance better than BY)  
5. Impact to Hershey’s:   
   1. improved forecast quality, especially for key planning workflows  
   2. is explainable and auditable  
   3. supports business adoption and future scaling  
   4. Set Hershey’s on a roadmap of AI-enhancement  
   5. Enabled Data scientists to improve the model easily with new features  
6. Impact for Keystone:  
   1. $2 MM revenue  
   2. Proof point for Keystone’s transition from a consulting work to reusable enterprise AI platform

## Key Project Challenges

1. **Replacing a mindset from using black-box solution to owning a science solution:**

**Situation:** The business teams did **not** have a strong native orientation toward science-led forecasting. They were more comfortable with something like:

- “give us the forecast”  
- “don’t make us manage model complexity”  
- “we don’t want a lot of scientific interpretation burden”  
- “we trust established vendor tools more than custom AI logic”

**Why was it a big challenge:** It led to: more discomfort with internal teams, uncertainty about who would operate / improve the model over time  
**Action:**  
**Results:**

2. **Change Management and Org Complexity:**

**Situation:**

- Hershey’s had a very complex planning org with multiple senior leaders and many downstream planners, which created challenges in co-ordinating and aligning our approach with a variety of stakeholders.  
- Business vs. science vs. engineering priorities  
- “The hardest part wasn’t building a model. It was aligning a multi-stakeholder planning ecosystem around one version of truth, an operating model, and one level of trust in the output”

**Action:**

- Keystone and Hershey’s leadership collaboration  
- Single POC at Hershey’s to co-ordinate across teams  
- Building trust with their team through bi-weekly results review and regular progress updates  
- Involvement of science and technology experts through different phases of solution development  
- In 2026, we expect more companies to follow the lead of AI front-runners, adopting an enterprise-wide strategy centered on a top-down program. Senior leadership picks the spots for focused AI investments, looking for a few key workflows or business processes where payoffs from AI can be big. Leadership then applies the right “enterprise muscle”—talent, technical resources, and change management.

**Results:**  
**Learning:**

3. **Trust/Explainability:**

**Situation:** Pressure to show measurable improvement while operating model was still maturing  
**Action:**  
**Results:**  
**Learning:**

4. **Something around parallelization of workflows**

**Situation:**  
**Action:**  
**Results:**  
**Learning:**

5. **Data / systems**

**Situation:** 

- data scattered across spreadsheets and enterprise systems: Data came from multiple sources such as ERP/SAP-related systems, shipment history, planning inputs, promotional and pricing data, spreadsheets, and retailer/customer inputs.   
- There were ongoing issues around data quality, ownership, legacy workflows, and migration/standardization.  
- inconsistent definitions / grains / hierarchies  
- manual overrides without clean traceability  
- historical planning logic embedded in people/processes rather than systems  
- weak reproducibility and low confidence in data lineage

**Action:**

- Prioritized canonical datasets  
- Aligned data definitions  
- Narrowed scope where upstream data foundations were not reliable enough  
- Made specific data requests based on learning from past projects

**Results:**  
**Learning:**

6. **Difficulty to improve model performance on lumpy/intermittent SKUs**

**Situation:** Difficulty to improve performance on lumpy/intermittent demand SKUs, which is common in CPG.   
**Action:**

1. Classified SKUs into regular, lumpy, intermittent, erratic  
2. Croston-style method  
3. Specialized sparse-demand handling

**Results:**  
**Learning:**

7. **Model development challenges:**

**Situation:** 

8. **Post model deployment issues:**

**Situation:** After deployment, the model showed:

- Under-bias  
- Visible week on week forecast swings  
- A declining business trend that did not fully match stakeholders intuition

**Action:**

- Under-bias, and some declining trend  
  - One main underbias contributing factor is the data update lag. Because we forecast on shipments, not order requests. The shipment records would in general come in after 1-3 weeks of the actual shipment event.  Since   
    - 1\. We were using all the past week history (not validating if the history is complete or not). We could sometimes use partial last few weeks of history to train the model.   
    - 2\. We initially did not use full week data for the training. For example, if the user triggers a model training on Wednesday of this week, we collect all the history up to Tuesday of this week ( which would be a partial week for this week, and less volume).  
  - Fix:   
    - Every time collecting history, make sure the last week history includes all 7 days, if not, remove the last week history.  
    - Even the full 7 days of history is included. Validate to make sure the volume is not too low compared to the previous few weeks. If lower than 70% of previous 4 weeks average, then pop warning, and do not use this week's history.   
- Week on week instability:   
  - Data deep-dive: if the input data fluctuated too much, which led to forecast fluctuation  
  - Instability introduced by retraining too frequently, and the model weights changed too much week over week.   
- Declining trend:  
  - The previous issues with data validation.  
  - We are seeing regular product launch and old product retirement in the shipment history. But the demand forecast model could only predict product retirement for existing products, not on new product launch volume with new product that is not showing in the shipment history.  THIS IS KNOWN, BUT WE DID NOT GENERATE ANY FIX SOLUTION TO IT.

**Result:**  
**Learnings:** In production forecasting accuracy is only one dimension. If the model is directionally biased or too volatile week to week, users experience it as unreliable even before they look at the official metric.

9. **Adoption issue:**

**Situation:** Despite building strong ML capabilities, business users were not adopting the platform effectively  
**Root cause:**

* the model deployed was an ensemble of different models and was difficult for their science teams to run and use  
  * We used the autogluon package, which has a selection of multiple models. The package will train on all selected models (autoARIMA, autoETS, THETA, TFT, chronos, deepAR, etc.). But the model selection process is mostly dependent on the forecast samples, which could vary a lot, and generating different model weights if inputs slightly change.  It is also difficult to debug since the model weight generating process happens inside the autogluon package.  
  * Another complexity of our model deployment was that we separated the demand forecasting process into detailed modules (data cleaning and transformation, model training, model inference, model reconciliation, and metrics generation). The multiple modules showing each step results are making the customers confused, and feels like this is a complicated process. 

**Action:**

1. Simplified workflows   
   1. Make the 4 modules (data cleaning and transformation, model inference, model reconciliation, and metrics generation) trigger automatically and in sequence. Customers only need to worry about the final results.   
2. Improved enablement/training for business users  
   1. Enables the customers to select the combination of algorithms used in autogluon (autoARIMA, autoETS, THETA, TFT, chronos, deepAR, etc.)  
   2. Auto trigger the model training every quarter, or manual trigger by customers.

**Result:**  
**Learning:** Enterprise AI adoption often fails not because the model is weak, but because the operating model around the model is weak.

10. **WAPE improvement was not good enough**

**Situation:** The model WAPE improvement was not good enough (x% to x% improvement).   
**Root Cause:**

- The model did not perform well on lumpy/intermittent demand SKUs (common in CPG)  
- Traditional forecasting methods assumed: Smooth demand patterns

**Actions:**

- Segmentation of SKUs based on ADI and CV  
- Segmented regular vs. intermittent/lumpy SKUs

**Results:**  
**Learnings:**

11. **Business users did not trust model outputs:**

**Situation:**  
**Root Cause:**

- Lack of explainability, transparency  
- Outputs appeared as black-box recommendations

**Actions:**

* Model explainability layers  
* Attribution of drivers (pricing, promotions, etc.)  
* Built: Clear narratives for business users

**Result:**  
**Learning:**

## Key Trade-offs

1. **Scope tradeoff**

**Situation:** We could have included all planning processes or focused on a single one.  
**Action:** Prioritized shipment forecast to go with phase-wise approach, build trust with teams and enable gradual improvement.

2. **POS forecasting trade-off**

**Situation:** POS forecasting: Leadership pushed for POS forecast to shipment forecast, while product realized that it was harder to use POS data to improve shipment forecasting.  
**Action:**

- Aligned Keystone leadership to implement POS forecasting as a POC instead of committing to a production solution.  
- Experimented and extracted some learning out of POS forecasting, which led to our long-term product roadmap

**Results:**  
**Learnings:**

3. **Science sophistication vs. operational adoption**

**Situation:** During product deployment phase, scientists at Hershey’s raised concerns around complex ensemble modelling approach. This ensemble approach was harder for client teams to run, debug, and trust  
**Action:**  
**Results:**  
**Learning:**

4. **Phased rollout vs. big-bang approach**

**Situation:** Hershey’s business teams wanted a phase-wise rollout to DFUs  
**Action:**

- Identified a criteria for rollout which covered 85% SKUs  
- because of that, the value gap between phase-wise and big-bang was smaller than it first appeared  
- running both systems in parallel long-term was discouraged

5. **Reconciliation approach trade-off**

**Situation:** 

- Generated forecasts at different hierarchies which were used for different business decisions.   
- But the forecasts across different hierarchies were inconsistent, which meant supply chain, sales and finance were operating on different numbers  
- Teams could not align on a single plan

**Trade-off:**

- Use simpler approaches (bottom-up/top-down) which were easier to implement, but optimized for a single hierarchy  
- Use a more sophisticated approach which provided better result but harder to operationalize

**Action:**

- Defined the problem clearly \- changed goal from improving forecast accuracy to deliver coherent forecasts across all hierarchies  
- Collaborated with business stakeholders to identify the level at which supply planning decision was taken: Item/Ship-to customer (most important)  
- Data deep-dive: Lower-level data was noisy, while higher-level data was too stable and lost patterns  
- Compared approaches:  
  - Bottom-up: Aggregates forecast upward from lowest levels, which can be inaccurate  
  - Top-down: Aggregates forecast from top to bottom, which loses signal  
  - WLS: Gives weights to all the levels based on forecast quality, and aggregates results  
- Chose WLS as it resulted forecast across levels, and prioritized the middle level:  
  - Combined signal across all levels

**Result:**

- Delivered consistent forecast across all hierarchies, eliminating cross-team misalignment   
- Achieved **significant improvement in WAPE across multiple hierarchy levels** (not just aggregate)  
- Increased **trust and adoption** among supply chain and planning teams  
- Reduced need for **manual overrides and adjustments**

**Learning:**

- Making science choices that the business could use for consistent decisions, is more critical than implementation 

## Key AI-failures

1. Over optimizing for model sophistication

Situation: We had technically stronger model but operationally harder to adopt model  
Learning: deployment success requires operational simplicity, not just technical strength.

2. Underestimating change management

Even a technically valid system can fail if users don’t trust it or know how to use it.

**Lesson:** explainability and adoption are first-class product requirements.

## Conflicts/Disagreements

1. Conflict b/w product and engineering  
2. Conflict b/w product and science  
3. B/w Keystone and Hershey’s stakeholders \-   
   1. POC scope:   
      1. Conflict: Hershey wanted keystone to use shipment history to predict shipments.  Keystone thinks the right approach should be using order requests (unconstrained) to predict order requests. Shipment history is constrained orders that already blended in out of stock, backorder, etc.    
      2. Action: Keystone investigated the order request history. And realized hershey only started recording order requests in October 2023 when they converted to S4 system. On the other side they did keep the raw shipment history from 2020\.  To get a more reliable forecast, Keystone decided to compromise and use shipment history to predict shipments. 

Specific interview questions  
**Tell me about a project you are proud of.**  
One project I’m especially proud of was leading Keystone’s Hershey Salty Snacks forecasting deployment. Hershey had a complex planning environment with multiple teams — commercial, sales, and demand/supply planning — each operating with different assumptions, grains, and forecasting workflows. They also relied on a packaged vendor solution, Blue Yonder, for shipment forecasting, which was useful operationally but limited in explainability, flexibility, and internal science ownership.

I helped define the product strategy for where we should enter that environment. Rather than trying to replace the entire planning stack at once, we chose shipment forecasting as the strategic wedge because it was operationally important, measurable against an existing baseline, and central to many downstream decisions like inventory, supply planning, and promotional readiness.

We deployed an in-house hierarchical forecasting solution in Hershey’s environment that outperformed Blue Yonder. The model combined statistical methods, deep learning, and transformer-based approaches, and used hierarchical reconciliation to maintain coherence across forecast levels. But what made the project especially meaningful to me is that the impact went beyond better accuracy. This became Hershey’s first real step toward an internal science-led forecasting capability. Their team could now add features, test new ideas, and continuously improve the model rather than being locked into a pre-packaged black box.

The project was hard because it sat at the intersection of science, engineering, and organizational change. We had to align on adjusted versus actual history, rollout strategy, model trust, operating ownership, and deployment readiness in a complex client environment. I’m proud of it because we didn’t just ship a model — we changed the client’s trajectory from outsourced forecasting toward an internal, improvable AI capability.

- Describe a situation where you had to translate technical ML concepts to non-technical stakeholders  
- Tell me about a time you had to advocate for AI safety against time-to-market pressure  
- What were the different AI approaches considered?  
- Have you ever faced a situation where a decision you made turned out to be a poor one? Upon realizing this, how did you own your decision, communicate, and take action to improve the situation?  
- Describe a situation where you had to translate technical ML concepts to non-technical stakeholders

### My role

- Led the product side across problem framing, architecture trade-offs, model evaluation strategy, explainability, adoption, and cross-functional alignment between Keystone and Hershey stakeholders.  
- 
