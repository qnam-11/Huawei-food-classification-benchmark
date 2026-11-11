export const en = {
  appTitle: "Vietnamese Food Recognition",
  appSubtitle:
    "Upload a dish photo, pick a model, and see the dish name with its nutrition.",
  language: "Language",
  uploadPrompt: "Drop a photo here or click to browse",
  uploadHint: "JPEG, PNG or WebP, up to {mb} MB",
  changePhoto: "Change photo",
  chooseModel: "Choose a model",
  loadingModels: "Loading models…",
  modelsError: "Could not load the model list.",
  retry: "Retry",
  analyze: "Analyze",
  analyzing: "Analyzing…",
  confidence: "Confidence",
  top3: "Top 3 predictions",
  per_100g: "Per 100 g",
  per_serving: "Per serving",
  kcal: "Calories",
  protein: "Protein",
  carb: "Carb",
  fat: "Fat",
  serving: "Serving",
  draft_badge: "Draft nutrition values",
  f1Label: "Val macro F1",
  footerNote:
    "Classification only. Nutrition values are per 100 g and per typical serving.",
  unrecognized:
    "The model cannot recognize the food, please upload another picture.",
  invalid_image: "This file is not a readable image.",
  file_too_large: "The image is larger than {mb} MB.",
  unsupported_type: "Please upload a JPEG, PNG or WebP image.",
  unknown_model: "The selected model is not available.",
  inference_failed: "Something went wrong. Please try again.",
  network_error: "Cannot reach the server. Please try again.",
};

export type Dict = typeof en;
