#!/usr/bin/env python3

import argparse
import base64
import json
import shutil
import subprocess
import sys
import tempfile
import time
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable


ROOT = Path(__file__).resolve().parents[1]
MODEL_RUNTIME = ROOT / "intelligence" / "model-gateway" / "runtime"
MULESOFT_RUNTIME = ROOT / "mulesoft"
for runtime_path in (MODEL_RUNTIME, MULESOFT_RUNTIME):
    if str(runtime_path) not in sys.path:
        sys.path.insert(0, str(runtime_path))

from hfs_model_gateway import (  # noqa: E402
    DeterministicRouter,
    MockAlphaAdapter,
    MockBetaAdapter,
    ModelGateway,
    ModelGatewayContract,
)
from mock_runtime import build_default_api  # noqa: E402


CONFIG_PATH = ROOT / "demo" / "harness-config-v1.json"
RESET_SCRIPT = ROOT / "scripts" / "apex" / "reset_demo.apex"
SEED_SCRIPT = ROOT / "scripts" / "apex" / "seed_demo.apex"
VERIFY_CONTEXT_SCRIPT = ROOT / "scripts" / "apex" / "verify_demo_context.apex"
ENSURE_PERMISSIONS_SCRIPT = (
    ROOT / "scripts" / "apex" / "ensure_demo_permissions.apex"
)
PREPARE_CONNECTED_SCRIPT = (
    ROOT / "scripts" / "apex" / "prepare_connected_demo.apex"
)
HOSPITAL_PURPOSE = "RESOLVE_HOSPITAL_OPERATION_RISK"
HOSPITAL_ACTION_PURPOSE = "EXECUTE_APPROVED_HOSPITAL_ACTION"
HOSPITAL_OUTCOME_PURPOSE = "CAPTURE_APPROVED_HOSPITAL_OUTCOME"
HOSPITAL_RECOMMENDATION_TYPE = "NORTH_STAR_HOSPITAL_RECOVERY_PLAN"
HOSPITAL_PROPOSED_ACTION_TYPE = "APPROVE_HOSPITAL_RECOVERY_ACTIONS"
HOSPITAL_SLACK_ACTION_TYPE = "SEND_SLACK_ALERT"
HOSPITAL_WHATSAPP_ACTION_TYPE = "SEND_WHATSAPP_ALERT"
HOSPITAL_CHANNEL_ACTION_TYPES = {
    HOSPITAL_SLACK_ACTION_TYPE,
    HOSPITAL_WHATSAPP_ACTION_TYPE,
}
HOSPITAL_TASK_ACTIONS = [
    {
        "key": "action-north-star-hospital-task-service-001",
        "actionType": "CREATE_PATIENT_SERVICE_TASK",
        "targetEntityKey": "DEPT-OUTPATIENT-RECEPTION",
        "ownerRoleAlias": "role:patient-experience-lead",
        "escalationRoleAlias": "role:operations-manager",
        "priorityRank": 1,
        "urgency": "HIGH",
        "riskClass": "PATIENT_TRUST",
        "serviceWindowMinutes": 20,
        "missedEscalationMinutes": 10,
    },
    {
        "key": "action-north-star-hospital-task-bed-cleaning-001",
        "actionType": "REQUEST_BED_CLEANING",
        "targetEntityKey": "RESOURCE-WARD-A3-DISCHARGE-ROOMS",
        "ownerRoleAlias": "role:bed-manager",
        "escalationRoleAlias": "role:operations-manager",
        "priorityRank": 2,
        "urgency": "HIGH",
        "riskClass": "CAPACITY",
        "serviceWindowMinutes": 30,
        "missedEscalationMinutes": 15,
    },
    {
        "key": "action-north-star-hospital-task-pharmacy-001",
        "actionType": "CREATE_PHARMACY_RESTOCK_REQUEST",
        "targetEntityKey": "RESOURCE-PHARMACY-IV-KITS",
        "ownerRoleAlias": "role:pharmacy-lead",
        "escalationRoleAlias": "role:duty-manager",
        "priorityRank": 3,
        "urgency": "MEDIUM_HIGH",
        "riskClass": "STOCK",
        "serviceWindowMinutes": 45,
        "missedEscalationMinutes": 25,
    },
    {
        "key": "action-north-star-hospital-task-lab-001",
        "actionType": "ESCALATE_LAB_VENDOR_CASE",
        "targetEntityKey": "PARTNER-ISLAND-DIAGNOSTICS",
        "ownerRoleAlias": "role:lab-coordination-lead",
        "escalationRoleAlias": "role:partner-manager",
        "priorityRank": 4,
        "urgency": "MEDIUM_HIGH",
        "riskClass": "PARTNER_SLA",
        "serviceWindowMinutes": 20,
        "missedEscalationMinutes": 10,
    },
    {
        "key": "action-north-star-hospital-task-billing-001",
        "actionType": "OPEN_BILLING_REVIEW",
        "targetEntityKey": "PROCESS-BILLING-INSURANCE-REVIEW",
        "ownerRoleAlias": "role:billing-supervisor",
        "escalationRoleAlias": "role:finance-manager",
        "priorityRank": 5,
        "urgency": "MEDIUM",
        "riskClass": "FINANCIAL_EXPOSURE",
        "serviceWindowMinutes": 60,
        "missedEscalationMinutes": 30,
    },
]
HOSPITAL_TASK_OUTCOME_TEMPLATES = {
    "CREATE_PATIENT_SERVICE_TASK": {
        "outcomeType": "WAIT_TIME_REDUCED",
        "metricKey": "outpatient_wait_time_reduced_minutes",
        "metricValue": 18,
        "sourceSystem": "salesforce-task",
        "sourceUri": "urn:hfs:source:hospital:patient-service-task",
        "summary": (
            "Patient-service task acknowledged and outpatient wait time "
            "reduced by 18 minutes."
        ),
    },
    "REQUEST_BED_CLEANING": {
        "outcomeType": "DISCHARGE_ROOMS_RELEASED",
        "metricKey": "rooms_released",
        "metricValue": 3,
        "sourceSystem": "salesforce-task",
        "sourceUri": "urn:hfs:source:hospital:bed-cleaning-task",
        "summary": (
            "Discharge-room cleaning task acknowledged and three rooms "
            "released for operations use."
        ),
    },
    "CREATE_PHARMACY_RESTOCK_REQUEST": {
        "outcomeType": "PHARMACY_STOCKOUT_AVOIDED",
        "metricKey": "stockout_avoided",
        "metricValue": 1,
        "sourceSystem": "salesforce-task",
        "sourceUri": "urn:hfs:source:hospital:pharmacy-restock-task",
        "summary": (
            "Pharmacy restock task acknowledged and the critical-stockout "
            "risk was avoided."
        ),
    },
    "ESCALATE_LAB_VENDOR_CASE": {
        "outcomeType": "LAB_PARTNER_SLA_ESCALATED",
        "metricKey": "partner_sla_escalated",
        "metricValue": 1,
        "sourceSystem": "salesforce-task",
        "sourceUri": "urn:hfs:source:hospital:lab-vendor-task",
        "summary": (
            "Lab vendor escalation task acknowledged and SLA follow-up "
            "started."
        ),
    },
    "OPEN_BILLING_REVIEW": {
        "outcomeType": "BILLING_REVIEW_OPENED",
        "metricKey": "billing_issue_routed",
        "metricValue": 1,
        "sourceSystem": "salesforce-task",
        "sourceUri": "urn:hfs:source:hospital:billing-review-task",
        "summary": (
            "Billing review task acknowledged and duplicate invoice/insurer "
            "follow-up routed."
        ),
    },
}
HOSPITAL_APPROVAL_POLICY_KEY = "north-star-hospital-manager-approval-v1"
CLINICAL_DECISION_REFUSED = "CLINICAL_DECISION_REFUSED"


class HarnessFailure(RuntimeError):
    pass


def apex_string(value: Any) -> str:
    text = str(value)
    return (
        text.replace("\\", "\\\\")
        .replace("'", "\\'")
        .replace("\r", "\\r")
        .replace("\n", "\\n")
    )


class CommandRunner:
    def resolve_command(self, command: list[str]) -> list[str]:
        executable = shutil.which(command[0])
        if executable is None:
            return command
        return [executable, *command[1:]]

    def run(self, command: list[str]) -> dict[str, Any]:
        completed = subprocess.run(
            self.resolve_command(command),
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        if completed.returncode != 0:
            detail_parts = []
            if completed.stdout.strip():
                detail_parts.append(f"stdout: {completed.stdout.strip()[-2000:]}")
            if completed.stderr.strip():
                detail_parts.append(f"stderr: {completed.stderr.strip()[-2000:]}")
            detail = f" {' '.join(detail_parts)}" if detail_parts else ""
            raise HarnessFailure(
                f"Command failed ({' '.join(command[:3])}) "
                f"with exit code {completed.returncode}.{detail}"
            )
        if "--json" not in command:
            return {"stdout": completed.stdout.strip()}
        try:
            payload = json.loads(completed.stdout)
        except json.JSONDecodeError as error:
            raise HarnessFailure(
                f"Command returned invalid JSON ({' '.join(command)})."
            ) from error
        if payload.get("status") not in (None, 0):
            raise HarnessFailure(
                f"Command reported failure ({' '.join(command)})."
            )
        return payload


class DemoHarness:
    def __init__(
        self,
        target_org: str,
        runner: CommandRunner | None = None,
        config: dict[str, Any] | None = None,
    ) -> None:
        self.target_org = target_org
        self.runner = runner or CommandRunner()
        self.config = config or json.loads(CONFIG_PATH.read_text())
        self.steps: list[dict[str, Any]] = []

    def step(self, name: str, operation: Callable[[], Any]) -> Any:
        started = time.monotonic()
        try:
            details = operation()
        except Exception as error:
            self.steps.append(
                {
                    "name": name,
                    "status": "failed",
                    "durationMs": round((time.monotonic() - started) * 1000),
                    "error": str(error),
                }
            )
            raise
        self.steps.append(
            {
                "name": name,
                "status": "passed",
                "durationMs": round((time.monotonic() - started) * 1000),
                "details": details,
            }
        )
        return details

    def validate_tools(self) -> dict[str, str]:
        required = ("node", "npm", "python3", "sf")
        missing = [tool for tool in required if shutil.which(tool) is None]
        if missing:
            raise HarnessFailure(
                f"Missing required command(s): {', '.join(missing)}"
            )
        node_version = self.runner.run(
            ["node", "-p", "process.versions.node"]
        )["stdout"]
        if int(node_version.split(".", 1)[0]) < 20:
            raise HarnessFailure("Node.js 20 or newer is required.")
        if sys.version_info < (3, 12):
            raise HarnessFailure("Python 3.12 or newer is required.")
        return {"node": node_version, "python": sys.version.split()[0]}

    def validate_org(self) -> dict[str, Any]:
        payload = self.runner.run(
            ["sf", "org", "display", "--target-org", self.target_org, "--json"]
        )
        if not payload.get("result"):
            raise HarnessFailure("Salesforce org display returned no result.")
        return {"targetOrg": self.target_org, "connected": True}

    def validate_local_contracts(self) -> dict[str, int]:
        commands = (["npm", "run", "check"],)
        for command in commands:
            self.runner.run(list(command))
        return {"checks": len(commands)}

    def run_apex(self, script: Path) -> dict[str, Any]:
        self.runner.run(
            [
                "sf",
                "apex",
                "run",
                "--file",
                str(script),
                "--target-org",
                self.target_org,
                "--json",
            ]
        )
        return {"script": str(script.relative_to(ROOT))}

    def run_apex_source(
        self,
        source: str,
        marker: str,
    ) -> dict[str, Any]:
        temporary_path: Path | None = None
        try:
            with tempfile.NamedTemporaryFile(
                mode="w",
                suffix=".apex",
                prefix="hfs-connected-",
                delete=False,
            ) as temporary:
                temporary.write(source)
                temporary_path = Path(temporary.name)
            payload = self.runner.run(
                [
                    "sf",
                    "apex",
                    "run",
                    "--file",
                    str(temporary_path),
                    "--target-org",
                    self.target_org,
                    "--json",
                ]
            )
            logs = payload.get("result", {}).get("logs", "")
            needle = f"DEBUG|{marker}:"
            for line in logs.splitlines():
                if needle not in line:
                    continue
                encoded = line.split(needle, 1)[1].strip()
                return json.loads(base64.b64decode(encoded).decode("utf-8"))
            raise HarnessFailure(f"Apex marker {marker} was not returned.")
        finally:
            if temporary_path is not None:
                temporary_path.unlink(missing_ok=True)

    def query_count(self, object_api_name: str) -> int:
        tenant_key = self.config["tenantKey"].replace("'", "\\'")
        query = (
            f"SELECT COUNT(Id) total FROM {object_api_name} "
            f"WHERE Tenant_Key__c = '{tenant_key}'"
        )
        payload = self.runner.run(
            [
                "sf",
                "data",
                "query",
                "--query",
                query,
                "--target-org",
                self.target_org,
                "--json",
            ]
        )
        records = payload.get("result", {}).get("records", [])
        if not records or "total" not in records[0]:
            raise HarnessFailure(
                f"Count query returned no total for {object_api_name}."
            )
        return int(records[0]["total"])

    def query_identifier(self, object_api_name: str, external_key: str) -> str:
        safe_key = external_key.replace("'", "\\'")
        query = (
            f"SELECT Id FROM {object_api_name} "
            f"WHERE External_Key__c = '{safe_key}' LIMIT 1"
        )
        payload = self.runner.run(
            [
                "sf",
                "data",
                "query",
                "--query",
                query,
                "--target-org",
                self.target_org,
                "--json",
            ]
        )
        records = payload.get("result", {}).get("records", [])
        if len(records) != 1 or not records[0].get("Id"):
            raise HarnessFailure(
                f"Expected one {object_api_name} record for {external_key}."
            )
        return str(records[0]["Id"])

    def query_one(self, query: str, label: str) -> dict[str, Any]:
        payload = self.runner.run(
            [
                "sf",
                "data",
                "query",
                "--query",
                query,
                "--target-org",
                self.target_org,
                "--json",
            ]
        )
        records = payload.get("result", {}).get("records", [])
        if len(records) != 1:
            raise HarnessFailure(f"Expected one record for {label}.")
        return {
            key: value
            for key, value in records[0].items()
            if key != "attributes"
        }

    def connected_source(self) -> dict[str, Any]:
        identifiers = self.config["identifiers"]
        work_key = identifiers["workItemExternalKey"].replace("'", "\\'")
        work_item = self.query_one(
            "SELECT Id, Primary_Entity__c, Trigger_Event__c "
            "FROM HFS_Work_Item__c "
            f"WHERE External_Key__c = '{work_key}' LIMIT 1",
            "connected work item",
        )
        evidence = self.query_one(
            "SELECT Id, Content_Hash__c "
            "FROM HFS_Evidence__c "
            f"WHERE Work_Item__c = '{work_item['Id']}' "
            "ORDER BY Captured_At__c ASC LIMIT 1",
            "connected evidence",
        )
        target_keys = {
            task["targetEntityKey"] for task in HOSPITAL_TASK_ACTIONS
        }
        target_entity_ids = {
            target_key: self.query_identifier("HFS_Entity__c", target_key)
            for target_key in sorted(target_keys)
        }
        return {
            "workItemId": work_item["Id"],
            "subjectEntityId": work_item["Primary_Entity__c"],
            "triggerEventId": work_item["Trigger_Event__c"],
            "evidenceId": evidence["Id"],
            "contentHash": evidence["Content_Hash__c"],
            "targetEntityIds": target_entity_ids,
        }

    def run_model_gateway(self, source: dict[str, Any]) -> dict[str, Any]:
        contract = ModelGatewayContract()
        fixture = contract.fixture
        profile = fixture["profiles"][0]
        deployments = fixture["deployments"]
        policy = fixture["policies"][0]

        def build_gateway(output: dict[str, Any]) -> ModelGateway:
            router = DeterministicRouter(
                contract=contract,
                profile=profile,
                deployments=deployments,
                policy=policy,
            )
            alpha = MockAlphaAdapter(output)
            beta = MockBetaAdapter(output)
            return ModelGateway(
                contract=contract,
                router=router,
                adapters={
                    alpha.adapter_key: alpha,
                    beta.adapter_key: beta,
                },
            )

        routing_request = deepcopy(fixture["routingRequests"]["primary"])
        generation_request = deepcopy(fixture["generateRequest"])
        output = deepcopy(fixture["normalizedResponses"][0]["output"])
        
        for value in (routing_request, generation_request):
            value["tenantKey"] = self.config["tenantKey"]
            value["correlationId"] = self.config["correlationId"]
            value["purpose"] = HOSPITAL_PURPOSE
        
        generation_request["context"]["evidenceIds"] = [
            source["evidenceId"]
        ]
        generation_request["context"]["sourceContentHashes"] = [
            source["contentHash"]
        ]
        output["evidenceIds"] = [source["evidenceId"]]

        success = build_gateway(output).generate(
            routing_request,
            generation_request,
        )
        if success.response is None:
            raise HarnessFailure("The qualified model path failed closed.")

        restricted_routing = deepcopy(routing_request)
        restricted_generation = deepcopy(generation_request)
        restricted_routing["dataClassification"] = "RESTRICTED"
        restricted_generation["context"]["dataClassification"] = "RESTRICTED"
        restricted = build_gateway(output).generate(
            restricted_routing,
            restricted_generation,
        )
        if (
            restricted.response is not None
            or restricted.decision["decision"] != "NO_QUALIFIED_DEPLOYMENT"
        ):
            raise HarnessFailure(
                "The unqualified model path did not fail closed."
            )

        return {
            "output": success.response["output"],
            "invocationId": success.response["invocationId"],
            "profileKey": success.response["profileKey"],
            "profileVersion": success.response["profileVersion"],
            "deploymentKey": success.response["deploymentKey"],
            "deploymentVersion": success.response["deploymentVersion"],
            "policyKey": success.audit["policyKey"],
            "policyVersion": success.audit["policyVersion"],
            "restrictedDecision": restricted.decision["decision"],
            "restrictedAuditStatus": restricted.audit["status"],
        }

    def persist_model_recommendation(
        self,
        source: dict[str, Any],
        model: dict[str, Any],
    ) -> dict[str, Any]:
        output = model["output"]
        recommendation_key = self.config["identifiers"][
            "recommendationExternalKey"
        ]
        script = f"""
HFS_RecommendationCommand command = new HFS_RecommendationCommand();
command.contractVersion = HFS_ServiceContract.VERSION;
command.correlationId = '{apex_string(self.config["correlationId"])}';
command.tenantKey = '{apex_string(self.config["tenantKey"])}';
command.purpose = '{HOSPITAL_PURPOSE}';
command.externalKey = '{apex_string(recommendation_key)}';
command.workItemId = '{apex_string(source["workItemId"])}';
command.subjectEntityId = '{apex_string(source["subjectEntityId"])}';
command.primaryEvidenceId = '{apex_string(source["evidenceId"])}';
command.recommendationType = '{HOSPITAL_RECOMMENDATION_TYPE}';
command.proposedActionType = '{HOSPITAL_PROPOSED_ACTION_TYPE}';
command.rationale = '{apex_string(output["recommendation"])}';
command.confidence = {output["confidence"]};
command.modelProfile = '{apex_string(model["profileKey"])}';
command.modelInvocationId = '{apex_string(model["invocationId"])}';
HFS_CommandResult stored = new HFS_RelationshipServiceImpl()
  .storeRecommendation(command);
System.assertEquals(true, stored.success, JSON.serialize(stored.errors));
Map<String, Object> result = new Map<String, Object>{{
  'recommendationId' => stored.recordId,
  'status' => stored.status,
  'modelInvocationId' => command.modelInvocationId
}};
System.debug(
  'HFS_CP3_RECOMMENDATION:' +
  EncodingUtil.base64Encode(Blob.valueOf(JSON.serialize(result)))
);
"""
        return self.run_apex_source(script, "HFS_CP3_RECOMMENDATION")

    def run_agentforce(
        self,
        source: dict[str, Any],
        recommendation: dict[str, Any],
        model: dict[str, Any],
    ) -> dict[str, Any]:
        policy_key = HOSPITAL_APPROVAL_POLICY_KEY
        script = f"""
HFS_AgentActionRequest explainRequest = new HFS_AgentActionRequest();
explainRequest.contractVersion = HFS_ServiceContract.VERSION;
explainRequest.action = HFS_AgentActionService.EXPLAIN;
explainRequest.tenantKey = '{apex_string(self.config["tenantKey"])}';
explainRequest.correlationId = '{apex_string(self.config["correlationId"])}';
explainRequest.purpose = '{HOSPITAL_PURPOSE}';
explainRequest.workItemId = '{apex_string(source["workItemId"])}';
HFS_AgentActionResult explanation = HFS_AgentExplainAction.invoke(
  new List<HFS_AgentActionRequest>{{ explainRequest }}
)[0];
System.assertEquals('SUCCESS', explanation.status, explanation.responseJson);

HFS_Work_Item__c inaccessibleWork = new HFS_Work_Item__c(
  External_Key__c = 'work-demo-inaccessible-check',
  Tenant_Key__c = explainRequest.tenantKey,
  Primary_Entity__c = '{apex_string(source["subjectEntityId"])}',
  Trigger_Event__c = '{apex_string(source["triggerEventId"])}',
  Status__c = 'AWAITING_APPROVAL',
  Priority__c = 'HIGH',
  Summary__c = 'Transient inaccessible-evidence verification.'
);
insert as user inaccessibleWork;
HFS_AgentActionRequest inaccessibleRequest = new HFS_AgentActionRequest();
inaccessibleRequest.contractVersion = HFS_ServiceContract.VERSION;
inaccessibleRequest.action = HFS_AgentActionService.EXPLAIN;
inaccessibleRequest.tenantKey = explainRequest.tenantKey;
inaccessibleRequest.correlationId = explainRequest.correlationId;
inaccessibleRequest.purpose = explainRequest.purpose;
inaccessibleRequest.workItemId = inaccessibleWork.Id;
HFS_AgentActionResult inaccessible = HFS_AgentExplainAction.invoke(
  new List<HFS_AgentActionRequest>{{ inaccessibleRequest }}
)[0];
System.assertEquals('REFUSED', inaccessible.status, inaccessible.responseJson);
System.assertEquals('INACCESSIBLE_EVIDENCE', inaccessible.refusalCode);
delete as user inaccessibleWork;

HFS_AgentActionRequest recommendationRequest = new HFS_AgentActionRequest();
recommendationRequest.contractVersion = HFS_ServiceContract.VERSION;
recommendationRequest.action = HFS_AgentActionService.RECOMMEND;
recommendationRequest.tenantKey = explainRequest.tenantKey;
recommendationRequest.correlationId = explainRequest.correlationId;
recommendationRequest.purpose = explainRequest.purpose;
recommendationRequest.workItemId = explainRequest.workItemId;
recommendationRequest.modelProfile = '{apex_string(model["profileKey"])}';
HFS_AgentActionResult recommendationResult =
  HFS_AgentRecommendationAction.invoke(
    new List<HFS_AgentActionRequest>{{ recommendationRequest }}
  )[0];
System.assertEquals(
  'SUCCESS',
  recommendationResult.status,
  recommendationResult.responseJson
);
Map<String, Object> recommendationResponse =
  (Map<String, Object>) JSON.deserializeUntyped(
    recommendationResult.responseJson
  );
Map<String, Object> recommendationBody =
  (Map<String, Object>) recommendationResponse.get('recommendation');
System.assert(
  ((List<Object>) recommendationBody.get('evidenceIds')).size() >= 7,
  recommendationResult.responseJson
);
Map<String, Object> recommendationCoverage =
  (Map<String, Object>) recommendationResponse.get('contextCoverage');
Map<String, Object> recommendationCategories =
  (Map<String, Object>) recommendationCoverage.get('evidenceCategories');
List<String> requiredCategories = new List<String>{{
  'complaint',
  'resource',
  'capacity',
  'partner',
  'billing',
  'stock',
  'staffing',
  'approval'
}};
for (String category : requiredCategories) {{
  Map<String, Object> categoryCoverage =
    (Map<String, Object>) recommendationCategories.get(category);
  System.assertEquals(
    true,
    (Boolean) categoryCoverage.get('applies'),
    category + ' coverage is missing'
  );
}}
Map<String, Object> preOutcomeCoverage =
  (Map<String, Object>) recommendationCategories.get('outcome');
System.assertEquals(false, (Boolean) preOutcomeCoverage.get('applies'));

HFS_AgentActionRequest approvalRequest = new HFS_AgentActionRequest();
approvalRequest.contractVersion = HFS_ServiceContract.VERSION;
approvalRequest.action = HFS_AgentActionService.APPROVE;
approvalRequest.tenantKey = explainRequest.tenantKey;
approvalRequest.correlationId = explainRequest.correlationId;
approvalRequest.purpose = explainRequest.purpose;
approvalRequest.workItemId = explainRequest.workItemId;
approvalRequest.recommendationId =
  '{apex_string(recommendation["recommendationId"])}';
approvalRequest.approvalPolicyKey = '{policy_key}';
HFS_AgentActionResult approvalResult =
  HFS_AgentApprovalRequestAction.invoke(
    new List<HFS_AgentActionRequest>{{ approvalRequest }}
  )[0];
System.assertEquals('SUCCESS', approvalResult.status, approvalResult.responseJson);
Map<String, Object> result = new Map<String, Object>{{
  'explanationStatus' => explanation.status,
  'citationEvidenceIds' => explanation.citationEvidenceIds,
  'inaccessibleStatus' => inaccessible.status,
  'inaccessibleRefusalCode' => inaccessible.refusalCode,
  'recommendationStatus' => recommendationResult.status,
  'recommendationEvidenceCount' =>
    ((List<Object>) recommendationBody.get('evidenceIds')).size(),
  'coveredCategories' => requiredCategories,
  'modelInvocationId' => recommendationResult.modelInvocationId,
  'approvalStatus' => approvalResult.status,
  'approvalId' => approvalResult.approvalId,
  'externalActionExecuted' => approvalResult.externalActionExecuted
}};
System.debug(
  'HFS_CP3_AGENTFORCE:' +
  EncodingUtil.base64Encode(Blob.valueOf(JSON.serialize(result)))
);
"""
        result = self.run_apex_source(script, "HFS_CP3_AGENTFORCE")
        if (
            result["modelInvocationId"] != model["invocationId"]
            or result["externalActionExecuted"] is not False
            or result["inaccessibleRefusalCode"]
            != "INACCESSIBLE_EVIDENCE"
        ):
            raise HarnessFailure(
                "Agentforce grounding, refusal, or execution invariants failed."
            )
        return result

    def verify_clinical_refusal(
        self,
        source: dict[str, Any],
        model: dict[str, Any],
    ) -> dict[str, Any]:
        clinical_evidence_id = self.query_identifier(
            "HFS_Evidence__c",
            "evidence-clinical-refusal-hospital-001",
        )
        clinical_key = "recommendation-demo-clinical-refused"
        script = f"""
HFS_RecommendationCommand command = new HFS_RecommendationCommand();
command.contractVersion = HFS_ServiceContract.VERSION;
command.correlationId = '{apex_string(self.config["correlationId"])}';
command.tenantKey = '{apex_string(self.config["tenantKey"])}';
command.purpose = '{HOSPITAL_PURPOSE}';
command.externalKey = '{clinical_key}';
command.workItemId = '{apex_string(source["workItemId"])}';
command.subjectEntityId = '{apex_string(source["subjectEntityId"])}';
command.primaryEvidenceId = '{apex_string(clinical_evidence_id)}';
command.recommendationType = 'CLINICAL_DECISION_REQUEST';
command.proposedActionType = 'DECIDE_TREATMENT_PRIORITY';
command.rationale = 'Decide which patient should receive treatment first.';
command.confidence = 0.91;
command.modelProfile = '{apex_string(model["profileKey"])}';
command.modelInvocationId = '{apex_string(model["invocationId"])}';
HFS_CommandResult refused = new HFS_RelationshipServiceImpl()
  .storeRecommendation(command);
System.assertEquals(false, refused.success);
System.assertEquals(
  HFS_ServiceContract.CLINICAL_DECISION_REFUSED,
  refused.errors[0].code
);
Integer storedCount = [
  SELECT COUNT()
  FROM HFS_Recommendation__c
  WHERE External_Key__c = '{clinical_key}'
];
System.assertEquals(0, storedCount);
Map<String, Object> result = new Map<String, Object>{{
  'status' => 'REFUSED',
  'errorCode' => refused.errors[0].code,
  'storedRecommendationCount' => storedCount,
  'clinicalEvidenceId' => '{apex_string(clinical_evidence_id)}'
}};
System.debug(
  'HFS_CP3_CLINICAL_REFUSAL:' +
  EncodingUtil.base64Encode(Blob.valueOf(JSON.serialize(result)))
);
"""
        result = self.run_apex_source(script, "HFS_CP3_CLINICAL_REFUSAL")
        if (
            result["errorCode"] != CLINICAL_DECISION_REFUSED
            or result["storedRecommendationCount"] != 0
        ):
            raise HarnessFailure(
                "Clinical-decision refusal did not fail closed."
            )
        return result

    def approve_and_log_action(
        self,
        source: dict[str, Any],
        recommendation: dict[str, Any],
        agentforce: dict[str, Any],
    ) -> dict[str, Any]:
        action_key = self.config["identifiers"]["actionExternalKey"]
        whatsapp_action_key = self.config["identifiers"][
            "whatsappActionExternalKey"
        ]
        task_blocks = []
        task_maps = []
        for index, task in enumerate(HOSPITAL_TASK_ACTIONS):
            command_name = f"taskCommand{index}"
            result_name = f"taskLogged{index}"
            target_entity_id = source["targetEntityIds"][
                task["targetEntityKey"]
            ]
            task_key = task["key"]
            task_type = task["actionType"]
            owner_role_alias = task["ownerRoleAlias"]
            escalation_role_alias = task["escalationRoleAlias"]
            priority_rank = task["priorityRank"]
            urgency = task["urgency"]
            risk_class = task["riskClass"]
            service_window_minutes = task["serviceWindowMinutes"]
            missed_escalation_minutes = task["missedEscalationMinutes"]
            task_blocks.append(
                f"""
HFS_ActionCommand {command_name} = new HFS_ActionCommand();
{command_name}.contractVersion = HFS_ServiceContract.VERSION;
{command_name}.correlationId = actionCommand.correlationId;
{command_name}.tenantKey = actionCommand.tenantKey;
{command_name}.purpose = actionCommand.purpose;
{command_name}.externalKey = '{apex_string(task_key)}';
{command_name}.idempotencyKey = '{apex_string(task_key)}-v1';
{command_name}.recommendationId = actionCommand.recommendationId;
{command_name}.approvalId = actionCommand.approvalId;
{command_name}.targetEntityId = '{apex_string(target_entity_id)}';
{command_name}.actionType = '{apex_string(task_type)}';
HFS_CommandResult {result_name} = service.logAction({command_name});
System.assertEquals(
  true,
  {result_name}.success,
  JSON.serialize({result_name}.errors)
);
System.assertEquals('PENDING', {result_name}.status);
"""
            )
            task_maps.append(
                f"""
  new Map<String, Object>{{
    'channel' => 'task',
    'actionType' => {command_name}.actionType,
    'sourceSystem' => 'salesforce-action',
    'actionId' => {result_name}.recordId,
    'actionStatus' => {result_name}.status,
    'actionExternalKey' => {command_name}.externalKey,
    'actionIdempotencyKey' => {command_name}.idempotencyKey,
    'targetEntityId' => {command_name}.targetEntityId,
    'ownerRoleAlias' => '{apex_string(owner_role_alias)}',
    'escalationRoleAlias' => '{apex_string(escalation_role_alias)}',
    'priorityRank' => {priority_rank},
    'urgency' => '{apex_string(urgency)}',
    'riskClass' => '{apex_string(risk_class)}',
    'serviceWindowMinutes' => {service_window_minutes},
    'missedEscalationMinutes' => {missed_escalation_minutes},
    'approvalRequired' => true,
    'escalatesBeforeWindowLoss' => true
  }}"""
            )
        task_action_script = "\n".join(task_blocks)
        task_actions_literal = ",\n".join(task_maps)
        script = f"""
HFS_ActionCommand actionCommand = new HFS_ActionCommand();
actionCommand.contractVersion = HFS_ServiceContract.VERSION;
actionCommand.correlationId = '{apex_string(self.config["correlationId"])}';
actionCommand.tenantKey = '{apex_string(self.config["tenantKey"])}';
actionCommand.purpose = '{HOSPITAL_ACTION_PURPOSE}';
actionCommand.externalKey = '{apex_string(action_key)}';
actionCommand.idempotencyKey = '{apex_string(action_key)}-v1';
actionCommand.recommendationId =
  '{apex_string(recommendation["recommendationId"])}';
actionCommand.approvalId = '{apex_string(agentforce["approvalId"])}';
actionCommand.targetEntityId = '{apex_string(source["subjectEntityId"])}';
actionCommand.actionType = '{HOSPITAL_SLACK_ACTION_TYPE}';
HFS_RelationshipService service = new HFS_RelationshipServiceImpl();
HFS_CommandResult blocked = service.logAction(actionCommand);
System.assertEquals(false, blocked.success);
System.assertEquals(
  HFS_ServiceContract.INVALID_STATE,
  blocked.errors[0].code
);

HFS_ApprovalDecisionCommand decision = new HFS_ApprovalDecisionCommand();
decision.contractVersion = HFS_ServiceContract.VERSION;
decision.correlationId = actionCommand.correlationId;
decision.tenantKey = actionCommand.tenantKey;
decision.purpose = 'HUMAN_REVIEW';
decision.approvalId = actionCommand.approvalId;
decision.decisionStatus = 'APPROVED';
decision.decisionNotes = 'Connected demo human approval.';
HFS_CommandResult approved = service.decideApproval(decision);
System.assertEquals(true, approved.success, JSON.serialize(approved.errors));

HFS_CommandResult logged = service.logAction(actionCommand);
System.assertEquals(true, logged.success, JSON.serialize(logged.errors));
System.assertEquals('PENDING', logged.status);

HFS_ActionCommand whatsappCommand = new HFS_ActionCommand();
whatsappCommand.contractVersion = HFS_ServiceContract.VERSION;
whatsappCommand.correlationId = actionCommand.correlationId;
whatsappCommand.tenantKey = actionCommand.tenantKey;
whatsappCommand.purpose = actionCommand.purpose;
whatsappCommand.externalKey = '{apex_string(whatsapp_action_key)}';
whatsappCommand.idempotencyKey = '{apex_string(whatsapp_action_key)}-v1';
whatsappCommand.recommendationId = actionCommand.recommendationId;
whatsappCommand.approvalId = actionCommand.approvalId;
whatsappCommand.targetEntityId = actionCommand.targetEntityId;
whatsappCommand.actionType = '{HOSPITAL_WHATSAPP_ACTION_TYPE}';
HFS_CommandResult whatsappLogged = service.logAction(whatsappCommand);
System.assertEquals(
  true,
  whatsappLogged.success,
  JSON.serialize(whatsappLogged.errors)
);
System.assertEquals('PENDING', whatsappLogged.status);

{task_action_script}

List<Object> channelActions = new List<Object>{{
  new Map<String, Object>{{
    'channel' => 'slack',
    'actionType' => actionCommand.actionType,
    'sourceSystem' => 'slack',
    'actionId' => logged.recordId,
    'actionStatus' => logged.status,
    'actionExternalKey' => actionCommand.externalKey,
    'actionIdempotencyKey' => actionCommand.idempotencyKey
  }},
  new Map<String, Object>{{
    'channel' => 'whatsapp',
    'actionType' => whatsappCommand.actionType,
    'sourceSystem' => 'whatsapp',
    'actionId' => whatsappLogged.recordId,
    'actionStatus' => whatsappLogged.status,
    'actionExternalKey' => whatsappCommand.externalKey,
    'actionIdempotencyKey' => whatsappCommand.idempotencyKey
  }}
}};
List<Object> taskActions = new List<Object>{{
{task_actions_literal}
}};
List<Object> actions = new List<Object>();
actions.addAll(channelActions);
actions.addAll(taskActions);
Map<String, Object> result = new Map<String, Object>{{
  'blockedErrorCode' => blocked.errors[0].code,
  'approvalId' => approved.recordId,
  'approvalStatus' => approved.status,
  'actionId' => logged.recordId,
  'actionStatus' => logged.status,
  'actionExternalKey' => actionCommand.externalKey,
  'actionIdempotencyKey' => actionCommand.idempotencyKey,
  'channelActions' => channelActions,
  'taskActions' => taskActions,
  'actions' => actions
}};
System.debug(
  'HFS_CP3_ACTION:' +
  EncodingUtil.base64Encode(Blob.valueOf(JSON.serialize(result)))
);
"""
        return self.run_apex_source(script, "HFS_CP3_ACTION")

    def run_mulesoft(
        self,
        source: dict[str, Any],
        recommendation: dict[str, Any],
        action: dict[str, Any],
    ) -> dict[str, Any]:
        api = build_default_api()
        example = api.contract.examples["operations"][
            "executeApprovedAction"
        ]["request"]
        channel_actions = action.get("channelActions") or action.get(
            "actions"
        ) or [
            {
                "channel": "slack",
                "actionType": HOSPITAL_SLACK_ACTION_TYPE,
                "sourceSystem": "slack",
                "actionId": action["actionId"],
                "actionExternalKey": action["actionExternalKey"],
                "actionIdempotencyKey": action["actionIdempotencyKey"],
            }
        ]

        def execution_body(channel_action: dict[str, Any]) -> dict[str, Any]:
            action_type = channel_action["actionType"]
            channel = channel_action["channel"]
            body = deepcopy(example["value"])
            if action_type == HOSPITAL_WHATSAPP_ACTION_TYPE:
                payload = {
                    "targetRole": "Patient Experience Lead",
                    "targetChannel": "wa-role-patient-experience-lead",
                    "messageTitle": "Hospital operations surge recovery",
                    "messageBody": (
                        "Coordinate patient-safe internal updates for "
                        "room readiness, pharmacy stock, lab response, "
                        "and billing review."
                    ),
                    "evidenceIds": [source["evidenceId"]],
                    "sourceRecommendationId": recommendation[
                        "recommendationId"
                    ],
                }
            else:
                payload = {
                    "targetRole": "Operations Manager",
                    "targetChannel": "#north-star-demo",
                    "messageTitle": "Hospital operations surge recovery",
                    "messageBody": (
                        "Coordinate room cleaning, pharmacy restock, lab "
                        "escalation, billing review, and privacy-safe "
                        "internal updates."
                    ),
                    "evidenceIds": [source["evidenceId"]],
                    "sourceRecommendationId": recommendation[
                        "recommendationId"
                    ],
                }
            body.update(
                {
                    "tenantKey": self.config["tenantKey"],
                    "correlationId": self.config["correlationId"],
                    "externalKey": channel_action["actionExternalKey"],
                    "idempotencyKey": channel_action[
                        "actionIdempotencyKey"
                    ],
                    "recommendationId": recommendation["recommendationId"],
                    "approvalId": action["approvalId"],
                    "actionId": channel_action["actionId"],
                    "targetEntityId": source["subjectEntityId"],
                    "actionType": action_type,
                    "sourceSystem": channel_action.get(
                        "sourceSystem",
                        channel,
                    ),
                    "payload": payload,
                }
            )
            return body

        def execution_headers(body: dict[str, Any]) -> dict[str, str]:
            headers = deepcopy(example["x-hfs-headers"])
            headers["X-Tenant-Id"] = self.config["tenantKey"]
            headers["X-Correlation-Id"] = self.config["correlationId"]
            headers["X-Idempotency-Key"] = body["idempotencyKey"]
            return headers

        blocked_body = execution_body(channel_actions[0])
        blocked_body["externalKey"] = "action-demo-unapproved"
        blocked_body["idempotencyKey"] = "action-demo-unapproved-v1"
        blocked_body["approvalId"] = "approval-not-approved"
        blocked_headers = execution_headers(blocked_body)
        blocked = api.request(
            "POST",
            "/v1/actions/executions",
            blocked_headers,
            blocked_body,
        )
        if blocked.status != 403 or api.outcomes:
            raise HarnessFailure(
                "The MuleSoft unapproved-action path did not fail closed."
            )

        execution_results = []
        outcomes = []
        delivery_by_type = {}
        for channel_action in channel_actions:
            api.write_back_adapter.register_approval(
                approval_id=action["approvalId"],
                tenant_key=self.config["tenantKey"],
                recommendation_id=recommendation["recommendationId"],
                action_id=channel_action["actionId"],
            )
            body = execution_body(channel_action)
            executed = api.request(
                "POST",
                "/v1/actions/executions",
                execution_headers(body),
                body,
            )
            if executed.status != 202:
                raise HarnessFailure(
                    f"The approved MuleSoft {channel_action['channel']} "
                    "action was not accepted."
                )
            outcome_key = f"outcome-{channel_action['actionExternalKey']}"
            outcome = api.outcomes.get(outcome_key)
            if outcome is None:
                raise HarnessFailure(
                    f"The approved MuleSoft {channel_action['channel']} "
                    "action did not produce its expected outcome."
                )
            if outcome["correlationId"] != self.config["correlationId"]:
                raise HarnessFailure(
                    "MuleSoft lost the correlation identifier."
                )
            source_record = api.write_back_adapter.source_records[
                outcome["sourceRecordId"]
            ]
            delivery = source_record.get("delivery", {})
            delivery_by_type[channel_action["actionType"]] = delivery
            outcomes.append(
                {
                    "channel": channel_action["channel"],
                    "actionType": channel_action["actionType"],
                    "actionId": channel_action["actionId"],
                    "outcome": outcome,
                    "delivery": delivery,
                }
            )
            execution_results.append(
                {
                    "channel": channel_action["channel"],
                    "actionType": channel_action["actionType"],
                    "status": executed.status,
                    "state": executed.body["status"],
                    "deliveryStatus": delivery.get("status"),
                    "provider": delivery.get("provider"),
                }
            )

        if len(api.outcomes) != len(channel_actions):
            raise HarnessFailure(
                "The approved MuleSoft channel actions did not produce "
                "one outcome each."
            )
        return {
            "blockedStatus": blocked.status,
            "blockedErrorCode": blocked.body["errors"][0]["code"],
            "executionStatus": execution_results[-1]["status"],
            "executionState": execution_results[-1]["state"],
            "sourceRecordId": outcomes[-1]["outcome"]["sourceRecordId"],
            "executionResults": execution_results,
            "deliveryByActionType": delivery_by_type,
            "outcomes": outcomes,
            "outcome": outcomes[0]["outcome"],
        }

    def capture_single_outcome(
        self,
        source: dict[str, Any],
        channel_outcome: dict[str, Any],
        index: int,
    ) -> dict[str, Any]:
        outcome = channel_outcome["outcome"]
        observed_at = (
            outcome["observedAt"].replace("T", " ").replace("Z", "")
        )
        payload_json = json.dumps(outcome, separators=(",", ":"), sort_keys=True)
        identifiers = self.config["identifiers"]
        evaluation_key = channel_outcome.get("evaluationExternalKey")
        if not evaluation_key:
            evaluation_key = (
                identifiers["evaluationExternalKey"]
                if index == 1
                else identifiers["whatsappEvaluationExternalKey"]
            )
        event_external_key = f"event-demo-outcome-{index:03d}"
        source_uri = channel_outcome.get("sourceUri") or (
            "urn:hfs:source:hospital:whatsapp-alert"
            if channel_outcome["actionType"] == HOSPITAL_WHATSAPP_ACTION_TYPE
            else "urn:hfs:source:hospital:slack-alert"
        )
        script = f"""
HFS_Event__c outcomeEvent = new HFS_Event__c(
  Event_Id__c = '{event_external_key}',
  Tenant_Key__c = '{apex_string(self.config["tenantKey"])}',
  Source_URI__c = '{source_uri}',
  Source_Record_Id__c = '{apex_string(outcome["sourceRecordId"])}',
  Event_Type__c = 'HOSPITAL_APPROVED_ACTION_EXECUTED',
  Subject__c = '{apex_string(outcome["summary"])}',
  Occurred_At__c = Datetime.valueOfGmt('{observed_at}'),
  Observed_At__c = Datetime.valueOfGmt('{observed_at}'),
  Source_Sequence__c = {index + 1},
  Idempotency_Key__c = '{event_external_key}-v1',
  Correlation_Id__c = '{apex_string(self.config["correlationId"])}',
  Schema_Version__c = HFS_ServiceContract.VERSION,
  Content_Hash__c =
    'sha256:7549cf0c63ad4a64f178d8500c1f3874d97478f6ee323e4debbab6d89b168b69',
  Payload_JSON__c = '{apex_string(payload_json)}',
  Intake_Result__c = 'ACCEPTED'
);
insert as user outcomeEvent;

HFS_OutcomeCommand command = new HFS_OutcomeCommand();
command.contractVersion = HFS_ServiceContract.VERSION;
command.correlationId = '{apex_string(self.config["correlationId"])}';
command.tenantKey = '{apex_string(self.config["tenantKey"])}';
command.purpose = '{HOSPITAL_OUTCOME_PURPOSE}';
command.externalKey = '{apex_string(outcome["externalKey"])}';
command.actionId = '{apex_string(channel_outcome["actionId"])}';
command.sourceEventId = outcomeEvent.Id;
command.outcomeType = '{apex_string(outcome["outcomeType"])}';
command.status = '{apex_string(outcome["status"])}';
command.observedAt = Datetime.valueOfGmt('{observed_at}');
command.summary = '{apex_string(outcome["summary"])}';
command.metricKey = '{apex_string(outcome["metricKey"])}';
command.metricValue = {outcome["metricValue"]};
HFS_CommandResult captured = new HFS_RelationshipServiceImpl()
  .captureOutcome(command);
System.assertEquals(true, captured.success, JSON.serialize(captured.errors));

HFS_Evaluation__c evaluation = new HFS_Evaluation__c(
  External_Key__c = '{apex_string(evaluation_key)}',
  Tenant_Key__c = command.tenantKey,
  Outcome__c = captured.recordId,
  Evaluation_Type__c = 'DEFINED_OUTCOME_METRIC',
  Evaluator_Type__c = 'RULE',
  Evaluator_Id__c = 'action-execution-success-v1',
  Score__c = 1,
  Verdict__c = 'PASS',
  Notes__c = 'The approved action produced the defined success outcome.',
  Evaluated_At__c = System.now()
);
insert as user evaluation;

Map<String, Object> result = new Map<String, Object>{{
  'channel' => '{apex_string(channel_outcome["channel"])}',
  'actionType' => '{apex_string(channel_outcome["actionType"])}',
  'outcomeId' => captured.recordId,
  'outcomeStatus' => captured.status,
  'evaluationId' => evaluation.Id,
  'actionId' => '{apex_string(channel_outcome["actionId"])}'
}};
System.debug(
  'HFS_CP3_CAPTURED_OUTCOME:' +
  EncodingUtil.base64Encode(Blob.valueOf(JSON.serialize(result)))
);
"""
        return self.run_apex_source(script, "HFS_CP3_CAPTURED_OUTCOME")

    def build_task_outcomes(
        self,
        action: dict[str, Any],
    ) -> list[dict[str, Any]]:
        observed_at = timestamp()
        outcomes = []
        for task_action in action.get("taskActions") or []:
            template = HOSPITAL_TASK_OUTCOME_TEMPLATES.get(
                task_action["actionType"]
            )
            if template is None:
                raise HarnessFailure(
                    "No business outcome template exists for "
                    f"{task_action['actionType']}."
                )
            templates = [template]
            if task_action["actionType"] == "CREATE_PATIENT_SERVICE_TASK":
                templates.append(
                    {
                        "outcomeType": "COMPLAINT_CONTAINED",
                        "metricKey": "complaint_contained",
                        "metricValue": 1,
                        "sourceSystem": "salesforce-task",
                        "sourceUri": (
                            "urn:hfs:source:hospital:"
                            "patient-service-recovery"
                        ),
                        "summary": (
                            "Patient complaint cluster contained through "
                            "approved service-recovery coordination."
                        ),
                    }
                )
            for template_index, outcome_template in enumerate(templates):
                suffix = (
                    ""
                    if template_index == 0
                    else f"-{outcome_template['metricKey'].replace('_', '-')}"
                )
                external_key = (
                    f"outcome-{task_action['actionExternalKey']}{suffix}"
                )
                source_record_id = (
                    "mock-task-outcome-"
                    f"{task_action['actionExternalKey'].removeprefix('action-')}"
                    f"{suffix}"
                )
                outcomes.append(
                    {
                        "channel": "task",
                        "actionType": task_action["actionType"],
                        "actionId": task_action["actionId"],
                        "sourceUri": outcome_template["sourceUri"],
                        "evaluationExternalKey": f"evaluation-{external_key}",
                        "outcome": {
                            "contractVersion": "1.0.0",
                            "tenantKey": self.config["tenantKey"],
                            "purpose": "CAPTURE_APPROVED_ACTION_OUTCOME",
                            "correlationId": self.config["correlationId"],
                            "externalKey": external_key,
                            "idempotencyKey": f"{external_key}-v1",
                            "actionId": task_action["actionId"],
                            "sourceEventId": f"event-{source_record_id}",
                            "sourceRecordId": source_record_id,
                            "sourceSystem": outcome_template["sourceSystem"],
                            "outcomeType": outcome_template["outcomeType"],
                            "status": "SUCCESS",
                            "observedAt": observed_at,
                            "summary": outcome_template["summary"],
                            "metricKey": outcome_template["metricKey"],
                            "metricValue": outcome_template["metricValue"],
                        },
                    },
                )
        return outcomes

    def verify_lightning_after_outcomes(
        self,
        source: dict[str, Any],
        expected_channel_count: int,
        expected_task_count: int,
        expected_business_outcome_count: int,
    ) -> dict[str, Any]:
        expected_action_count = expected_channel_count + expected_task_count
        expected_outcome_count = (
            expected_channel_count + expected_business_outcome_count
        )
        script = f"""
HFS_ContextRequest contextRequest = new HFS_ContextRequest();
contextRequest.contractVersion = HFS_ServiceContract.VERSION;
contextRequest.tenantKey = '{apex_string(self.config["tenantKey"])}';
contextRequest.workItemId = '{apex_string(source["workItemId"])}';
contextRequest.purpose = '{HOSPITAL_PURPOSE}';
contextRequest.correlationId = '{apex_string(self.config["correlationId"])}';
contextRequest.includeProvenance = true;
contextRequest.timelineLimit = 100;
HFS_CommandCenterResponse commandCenter =
  HFS_RelationshipController.loadCommandCenter(contextRequest);
System.assertEquals(0, commandCenter.context.errors.size());
System.assertEquals('COMPLETED', commandCenter.context.workItem.status);
System.assertEquals({expected_action_count}, commandCenter.context.actions.size());
System.assertEquals({expected_outcome_count}, commandCenter.context.outcomes.size());
System.assertEquals({expected_outcome_count}, commandCenter.context.evaluations.size());
Set<String> actionTypes = new Set<String>();
Integer executedChannelActions = 0;
Integer executedTaskActions = 0;
Integer pendingTaskActions = 0;
for (HFS_ContextItem item : commandCenter.context.actions) {{
  actionTypes.add(item.recordType);
  Boolean isChannelAction =
    item.recordType == '{HOSPITAL_SLACK_ACTION_TYPE}' ||
    item.recordType == '{HOSPITAL_WHATSAPP_ACTION_TYPE}';
  if (item.status == 'EXECUTED' && isChannelAction) {{
    executedChannelActions++;
  }}
  if (item.status == 'EXECUTED' && !isChannelAction) {{
    executedTaskActions++;
  }}
  if (
    item.status == 'PENDING' &&
    !isChannelAction
  ) {{
    pendingTaskActions++;
  }}
}}
System.assertEquals({expected_channel_count}, executedChannelActions);
System.assertEquals({expected_task_count}, executedTaskActions);
System.assertEquals(0, pendingTaskActions);
System.assertEquals(true, actionTypes.contains('{HOSPITAL_SLACK_ACTION_TYPE}'));
System.assertEquals(
  true,
  actionTypes.contains('{HOSPITAL_WHATSAPP_ACTION_TYPE}')
);
System.assertEquals(true, actionTypes.contains('CREATE_PATIENT_SERVICE_TASK'));
System.assertEquals(true, actionTypes.contains('REQUEST_BED_CLEANING'));
System.assertEquals(true, actionTypes.contains('CREATE_PHARMACY_RESTOCK_REQUEST'));
System.assertEquals(true, actionTypes.contains('ESCALATE_LAB_VENDOR_CASE'));
System.assertEquals(true, actionTypes.contains('OPEN_BILLING_REVIEW'));
System.assertEquals(true, commandCenter.permissions.canApprove);
System.assertEquals(true, commandCenter.permissions.canExecute);
Map<String, Object> result = new Map<String, Object>{{
  'workItemStatus' => commandCenter.context.workItem.status,
  'actionStatus' => 'EXECUTED',
  'actionCount' => commandCenter.context.actions.size(),
  'taskActionCount' => {expected_task_count},
  'pendingTaskActionCount' => pendingTaskActions,
  'executedTaskActionCount' => executedTaskActions,
  'executedChannelActionCount' => executedChannelActions,
  'outcomeCount' => commandCenter.context.outcomes.size(),
  'evaluationCount' => commandCenter.context.evaluations.size(),
  'actionTypes' => new List<String>(actionTypes),
  'lightningCanApprove' => commandCenter.permissions.canApprove,
  'lightningCanExecute' => commandCenter.permissions.canExecute
}};
System.debug(
  'HFS_CP3_OUTCOME_VERIFY:' +
  EncodingUtil.base64Encode(Blob.valueOf(JSON.serialize(result)))
);
"""
        return self.run_apex_source(script, "HFS_CP3_OUTCOME_VERIFY")

    def capture_outcome(
        self,
        source: dict[str, Any],
        action: dict[str, Any],
        mulesoft: dict[str, Any],
    ) -> dict[str, Any]:
        channel_outcomes = mulesoft.get("outcomes") or [
            {
                "channel": "slack",
                "actionType": HOSPITAL_SLACK_ACTION_TYPE,
                "actionId": action["actionId"],
                "outcome": mulesoft["outcome"],
                "delivery": mulesoft.get("deliveryByActionType", {}).get(
                    HOSPITAL_SLACK_ACTION_TYPE,
                    {},
                ),
            }
        ]
        task_outcomes = self.build_task_outcomes(action)
        capturable_outcomes = channel_outcomes + task_outcomes
        captured = [
            self.capture_single_outcome(source, channel_outcome, index)
            for index, channel_outcome in enumerate(
                capturable_outcomes,
                start=1,
            )
        ]
        verification = self.verify_lightning_after_outcomes(
            source,
            len(channel_outcomes),
            len(action.get("taskActions") or []),
            len(task_outcomes),
        )
        return {
            **verification,
            "outcomeStatus": "SUCCESS",
            "capturedOutcomes": captured,
            "businessOutcomeCount": len(task_outcomes),
            "channelDeliveries": {
                channel_outcome["actionType"]: channel_outcome.get(
                    "delivery",
                    {},
                )
                for channel_outcome in channel_outcomes
            },
        }

    def verify_apex_final_context(
        self,
        source: dict[str, Any],
    ) -> dict[str, Any]:
        script = f"""
HFS_ContextRequest contextRequest = new HFS_ContextRequest();
contextRequest.contractVersion = HFS_ServiceContract.VERSION;
contextRequest.tenantKey = '{apex_string(self.config["tenantKey"])}';
contextRequest.workItemId = '{apex_string(source["workItemId"])}';
contextRequest.purpose = '{HOSPITAL_PURPOSE}';
contextRequest.correlationId = '{apex_string(self.config["correlationId"])}';
contextRequest.includeProvenance = true;
contextRequest.timelineLimit = 100;

HFS_ContextResponse context = new HFS_RelationshipServiceImpl()
  .getContext(contextRequest);
System.assertEquals(0, context.errors.size(), JSON.serialize(context.errors));
System.assertEquals('COMPLETED', context.workItem.status);

Set<String> entityTypes = new Set<String>();
Set<String> entityExternalKeys = new Set<String>();
for (HFS_ContextItem item : context.entities) {{
  entityTypes.add(item.recordType);
  entityExternalKeys.add(item.externalKey);
}}
System.assertEquals(true, entityTypes.contains('CUSTOMER_ALIAS'));
System.assertEquals(true, entityTypes.contains('LOCATION'));
System.assertEquals(true, entityTypes.contains('RESOURCE'));
System.assertEquals(true, entityTypes.contains('PARTNER'));
System.assertEquals(true, entityTypes.contains('PROCESS'));
System.assertEquals(
  true,
  entityExternalKeys.contains('ALIAS-PATIENT-GROUP-MORNING-001')
);
System.assertEquals(
  true,
  entityExternalKeys.contains('DEPT-OUTPATIENT-RECEPTION')
);
System.assertEquals(
  true,
  entityExternalKeys.contains('RESOURCE-WARD-A3-DISCHARGE-ROOMS')
);
System.assertEquals(
  true,
  entityExternalKeys.contains('RESOURCE-PHARMACY-IV-KITS')
);
System.assertEquals(
  true,
  entityExternalKeys.contains('PARTNER-ISLAND-DIAGNOSTICS')
);
System.assertEquals(
  true,
  entityExternalKeys.contains('PROCESS-BILLING-INSURANCE-REVIEW')
);

Set<String> evidenceTypes = new Set<String>();
for (HFS_EvidenceCitation citation : context.evidence) {{
  evidenceTypes.add(citation.evidenceType);
}}
System.assertEquals(true, evidenceTypes.contains('PATIENT_COMPLAINT_CLUSTER'));
System.assertEquals(true, evidenceTypes.contains('RESOURCE_CAPACITY'));
System.assertEquals(true, evidenceTypes.contains('PHARMACY_STOCK_POSITION'));
System.assertEquals(true, evidenceTypes.contains('PARTNER_RESPONSE_STATUS'));
System.assertEquals(true, evidenceTypes.contains('BILLING_AND_INSURANCE_HOLD'));
System.assertEquals(true, evidenceTypes.contains('STAFF_QUEUE_RISK'));
System.assertEquals(true, evidenceTypes.contains('CLINICAL_DECISION_REFUSAL'));

Set<String> actionTypes = new Set<String>();
for (HFS_ContextItem item : context.actions) {{
  actionTypes.add(item.recordType);
}}
System.assert(context.actions.size() >= 7);
System.assertEquals(true, actionTypes.contains('CREATE_PATIENT_SERVICE_TASK'));
System.assertEquals(true, actionTypes.contains('REQUEST_BED_CLEANING'));
System.assertEquals(true, actionTypes.contains('CREATE_PHARMACY_RESTOCK_REQUEST'));
System.assertEquals(true, actionTypes.contains('ESCALATE_LAB_VENDOR_CASE'));
System.assertEquals(true, actionTypes.contains('OPEN_BILLING_REVIEW'));
System.assertEquals(true, actionTypes.contains('{HOSPITAL_SLACK_ACTION_TYPE}'));
System.assertEquals(
  true,
  actionTypes.contains('{HOSPITAL_WHATSAPP_ACTION_TYPE}')
);

Set<String> outcomeTypes = new Set<String>();
Set<String> outcomeMetricKeys = new Set<String>();
for (HFS_ContextItem item : context.outcomes) {{
  outcomeTypes.add(item.recordType);
  outcomeMetricKeys.add(item.metricKey);
}}
System.assert(context.outcomes.size() >= 8);
System.assert(context.evaluations.size() >= 8);
System.assertEquals(true, outcomeTypes.contains('SLACK_ALERT_DELIVERY'));
System.assertEquals(true, outcomeTypes.contains('WHATSAPP_ALERT_DELIVERY'));
System.assertEquals(true, outcomeTypes.contains('WAIT_TIME_REDUCED'));
System.assertEquals(true, outcomeTypes.contains('COMPLAINT_CONTAINED'));
System.assertEquals(true, outcomeTypes.contains('DISCHARGE_ROOMS_RELEASED'));
System.assertEquals(true, outcomeTypes.contains('PHARMACY_STOCKOUT_AVOIDED'));
System.assertEquals(true, outcomeTypes.contains('LAB_PARTNER_SLA_ESCALATED'));
System.assertEquals(true, outcomeTypes.contains('BILLING_REVIEW_OPENED'));
System.assertEquals(true, outcomeMetricKeys.contains('slack_alert_delivery_success'));
System.assertEquals(
  true,
  outcomeMetricKeys.contains('whatsapp_alert_delivery_success')
);
System.assertEquals(
  true,
  outcomeMetricKeys.contains('outpatient_wait_time_reduced_minutes')
);
System.assertEquals(true, outcomeMetricKeys.contains('complaint_contained'));
System.assertEquals(true, outcomeMetricKeys.contains('rooms_released'));
System.assertEquals(true, outcomeMetricKeys.contains('stockout_avoided'));
System.assertEquals(true, outcomeMetricKeys.contains('partner_sla_escalated'));
System.assertEquals(true, outcomeMetricKeys.contains('billing_issue_routed'));
System.assertEquals(1, context.recommendations.size());
System.assertEquals(1, context.approvals.size());

Map<String, Object> output = new Map<String, Object>{{
  'workItemStatus' => context.workItem.status,
  'entityTypes' => new List<String>(entityTypes),
  'entityExternalKeys' => new List<String>(entityExternalKeys),
  'evidenceTypes' => new List<String>(evidenceTypes),
  'actionTypes' => new List<String>(actionTypes),
  'outcomeTypes' => new List<String>(outcomeTypes),
  'outcomeMetricKeys' => new List<String>(outcomeMetricKeys),
  'recommendationCount' => context.recommendations.size(),
  'approvalCount' => context.approvals.size(),
  'actionCount' => context.actions.size(),
  'outcomeCount' => context.outcomes.size(),
  'evaluationCount' => context.evaluations.size()
}};
System.debug(
  'HFS_CP3_APEX_FINAL_CONTEXT:' +
  EncodingUtil.base64Encode(Blob.valueOf(JSON.serialize(output)))
);
"""
        return self.run_apex_source(script, "HFS_CP3_APEX_FINAL_CONTEXT")

    def verify_agentforce_after_outcomes(
        self,
        source: dict[str, Any],
        model: dict[str, Any],
    ) -> dict[str, Any]:
        script = f"""
HFS_AgentActionRequest request = new HFS_AgentActionRequest();
request.contractVersion = HFS_ServiceContract.VERSION;
request.action = HFS_AgentActionService.RECOMMEND;
request.tenantKey = '{apex_string(self.config["tenantKey"])}';
request.correlationId = '{apex_string(self.config["correlationId"])}';
request.purpose = '{HOSPITAL_PURPOSE}';
request.workItemId = '{apex_string(source["workItemId"])}';
request.modelProfile = '{apex_string(model["profileKey"])}';
HFS_AgentActionResult result = HFS_AgentRecommendationAction.invoke(
  new List<HFS_AgentActionRequest>{{ request }}
)[0];
System.assertEquals('SUCCESS', result.status, result.responseJson);
Map<String, Object> response =
  (Map<String, Object>) JSON.deserializeUntyped(result.responseJson);
Map<String, Object> coverage =
  (Map<String, Object>) response.get('contextCoverage');
Map<String, Object> categories =
  (Map<String, Object>) coverage.get('evidenceCategories');
Map<String, Object> outcomeCoverage =
  (Map<String, Object>) categories.get('outcome');
System.assertEquals(
  true,
  (Boolean) outcomeCoverage.get('applies'),
  result.responseJson
);
System.assert(((List<Object>) outcomeCoverage.get('recordIds')).size() >= 8);
Map<String, Object> recordsByPrimitive =
  (Map<String, Object>) coverage.get('recordIdsByPrimitive');
System.assert(
  ((List<Object>) recordsByPrimitive.get('actions')).size() >= 7,
  result.responseJson
);
System.assert(
  ((List<Object>) recordsByPrimitive.get('metrics')).size() >= 8,
  result.responseJson
);
Map<String, Object> output = new Map<String, Object>{{
  'status' => result.status,
  'outcomeContextCovered' => (Boolean) outcomeCoverage.get('applies'),
  'outcomeRecordCount' =>
    ((List<Object>) outcomeCoverage.get('recordIds')).size(),
  'actionRecordCount' =>
    ((List<Object>) recordsByPrimitive.get('actions')).size(),
  'metricCount' =>
    ((List<Object>) recordsByPrimitive.get('metrics')).size()
}};
System.debug(
  'HFS_CP3_AGENTFORCE_OUTCOME_CONTEXT:' +
  EncodingUtil.base64Encode(Blob.valueOf(JSON.serialize(output)))
);
"""
        return self.run_apex_source(
            script,
            "HFS_CP3_AGENTFORCE_OUTCOME_CONTEXT",
        )

    def verify_connected(self) -> dict[str, Any]:
        identifiers = self.config["identifiers"]
        return {
            "counts": self.verify_counts(
                self.config["connectedExpectedCounts"]
            ),
            "identifiers": {
                "workItemId": self.query_identifier(
                    "HFS_Work_Item__c",
                    identifiers["workItemExternalKey"],
                ),
                "recommendationId": self.query_identifier(
                    "HFS_Recommendation__c",
                    identifiers["recommendationExternalKey"],
                ),
                "actionId": self.query_identifier(
                    "HFS_Action__c",
                    identifiers["actionExternalKey"],
                ),
                "whatsappActionId": self.query_identifier(
                    "HFS_Action__c",
                    identifiers["whatsappActionExternalKey"],
                ),
                "outcomeId": self.query_identifier(
                    "HFS_Outcome__c",
                    identifiers["outcomeExternalKey"],
                ),
                "whatsappOutcomeId": self.query_identifier(
                    "HFS_Outcome__c",
                    identifiers["whatsappOutcomeExternalKey"],
                ),
                "evaluationId": self.query_identifier(
                    "HFS_Evaluation__c",
                    identifiers["evaluationExternalKey"],
                ),
                "whatsappEvaluationId": self.query_identifier(
                    "HFS_Evaluation__c",
                    identifiers["whatsappEvaluationExternalKey"],
                ),
            },
        }

    def verify_counts(self, expected: dict[str, int]) -> dict[str, int]:
        actual = {
            object_api_name: self.query_count(object_api_name)
            for object_api_name in expected
        }
        mismatches = {
            object_api_name: {
                "expected": expected[object_api_name],
                "actual": actual[object_api_name],
            }
            for object_api_name in expected
            if actual[object_api_name] != expected[object_api_name]
        }
        if mismatches:
            raise HarnessFailure(
                f"Fixture counts did not match: {json.dumps(mismatches, sort_keys=True)}"
            )
        return actual

    def verify_seed(self) -> dict[str, Any]:
        identifiers = self.config["identifiers"]
        return {
            "counts": self.verify_counts(self.config["expectedCounts"]),
            "identifiers": {
                "workItemId": self.query_identifier(
                    "HFS_Work_Item__c",
                    identifiers["workItemExternalKey"],
                ),
                "recommendationId": self.query_identifier(
                    "HFS_Recommendation__c",
                    identifiers["recommendationExternalKey"],
                ),
                "approvalId": self.query_identifier(
                    "HFS_Approval__c",
                    identifiers["approvalExternalKey"],
                ),
            },
        }

    def verify_reset(self) -> dict[str, int]:
        expected = {
            object_api_name: 0
            for object_api_name in self.config["expectedCounts"]
        }
        return self.verify_counts(expected)

    def execute(self, command: str) -> dict[str, Any]:
        self.step("tools", self.validate_tools)
        self.step("salesforce-org", self.validate_org)
        if command in ("check", "run"):
            self.step("local-contracts", self.validate_local_contracts)
        if command in ("seed", "run"):
            self.step(
                "ensure-permissions",
                lambda: self.run_apex(ENSURE_PERMISSIONS_SCRIPT),
            )
        if command in ("reset", "seed", "run"):
            self.step("reset", lambda: self.run_apex(RESET_SCRIPT))
        if command == "reset":
            self.step("verify-reset", self.verify_reset)
        if command in ("seed", "run"):
            self.step("seed", lambda: self.run_apex(SEED_SCRIPT))
            seed_details = self.step("verify-seed", self.verify_seed)
            self.step(
                "verify-context",
                lambda: self.run_apex(VERIFY_CONTEXT_SCRIPT),
            )
            if command == "seed":
                return seed_details
            self.step(
                "prepare-connected",
                lambda: self.run_apex(PREPARE_CONNECTED_SCRIPT),
            )
            source = self.step("connected-source", self.connected_source)
            model = self.step(
                "model-gateway",
                lambda: self.run_model_gateway(source),
            )
            recommendation = self.step(
                "persist-recommendation",
                lambda: self.persist_model_recommendation(source, model),
            )
            agentforce = self.step(
                "agentforce",
                lambda: self.run_agentforce(
                    source,
                    recommendation,
                    model,
                ),
            )
            clinical_refusal = self.step(
                "clinical-refusal",
                lambda: self.verify_clinical_refusal(source, model),
            )
            action = self.step(
                "human-approval-and-action-log",
                lambda: self.approve_and_log_action(
                    source,
                    recommendation,
                    agentforce,
                ),
            )
            mulesoft = self.step(
                "mulesoft-writeback",
                lambda: self.run_mulesoft(
                    source,
                    recommendation,
                    action,
                ),
            )
            outcome = self.step(
                "outcome-and-lightning-refresh",
                lambda: self.capture_outcome(source, action, mulesoft),
            )
            post_outcome_agentforce = self.step(
                "agentforce-outcome-context",
                lambda: self.verify_agentforce_after_outcomes(source, model),
            )
            apex_final_context = self.step(
                "apex-final-context",
                lambda: self.verify_apex_final_context(source),
            )
            connected = self.step(
                "verify-connected",
                self.verify_connected,
            )
            return {
                "seed": seed_details,
                "model": {
                    key: value
                    for key, value in model.items()
                    if key != "output"
                },
                "agentforce": agentforce,
                "clinicalRefusal": clinical_refusal,
                "action": action,
                "mulesoft": {
                    key: value
                    for key, value in mulesoft.items()
                    if key != "outcome"
                },
                "outcome": outcome,
                "postOutcomeAgentforce": post_outcome_agentforce,
                "apexFinalContext": apex_final_context,
                "connected": connected,
            }
        if command == "verify":
            details = self.step("verify-seed", self.verify_seed)
            self.step(
                "verify-context",
                lambda: self.run_apex(VERIFY_CONTEXT_SCRIPT),
            )
            return details
        return {}


def timestamp() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def run_harness(
    command: str,
    target_org: str,
    runner: CommandRunner | None = None,
    config: dict[str, Any] | None = None,
) -> tuple[dict[str, Any], int]:
    started_at = timestamp()
    harness = DemoHarness(target_org, runner=runner, config=config)
    status = "passed"
    error_message = None
    details: dict[str, Any] = {}
    exit_code = 0
    try:
        details = harness.execute(command)
    except Exception as error:
        status = "failed"
        error_message = str(error)
        exit_code = 1
    report = {
        "schemaVersion": harness.config["schemaVersion"],
        "command": command,
        "status": status,
        "startedAt": started_at,
        "completedAt": timestamp(),
        "targetOrg": target_org,
        "tenantKey": harness.config["tenantKey"],
        "steps": harness.steps,
        "details": details,
    }
    if error_message:
        report["error"] = error_message
    return report, exit_code


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "command",
        choices=("check", "seed", "reset", "verify", "run"),
    )
    parser.add_argument("--target-org", default="dev-ed")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    report, exit_code = run_harness(args.command, args.target_org)
    serialized = json.dumps(report, indent=2, sort_keys=True)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(serialized + "\n")
    print(serialized)
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
