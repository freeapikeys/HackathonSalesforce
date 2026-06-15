import { api, LightningElement } from "lwc";
import loadCommandCenter from "@salesforce/apex/HFS_RelationshipController.loadCommandCenter";
import decideApproval from "@salesforce/apex/HFS_RelationshipController.decideApproval";
import requestCorrectionReview from "@salesforce/apex/HFS_RelationshipController.requestCorrectionReview";
import {
  DEFAULT_PROFILE_KEY,
  getProfile,
  getUiState,
  UI_STATE_VERSION
} from "./fixtures";
import { mapCommandCenterPayload, mapTransportError } from "./stateAdapter";

export default class HfsRelationshipCommandCenter extends LightningElement {
  _stateName = "ready";
  _profileKey = DEFAULT_PROFILE_KEY;
  _connected = false;
  @api recordId;
  @api workItemId;
  @api tenantKey;
  @api purpose = "RESOLVE_RETAIL_RISK";
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
  get profileKey() {
    return this._profileKey;
  }

  set profileKey(value) {
    const nextProfileKey = value || DEFAULT_PROFILE_KEY;
    if (nextProfileKey === this._profileKey) {
      return;
    }
    this._profileKey = nextProfileKey;
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
      this.state = getUiState(this._stateName, this.profileKey);
      return;
    }

    this.state = getUiState("loading", this.profileKey);
    const effectiveWorkItemId = this.workItemId || this.recordId;
    const correlationId = this.createCorrelationId();
    if (!effectiveWorkItemId || !this.tenantKey) {
      this.state = this.withProfile({
        ...getUiState("error"),
        errorCode: "INVALID_CONFIGURATION",
        message:
          "Configure a tenant key and provide an HFS work item record before loading live context.",
        correlationId,
        retryable: false
      });
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
      this.state = this.withProfile(
        mapCommandCenterPayload(payload, this.purpose)
      );
    } catch (error) {
      this.state = this.withProfile(mapTransportError(error, correlationId));
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

  get profileOptions() {
    return this.state.profileOptions || [];
  }

  get hasProfileOptions() {
    return this.profileOptions.length > 1;
  }

  get operatingLayer() {
    return (
      this.state.case?.operatingLayer || {
        kpis: [],
        trendTitle: "Operating forecast",
        trend: [],
        brief: [],
        agents: [],
        channels: []
      }
    );
  }

  get operatingKpis() {
    return this.operatingLayer.kpis;
  }

  get operatingTrendTitle() {
    return this.operatingLayer.trendTitle;
  }

  get operatingTrend() {
    return this.operatingLayer.trend;
  }

  get operatingBrief() {
    return this.operatingLayer.brief;
  }

  get operatingAgents() {
    return this.operatingLayer.agents;
  }

  get operatingChannels() {
    return this.operatingLayer.channels;
  }

  get hasRecommendationAssumptions() {
    return Boolean(this.state.case?.recommendation?.assumptions?.length);
  }

  get hasRelationshipHistory() {
    return Boolean(this.state.case?.relationshipHistory?.length);
  }

  get hasIdentityLinks() {
    return Boolean(this.state.case?.identityLinks?.length);
  }

  get hasRelationshipContradictions() {
    return Boolean(this.state.case?.relationshipContradictions?.length);
  }

  get hasCorrectionActions() {
    return Boolean(this.state.case?.correctionActions?.length);
  }

  get disableCorrectionControls() {
    return !this.state.permissions.canRequestCorrection;
  }

  withProfile(state) {
    return {
      ...state,
      profile: getProfile(this.profileKey)
    };
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

  handleProfileSelect(event) {
    const selectedProfileKey = event.currentTarget.dataset.profileKey;
    if (!selectedProfileKey || selectedProfileKey === this.profileKey) {
      return;
    }
    this._profileKey = selectedProfileKey;
    this.dispatchEvent(
      new CustomEvent("profileselect", {
        detail: {
          profileKey: selectedProfileKey,
          stateVersion: this.state.stateVersion
        }
      })
    );
    this.loadState();
  }

  async handleCorrectionRequest(event) {
    const actionId = event.currentTarget.dataset.actionId;
    const action = (this.state.case.correctionActions || []).find(
      (candidate) => candidate.id === actionId
    );
    this.dispatchEvent(
      new CustomEvent("relationshipcorrectionrequest", {
        detail: {
          action,
          correlationId: this.state.correlationId,
          stateVersion: this.state.stateVersion
        }
      })
    );
    if (this.mockMode || !action || this.disableCorrectionControls) {
      return;
    }

    this.commandMessage = null;
    this.commandError = null;
    try {
      const result = await requestCorrectionReview({
        command: {
          contractVersion: UI_STATE_VERSION,
          correlationId: this.createCorrelationId(),
          tenantKey: this.tenantKey,
          purpose: this.purpose,
          externalKey: `correction-${action.id}`,
          sourceRelationshipId: action.sourceRelationshipId,
          sourceParticipantId: action.sourceParticipantId,
          targetLabel: action.target,
          reason: action.reason
        }
      });
      if (!result?.success) {
        const error = result?.errors?.[0];
        this.commandError =
          error?.message || "The correction review was not accepted.";
        return;
      }
      await this.loadState(true);
      this.commandMessage =
        "Correction review work item created and approval requested.";
    } catch (error) {
      this.commandError =
        error?.body?.message ||
        error?.message ||
        "The correction review could not be requested.";
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
          decisionNotes: `${decisionStatus} from the ${this.state.profile.shortName} command center.`
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
