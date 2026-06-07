import { api, LightningElement } from "lwc";
import { getUiState, UI_STATE_VERSION } from "./fixtures";

export default class HfsRelationshipCommandCenter extends LightningElement {
  _stateName = "ready";
  _connected = false;
  state = getUiState("loading");

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

  loadState() {
    this.state = getUiState(this._stateName);
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
    return this.isReady && this.state.permissions.canApprove;
  }

  get showRestrictedNotice() {
    return this.isReady && !this.state.permissions.canApprove;
  }

  get uiVersionLabel() {
    return `UI state ${UI_STATE_VERSION}`;
  }

  handleApprove() {
    this.dispatchDecision("APPROVE");
  }

  handleModify() {
    this.dispatchDecision("MODIFY");
  }

  handleReject() {
    this.dispatchDecision("REJECT");
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
}
