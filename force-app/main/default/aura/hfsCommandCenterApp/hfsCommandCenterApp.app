<aura:application access="GLOBAL" extends="force:slds">
  <div class="slds-p-around_medium">
    <c:hfsRelationshipCommandCenter
      mockMode="true"
      purpose="RESOLVE_RETAIL_RISK"
      stateName="ready"
      tenantKey="tenant:closed-loop-demo"
    />
  </div>
</aura:application>
