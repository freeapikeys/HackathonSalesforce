public class HFS_ServiceContract {
  public static final String VERSION = '1.0.0';

  public static final String READ_CONTEXT = 'READ_CONTEXT';
  public static final String READ_PROVENANCE = 'READ_PROVENANCE';
  public static final String PERSIST_EVENT = 'PERSIST_EVENT';
  public static final String STORE_RECOMMENDATION = 'STORE_RECOMMENDATION';
  public static final String REQUEST_APPROVAL = 'REQUEST_APPROVAL';
  public static final String DECIDE_APPROVAL = 'DECIDE_APPROVAL';
  public static final String LOG_ACTION = 'LOG_ACTION';
  public static final String CAPTURE_OUTCOME = 'CAPTURE_OUTCOME';

  public static final String INVALID_REQUEST = 'INVALID_REQUEST';
  public static final String UNSUPPORTED_CONTRACT_VERSION = 'UNSUPPORTED_CONTRACT_VERSION';
  public static final String PERMISSION_DENIED = 'PERMISSION_DENIED';
  public static final String CUSTOM_PERMISSION_REQUIRED = 'CUSTOM_PERMISSION_REQUIRED';
  public static final String RECORD_NOT_FOUND = 'RECORD_NOT_FOUND';
  public static final String SOURCE_EVIDENCE_INACCESSIBLE = 'SOURCE_EVIDENCE_INACCESSIBLE';
  public static final String TENANT_MISMATCH = 'TENANT_MISMATCH';
  public static final String INVALID_STATE = 'INVALID_STATE';
  public static final String IDEMPOTENCY_CONFLICT = 'IDEMPOTENCY_CONFLICT';
  public static final String VALIDATION_FAILED = 'VALIDATION_FAILED';
  public static final String RETRYABLE_DEPENDENCY_FAILURE = 'RETRYABLE_DEPENDENCY_FAILURE';
  public static final String PARTIAL_FAILURE = 'PARTIAL_FAILURE';
  public static final String UNEXPECTED_ERROR = 'UNEXPECTED_ERROR';

  public static final Set<String> OPERATIONS = new Set<String>{
    READ_CONTEXT,
    READ_PROVENANCE,
    PERSIST_EVENT,
    STORE_RECOMMENDATION,
    REQUEST_APPROVAL,
    DECIDE_APPROVAL,
    LOG_ACTION,
    CAPTURE_OUTCOME
  };

  public static Boolean supportsVersion(String requestedVersion) {
    return VERSION == requestedVersion;
  }
}
