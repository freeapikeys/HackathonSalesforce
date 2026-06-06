public class HFS_ServiceSupport {
  private static final String SEPARATOR = '|||';

  @TestVisible
  private static Map<String, Boolean> permissionOverrides = new Map<String, Boolean>();

  public static void validateRequest(
    String contractVersion,
    String tenantKey,
    String purpose,
    String correlationId
  ) {
    if (!HFS_ServiceContract.supportsVersion(contractVersion)) {
      fail(
        HFS_ServiceContract.UNSUPPORTED_CONTRACT_VERSION,
        'Unsupported service contract version.',
        'contractVersion'
      );
    }
    requireText(tenantKey, 'tenantKey');
    requireText(purpose, 'purpose');
    requireText(correlationId, 'correlationId');
  }

  public static void requireText(String value, String fieldName) {
    if (String.isBlank(value)) {
      fail(
        HFS_ServiceContract.INVALID_REQUEST,
        'A required value is missing.',
        fieldName
      );
    }
  }

  public static Id requireId(String value, String fieldName) {
    requireText(value, fieldName);
    try {
      return Id.valueOf(value);
    } catch (Exception ignored) {
      fail(
        HFS_ServiceContract.INVALID_REQUEST,
        'The value is not a valid Salesforce record ID.',
        fieldName
      );
    }
    return null;
  }

  public static void requireTenant(
    String expectedTenant,
    String actualTenant,
    String fieldName
  ) {
    if (expectedTenant != actualTenant) {
      fail(
        HFS_ServiceContract.TENANT_MISMATCH,
        'The referenced record belongs to a different tenant.',
        fieldName
      );
    }
  }

  public static void requirePermission(String customPermission) {
    Boolean allowed = permissionOverrides.containsKey(customPermission)
      ? permissionOverrides.get(customPermission)
      : FeatureManagement.checkPermission(customPermission);
    if (!allowed) {
      fail(
        HFS_ServiceContract.CUSTOM_PERMISSION_REQUIRED,
        'The required custom permission is not assigned.',
        customPermission
      );
    }
  }

  @TestVisible
  static void setPermissionOverride(String customPermission, Boolean allowed) {
    permissionOverrides.put(customPermission, allowed);
  }

  @TestVisible
  static void clearPermissionOverrides() {
    permissionOverrides.clear();
  }

  public static void fail(String code, String message, String fieldName) {
    throw new HFS_ServiceException(
      code + SEPARATOR + String.valueOf(fieldName) + SEPARATOR + message
    );
  }

  public static HFS_ServiceError error(Exception exceptionValue) {
    if (exceptionValue instanceof HFS_ServiceException) {
      List<String> parts = exceptionValue.getMessage().split('\\|\\|\\|', 3);
      return error(
        parts.size() > 0 ? parts[0] : HFS_ServiceContract.UNEXPECTED_ERROR,
        parts.size() > 2 ? parts[2] : 'The operation could not be completed.',
        parts.size() > 1 && parts[1] != 'null' ? parts[1] : null,
        false,
        null
      );
    }

    if (
      exceptionValue instanceof QueryException ||
      exceptionValue instanceof SecurityException
    ) {
      return error(
        HFS_ServiceContract.PERMISSION_DENIED,
        'The current user cannot access the required data.',
        null,
        false,
        null
      );
    }

    if (exceptionValue instanceof DmlException) {
      DmlException dmlError = (DmlException) exceptionValue;
      String code = HFS_ServiceContract.VALIDATION_FAILED;
      if (
        dmlError.getNumDml() > 0 &&
        dmlError.getDmlStatusCode(0) == 'DUPLICATE_VALUE'
      ) {
        code = HFS_ServiceContract.IDEMPOTENCY_CONFLICT;
      }
      return error(
        code,
        'Salesforce rejected the requested record change.',
        null,
        false,
        null
      );
    }

    return error(
      HFS_ServiceContract.UNEXPECTED_ERROR,
      'The operation could not be completed.',
      null,
      false,
      null
    );
  }

  public static HFS_ServiceError error(
    String code,
    String message,
    String fieldName,
    Boolean retryable,
    String details
  ) {
    HFS_ServiceError response = new HFS_ServiceError();
    response.code = code;
    response.message = message;
    response.fieldName = fieldName;
    response.retryable = retryable;
    response.details = details;
    return response;
  }

  public static HFS_CommandResult success(
    String operation,
    String correlationId,
    SObject recordValue,
    String status,
    Boolean replayed
  ) {
    HFS_CommandResult result = baseResult(operation, correlationId);
    result.success = true;
    result.replayed = replayed;
    result.recordId = String.valueOf(recordValue.get('Id'));
    result.recordType = recordValue.getSObjectType().getDescribe().getName();
    result.status = status;
    return result;
  }

  public static HFS_CommandResult failure(
    String operation,
    String correlationId,
    Exception exceptionValue
  ) {
    HFS_CommandResult result = baseResult(operation, correlationId);
    result.success = false;
    result.replayed = false;
    result.errors.add(error(exceptionValue));
    return result;
  }

  public static Boolean same(Object firstValue, Object secondValue) {
    if (firstValue == null || secondValue == null) {
      return firstValue == secondValue;
    }
    if (firstValue instanceof Decimal && secondValue instanceof Decimal) {
      return (Decimal) firstValue == (Decimal) secondValue;
    }
    if (firstValue instanceof Datetime && secondValue instanceof Datetime) {
      return ((Datetime) firstValue).getTime() / 1000 ==
        ((Datetime) secondValue).getTime() / 1000;
    }
    if (firstValue instanceof Date && secondValue instanceof Date) {
      return (Date) firstValue == (Date) secondValue;
    }
    return String.valueOf(firstValue) == String.valueOf(secondValue);
  }

  private static HFS_CommandResult baseResult(
    String operation,
    String correlationId
  ) {
    HFS_CommandResult result = new HFS_CommandResult();
    result.contractVersion = HFS_ServiceContract.VERSION;
    result.correlationId = correlationId;
    result.operation = operation;
    result.errors = new List<HFS_ServiceError>();
    return result;
  }
}
