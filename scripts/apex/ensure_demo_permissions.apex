Set<String> requiredPermissionSets = new Set<String>{
  'HFS_Approver',
  'HFS_Integration_User'
};
Map<String, Id> permissionSetIds = new Map<String, Id>();
for (PermissionSet permissionSetValue : [
  SELECT Id, Name
  FROM PermissionSet
  WHERE Name IN :requiredPermissionSets
]) {
  permissionSetIds.put(permissionSetValue.Name, permissionSetValue.Id);
}
System.assertEquals(
  requiredPermissionSets,
  permissionSetIds.keySet(),
  'The demo permission sets must be deployed before the connected run.'
);

Set<Id> assignedPermissionSetIds = new Set<Id>();
for (PermissionSetAssignment assignment : [
  SELECT PermissionSetId
  FROM PermissionSetAssignment
  WHERE
    AssigneeId = :UserInfo.getUserId()
    AND PermissionSetId IN :permissionSetIds.values()
]) {
  assignedPermissionSetIds.add(assignment.PermissionSetId);
}

List<PermissionSetAssignment> missingAssignments = new List<PermissionSetAssignment>();
for (Id permissionSetId : permissionSetIds.values()) {
  if (!assignedPermissionSetIds.contains(permissionSetId)) {
    missingAssignments.add(
      new PermissionSetAssignment(
        AssigneeId = UserInfo.getUserId(),
        PermissionSetId = permissionSetId
      )
    );
  }
}
if (!missingAssignments.isEmpty()) {
  insert missingAssignments;
}

System.debug(
  'HFS_DEMO_PERMISSIONS:' +
  String.join(new List<String>(requiredPermissionSets), ',')
);
