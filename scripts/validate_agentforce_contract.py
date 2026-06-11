#!/usr/bin/env python3

import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker


ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = (
    ROOT
    / "intelligence"
    / "agentforce"
    / "schemas"
    / "agentforce-actions-v1.schema.json"
)
FIXTURE_PATH = (
    ROOT
    / "intelligence"
    / "agentforce"
    / "fixtures"
    / "agentforce-scenarios-v1.json"
)
HOSPITAL_PURPOSE = "RESOLVE_HOSPITAL_OPERATION_RISK"
HOSPITAL_MODEL_PROFILE = "hospital_action_reasoning"
RETAIL_MODEL_PROFILE = "north-star-retail-recommendation"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> int:
    schema = json.loads(SCHEMA_PATH.read_text())
    fixtures = json.loads(FIXTURE_PATH.read_text())
    Draft202012Validator(
        schema,
        format_checker=FormatChecker(),
    ).validate(fixtures)

    action_names = {
        definition["action"] for definition in fixtures["actionCatalog"]
    }
    require(
        action_names
        == {
            "EXPLAIN_RELATIONSHIP_CASE",
            "DRAFT_RELATIONSHIP_RECOMMENDATION",
            "REQUEST_HUMAN_APPROVAL",
        },
        "The executable action catalog changed.",
    )

    scenario_names = set()
    for scenario in fixtures["scenarios"]:
        name = scenario["name"]
        request = scenario["request"]
        response = scenario["response"]
        require(name not in scenario_names, f"Duplicate scenario: {name}")
        scenario_names.add(name)
        require(
            response["action"] == request["action"],
            f"{name}: response action does not match request.",
        )
        for identifier in ("contractVersion", "tenantKey", "correlationId"):
            require(
                response[identifier] == request[identifier],
                f"{name}: {identifier} was not preserved.",
            )
        require(
            response["audit"]["purpose"] == request["purpose"],
            f"{name}: purpose was not preserved in audit.",
        )
        require(
            response["audit"]["externalActionExecuted"] is False,
            f"{name}: an Agentforce action claimed external execution.",
        )

        citation_ids = {
            citation["evidenceId"] for citation in response["citations"]
        }
        fact_ids = {fact["factId"] for fact in response["facts"]}
        coverage = response["contextCoverage"]
        if coverage:
            require(
                set(coverage["evidenceIds"]) <= citation_ids,
                f"{name}: context coverage cites inaccessible evidence.",
            )
            for category_name, category in coverage[
                "evidenceCategories"
            ].items():
                require(
                    set(category["evidenceIds"]) <= citation_ids,
                    f"{name}: {category_name} coverage cites inaccessible evidence.",
                )
        for fact in response["facts"]:
            require(
                set(fact["evidenceIds"]) <= citation_ids,
                f"{name}: fact cites evidence not returned to the user.",
            )
        for inference in response["inferences"]:
            require(
                set(inference["basisFactIds"]) <= fact_ids,
                f"{name}: inference is not grounded in returned facts.",
            )

        recommendation = response["recommendation"]
        if recommendation:
            require(
                set(recommendation["evidenceIds"]) <= citation_ids,
                f"{name}: recommendation cites inaccessible evidence.",
            )
            require(
                recommendation["requiresHumanApproval"] is True,
                f"{name}: recommendation bypasses human approval.",
            )
            require(
                response["audit"]["modelInvocationId"]
                == recommendation["modelInvocationId"],
                f"{name}: model invocation provenance was not preserved.",
            )
            reasoning = recommendation.get("inventoryWasteReasoning")
            if reasoning:
                for action in reasoning["recommendedActions"]:
                    require(
                        set(action["evidenceIds"]) <= citation_ids,
                        f"{name}: recommended action cites inaccessible evidence.",
                    )
                    require(
                        action["requiresHumanApproval"] is True,
                        f"{name}: recommended action bypasses approval.",
                    )
                for action in reasoning["blockedActions"]:
                    require(
                        set(action["evidenceIds"]) <= citation_ids,
                        f"{name}: blocked action cites inaccessible evidence.",
                    )
                require(
                    set(reasoning["supplierCaution"]["evidenceIds"])
                    <= citation_ids,
                    f"{name}: supplier caution cites inaccessible evidence.",
                )
            hospital_reasoning = recommendation.get(
                "hospitalOperationsReasoning"
            )
            if hospital_reasoning:
                require(
                    recommendation["modelProfile"] == HOSPITAL_MODEL_PROFILE,
                    f"{name}: hospital recommendation used the wrong model profile.",
                )
                require(
                    request["purpose"] == HOSPITAL_PURPOSE,
                    f"{name}: hospital request used the wrong purpose.",
                )
                for calculation in hospital_reasoning["calculations"]:
                    require(
                        set(calculation["evidenceIds"]) <= citation_ids,
                        f"{name}: hospital calculation cites inaccessible evidence.",
                    )
                for action in hospital_reasoning["recommendedActions"]:
                    require(
                        set(action["evidenceIds"]) <= citation_ids,
                        f"{name}: hospital recommended action cites inaccessible evidence.",
                    )
                    require(
                        action["requiresHumanApproval"] is True,
                        f"{name}: hospital recommended action bypasses approval.",
                    )
                for action in hospital_reasoning["blockedActions"]:
                    require(
                        set(action["evidenceIds"]) <= citation_ids,
                        f"{name}: hospital blocked action cites inaccessible evidence.",
                    )
                require(
                    set(hospital_reasoning["partnerCaution"]["evidenceIds"])
                    <= citation_ids,
                    f"{name}: hospital partner caution cites inaccessible evidence.",
                )
                require(
                    set(
                        hospital_reasoning["clinicalBoundary"][
                            "evidenceIds"
                        ]
                    )
                    <= citation_ids,
                    f"{name}: hospital clinical boundary cites inaccessible evidence.",
                )
                for finding in hospital_reasoning["evidenceQualityFindings"]:
                    require(
                        set(finding["evidenceIds"]) <= citation_ids,
                        f"{name}: hospital evidence-quality finding cites inaccessible evidence.",
                    )
                for conflict in hospital_reasoning["conflictResolutions"]:
                    require(
                        set(conflict["evidenceIds"]) <= citation_ids,
                        f"{name}: hospital conflict resolution cites inaccessible evidence.",
                    )
                for update in hospital_reasoning["recommendationUpdates"]:
                    require(
                        update["changedByEvidenceId"] in citation_ids,
                        f"{name}: hospital recommendation update cites inaccessible trigger evidence.",
                    )
                    require(
                        set(update["evidenceIds"]) <= citation_ids,
                        f"{name}: hospital recommendation update cites inaccessible evidence.",
                    )
                service_response = hospital_reasoning["serviceRecoveryDraft"]
                if service_response:
                    require(
                        set(service_response["evidenceIds"]) <= citation_ids,
                        f"{name}: hospital service response draft cites inaccessible evidence.",
                    )
                for decision in hospital_reasoning["approvalDecisions"]:
                    require(
                        set(decision["evidenceIds"]) <= citation_ids,
                        f"{name}: hospital approval decision cites inaccessible evidence.",
                    )
                    require(
                        decision["policyReason"]
                        and decision["approverRole"]
                        and decision["approvalId"]
                        and decision["actionId"],
                        f"{name}: hospital approval decision is missing audit detail.",
                    )
                financial_impact = hospital_reasoning["financialImpact"]
                if financial_impact:
                    require(
                        set(financial_impact["evidenceIds"]) <= citation_ids,
                        f"{name}: hospital financial impact cites inaccessible evidence.",
                    )
                    require(
                        0 < financial_impact["confidence"] <= 1,
                        f"{name}: hospital financial confidence is not bounded.",
                    )
                for outcome in hospital_reasoning["expectedOutcomes"]:
                    require(
                        set(outcome["evidenceIds"]) <= citation_ids,
                        f"{name}: hospital expected outcome cites inaccessible evidence.",
                    )

        if response["status"] == "SUCCESS":
            require(response["refusal"] is None, f"{name}: success has refusal.")
            require(not response["errors"], f"{name}: success has errors.")
        elif response["status"] == "REFUSED":
            require(response["refusal"] is not None, f"{name}: refusal missing.")
            require(
                not response["facts"]
                and not response["inferences"]
                and not response["citations"]
                and response["recommendation"] is None
                and response["approval"] is None,
                f"{name}: refusal disclosed protected action content.",
            )
        else:
            require(response["errors"], f"{name}: error details missing.")

        if request["action"] == "REQUEST_HUMAN_APPROVAL" and response[
            "status"
        ] == "SUCCESS":
            require(
                response["approval"]["status"] == "PENDING",
                f"{name}: approval was not left pending for a human.",
            )
        if request["action"] == "EXECUTE_EXTERNAL_ACTION":
            require(
                response["status"] == "REFUSED"
                and response["refusal"]["code"] == "UNAUTHORIZED_ACTION",
                f"{name}: protected external execution did not fail closed.",
            )

    required_scenarios = {
        "accessible-grounded-explanation",
        "grounded-recommendation",
        "pending-human-approval",
        "inaccessible-evidence-refusal",
        "unauthorized-external-action-refusal",
        "no-qualified-model-refusal",
        "invalid-approval-request-error",
        "changed-recommendation-after-supplier-response",
        "inventory-waste-missing-expiry-caution",
        "inventory-waste-clean-stockout",
        "inventory-waste-near-expiry-markdown",
        "inventory-waste-overstock-household",
        "hospital-operations-action-plan",
        "hospital-missing-capacity-evidence",
        "hospital-clinical-refusal",
    }
    require(
        required_scenarios <= scenario_names,
        "A material Agentforce contract scenario is missing.",
    )
    for scenario in fixtures["scenarios"]:
        recommendation = scenario["response"]["recommendation"]
        if recommendation:
            has_hospital_reasoning = bool(
                recommendation.get("hospitalOperationsReasoning")
            )
            expected_profile = (
                HOSPITAL_MODEL_PROFILE
                if has_hospital_reasoning
                else RETAIL_MODEL_PROFILE
            )
            require(
                recommendation["modelProfile"] == expected_profile,
                f"{scenario['name']}: recommendation used an unexpected model profile.",
            )
    inventory_waste = next(
        scenario
        for scenario in fixtures["scenarios"]
        if scenario["name"] == "inventory-waste-missing-expiry-caution"
    )
    reasoning = inventory_waste["response"]["recommendation"][
        "inventoryWasteReasoning"
    ]
    require(
        reasoning["riskType"] == "MIXED"
        and reasoning["severity"] == "High",
        "Inventory/Waste scenario did not classify mixed high risk.",
    )
    require(
        reasoning["missingEvidence"],
        "Inventory/Waste scenario did not name missing evidence.",
    )
    require(
        reasoning["supplierCaution"]["applies"] is True,
        "Inventory/Waste scenario did not apply supplier caution.",
    )
    require(
        any(
            action["actionType"] == "BLIND_SUPPLIER_REORDER"
            for action in reasoning["blockedActions"]
        ),
        "Inventory/Waste scenario did not block blind supplier reorder.",
    )
    clean_stockout = next(
        scenario
        for scenario in fixtures["scenarios"]
        if scenario["name"] == "inventory-waste-clean-stockout"
    )
    clean_reasoning = clean_stockout["response"]["recommendation"][
        "inventoryWasteReasoning"
    ]
    require(
        clean_reasoning["riskType"] == "STOCKOUT"
        and clean_reasoning["severity"] == "Critical",
        "Clean supplier scenario did not classify critical stockout risk.",
    )
    require(
        clean_reasoning["supplierCaution"]["applies"] is False,
        "Clean supplier scenario incorrectly applied supplier caution.",
    )
    expiry_markdown = next(
        scenario
        for scenario in fixtures["scenarios"]
        if scenario["name"] == "inventory-waste-near-expiry-markdown"
    )
    expiry_reasoning = expiry_markdown["response"]["recommendation"][
        "inventoryWasteReasoning"
    ]
    require(
        expiry_reasoning["riskType"] == "WASTE"
        and expiry_reasoning["severity"] == "High",
        "Near-expiry scenario did not classify high waste risk.",
    )
    require(
        any(
            action["actionType"] == "MARKDOWN_AND_ROTATION_REVIEW"
            for action in expiry_reasoning["recommendedActions"]
        ),
        "Near-expiry scenario did not recommend markdown and rotation review.",
    )
    overstock = next(
        scenario
        for scenario in fixtures["scenarios"]
        if scenario["name"] == "inventory-waste-overstock-household"
    )
    overstock_reasoning = overstock["response"]["recommendation"][
        "inventoryWasteReasoning"
    ]
    require(
        overstock_reasoning["riskType"] == "OVERSTOCK",
        "Household scenario did not classify overstock risk.",
    )
    require(
        any(
            action["actionType"] == "ADDITIONAL_REORDER"
            for action in overstock_reasoning["blockedActions"]
        ),
        "Household overstock scenario did not block additional reorder.",
    )
    hospital_action = next(
        scenario
        for scenario in fixtures["scenarios"]
        if scenario["name"] == "hospital-operations-action-plan"
    )
    hospital_response = hospital_action["response"]
    hospital_recommendation = hospital_response["recommendation"]
    hospital_reasoning = hospital_recommendation[
        "hospitalOperationsReasoning"
    ]
    require(
        hospital_reasoning["riskType"] == "MIXED"
        and hospital_reasoning["severity"] == "High",
        "Hospital action scenario did not classify mixed high risk.",
    )
    hospital_fact_ids = {fact["factId"] for fact in hospital_response["facts"]}
    require(
        {
            "fact-hospital-complaints",
            "fact-hospital-capacity",
            "fact-hospital-pharmacy",
            "fact-hospital-partner",
            "fact-hospital-billing",
            "fact-hospital-staffing",
            "fact-hospital-clinical-refusal",
        }
        <= hospital_fact_ids,
        "Hospital action scenario is missing required grounded facts.",
    )
    hospital_inference_ids = {
        inference["inferenceId"] for inference in hospital_response["inferences"]
    }
    require(
        {
            "inference-hospital-capacity-pressure",
            "inference-hospital-cross-functional-plan",
        }
        <= hospital_inference_ids,
        "Hospital action scenario is missing required cross-functional inferences.",
    )
    require(
        0 < hospital_recommendation["confidence"] <= 1,
        "Hospital action scenario did not define a bounded confidence value.",
    )
    require(
        hospital_reasoning["assumptions"],
        "Hospital action scenario did not preserve assumptions.",
    )
    evidence_quality_types = {
        finding["findingType"]
        for finding in hospital_reasoning["evidenceQualityFindings"]
    }
    require(
        {
            "MISSING",
            "CONTRADICTORY",
            "RESTRICTED",
            "DUPLICATE",
            "LATE",
            "OUT_OF_ORDER",
            "MALFORMED",
            "LOW_CONFIDENCE",
        }
        <= evidence_quality_types,
        "Hospital action scenario is missing evidence-quality findings.",
    )
    conflict_ids = {
        conflict["conflictId"]
        for conflict in hospital_reasoning["conflictResolutions"]
    }
    require(
        {
            "conflict-patient-trust-capacity",
            "conflict-finance-stock-action-plan",
            "conflict-clinical-boundary",
        }
        <= conflict_ids,
        "Hospital action scenario is missing conflict resolutions.",
    )
    update_triggers = {
        update["changedByEvidenceId"]
        for update in hospital_reasoning["recommendationUpdates"]
    }
    require(
        {
            "a06000000000022AAA",
            "a06000000000024AAA",
            "a06000000000025AAA",
        }
        <= update_triggers,
        "Hospital action scenario is missing post-evidence recommendation updates.",
    )
    service_response = hospital_reasoning["serviceRecoveryDraft"]
    require(
        service_response
        and service_response["approvalRequired"] is True
        and service_response["privacySafe"] is True
        and "clinical" in service_response["message"].lower(),
        "Hospital action scenario is missing an approved privacy-safe service response draft.",
    )
    approval_states = {
        decision["decisionState"]
        for decision in hospital_reasoning["approvalDecisions"]
    }
    require(
        {
            "APPROVE",
            "REJECT",
            "MODIFY",
            "DEFER",
            "EXECUTE_READY",
        }
        <= approval_states,
        "Hospital action scenario is missing approval decision states.",
    )
    financial_impact = hospital_reasoning["financialImpact"]
    require(
        financial_impact is not None,
        "Hospital action scenario is missing financial impact analysis.",
    )
    require(
        {
            "duplicate_invoice",
            "claim_pending",
            "refund_request",
            "voucher_request",
            "compensation_review",
            "payment_failure",
            "revenue_risk",
        }
        <= set(financial_impact["detectedCaseTypes"]),
        "Hospital action scenario is missing financial case types.",
    )
    require(
        financial_impact["approvalRequired"] is True
        and financial_impact["exposureFormula"]
        and financial_impact["timeWindow"]
        and financial_impact["personalDataPolicy"],
        "Hospital action scenario did not define financial formula, time window, privacy policy, and approval.",
    )
    coverage = hospital_response["contextCoverage"]
    coverage_categories = coverage["evidenceCategories"]
    required_categories = {
        "complaint",
        "resource",
        "capacity",
        "partner",
        "billing",
        "stock",
        "staffing",
        "approval",
        "outcome",
    }
    require(
        required_categories <= set(coverage_categories),
        "Hospital action scenario is missing context coverage categories.",
    )
    covered_categories = {
        key
        for key, value in coverage_categories.items()
        if key == "outcome" or value.get("evidenceIds")
    }
    require(
        required_categories <= covered_categories,
        "Hospital action scenario has empty evidence coverage categories.",
    )
    primitive_records = coverage["recordIdsByPrimitive"]
    for primitive in [
        "customerAliases",
        "departments",
        "locations",
        "resources",
        "partners",
        "processes",
        "recommendations",
        "approvals",
    ]:
        require(
            primitive_records.get(primitive),
            f"Hospital action scenario is missing {primitive} primitive links.",
        )
    hospital_metrics = {
        calculation["metricKey"]
        for calculation in hospital_reasoning["calculations"]
    }
    require(
        {
            "available_room_capacity",
            "demand_pressure",
            "queue_load_against_target",
            "stock_cover_hours",
            "partner_sla_delay_minutes",
            "staff_coverage_gap",
            "financial_exposure_estimate",
        }
        <= hospital_metrics,
        "Hospital action scenario is missing required calculations.",
    )
    hospital_actions = {
        action["actionType"]
        for action in hospital_reasoning["recommendedActions"]
    }
    require(
        {
            "REQUEST_BED_CLEANING",
            "CREATE_PATIENT_SERVICE_TASK",
            "REQUEST_PORTER_SUPPORT_TASK",
            "OPEN_FRONT_DESK_QUEUE_TASK",
            "CREATE_PHARMACY_RESTOCK_REQUEST",
            "ESCALATE_LAB_VENDOR_CASE",
            "OPEN_BILLING_REVIEW",
            "REQUEST_INSURANCE_FOLLOWUP",
            "CREATE_MANAGER_REVIEW_TASK",
        }
        <= hospital_actions,
        "Hospital action scenario is missing cross-functional actions.",
    )
    require(
        hospital_reasoning["partnerCaution"]["applies"] is True,
        "Hospital action scenario did not apply partner caution.",
    )
    require(
        hospital_reasoning["clinicalBoundary"]["applies"] is True,
        "Hospital action scenario did not apply the clinical boundary.",
    )
    require(
        any(
            action["actionType"] == "CLINICAL_TRIAGE_DECISION"
            for action in hospital_reasoning["blockedActions"]
        ),
        "Hospital action scenario did not block clinical triage.",
    )
    require(
        hospital_reasoning["expectedOutcomes"],
        "Hospital action scenario did not define expected outcomes.",
    )
    hospital_outcome_metrics = {
        outcome["metricKey"] for outcome in hospital_reasoning["expectedOutcomes"]
    }
    require(
        {
            "outpatient_wait_time_minutes",
            "rooms_released",
            "pharmacy_stock_cover_hours",
            "lab_partner_acknowledgement",
            "financial_exposure_contained",
        }
        <= hospital_outcome_metrics,
        "Hospital action scenario is missing required expected outcomes.",
    )

    missing_capacity = next(
        scenario
        for scenario in fixtures["scenarios"]
        if scenario["name"] == "hospital-missing-capacity-evidence"
    )
    missing_reasoning = missing_capacity["response"]["recommendation"][
        "hospitalOperationsReasoning"
    ]
    require(
        missing_reasoning["missingEvidence"],
        "Missing capacity scenario did not name missing evidence.",
    )
    require(
        {
            "Current ready rooms",
            "Blocked discharge rooms",
            "Outpatient waiting count",
            "Available staff by role",
        }
        <= set(missing_reasoning["missingEvidence"]),
        "Missing capacity scenario did not ask for the required operational evidence.",
    )
    require(
        any(
            action["actionType"] == "CLAIM_BED_RELEASE_IMPACT"
            for action in missing_reasoning["blockedActions"]
        ),
        "Missing capacity scenario did not block unsupported bed-release claims.",
    )

    clinical_refusal = next(
        scenario
        for scenario in fixtures["scenarios"]
        if scenario["name"] == "hospital-clinical-refusal"
    )
    clinical_reasoning = clinical_refusal["response"]["recommendation"][
        "hospitalOperationsReasoning"
    ]
    require(
        clinical_reasoning["riskType"] == "CLINICAL_REFUSAL",
        "Clinical refusal scenario did not classify clinical refusal risk.",
    )
    require(
        any(
            action["actionType"] == "DECIDE_TREATMENT_PRIORITY"
            for action in clinical_reasoning["blockedActions"]
        ),
        "Clinical refusal scenario did not block treatment priority decisions.",
    )
    require(
        clinical_reasoning["clinicalBoundary"]["applies"] is True,
        "Clinical refusal scenario did not apply the clinical boundary.",
    )
    print(
        "Agentforce action contract is valid "
        f"({len(fixtures['actionCatalog'])} actions, "
        f"{len(fixtures['scenarios'])} scenarios)."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
