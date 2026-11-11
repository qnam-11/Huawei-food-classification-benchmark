import type { Dict } from "./en";

export const vi: Dict = {
  appTitle: "Nhận diện món ăn Việt Nam",
  appSubtitle:
    "Tải ảnh món ăn lên, chọn mô hình và xem tên món cùng thông tin dinh dưỡng.",
  language: "Ngôn ngữ",
  uploadPrompt: "Kéo thả ảnh vào đây hoặc bấm để chọn ảnh",
  uploadHint: "JPEG, PNG hoặc WebP, tối đa {mb} MB",
  changePhoto: "Đổi ảnh",
  chooseModel: "Chọn mô hình",
  loadingModels: "Đang tải mô hình…",
  modelsError: "Không tải được danh sách mô hình.",
  retry: "Thử lại",
  analyze: "Phân tích",
  analyzing: "Đang phân tích…",
  confidence: "Độ tin cậy",
  top3: "3 dự đoán hàng đầu",
  per_100g: "Trên 100 g",
  per_serving: "Mỗi khẩu phần",
  kcal: "Calo",
  protein: "Protein",
  carb: "Carb",
  fat: "Chất béo",
  serving: "Khẩu phần",
  draft_badge: "Giá trị dinh dưỡng tạm tính",
  f1Label: "F1 macro (tập kiểm định)",
  footerNote:
    "Ứng dụng chỉ phân loại món ăn. Giá trị dinh dưỡng tính trên 100 g và theo khẩu phần thông thường.",
  unrecognized:
    "Mô hình không nhận diện được món ăn, vui lòng tải lên ảnh khác.",
  invalid_image: "Tệp này không phải ảnh hợp lệ.",
  file_too_large: "Ảnh lớn hơn {mb} MB.",
  unsupported_type: "Vui lòng tải lên ảnh JPEG, PNG hoặc WebP.",
  unknown_model: "Mô hình đã chọn không khả dụng.",
  inference_failed: "Đã xảy ra lỗi. Vui lòng thử lại.",
  network_error: "Không kết nối được máy chủ. Vui lòng thử lại.",
};
