"""Build the one-time, source-verified September 2026 calibration sample.

This is a curated research record, not a recurring discovery or application tool.
It does not access accounts, contact employers, or alter candidate evidence.
"""

from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parents[1]
STAMP = datetime.now(timezone.utc).isoformat(timespec="seconds")
FIELDS = [
    "job_id", "company", "sector", "role_title", "normalized_level", "location",
    "country", "remote_or_hybrid", "posted_date", "source", "canonical_url",
    "comp_min", "comp_max", "currency", "compensation_confidence", "role_cluster",
    "ai_classification", "core_requirements", "hard_prerequisites", "fit_summary",
    "primary_gap", "hard_experience_gap", "experience_fit_score",
    "interview_probability_score", "level_fit_score", "compensation_fit_score",
    "career_capital_score", "location_fit_score", "priority_score", "application_lane",
    "recommended_resume_variant", "recommended_portfolio_artifact",
    "classification_confidence", "discovered_at", "last_verified_at", "status",
]
QUEUE_FIELDS = [
    "Company", "Role", "Sector", "Level", "Location", "Posted date", "Compensation",
    "Role cluster", "AI classification", "Priority score", "Lane", "Primary gap",
    "Hard X gap?", "Fit rationale", "Recommended resume", "Recommended portfolio artifact",
    "Canonical URL", "Classification confidence",
]
JOBS = []


def add(job_id, company, sector, title, level, location, country, mode, url,
        pay, cluster, ai, requirements, prerequisites, rationale, gap, scores,
        lane, resume, artifact, confidence="MEDIUM", posted=""):
    """Record only facts read from a current employer/official ATS posting."""
    low, high, currency = pay
    e, i, l, c, k, g = scores
    if low is None or high is None:
        assert low is high is currency is None and c == 3
        pay_confidence = "LOW"
    else:
        pay_confidence = "HIGH"
    priority = round(20 * (.25 * e + .20 * i + .15 * l + .15 * c + .15 * k + .10 * g), 1)
    parsed = urlparse(url)
    assert parsed.scheme == "https" and parsed.netloc
    assert all(1 <= score <= 5 for score in scores)
    assert gap in {"NONE", "K", "V", "E", "X"}
    assert lane in {"APPLY NOW", "APPLY + BRIDGE", "BUILD TOWARD", "SKIP"}
    assert (gap == "X") == (lane == "BUILD TOWARD") or lane == "SKIP"
    assert sector != "" and requirements and prerequisites and rationale
    JOBS.append(dict(zip(FIELDS, [
        job_id, company, sector, title, level, location, country, mode, posted,
        f"Official employer/ATS page ({parsed.netloc})", url, low, high, currency, pay_confidence,
        cluster, ai, requirements, prerequisites, rationale, gap, gap == "X",
        e, i, l, c, k, g, priority, lane, resume, artifact, confidence,
        STAMP, STAMP, "live_verified",
    ])))


P = "Principal / Staff-equivalent"
G = "Lead / Group-equivalent"
D = "Director conditional"
S = "Senior PM conditional"
M = "PM conditional"
AI = "AI / Agents / Evals"
DATA = "Data / ML Platform"
ENTERPRISE = "Enterprise / Developer Platform"
FIN = "Fintech / Payments / Credit"
OPS = "Marketplace / Supply Chain / Operations"
GROWTH = "Growth / Monetization / Consumer"
SEARCH = "Search / Retrieval / Knowledge"
RISK = "Security / Risk"
RD = "Data / ML Platform"
RA = "Agents / 0→1 Platform"
RE = "Enterprise Platform"
RF = "Fintech / Payments"
RG = "Growth / Consumer"
RGEN = "General Principal PM"
REV = "AI Evals / Quality"
ART_DATA = "Enterprise Data Platform"
ART_AGENT = "Forecasting Agent / Agent Evaluation"
ART_PATENT = "Patent AI Search / Retrieval Evaluation"
ART_FIN = "Amazon Financial Services"
ART_ML = "Amazon ML Platform"
ART_SUPPLY = "Amazon Supply Chain / Optimization"
ART_ENT = "Deep Enterprise"
UNKNOWN = (None, None, None)

# Big Tech / major tech: four verified live listings.
add("10514206", "Amazon", "Big Tech", "Principal Product Manager Technical, AWS Applied AI Solutions - Core Services", P, "Seattle, WA", "US", "On-site / unspecified", "https://amazon.jobs/en/jobs/10514206/principal-product-manager-technical-aws-applied-ai-solutions-core-services", (181100,245000,"USD"), AI, "AI-heavy", "Own AI agent evaluation platform product strategy, adoption, and revenue.", "Senior technical PM experience; AI platform and evaluation judgment.", "Forecasting Agent evaluation and platform strategy map directly; AWS-specific go-to-market proof is thinner.", "E", (5,4,5,4,5,5), "APPLY NOW", REV, ART_AGENT, "HIGH")
add("10487511", "Amazon", "Big Tech", "Principal Product Manager- Tech, Amazon Customer Service", P, "Seattle, WA", "US", "On-site / unspecified", "https://amazon.jobs/en/jobs/10487511/principal-product-manager-tech-amazon-customer-service", (179900,243400,"USD"), AI, "AI-heavy", "Lead agentic customer-service product strategy across customer journeys.", "Principal-level technical PM and customer experience ownership.", "Amazon PM-T history plus enterprise agent and customer experience evidence provide a credible near-term story.", "NONE", (5,4,5,4,4,5), "APPLY NOW", RA, ART_AGENT, "HIGH")
add("10439720", "Amazon", "Big Tech", "Principal Product Manager-Tech, PV Commerce", P, "Seattle, WA", "US", "On-site / unspecified", "https://amazon.jobs/en/jobs/10439720/principal-product-manager-tech-pv-commerce-prime-video-commerce", (179900,243400,"USD"), GROWTH, "Non-AI", "Own Prime Video commerce product opportunities and customer monetization.", "Principal technical PM; consumer commerce and cross-functional delivery.", "Amazon commerce and consumer product work transfers; streaming-specific monetization needs interview framing.", "V", (4,3,5,4,4,5), "APPLY + BRIDGE", RG, ART_FIN)
add("10487601", "Amazon", "Big Tech", "Principal Product Manager-Tech, Featured Merchant Algorithm", P, "Bengaluru", "India", "On-site / unspecified", "https://www.amazon.jobs/en/jobs/10487601/principal-product-manager-tech-featured-merchant-algorithm", UNKNOWN, OPS, "AI-adjacent", "Set product direction for merchant offer selection algorithm and customer experience.", "Principal technical PM; marketplace algorithm and seller/customer tradeoffs.", "Amazon and ML platform history match the algorithmic marketplace scope; India work authorization remains unconfirmed.", "E", (4,3,5,3,4,5), "APPLY + BRIDGE", RD, ART_ML)

# Banking: non-AI and AI-adjacent roles deliberately retained despite non-Seattle locations.
add("R-575564", "Wells Fargo", "Banking", "Senior Lead Product Manager", G, "Charlotte, NC; Columbus, OH; Wilmington, DE", "US", "Hybrid", "https://www.wellsfargojobs.com/en/jobs/r-575564/senior-lead-product-manager/", (139000,239000,"USD"), FIN, "AI-adjacent", "Lead real-time credit decisioning product and cross-functional strategy.", "Senior product leadership and credit decisioning domain fluency.", "Amazon Financial Services and credit products are strong evidence; bank-specific decisioning terms need translation.", "V", (5,4,4,3,4,2), "APPLY + BRIDGE", RF, ART_FIN, "HIGH", "2026-09-17")
add("R-553892", "Wells Fargo", "Banking", "Lead Product Manager - Liquidity Transformation Strategy", G, "Charlotte, NC; Minneapolis, MN", "US", "Hybrid", "https://www.wellsfargojobs.com/en/jobs/r-553892/lead-product-manager-liquidity-transformation-strategy/", UNKNOWN, FIN, "Non-AI", "Modernize liquidity/transaction banking product processes and portfolio.", "Five-plus years product management; treasury expertise is desired rather than required.", "Financial-services product and platform leadership transfer; liquidity vocabulary is the main bridge.", "V", (4,3,4,3,4,2), "APPLY + BRIDGE", RF, ART_FIN, "MEDIUM", "2026-09-14")
add("R-575654", "Wells Fargo", "Banking", "Senior Lead Product Manager - Paper Receivables", G, "Charlotte, NC; Irving, TX; Minneapolis, MN; San Francisco, CA; Tampa, FL", "US", "Hybrid", "https://www.wellsfargojobs.com/en/jobs/r-575654/senior-lead-product-manager-paper-receivables/", (139000,260000,"USD"), FIN, "Non-AI", "Own senior-IC receivables portfolio and product strategy.", "Seven-plus years product management; deep paper-receivables knowledge is desired.", "Banking and platform leadership transfer; paper receivables proof is limited, but it is not a hard requirement.", "K", (3,2,4,4,3,2), "APPLY + BRIDGE", RF, ART_FIN, "MEDIUM", "2026-09-15")

# Insurance: range from adjacent platform scope to a genuine specialist gap.
add("3e40be54-5d36-4cbc-88f2-eed63a09f545", "Assured", "Insurance", "Staff Product Manager", P, "Remote (country not specified)", "Unknown", "Remote", "https://jobs.ashbyhq.com/assured/3e40be54-5d36-4cbc-88f2-eed63a09f545", (210000,250000,"USD"), ENTERPRISE, "AI-adjacent", "Lead insurance claims software/platform and automation products.", "Staff-level product ownership and complex enterprise workflow delivery.", "Enterprise AI and workflow platform experience transfer; US remote eligibility should be confirmed.", "V", (4,3,5,4,4,2), "APPLY + BRIDGE", RE, ART_ENT)
add("ffcfb7c0-7ca2-4fa1-a91d-0f0f236bb2b9", "Nirvana Insurance", "Insurance", "Senior Product Manager", S, "San Francisco, CA; New York, NY; Remote", "US", "Location type listed on-site; remote option ambiguous", "https://jobs.ashbyhq.com/nirvana/ffcfb7c0-7ca2-4fa1-a91d-0f0f236bb2b9", (155000,220000,"USD"), DATA, "AI-adjacent", "Own data/core insurance platform across pricing, risk and policy lifecycle.", "Senior technical product management and platform/data fluency.", "Scope appears broader than ordinary Senior PM; insurance terminology and work-mode details need checking.", "V", (4,3,4,3,4,2), "APPLY + BRIDGE", RD, ART_DATA, "LOW")
add("50191019-226e-4274-915f-e9e2da68cfa3", "Steadily", "Insurance", "Principal Product Manager", P, "Austin, TX", "US", "On-site", "https://jobs.ashbyhq.com/Steadily/50191019-226e-4274-915f-e9e2da68cfa3", UNKNOWN, FIN, "Non-AI", "Own insurance billing, renewals, endorsements and cancellations.", "Principal product ownership; insurance operations fluency.", "Financial-services systems leadership transfers, but Austin relocation and direct insurance process depth are uncertain.", "K", (3,2,5,3,3,2), "APPLY + BRIDGE", RF, ART_FIN, "MEDIUM")
add("23749240", "Travelers", "Insurance", "Director, Product Management - California State Team", D, "Hartford, CT", "US", "On-site / unspecified", "https://careers.travelers.com/job/23749240/director-product-management-california-state-team-hartford-ct/", (120400,198700,"USD"), GROWTH, "Non-AI", "Manage state P&C product profitability, pricing and team leadership.", "Direct P&C state-product/rating experience and people leadership.", "Financial-services PM background helps, but state P&C actuarial/product ownership and formal team management are not evidenced; economics and management shift further weaken fit.", "X", (2,1,3,2,3,2), "SKIP", RGEN, ART_FIN, "HIGH")

# Fintech and Payments, including direct-domain and PM-management hard gaps.
add("fa5d826d-18e1-4ce1-b103-204a5701a701", "Socure", "Fintech", "Principal Product Manager", P, "Seattle, WA", "US", "Hybrid", "https://jobs.ashbyhq.com/socure/fa5d826d-18e1-4ce1-b103-204a5701a701", (237000,285000,"USD"), RISK, "AI-adjacent", "Own identity/fraud platform strategy serving financial institutions.", "Principal product ownership in data-driven risk/identity workflows.", "Credit-risk and ML platform history is compelling; identity-specific proof should be highlighted in interviews.", "E", (4,3,5,5,5,5), "APPLY NOW", RF, ART_FIN, "HIGH")
add("6630580", "Adyen", "Payments", "Group Product Manager, Credit and Data Platform", G, "Chicago, IL; San Francisco, CA", "US", "Office-first", "https://job-boards.greenhouse.io/adyen/jobs/6630580", (235000,317000,"USD"), FIN, "Non-AI", "Lead credit and data product strategy and a team of PMs.", "Three-plus years credit product and direct management of three-plus PMs.", "Credit/data background is strong; direct PM people-management prerequisite is not evidenced.", "X", (3,2,4,5,4,2), "BUILD TOWARD", RF, ART_FIN, "HIGH")
add("4694576005", "Flex", "Payments", "Principal Product Manager, Payments", P, "New York, NY; San Francisco, CA", "US", "Hybrid", "https://job-boards.greenhouse.io/flex/jobs/4694576005", (248000,310000,"USD"), FIN, "Non-AI", "Own payment rails/fraud systems and player-coach product delivery.", "Three-plus years direct payments/fraud and PM management.", "Amazon financial products help, but hands-on payments-rail tenure and PM management are not evidenced.", "X", (2,2,5,5,4,2), "BUILD TOWARD", RF, ART_FIN, "HIGH")
add("fbca55c0-c7a1-4ed2-aed3-fe26a9255bb2", "Latitude", "Payments", "Technical Product Lead", G, "United States", "US", "Remote", "https://jobs.ashbyhq.com/latitude-global/fbca55c0-c7a1-4ed2-aed3-fe26a9255bb2", UNKNOWN, FIN, "Non-AI", "First product hire; own global money movement roadmap, payment APIs and regulatory product decisions.", "Senior technical PM, API-first product, startup fluency and expertise in one payments/FX/crypto/treasury/identity area.", "Founder-level product ownership fits the target level; direct rails knowledge and early-stage startup proof remain uncertain.", "E", (3,2,4,3,5,4), "APPLY + BRIDGE", RF, ART_FIN, "MEDIUM")

# Enterprise software and developer/data infrastructure.
add("f7225fae-2203-4332-8ea4-8569c7e371d1", "Vanta", "Enterprise Software", "Staff Product Manager, Data Platform", P, "United States", "US", "Remote", "https://jobs.ashbyhq.com/vanta/f7225fae-2203-4332-8ea4-8569c7e371d1", (243000,286000,"USD"), DATA, "AI-adjacent", "Set data platform strategy for enterprise trust/compliance products.", "Staff-level platform PM and data architecture/customer outcome experience.", "Keystone enterprise data platform maps closely; compliance domain is learnable rather than a hard direct prerequisite.", "NONE", (5,4,5,5,5,4), "APPLY NOW", RD, ART_DATA, "HIGH")
add("81b94a4e-53d3-40d5-9c04-af57bd01961c", "Confluent", "Data / Developer Infrastructure", "Staff Product Manager, Real-Time Data Analytics Platform", P, "United States", "US", "Remote", "https://jobs.ashbyhq.com/confluent/81b94a4e-53d3-40d5-9c04-af57bd01961c", (231500,272000,"USD"), DATA, "AI-adjacent", "Drive real-time analytics platform direction, developer experience and adoption.", "Technical data-platform PM; streaming analytics fluency.", "Enterprise data platform evidence is strong; real-time OLAP and streaming-engine concepts need technical preparation.", "K", (4,3,5,4,5,4), "APPLY + BRIDGE", RD, ART_DATA, "MEDIUM")
add("4712069006", "Couchbase", "Data / Developer Infrastructure", "Principal Product Manager, Couchbase Mobile", P, "United States", "US", "Remote", "https://job-boards.greenhouse.io/couchbaseinc/jobs/4712069006", (160000,188000,"USD"), ENTERPRISE, "AI-adjacent", "Own execution of mobile/edge database and sync portfolio.", "Eight-plus years PM plus three-plus years hands-on production software development and client-side app architecture.", "Platform PM evidence transfers, but required hands-on development and mobile embedded database background are not evidenced.", "X", (2,1,5,2,3,4), "BUILD TOWARD", RE, ART_DATA, "HIGH")
add("JB0074880", "ServiceNow", "Enterprise Software", "Staff Technical Product Manager - AI/LLM Expertise + AI Evaluation Science", P, "Hyderabad", "India", "Flexible", "https://careers.servicenow.com/jobs/744000145693831/staff-technical-product-manager-aillm-expertise-plus-ai-evaluation-science/", UNKNOWN, AI, "AI-heavy", "Lead AI evaluation science and LLM product quality strategy.", "Staff technical PM; AI evaluation and cross-functional research/engineering fluency.", "Forecasting Agent and Patent AI evaluation are strong matching evidence; India eligibility is still unconfirmed.", "NONE", (5,4,5,3,5,4), "APPLY NOW", REV, ART_AGENT, "HIGH", "2026-08-26")

# Retail/marketplace: mature tech, commerce, and specialist retrieval products.
add("R-2538197", "Walmart", "Retail / Commerce", "Principal Product Manager - Inventory Planning", P, "Bentonville, AR", "US", "On-site / unspecified", "https://careers.walmart.com/us/en/jobs/R-2538197", (110000,220000,"USD"), OPS, "AI-adjacent", "Lead forecasting and inventory planning product strategy.", "Principal product ownership in supply chain and data-driven planning.", "Amazon supply-chain/optimization and forecasting work match; Bentonville location is the main viability question, and supply-chain impact needs prominent resume proof.", "E", (5,4,5,3,4,2), "APPLY + BRIDGE", RD, ART_SUPPLY, "MEDIUM")
add("R-2409416", "Walmart", "Retail / Commerce", "Principal Product Manager - Core Recommendations", P, "Sunnyvale, CA", "US", "On-site / unspecified", "https://careers.walmart.com/us/en/jobs/R-2409416", (143000,286000,"USD"), SEARCH, "AI-heavy", "Lead recommendation and personalization product outcomes at scale.", "Principal PM and ML/recommendations product background.", "Amazon marketplace and ML platform experience map well; recommendation-specific proof should be foregrounded.", "E", (4,3,5,4,4,3), "APPLY + BRIDGE", RD, ART_ML, "MEDIUM")
add("8734135002", "OpenTable", "Marketplace / Consumer", "Principal Product Manager - Restaurant Product", P, "San Francisco, CA", "US", "Hybrid, two office days weekly", "https://job-boards.greenhouse.io/opentable/jobs/8734135002", (190000,220000,"USD"), GROWTH, "AI-heavy", "Own 0-to-1 AI/ML restaurant revenue optimization products.", "Ten-plus years PM, AI/ML shipped products, 0-to-1 delivery; restaurant domain preferred.", "Enterprise AI and optimization evidence fit; restaurant revenue/yield vocabulary is a bridge, not a hard experience gap.", "V", (4,3,5,3,4,2), "APPLY + BRIDGE", RG, ART_AGENT, "HIGH")
add("4233299e-f003-4745-8fc0-6622abff1749", "Constructor", "Retail / Commerce", "Staff Product Manager, Product Discovery Engine", P, "Remote (US eligibility indicated by benefits)", "US", "Remote", "https://jobs.ashbyhq.com/constructor/4233299e-f003-4745-8fc0-6622abff1749/", UNKNOWN, SEARCH, "AI-heavy", "Own search quality, recall/ranking and retail conversion metrics across a product-discovery engine.", "Eight-plus years PM in search/ML/NLP-heavy products and deep search pipeline understanding.", "Patent AI retrieval/evaluation proves adjacent depth, but live high-scale retail ranking proof needs careful evidence framing.", "E", (4,3,5,3,5,4), "APPLY + BRIDGE", REV, ART_PATENT, "MEDIUM")

# Healthcare, including one intentional down-level Skip.
add("3dd3085b-471c-4416-a782-9c9fccf7e32f", "Headway", "Healthcare", "Principal Product Manager", P, "Remote; Seattle, WA; New York, NY; San Francisco, CA", "US", "Remote / listed offices", "https://jobs.ashbyhq.com/headway/3dd3085b-471c-4416-a782-9c9fccf7e32f", (300000,375000,"USD"), OPS, "AI-adjacent", "Lead products across mental-health insurance-enabled marketplace workflows.", "Principal ownership and complex platform/consumer/operations product experience.", "Enterprise platforms and financial-service workflows transfer; healthcare payer/provider terminology needs preparation.", "V", (4,3,5,5,5,5), "APPLY + BRIDGE", RGEN, ART_ENT, "MEDIUM")
add("67be8703-070b-459d-8c5c-191a1478f803", "R37 Lab / R1 RCM", "Healthcare", "Principal Product Manager", P, "United States", "US", "Remote", "https://jobs.ashbyhq.com/r37/67be8703-070b-459d-8c5c-191a1478f803", (216000,270000,"USD"), AI, "AI-heavy", "Own AI-enabled healthcare revenue-cycle strategy and workflow automation.", "Principal AI PM plus healthcare/RCM experience in coding, billing or claims.", "Agent/platform experience is strong; direct RCM operating context appears central and is not evidenced.", "X", (3,2,5,4,5,4), "BUILD TOWARD", RA, ART_AGENT, "MEDIUM")
add("0762f803-07d5-4946-bd06-decbece48fdc", "Included Health", "Healthcare", "Staff Product Manager, Care Application Platform", P, "United States", "US", "Remote", "https://jobs.lever.co/includedhealth/0762f803-07d5-4946-bd06-decbece48fdc", (163000,277704,"USD"), ENTERPRISE, "AI-adjacent", "Own care application platform and AI-enabled clinician/expert workflows.", "Five-plus years PM and complex expert/high-stakes workflow experience.", "Enterprise planning and regulated financial products are credible high-stakes analogs; clinical language needs a bridge.", "V", (4,3,5,4,4,4), "APPLY + BRIDGE", RE, ART_ENT, "HIGH")
add("4ffc91f2-542c-4b06-8276-1843276a8f00", "Clarify Health", "Healthcare", "Senior Product Manager", S, "United States", "US", "Remote", "https://jobs.lever.co/clarifyhealth/4ffc91f2-542c-4b06-8276-1843276a8f00", (162000,190000,"USD"), DATA, "AI-adjacent", "Own components of Meridian; prototype, QA, release and support existing capabilities.", "Five-plus years PM/product analytics and hands-on component delivery.", "Component-level ownership and Senior title are a meaningful step below current Principal scope; skip despite relevant analytics skills.", "NONE", (4,3,1,2,2,4), "SKIP", RD, ART_DATA, "HIGH")

# AI-native: product title is conditional where global platform scope is senior-equivalent.
add("7a8fba25-fe2f-4b23-a224-ac48e943725d", "interface.ai", "AI-native", "Principal Product Manager, AI Platform", P, "San Francisco, CA", "US", "On-site", "https://jobs.ashbyhq.com/interface-ai/7a8fba25-fe2f-4b23-a224-ac48e943725d/", (250000,320000,"USD"), AI, "AI-heavy", "Lead production AI platform for financial-service customer agents.", "Eight-plus years PM and three-plus at Staff/Principal level; AI platform depth.", "Agent and fintech platform record is strong; exact Staff/Principal tenure and SF relocation need confirmation.", "E", (4,3,5,5,5,2), "APPLY + BRIDGE", RA, ART_AGENT, "MEDIUM")
add("product-manager-api-agents-san-francisco", "OpenAI", "AI-native", "Product Manager, API Agents", M, "San Francisco, CA", "US", "On-site", "https://openai.com/careers/product-manager-api-agents-san-francisco/", (293000,325000,"USD"), AI, "AI-heavy", "Set strategy for global developer API agent infrastructure and primitives.", "Five-plus years PM; developer-facing APIs, high-growth customers and technical research partnership.", "Despite generic PM title, global agent API ownership and pay suggest senior-equivalent scope; developer API proof needs emphasis.", "E", (4,2,4,5,5,2), "APPLY + BRIDGE", RA, ART_AGENT, "MEDIUM")
add("5153924008", "Anthropic", "AI-native", "Product Manager, Multi-Cloud Growth - Google", M, "San Francisco, CA", "US", "Hybrid, at least 25% office time", "https://job-boards.greenhouse.io/anthropic/jobs/5153924008", (305000,460000,"USD"), ENTERPRISE, "AI-heavy", "Own hyperscaler partner growth, enterprise API strategy and commercial outcomes.", "Shipped with a hyperscaler partner and owned revenue/margin/channel P&L.", "Amazon and enterprise platform background help, but direct hyperscaler-partner delivery plus commercial P&L proof are not established.", "X", (3,1,4,5,5,2), "BUILD TOWARD", RE, ART_ENT, "MEDIUM")


def write_csv(path, fields, rows):
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def main():
    assert 25 <= len(JOBS) <= 40, len(JOBS)
    assert len({job["job_id"] for job in JOBS}) == len(JOBS)
    assert all(job["status"] == "live_verified" for job in JOBS)
    assert sum(job["application_lane"] == "BUILD TOWARD" for job in JOBS) == 5
    assert sum(job["application_lane"] == "SKIP" for job in JOBS) == 2
    data = ROOT / "data"
    with (data / "jobs_raw.jsonl").open("w", encoding="utf-8") as handle:
        for job in JOBS:
            handle.write(json.dumps({**job, "verification_method": "Current official posting with live apply control checked in browser; no application submitted"}, ensure_ascii=False) + "\n")
    write_csv(data / "jobs_master.csv", FIELDS, JOBS)
    lane_order = {"APPLY NOW": 0, "APPLY + BRIDGE": 1, "BUILD TOWARD": 2}
    queue = [job for job in JOBS if job["application_lane"] != "SKIP"]
    queue.sort(key=lambda job: (lane_order[job["application_lane"]], -int(job["posted_date"].replace("-", "") or 0), -job["priority_score"], job["company"]))
    formatted = []
    for job in queue:
        pay = "Unpublished" if job["comp_min"] is None else f'{job["currency"]} {job["comp_min"]:,}–{job["comp_max"]:,} (official range)'
        formatted.append(dict(zip(QUEUE_FIELDS, [
            job["company"], job["role_title"], job["sector"], job["normalized_level"],
            job["location"], job["posted_date"], pay, job["role_cluster"],
            job["ai_classification"], job["priority_score"], job["application_lane"],
            job["primary_gap"], "Yes" if job["hard_experience_gap"] else "No",
            job["fit_summary"], job["recommended_resume_variant"],
            job["recommended_portfolio_artifact"], job["canonical_url"],
            job["classification_confidence"],
        ])))
    write_csv(data / "review_queue.csv", QUEUE_FIELDS, formatted)
    write_csv(data / "discovery_log.csv", ["timestamp_utc", "event", "count", "notes"], [
        {"timestamp_utc": STAMP, "event": "calibration_discovery", "count": len(JOBS),
         "notes": "Diverse first calibration; official employer/ATS postings checked for active apply paths; stale/closed results excluded; no applications or outreach."},
        {"timestamp_utc": STAMP, "event": "classification", "count": len(JOBS),
         "notes": "Six weighted scores, primary gap, hard-X flag, lane, resume and portfolio recommendations; unpublished pay neutral at 3."},
        {"timestamp_utc": STAMP, "event": "review_queue", "count": len(queue),
         "notes": "All Apply Now and Apply + Bridge plus five Build Toward; two Skip roles excluded."},
        {"timestamp_utc": STAMP, "event": "stale_result_exclusions", "count": 6,
         "notes": "Search-indexed results with closed/404 individual postings were excluded: Snapdocs, Foxglove, Harvey, Sierra and two Walmart requisitions. No unverified job retained."},
    ])
    print(f"Wrote {len(JOBS)} live jobs and {len(queue)} review items at {STAMP}")


if __name__ == "__main__":
    main()
