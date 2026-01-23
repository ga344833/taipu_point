from drf_standardized_errors.handler import exception_handler as standardized_exception_handler
from rest_framework.exceptions import ValidationError

DIALOG_CODE_CONDITIONS = {
    "required": True,
}  ## 自定義 dialog對於 CODE 的條件 ，依照 code 定義是否開啟對話框

DIALOG_ERROR_TYPE_CONDITIONS = {
    "validation_error": True,
}  ## 自定義 dialog對於 ERROR_TYPE 的條件 ，依照 error_type 定義是否開啟對話框


def extract_raw_errors(data):
    """
    從 response.data 中提取原始錯誤資料。
    如果資料是一個 dict 且包含 'errors' 鍵，且該鍵的值為 list，則返回該列表，
    否則返回原始資料。
    """
    if isinstance(data, dict) and "errors" in data and isinstance(data["errors"], list):
        return data["errors"]
    return data


def aggregate_errors_by_key(raw_errors):
    """
    將錯誤資訊根據 (code, detail) 進行聚合。
    每個聚合項將收集所有對應的欄位名稱。
    返回一個字典，鍵為 (code, detail)，值為欄位名稱的列表。
    """
    errors_by_key = {}
    if isinstance(raw_errors, list):
        for error in raw_errors:
            if isinstance(error, dict):
                code = error.get("code", "error")
                detail = error.get("detail", "")
                attr = error.get("attr", "")
                key = (code, detail)
                if key not in errors_by_key:
                    errors_by_key[key] = []
                if attr:
                    errors_by_key[key].append(attr)
            else:
                key = ("error", str(error))
                if key not in errors_by_key:
                    errors_by_key[key] = []
    elif isinstance(raw_errors, dict):
        for field, field_errors in raw_errors.items():
            if not isinstance(field_errors, list):
                field_errors = [field_errors]
            for error in field_errors:
                if isinstance(error, dict):
                    code = error.get("code", "error")
                    detail = error.get("detail", "")
                else:
                    code = "error"
                    detail = str(error)
                key = (code, detail)
                if key not in errors_by_key:
                    errors_by_key[key] = []
                errors_by_key[key].append(field)
    else:
        key = ("error", str(raw_errors))
        errors_by_key[key] = []
    return errors_by_key


def build_aggregated_details(errors_by_key):
    """
    根據聚合後的 errors_by_key 建立一個包含所有錯誤詳細資訊的字串，
    每個錯誤以 "detail , field1, field2" 的格式，用換行符分隔。
    """
    aggregated_lines = []
    for (code, detail), fields in errors_by_key.items():
        # 去除重複並排序欄位名稱，然後以逗號連接
        field_str = ", ".join(sorted(set(fields)))
        aggregated_lines.append(f"{detail} , {field_str}")
    return "\n".join(aggregated_lines)


def determine_dialog(raw_errors):
    """
    根據原始錯誤資料判定是否需要開啟對話框。
    如果任何錯誤的 code 在 DIALOG_CODE_CONDITIONS 中且其值為 True，
    或者任何錯誤的 type 在 DIALOG_ERROR_TYPE_CONDITIONS 中且其值為 True，
    則返回 True。
    """
    if isinstance(raw_errors, list):
        for error in raw_errors:
            if isinstance(error, dict):
                code = error.get("code", "")
                if code in DIALOG_CODE_CONDITIONS and DIALOG_CODE_CONDITIONS[code]:
                    return True
                error_type = error.get("type", "")
                if (
                    error_type in DIALOG_ERROR_TYPE_CONDITIONS
                    and DIALOG_ERROR_TYPE_CONDITIONS[error_type]
                ):
                    return True
    return False


def custom_exception_handler(exc, context):
    """
    自定義的錯誤處理函數，根據原始錯誤資訊聚合並生成一個更友好的錯誤回應格式，
    同時根據錯誤條件決定是否需要開啟對話框（dialog）。
    """
    response = standardized_exception_handler(exc, context)

    if response is not None and response.status_code in [400, 401, 402, 403, 404, 422]:
        # 根據 response.data 中是否包含 type 決定 error_type，否則預設為 validation_error
        if isinstance(response.data, dict) and "type" in response.data:
            error_type = response.data["type"]
        else:
            error_type = "validation_error"

        # 提取原始錯誤資料
        raw_errors = extract_raw_errors(response.data)
        # 聚合錯誤資訊
        errors_by_key = aggregate_errors_by_key(raw_errors)
        aggregated_details = build_aggregated_details(errors_by_key)
        # 判定是否需要開啟對話框
        dialog = determine_dialog(raw_errors)

        response.data = {
            "type": error_type,
            "errors": raw_errors,  # 原始錯誤資訊，便於後端調試
            "details": aggregated_details,  # 聚合後的錯誤資訊，用於前端顯示
            "dialog": dialog,
        }
    return response


