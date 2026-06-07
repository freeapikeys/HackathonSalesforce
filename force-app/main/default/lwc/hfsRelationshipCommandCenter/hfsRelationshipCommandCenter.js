import { api, LightningElement } from "lwc";
import loadCommandCenter from "@salesforce/apex/HFS_RelationshipController.loadCommandCenter";
import decideApproval from "@salesforce/apex/HFS_RelationshipController.decideApproval";
import { getUiState, UI_STATE_VERSION } from "./fixtures";
import { mapCommandCenterPayload, mapTransportError } from "./stateAdapter";

export default class HfsRelationshipCommandCenter extends LightningElement {
  _stateName = "ready";
  _connected = false;
  @api recordId;
  @api workItemId;
  @api tenantKey;
  @api purpose = "RELATIONSHIP_SERVICE";
  @api mockMode = false;
  state = getUiState("loading");
  decisionPending = false;
  commandMessage;
  commandError;

  @api
  get stateName() {
    return this._stateName;
  }

  set stateName(value) {
    this._stateName = value || "ready";
    if (this._connected) {
      this.loadState();
    }
  }

  @api
  refresh() {
    this.loadState();
  }

  connectedCallback() {
    this._connected = true;
    this.loadState();
  }

  async loadState(preserveFeedback = false) {
    if (!preserveFeedback) {
      this.commandMessage = null;
      this.commandError = null;
    }
    if (this.mockMode) {
      this.state = getUiState(this._stateName);
      return;
    }

    this.state = getUiState("loading");
    const effectiveWorkItemId = this.workItemId || this.recordId;
    const correlationId = this.createCorrelationId();
    if (!effectiveWorkItemId || !this.tenantKey) {
      this.state = {
        ...getUiState("error"),
        errorCode: "INVALID_CONFIGURATION",
        message:
          "Configure a tenant key and provide an HFS work item record before loading live context.",
        correlationId,
        retryable: false
      };
      return;
    }

    try {
      const payload = await loadCommandCenter({
        request: {
          contractVersion: UI_STATE_VERSION,
          tenantKey: this.tenantKey,
          workItemId: effectiveWorkItemId,
          subjectEntityId: null,
          purpose: this.purpose,
          correlationId,
          includeProvenance: true,
          timelineLimit: 100
        }
      });
      this.state = mapCommandCenterPayload(payload, this.purpose);
    } catch (error) {
      this.state = mapTransportError(error, correlationId);
    }
  }

  get isLoading() {
    return this.state.mode === "loading";
  }

  get isEmpty() {
    return this.state.mode === "empty";
  }

  get isDenied() {
    return this.state.mode === "denied";
  }

  get isError() {
    return this.state.mode === "error";
  }

  get isReady() {
    return this.state.mode === "ready";
  }

  get showApprovalControls() {
    return (
      this.isReady &&
      (this.state.permissions.canApprove ||
        this.state.permissions.canModify ||
        this.state.permissions.canReject)
    );
  }

  get showRestrictedNotice() {
    return (
      this.isReady &&
      this.state.case.approval.status.toUpperCase() === "PENDING" &&
      !this.showApprovalControls
    );
  }

  get showApproveControl() {
    return this.showApprovalControls && this.state.permissions.canApprove;
  }

  get showModifyControl() {
    return this.showApprovalControls && this.state.permissions.canModify;
  }

  get showRejectControl() {
    return this.showApprovalControls && this.state.permissions.canReject;
  }

  get uiVersionLabel() {
    return `UI state ${UI_STATE_VERSION}`;
  }

  async handleApprove() {
    await this.submitDecision("APPROVE", "APPROVED");
  }

  handleModify() {
    this.dispatchDecision("MODIFY");
  }

  async handleReject() {
    await this.submitDecision("REJECT", "REJECTED");
  }

  handleRetry() {
    this.dispatchEvent(
      new CustomEvent("retry", {
        detail: {
          correlationId: this.state.correlationId,
          stateVersion: this.state.stateVersion
        }
      })
    );
    if (!this.mockMode) {
      this.loadState();
    }
  }

  dispatchDecision(decision) {
    this.dispatchEvent(
      new CustomEvent("approvalaction", {
        detail: {
          decision,
          recommendationId: this.state.case.recommendation.id,
          approvalId: this.state.case.approval.id,
          correlationId: this.state.correlationId,
          stateVersion: this.state.stateVersion
        }
      })
    );
  }

  async submitDecision(intent, decisionStatus) {
    this.dispatchDecision(intent);
    if (this.mockMode) {
      return;
    }

    this.decisionPending = true;
    this.commandMessage = null;
    this.commandError = null;
    try {
      const result = await decideApproval({
        command: {
          contractVersion: UI_STATE_VERSION,
          correlationId: this.createCorrelationId(),
          tenantKey: this.tenantKey,
          purpose: this.purpose,
          approvalId: this.state.case.approval.id,
          decisionStatus,
          decisionNotes: `${decisionStatus} from the relationship command center.`
        }
      });
      if (!result?.success) {
        const error = result?.errors?.[0];
        this.commandError =
          error?.message || "The approval decision was not accepted.";
        return;
      }

      await this.loadState(true);
      this.commandMessage = `Approval ${decisionStatus.toLowerCase()} and context refreshed.`;
      this.dispatchEvent(
        new CustomEvent("approvalcomplete", {
          detail: {
            approvalId: result.recordId,
            status: result.status,
            correlationId: result.correlationId,
            replayed: result.replayed
          }
        })
      );
    } catch (error) {
      this.commandError =
        error?.body?.message ||
        error?.message ||
        "The approval decision could not be completed.";
    } finally {
      this.decisionPending = false;
    }
  }

  createCorrelationId() {
    return `hfs-${Date.now()}-${Math.random().toString(16).slice(2)}`;
  }
}
