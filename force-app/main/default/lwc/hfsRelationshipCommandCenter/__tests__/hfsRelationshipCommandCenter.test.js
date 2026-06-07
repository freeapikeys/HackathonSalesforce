import { createElement } from "lwc";
import HfsRelationshipCommandCenter from "c/hfsRelationshipCommandCenter";
import { UI_STATE_VERSION } from "../fixtures";

function createComponent(stateName = "ready") {
  const element = createElement("c-hfs-relationship-command-center", {
    is: HfsRelationshipCommandCenter
  });
  element.stateName = stateName;
  document.body.appendChild(element);
  return element;
}

describe("c-hfs-relationship-command-center", () => {
  afterEach(() => {
    while (document.body.firstChild) {
      document.body.removeChild(document.body.firstChild);
    }
  });

  it("renders the complete synthetic relationship case", () => {
    const element = createComponent();
    const root = element.shadowRoot;

    expect(root.querySelector('[data-testid="ready-view"]')).not.toBeNull();
    expect(root.textContent).toContain("Repeated service interruption");
    expect(root.textContent).toContain("Relationship and dependencies");
    expect(root.textContent).toContain("Chronological evidence view");
    expect(root.textContent).toContain("Accessible source evidence");
    expect(root.textContent).toContain("Major incident relationship response");
    expect(root.textContent).toContain(
      "Send a proactive service status update"
    );
    expect(root.textContent).toContain("Approval decision");
    expect(root.textContent).toContain("Action and outcome history");
    expect(root.textContent).toContain(`UI state ${UI_STATE_VERSION}`);
    expect(root.querySelectorAll(".timeline li")).toHaveLength(5);
    expect(root.querySelectorAll(".evidence-card")).toHaveLength(2);
  });

  it.each([
    ["loading", "loading-view", "Loading relationship context"],
    ["empty", "empty-view", "No relationship work is assigned"],
    ["denied", "denied-view", "Context is not available"],
    ["error", "error-view", "The command center could not load"]
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
    expect(root.textContent).toContain("Repeated service interruption");
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
      recommendationId: "recommendation-status-update-001",
      approvalId: "approval-status-update-001",
      correlationId: "10000000-0000-4000-8000-000000000001",
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
      correlationId: "10000000-0000-4000-8000-000000000003",
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
});
