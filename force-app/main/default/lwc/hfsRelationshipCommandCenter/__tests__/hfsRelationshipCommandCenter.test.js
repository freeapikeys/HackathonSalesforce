import { createElement } from "lwc";
import HfsRelationshipCommandCenter from "c/hfsRelationshipCommandCenter";
import loadCommandCenter from "@salesforce/apex/HFS_RelationshipController.loadCommandCenter";
import decideApproval from "@salesforce/apex/HFS_RelationshipController.decideApproval";
import { UI_STATE_VERSION } from "../fixtures";

jest.mock(
  "@salesforce/apex/HFS_RelationshipController.loadCommandCenter",
  () => ({ default: jest.fn() }),
  { virtual: true }
);
jest.mock(
  "@salesforce/apex/HFS_RelationshipController.decideApproval",
  () => ({ default: jest.fn() }),
  { virtual: true }
);

function createComponent(stateName = "ready", profileKey) {
  const element = createElement("c-hfs-relationship-command-center", {
    is: HfsRelationshipCommandCenter
  });
  element.mockMode = true;
  element.stateName = stateName;
  if (profileKey) {
    element.profileKey = profileKey;
  }
  document.body.appendChild(element);
  return element;
}

function createLiveComponent() {
  const element = createElement("c-hfs-relationship-command-center", {
    is: HfsRelationshipCommandCenter
  });
  element.recordId = "a01000000000001AAA";
  element.tenantKey = "tenant-live-test";
  element.purpose = "RESOLVE_RETAIL_RISK";
  document.body.appendChild(element);
  return element;
}

function flushPromises() {
  return Promise.resolve()
    .then(() => Promise.resolve())
    .then(() => Promise.resolve());
}

const livePayload = {
  userLabel: "approver@example.test",
  permissions: {
    canApprove: true,
    canModify: false,
    canReject: true,
    canExecute: false
  },
  context: {
    contractVersion: "1.0.0",
    correlationId: "correlation-live-test",
    tenantKey: "tenant-live-test",
    generatedAt: "2026-06-07T08:00:00.000Z",
    workItem: {
      recordId: "a01000000000001AAA",
      objectApiName: "HFS_Work_Item__c",
      externalKey: "work-live-test",
      recordType: "HIGH",
      label: "Live North Star case",
      status: "AWAITING_APPROVAL",
      summary: "A permitted user must decide the current recommendation.",
      occurredAt: "2026-06-07T07:00:00.000Z",
      subjectEntityId: "a02000000000001AAA",
      ownerLabel: "Relationship Operations",
      dueAt: "2026-06-07T10:00:00.000Z"
    },
    entities: [
      {
        recordId: "a02000000000001AAA",
        recordType: "PERSON",
        label: "Live customer"
      },
      {
        recordId: "a02000000000002AAA",
        recordType: "ORGANIZATION",
        label: "Live business"
      }
    ],
    relationships: [
      {
        recordId: "a03000000000001AAA",
        objectApiName: "HFS_Relationship__c",
        label: "Customer relationship",
        relationshipType: "CUSTOMER_OF",
        subjectEntityId: "a02000000000001AAA",
        objectEntityId: "a02000000000002AAA"
      }
    ],
    agreements: [],
    sopExecutions: [
      {
        recordId: "a04000000000001AAA",
        recordType: "PROACTIVE_UPDATE",
        status: "RUNNING",
        summary: "REVIEW_AND_APPROVE",
        definitionVersion: "1.0.0"
      }
    ],
    timeline: [
      {
        recordId: "a05000000000001AAA",
        objectApiName: "HFS_Event__c",
        recordType: "CASE_STATUS_CHANGED",
        label: "Status changed",
        summary: "The customer is waiting for an update.",
        occurredAt: "2026-06-07T07:00:00.000Z",
        sourceUri: "urn:test:service"
      }
    ],
    evidence: [
      {
        evidenceId: "a06000000000001AAA",
        sourceUri: "urn:test:service",
        contentHash:
          "sha256:86a1b1848320a798ea3df9b248f12b86976b8d6c4d86c31bbef5d2a26e49df5f",
        summary: "The customer is waiting for an update.",
        capturedAt: "2026-06-07T07:01:00.000Z"
      }
    ],
    recommendations: [
      {
        recordId: "a07000000000001AAA",
        recordType: "PROACTIVE_UPDATE",
        status: "PENDING_APPROVAL",
        summary: "Send a grounded service update.",
        confidence: 0.91,
        proposedActionType: "SEND_STATUS_UPDATE",
        modelProfile: "north-star-retail-recommendation",
        modelInvocationId: "invocation-live-test"
      }
    ],
    approvals: [
      {
        recordId: "a08000000000001AAA",
        recordType: "EXTERNAL_COMMUNICATION",
        status: "PENDING",
        requestedAt: "2026-06-07T07:05:00.000Z"
      }
    ],
    actions: [],
    outcomes: [],
    evaluations: [],
    errors: []
  }
};

describe("c-hfs-relationship-command-center", () => {
  afterEach(() => {
    jest.clearAllMocks();
    while (document.body.firstChild) {
      document.body.removeChild(document.body.firstChild);
    }
  });

  it("renders the complete synthetic North Star case", () => {
    const element = createComponent();
    const root = element.shadowRoot;

    expect(root.querySelector('[data-testid="ready-view"]')).not.toBeNull();
    expect(root.textContent).toContain("North Star weekend promotion recovery");
    expect(root.textContent).toContain("North Star retail signals");
    expect(root.textContent).toContain("Product, batch, and stock");
    expect(root.textContent).toContain("Complaint cluster");
    expect(root.textContent).toContain("Supplier response");
    expect(root.textContent).toContain("Source records");
    expect(root.textContent).toContain("Accessible source evidence");
    expect(root.textContent).toContain("North Star retail recovery");
    expect(root.textContent).toContain("Approve retail recovery actions");
    expect(root.textContent).toContain("Approval decision");
    expect(root.textContent).toContain("Store tasks and channel log");
    expect(root.textContent).toContain("Slack");
    expect(root.textContent).toContain("WhatsApp-style");
    expect(root.textContent).toContain("Stockout avoided");
    expect(root.textContent).toContain(`UI state ${UI_STATE_VERSION}`);
    expect(root.querySelectorAll(".timeline li")).toHaveLength(5);
    expect(root.querySelectorAll(".evidence-card")).toHaveLength(4);
  });

  it("renders the Nexavenu revenue gift profile without replacing North Star", () => {
    const element = createComponent("ready", "nexavenu-revenue");
    const root = element.shadowRoot;

    expect(root.querySelector('[data-testid="ready-view"]')).not.toBeNull();
    expect(root.textContent).toContain("Nexavenu champion nurture tower");
    expect(root.textContent).toContain("Revenue and buyer-readiness signals");
    expect(root.textContent).toContain("Prospect, champion, and opportunity");
    expect(root.textContent).toContain("Contact-sourced assumptions");
    expect(root.textContent).toContain("Approve champion nurture actions");
    expect(root.textContent).toContain("Revenue approval decision");
    expect(root.textContent).toContain("Nurture actions and handoff log");
    expect(root.textContent).toContain("Readiness target");
    expect(root.textContent).not.toContain("North Star retail signals");
  });

  it.each([
    ["loading", "loading-view", "Loading North Star context"],
    ["empty", "empty-view", "No North Star work is assigned"],
    ["denied", "denied-view", "North Star context is not available"],
    ["error", "error-view", "North Star could not load"]
  ])("renders the %s material state", (stateName, testId, expectedText) => {
    const element = createComponent(stateName);
    const root = element.shadowRoot;

    expect(root.querySelector(`[data-testid="${testId}"]`)).not.toBeNull();
    expect(root.textContent).toContain(expectedText);
    expect(root.querySelector('[data-testid="ready-view"]')).toBeNull();
  });

  it("shows accessible facts but removes approval controls for restricted role", () => {
    const element = createComponent("restricted");
    const root = element.shadowRoot;

    expect(root.querySelector('[data-testid="ready-view"]')).not.toBeNull();
    expect(root.textContent).toContain("North Star weekend promotion recovery");
    expect(
      root.querySelector('[data-testid="restricted-notice"]')
    ).not.toBeNull();
    expect(root.querySelector('[data-testid="approval-controls"]')).toBeNull();
  });

  it.each([
    ["approve-button", "APPROVE"],
    ["modify-button", "MODIFY"],
    ["reject-button", "REJECT"]
  ])("emits governed approval intent from %s", (testId, decision) => {
    const element = createComponent();
    const handler = jest.fn();
    element.addEventListener("approvalaction", handler);

    element.shadowRoot
      .querySelector(`[data-testid="${testId}"]`)
      .dispatchEvent(new CustomEvent("click"));

    expect(handler).toHaveBeenCalledTimes(1);
    expect(handler.mock.calls[0][0].detail).toEqual({
      decision,
      recommendationId: "recommendation-north-star-retail-001",
      approvalId: "approval-north-star-retail-001",
      correlationId: "20000000-0000-4000-8000-000000000001",
      stateVersion: UI_STATE_VERSION
    });
  });

  it("emits retry intent with correlation and state version", () => {
    const element = createComponent("error");
    const handler = jest.fn();
    element.addEventListener("retry", handler);

    element.shadowRoot
      .querySelector('[data-testid="retry-button"]')
      .dispatchEvent(new CustomEvent("click"));

    expect(handler).toHaveBeenCalledTimes(1);
    expect(handler.mock.calls[0][0].detail).toEqual({
      correlationId: "20000000-0000-4000-8000-000000000003",
      stateVersion: UI_STATE_VERSION
    });
  });

  it("uses alert semantics for denied and error states", () => {
    const denied = createComponent("denied");
    expect(
      denied.shadowRoot
        .querySelector('[data-testid="denied-view"]')
        .getAttribute("role")
    ).toBe("alert");

    document.body.removeChild(denied);
    const error = createComponent("error");
    expect(
      error.shadowRoot
        .querySelector('[data-testid="error-view"]')
        .getAttribute("role")
    ).toBe("alert");
  });

  it("loads live governed context through Apex and maps it to the frozen UI state", async () => {
    loadCommandCenter.mockResolvedValue(livePayload);

    const element = createLiveComponent();
    await flushPromises();

    expect(loadCommandCenter).toHaveBeenCalledTimes(1);
    expect(loadCommandCenter.mock.calls[0][0].request).toEqual(
      expect.objectContaining({
        contractVersion: UI_STATE_VERSION,
        tenantKey: "tenant-live-test",
        workItemId: "a01000000000001AAA",
        purpose: "RESOLVE_RETAIL_RISK",
        includeProvenance: true
      })
    );
    expect(element.shadowRoot.textContent).toContain("Live North Star case");
    expect(element.shadowRoot.textContent).toContain("Live customer");
    expect(element.shadowRoot.textContent).toContain(
      "Send a grounded service update."
    );
    expect(
      element.shadowRoot.querySelector('[data-testid="modify-button"]')
    ).toBeNull();
    expect(
      element.shadowRoot.querySelector('[data-testid="approve-button"]')
    ).not.toBeNull();
  });

  it("keeps live facts visible while removing controls for a restricted user", async () => {
    loadCommandCenter.mockResolvedValue({
      ...livePayload,
      permissions: {
        canApprove: false,
        canModify: false,
        canReject: false,
        canExecute: false
      }
    });

    const element = createLiveComponent();
    await flushPromises();

    expect(element.shadowRoot.textContent).toContain("Live North Star case");
    expect(
      element.shadowRoot.querySelector('[data-testid="restricted-notice"]')
    ).not.toBeNull();
    expect(
      element.shadowRoot.querySelector('[data-testid="approval-controls"]')
    ).toBeNull();
  });

  it("records a live approval decision and refreshes the governed context", async () => {
    loadCommandCenter.mockResolvedValue(livePayload);
    decideApproval.mockResolvedValue({
      contractVersion: "1.0.0",
      correlationId: "correlation-decision-test",
      operation: "DECIDE_APPROVAL",
      success: true,
      replayed: false,
      recordId: "a08000000000001AAA",
      recordType: "HFS_Approval__c",
      status: "APPROVED",
      errors: []
    });
    const completionHandler = jest.fn();
    const element = createLiveComponent();
    element.addEventListener("approvalcomplete", completionHandler);
    await flushPromises();

    element.shadowRoot
      .querySelector('[data-testid="approve-button"]')
      .dispatchEvent(new CustomEvent("click"));
    await flushPromises();
    await flushPromises();

    expect(decideApproval).toHaveBeenCalledTimes(1);
    expect(decideApproval.mock.calls[0][0].command).toEqual(
      expect.objectContaining({
        tenantKey: "tenant-live-test",
        approvalId: "a08000000000001AAA",
        decisionStatus: "APPROVED"
      })
    );
    expect(loadCommandCenter).toHaveBeenCalledTimes(2);
    expect(
      element.shadowRoot.querySelector('[data-testid="command-success"]')
    ).not.toBeNull();
    expect(completionHandler).toHaveBeenCalledWith(
      expect.objectContaining({
        detail: expect.objectContaining({
          status: "APPROVED",
          correlationId: "correlation-decision-test"
        })
      })
    );
  });

  it("shows a governed service error without claiming the decision completed", async () => {
    loadCommandCenter.mockResolvedValue(livePayload);
    decideApproval.mockResolvedValue({
      success: false,
      errors: [
        {
          code: "CUSTOM_PERMISSION_REQUIRED",
          message: "The required custom permission is not assigned."
        }
      ]
    });
    const element = createLiveComponent();
    await flushPromises();

    element.shadowRoot
      .querySelector('[data-testid="reject-button"]')
      .dispatchEvent(new CustomEvent("click"));
    await flushPromises();

    expect(
      element.shadowRoot.querySelector('[data-testid="command-error"]')
    ).not.toBeNull();
    expect(element.shadowRoot.textContent).toContain(
      "The required custom permission is not assigned."
    );
    expect(loadCommandCenter).toHaveBeenCalledTimes(1);
  });
});
