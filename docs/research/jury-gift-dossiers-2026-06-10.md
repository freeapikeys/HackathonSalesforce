# Jury Gift Dossiers - 2026-06-10

Status: private local research checkpoint  
Branch: `codex/closed-loop-intelligence-rm`  
Purpose: identify tailored "gift" demos for visible Agentforce hackathon jury
companies using OSINT, provided screenshots, and the Air Mauritius challenge
document.

## Research Method

Evidence grades:

- **Confirmed**: supported by official company material, regulatory/market
  filings, annual reports, official challenge documents, or direct screenshot
  evidence.
- **Likely inference**: a reasonable product implication from confirmed public
  facts.
- **Weak signal**: public review, social chatter, third-party article, or
  incomplete source that should not be presented as fact.
- **Unknown**: needs direct confirmation from the company, organizer, or jury.

Product boundary:

- Use only first-party, authorized, or public-source-inspired synthetic data.
- Do not pitch surveillance, scraping, autonomous regulated decisions, or
  unapproved external actions.
- Keep Agentforce as decision support and drafting; humans approve protected
  actions.
- Keep MuleSoft as the integration/orchestration boundary.
- Preserve source evidence, confidence, policy, approvals, action outcomes, and
  feedback.

## Visible Jury/Company Targets

Known from screenshots and provided materials:

- Air Mauritius
- Constance Hospitality / Constance Hotels Services Limited
- AfrAsia
- Nexavenu
- Sun Resorts / Sunlife

## Cross-Target Synthesis

The strongest single story is not "CRM automation." It is a **closed-loop
relationship intelligence operating system**:

1. fragmented proprietary data arrives from operational systems, emails,
   documents, reviews, bookings, cases, payments, ERP, HR, or partner systems;
2. MuleSoft validates and orchestrates the data;
3. Salesforce preserves evidence and relationship context;
4. Agentforce separates facts, claims, inferences, recommendations, decisions,
   actions, and outcomes;
5. protected actions require approval;
6. outcomes feed back into the next recommendation.

The gifts should feel different per juror, but share one platform spine.

| Target        | Gift Name                                       | Best Surface                               | Core Emotional Hit                                            |
| ------------- | ----------------------------------------------- | ------------------------------------------ | ------------------------------------------------------------- |
| Air Mauritius | Passenger Recovery Command Center               | Salesforce airline claims console          | "You can turn disruption chaos into governed recovery."       |
| Constance     | Guest Revenue and Operations Loop               | Salesforce hospitality console + sidecar   | "Your bookings, FX, reviews, and occupancy become one brief." |
| AfrAsia       | Relationship Intelligence Control Tower         | Secure banker relationship cockpit         | "AI strengthens the relationship banker safely."              |
| Nexavenu      | Client AI Readiness and Action Command Center   | Salesforce delivery/discovery cockpit      | "You can reuse this to sell Agentforce transformation."       |
| Sunlife       | Guest Recovery and Experience Intelligence Loop | Hospitality command center + WhatsApp mock | "Premium guest experience scales without losing control."     |

## Air Mauritius

### Top Pains

1. **Operational reliability and aircraft availability**
   - Confirmed: Air Mauritius reported Q1 FY2025/26 profit while also facing
     aircraft-on-ground disruption, including an A330-900neo out of service for
     much of the quarter and 24 AOG incidents.
   - Confirmed: Air Mauritius reported February 2026 Rodrigues disruptions
     because only one of four ATR 72 aircraft was available.
   - Likely inference: disruption creates downstream passenger claims, call
     center load, compensation exposure, rebooking work, baggage issues, and
     margin leakage.

2. **Passenger disruption handling and proactive communication**
   - Confirmed: Air Mauritius has support flows for delays, cancellations,
     denied boarding, refunds, baggage, and other claims.
   - Confirmed: recent newsroom items include flight delays and luggage
     offloading communications.
   - Weak signal: public review/social sources complain about communication and
     claim follow-up, but these sources are self-selecting and should be used
     only as color.

3. **Claims, refunds, and EU261-style compensation complexity**
   - Confirmed: the provided
     `/Users/wenli/Downloads/Hackathon-MuleSoft-ClaimsProcessing.docx` asks for
     automated airline claims processing using MuleSoft, AI intent detection,
     CRM service requests, reservation/flight lookup, and simplified EU/non-EU
     compensation rules.
   - Confirmed: Air Mauritius conditions of carriage include EU261 compensation
     claim rules and direct passenger submission requirements.
   - Likely inference: a governed eligibility, evidence, response, and approval
     workflow is highly relevant.

4. **Baggage and service fragmentation**
   - Confirmed: Air Mauritius exposes separate support flows and contacts for
     damaged, delayed, and lost baggage.
   - Likely inference: baggage status, passenger disruption, compensation, and
     service recovery should be connected in one passenger recovery loop.

5. **Margin protection while modernizing customer experience**
   - Confirmed: Air Mauritius reported H1 FY2025/26 profit of MUR 1.1B / EUR
     22.03M and continues public digital/customer experience work.
   - Confirmed: Branchspace describes the Air Mauritius website revamp,
     direct-online-sales gains, and a planned generative-AI virtual assistant.
   - Likely inference: the best gift should combine AI/CX with operational
     discipline, not just a chatbot.

### Gift Concept

**Passenger Recovery Command Center**

Scenario: a fleet/weather disruption affects Rodrigues or Paris passengers.
MuleSoft ingests flight status, booking records, passenger tier, baggage status,
claim text, EU/non-EU eligibility, and operational cause. Salesforce creates the
case/evidence spine. Agentforce produces a recovery plan:

- classify facts, claims, inferences, and unknowns;
- identify affected passengers and priority cases;
- recommend reroute/refund/meal/hotel/compensation actions;
- draft WhatsApp/email/call-center scripts;
- open Salesforce tasks and service requests;
- require manager approval before compensation, refund, or outbound message;
- execute approved MuleSoft mock write-backs;
- capture outcomes: passenger contacted, case resolved, claim approved/denied,
  compensation paid, SLA risk reduced.

### Best Surface

Primary: Salesforce airline claims/recovery console.  
Secondary: WhatsApp-style passenger message mock and Slack/Teams operations
alert.  
MuleSoft mocks: flight ops, booking/PSS, baggage/WorldTracer-style status,
payment/refund, customer support forms.

### Claims To Avoid

- Do not imply Air Mauritius has safety issues.
- Do not present review complaints as representative fact.
- Do not promise legally final EU261 decisions; present eligibility triage and
  human/legal approval.
- Do not claim internal-system access.

### Source Locators

- Air Mauritius challenge doc:
  `/Users/wenli/Downloads/Hackathon-MuleSoft-ClaimsProcessing.docx`
- Air Mauritius Customer Support:
  <https://www.airmauritius.com/customer-support>
- Air Mauritius Contact Us:
  <https://www.airmauritius.com/en/help/contact-us>
- Air Mauritius EU261 / conditions:
  <https://www.airmauritius.com/en/legal-regulations-links/conditions-of-carriage/schedules-delays-cancellation-of-flights>
- Air Mauritius newsroom:
  <https://www.airmauritius.com/en/footer/newsroom>
- Air Mauritius Rodrigues disruption, February 2026:
  <https://www.airmauritius.com/en-re/footer/newsroom/press-communique-operational-disruptions-to-and-from-rodrigues>
- Air Mauritius Q1 FY2025/26:
  <https://my.airmauritius.com/en-nl/footer/newsroom/news-release-air-mauritius-posts-first-quarter-profits>
- Air Mauritius H1 FY2025/26:
  <https://www.airmauritius.com/it/newsroom/press-communique-financial-result-of-first-semester>
- Branchspace digital transformation case:
  <https://www.branchspace.com/customer-insights/air-mauritius>
- Airbus Fleet Technical Management:
  <https://www.airbus.com/en/newsroom/press-releases/2024-07-air-mauritius-selects-airbus-services-for-enhanced-operational>
- Weak signal / review source:
  <https://ie.trustpilot.com/review/www.airmauritius.com>

## Constance Hospitality

### Top Pains

1. **Occupancy and demand volatility while protecting premium rates**
   - Confirmed: CHSL 2025 reporting shows occupancy pressure in parts of the
     portfolio while management emphasizes revenue management, profitability,
     and operational adjustment.
   - Likely inference: they need forward-looking demand, occupancy, and RevPAR
     intelligence linked to action, not another static dashboard.

2. **Fragmented operational data and manual extraction**
   - Confirmed from screenshot: Constance requested reservation email extraction
     into structured booking lists, exchange-rate extraction/load to ERP, and
     sentiment analysis to predict occupancy.
   - Confirmed: CHSL annual material discusses investment in digital
     infrastructure, data capabilities, cybersecurity, automation, and practical
     AI.

3. **FX, finance, and cost-control pressure**
   - Confirmed: CHSL public risk material includes foreign currency, liquidity,
     pricing, receivables/payables, inflation, payroll/taxation, and cost
     pressures.
   - Confirmed: Bank of Mauritius publishes daily indicative exchange rates,
     making an FX-to-ERP automation credible.

4. **Luxury guest-experience consistency and reputation risk**
   - Confirmed: CHSL reports high satisfaction and review index metrics, while
     also naming reputation, adverse publicity, service quality, safety, talent
     shortages, and corrective action from feedback as risks.
   - Weak signal: public review comments mention isolated room/service issues,
     but the overall review picture remains strong.

5. **Portfolio expansion and standardization**
   - Confirmed: CHSL operates across multiple destinations and took over
     Constance Le Chaland in 2026.
   - Likely inference: new-property integration and consistent operating
     intelligence matter.

### Gift Concept

**Constance Guest Revenue and Operations Loop**

Scenario: reservation emails, daily Bank of Mauritius FX rates, review/sentiment
signals, and occupancy forecast data arrive in MuleSoft. Salesforce creates
structured booking, guest, property, rate, FX, sentiment, and task records.
Agentforce detects a soft-demand or guest-risk window, explains the evidence,
predicts occupancy/RevPAR risk, recommends action, and requests approval for:

- targeted guest outreach;
- rate/package adjustment;
- reservation team task;
- housekeeping/maintenance task;
- restaurant capacity task;
- ERP FX update.

Outcomes feed back into the next occupancy and guest-risk recommendation.

### Best Surface

Primary: Salesforce hospitality/revenue operations console.  
Sidecars: MuleSoft/API log panel and WhatsApp/Slack-style operations alert.

Wow moments:

- email-to-booking extraction;
- Bank of Mauritius FX-to-ERP load;
- sentiment-to-occupancy forecast with evidence and approval.

### Claims To Avoid

- Do not claim Constance has broken systems.
- Do not imply poor guest satisfaction; public metrics are strong.
- Do not say manual workflows are confirmed beyond the screenshot clues unless
  the jury confirms them.
- Do not imply autonomous price changes, guest messages, or ERP writes.

### Source Locators

- Screenshot clue:
  `/var/folders/3j/9cl2tssj65l6xrj2csj5xbx40000gn/T/TemporaryItems/NSIRD_screencaptureui_Z9os6b/Screenshot 2026-06-10 at 10.28.44.png`
- CHSL Annual Report 2025:
  <https://constance-ebook.cld.bz/Constance-Hotels-Services-Limited-Annual-Report-2025>
- CHSL annual report operating review page:
  <https://constance-ebook.cld.bz/Constance-Hotels-Services-Limited-Annual-Report-2025/18>
- CHSL risk page:
  <https://constance-ebook.cld.bz/Constance-Hotels-Services-Limited-Annual-Report-2025/60/>
- CHSL financial figures:
  <https://www.constancehrg.com/en/financial-figures/>
- CHSL abridged 2025:
  <https://www.stockexchangeofmauritius.com/media/12281/chsl-abridged-2025-final.pdf>
- Bank of Mauritius exchange rates:
  <https://www.bom.mu/markets/foreign-exchange/consolidated-indicative-exchange-rates>
- Salesforce hospitality integration reference:
  <https://www.salesforce.com/in/blog/frictionless-hospitality/>
- Booking.com review weak signal:
  <https://www.booking.com/reviews/mu/hotel/constance-belle-mare-plage.html>
- Constance Tripadvisor recognition:
  <https://www.constancehotels.com/en/news/celebrating-recognition-2025-tripadvisor-travelers-choice-awards/>

## AfrAsia

### Top Pains

1. **Post-acquisition cross-border coordination**
   - Confirmed: Access Bank UK finalized a 76% majority stake in AfrAsia on
     2025-07-24.
   - Confirmed: AfrAsia positions the relationship as strengthening private
     banking, wealth, trade flows, and client service across international
     markets.
   - Likely inference: relationship, product, compliance, referral, and client
     context can fragment across markets without a governed relationship layer.

2. **Relationship-led private banking needs scale**
   - Confirmed: AfrAsia publicly emphasizes private banking, dedicated
     relationship managers, tailored advice, wealth planning, discretionary and
     non-discretionary portfolio management, EAM services, custody, structured
     products, and timely expertise.
   - Likely inference: relationship managers need a "what changed, why it
     matters, what can I safely do next?" cockpit.

3. **Compliance/KYC/AML pressure**
   - Confirmed: AfrAsia compliance covers regulatory interaction, KYC/CDD,
     transaction monitoring, investigation/reporting, fraud, and AML training.
   - Confirmed: Mauritius' 2025 national AML/CFT material rates money-laundering
     risk as material and emphasizes risk-based supervision and data collection.
   - Likely inference: AI must support compliance review, not replace it.

4. **Cross-border FX, custody, payments, and market complexity**
   - Confirmed: AfrAsia serves clients across many countries and offers access
     to many financial markets, with meaningful FX/trading and fee income.
   - Likely inference: bankers need timely signals tied to FX, portfolios,
     custody events, client intent, suitability, and approval policy.

5. **Digitalization, cyber, and operational resilience**
   - Confirmed: AfrAsia maintains a Cyber and Technology Committee covering IT,
     cybersecurity, digitalization, technology strategy, regulatory compliance,
     and risk appetite.
   - Confirmed: AfrAsia enhanced online banking features in 2026.
   - Likely inference: the gift must show speed and service while preserving
     auditability, cyber controls, and human approval.

### Gift Concept

**AfrAsia Relationship Intelligence Control Tower**

Scenario: a high-net-worth non-resident client with Mauritius, Dubai, and South
Africa exposure has a portfolio drift, upcoming FX/payment need, pending KYC
refresh, and possible Access-network referral opportunity. Agentforce assembles
CRM, portfolio, KYC, transaction/payment, FX, RM-note, feedback, and policy
evidence. It separates facts, inferences, recommendations, approval needs, and
expected outcomes.

Agents:

- Relationship Orchestrator: one next-best plan for the banker.
- Compliance Guardrail Agent: KYC/CDD, callback, communication audit trail, and
  suitability checks.
- Treasury/FX Opportunity Agent: liquidity, maturity, hedging, and market
  trigger suggestions.
- Client Service Recovery Agent: unresolved feedback, delayed onboarding,
  missing documents, or high-value instruction risk.

Core gift sentence: "Here is what changed, here is the evidence, here is the
compliant next action, here is who must approve it, and here is the outcome
after execution."

### Best Surface

Primary: secure Salesforce banker cockpit / relationship console.  
Secondary: Teams/Slack-style internal alert, approved WhatsApp/email draft, and
optional client portal card.

Avoid making WhatsApp the main surface. For private banking, channels are
execution rails; the cockpit is the gift.

### Claims To Avoid

- Do not claim AfrAsia has bad onboarding or confirmed data fragmentation.
- Do not pitch autonomous financial advice, autonomous AML decisions, or
  autonomous payment execution.
- Do not say AI determines suspicion; it surfaces indicators and evidence for
  review.
- Do not say "replace relationship managers"; say "make each banker faster,
  better prepared, and safer."

### Source Locators

- AfrAsia ownership change:
  <https://www.afrasiabank.com/en/about/newsroom/communique/2025/change-in-share-ownership/>
- AfrAsia brand/interview:
  <https://www.afrasiabank.com/en/about/newsroom/news/2025/afrasia-bank-to-continue-operating-under-its-current-brand-1/>
- AfrAsia shareholding:
  <https://www.afrasiabank.com/en/about/investors/shareholding-structure>
- AfrAsia Private Banking:
  <https://www.afrasiabank.com/en/private>
- Wealth Management and Advisory:
  <https://www.afrasiabank.com/en/private/investment-solutions/wealth-management-advisory/>
- External Asset Manager:
  <https://www.afrasiabank.com/en/private/external-asset-manager>
- AfrAsia Compliance:
  <https://www.afrasiabank.com/en/about/corporate-governance/compliance>
- Bank of Mauritius AML/CFT/CPF:
  <https://www.bom.mu/financial-stability/amlcft>
- BoM Private Banking Guideline:
  <https://www.bom.mu/sites/default/files/guideline_on_private_banking_06.12.2021.pdf>
- AfrAsia International Banking:
  <https://www.afrasiabank.com/en/international>
- AfrAsia Global Custody:
  <https://www.afrasiabank.com/en/private/investment-solutions/securities-services/>
- AfrAsia FI team:
  <https://www.afrasiabank.com/en/treasury/financial-institution?ref=%2Fen%2Ftreasury%2Fexchange-rates>
- AfrAsia FY2025 results:
  <https://www.afrasiabank.com/en/about/newsroom/news/2025/afrasia-bank-delivers-a-strong-financial-performance-with-profits-of-mur-63bn-for-the-financial-year-ended-30-june-2025/>
- AfrAsia 2025 annual report:
  <https://www.afrasiabank.com/media/17594/afrasia-bank-limited-annual-report-2025.pdf>
- Cyber and Technology Committee terms:
  <https://www.afrasiabank.com/media/17264/cyber-and-technology-committee-terms-of-reference.pdf>
- Enhanced online banking:
  <https://www.afrasiabank.com/en/about/newsroom/communique/2026/enhanced-online-banking-platform/>

## Nexavenu

### Identity

High-confidence match: Nexavenu / Nexavenu PTY LTD is a Salesforce consulting
and digital transformation partner with Australia and Mauritius presence. Public
positioning emphasizes Agentforce, Data 360, MuleSoft integration/API strategy,
Field Service, Service Cloud, AI readiness, and operational productivity.

### Top Pains / Opportunities

1. **AI readiness is a board-level customer concern**
   - Confirmed: Nexavenu sells Data 360, Agentforce, AI readiness, AI rollout,
     governance, and Salesforce implementation services.
   - Likely inference: a reusable client AI-readiness cockpit is useful as a
     sales and delivery accelerator.

2. **Integration sprawl is central to their value proposition**
   - Confirmed: Nexavenu event and service pages discuss modernization for AI,
     API-led architecture, point-to-point integration reduction, microservices,
     RPA, IDP, and AI agents.
   - Likely inference: they will reward a demo where MuleSoft is visibly the
     action/integration layer.

3. **Field service and physical operations are a sweet spot**
   - Confirmed: Nexavenu public materials reference Field Service, ServiceMax,
     Asset360, integrations, energy/utilities, manufacturing, transport,
     logistics, and operational industries.
   - Likely inference: EV charging / field-service / asset-lifecycle demos fit
     better than generic CRM or retail.

4. **Clients need end-to-end operational visibility**
   - Confirmed: Nexavenu customer material references tracking an EV charging
     site from inception through ongoing management and maintenance.
   - Likely inference: a closed-loop asset/service intelligence demo can become
     a client-facing sales asset for Nexavenu.

5. **Scaling delivery across regions and talent**
   - Confirmed: Nexavenu careers and office pages show multi-region presence and
     hiring in Salesforce/MuleSoft roles.
   - Likely inference: standardized discovery, qualification, demo, and
     proposal artifacts are valuable.

### Gift Concept

**Client AI Readiness and Action Command Center**

Gift angle: give Nexavenu a demo they can reuse in client discovery. A
consultant loads messy client signals: CRM cases, field-service work orders,
asset/site records, emails/docs, integration inventory, customer complaints, SLA
breaches, and operational KPIs. Agentforce classifies facts, claims, and
inferences; detects the top bottleneck; recommends an AI/MuleSoft/Salesforce
modernization path; drafts a client-facing action plan; and routes protected
actions for approval.

Best story vertical: EV charging / field service / asset maintenance, inspired
by Nexavenu's JOLT-type customer story and public industry positioning.

### Best Surface

Primary: Salesforce Lightning AI Readiness Command Center.

Panels:

- evidence timeline;
- client/site/asset relationship graph;
- Agentforce facts/inferences/actions panel;
- MuleSoft integration map;
- approval cockpit;
- outcome loop.

### Claims To Avoid

- Do not claim Nexavenu itself has internal data fragmentation unless confirmed.
- Do not claim a specific person is on the jury unless event material confirms
  it.
- Do not overstate Data 360 implementation details.
- Do not pitch autonomous external action.
- Do not make the demo supermarket-only.

### Source Locators

- Nexavenu:
  <https://nexavenu.com/>
- Salesforce AppExchange listing:
  <https://appexchange.salesforce.com/appxConsultingListingDetail?listingId=a0N3A00000GCUtzUAH>
- LinkedIn:
  <https://au.linkedin.com/company/nexavenu>
- Nexavenu MuleSoft Mauritius event:
  <https://nexavenu.com/mulesoftevent-mauritius-2025>
- Nexavenu Data 360:
  <https://nexavenu.com/data360>
- Nexavenu customer stories:
  <https://nexavenu.com/customer-success-stories>
- Nexavenu careers:
  <https://nexavenu.com/careers>
- Nexavenu BDR role:
  <https://nexavenu.com/bdr-middle-east>
- Agentforce hackathon criteria:
  <https://agentforcehackathon.devpost.com/>

## Sun Resorts / Sunlife

### Top Pains

1. **Efficiency pressure under high occupancy**
   - Confirmed: Sunlife is performing well, with strong occupancy and RevPAR
     metrics in public financial material.
   - Confirmed: management still emphasizes cost discipline, yield optimization,
     and digitalization for guest experience and efficiencies.
   - Likely inference: the right demo is not rescue; it is premium scaling.

2. **Guest experience must scale without losing service quality**
   - Confirmed: public analyst material reports strong customer satisfaction
     and competitive GRI position while keeping guest experience as a priority.
   - Likely inference: they need faster recovery loops during high occupancy,
     not generic complaint handling.

3. **Fragmented guest channels after app discontinuation**
   - Confirmed: Sunlife FAQ pages say the Sunlife Resorts App is no longer
     available for several properties and direct guests to chat, WhatsApp,
     email, and phone.
   - Likely inference: unified guest-channel intelligence is a natural fit.

4. **Workforce retention, training, and productivity**
   - Confirmed: Sunlife sustainability material reports workforce size,
     retention improvement, training hours, and turnover targets.
   - Likely inference: staff task clarity and support matters because guest
     experience depends on employee execution.

5. **Sustainability and supplier traceability pressure**
   - Confirmed: Sunlife sustainability targets include renewable energy, waste
     diversion, water monitoring, local sourcing, and supplier ESG screening.
   - Likely inference: sustainability should become operational evidence in the
     guest/service loop, not a separate report.

### Gift Concept

**Sunlife Guest Recovery and Experience Intelligence Loop**

Scenario: a high-value guest reports a dining/service issue over WhatsApp during
a busy high-occupancy evening. The system connects guest profile, stay context,
reservation/package, returning-guest value, restaurant capacity, staff roster,
service complaint, sustainability preference, local supplier/menu constraints,
and manager approval.

Agentforce separates facts from inferences, recommends a recovery plan, creates
staff tasks, drafts a WhatsApp response, requires manager approval for
compensation or external messaging, and records the outcome: guest satisfaction
recovered, task completed, response time, comp cost, and repeat-stay risk
reduced.

### Best Surface

Primary: Salesforce hospitality command center.  
Sidecars: WhatsApp guest operations mock and staff task cockpit.

This should not be a pure revenue dashboard or pure chatbot. The gift is the
closed loop between guest promise, staff execution, partner/supplier context,
sustainability evidence, and revenue impact.

### Claims To Avoid

- Do not claim Sunlife is failing on service.
- Do not say the app failed; only say it is no longer available per current FAQ.
- Do not pitch employee surveillance.
- Do not make sustainability claims without source evidence, time windows, and
  formulas.

### Source Locators

- Sunlife financial information:
  <https://www.yoursunlife.com/financial-information/>
- Sunlife Q2 FY26 analyst deck:
  <https://www.yoursunlife.com/media/pxphsrld/sun-limited_q2-fy26-analyst-meeting_12-feb-2026.pdf>
- Long Beach FAQ:
  <https://www.yoursunlife.com/longbeachmauritius/faqs/>
- La Pirogue FAQ:
  <https://www.yoursunlife.com/lapiroguemauritius/faqs/>
- Sugar Beach FAQ:
  <https://www.yoursunlife.com/sugarbeachmauritius/faqs/>
- Sunlife Sustainability Report 2025:
  <https://www.yoursunlife.com/media/rajlyhcu/sl_sustainability-report-2025_.pdf>

## Build Priority Recommendation

Use three layers for the demo strategy:

1. **Universal platform demo**: evidence, Agentforce reasoning, approval, action,
   outcome.
2. **Two flagship gifts**:
   - Air Mauritius Passenger Recovery Command Center because the provided DOCX
     maps directly to MuleSoft + AI + claims and is highly demoable.
   - Constance Guest Revenue and Operations Loop because the screenshot gives
     explicit requested workflows and the demo has three obvious wow moments.
3. **Three tailored overlays**:
   - AfrAsia secure banker cockpit for regulated RM.
   - Sunlife guest recovery loop for WhatsApp/staff/service execution.
   - Nexavenu AI readiness command center as a reusable partner sales asset.

The product should not become five unrelated demos. Build the same evidence and
action spine once, then swap scenario fixtures, labels, agent prompts, and mock
connectors per target.

## Open Intel Gaps

- Exact full jury roster and roles.
- Which juror belongs to which company and what they personally care about.
- Whether AfrAsia, Sunlife, or Nexavenu gave private challenge prompts similar
  to Air Mauritius and Constance.
- Whether the presentation environment will support a Salesforce org, local
  web app, MuleSoft live mock, or recorded fallback.
- Whether organizers allow personalized "gift" framing in the pitch or prefer
  a single product story.
