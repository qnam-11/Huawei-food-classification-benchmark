export type ModelSummary = {
  id: string;
  display_name: string;
  val_macro_f1: number;
  img: number;
};

export type ModelsResponse = {
  models: ModelSummary[];
  max_upload_mb: number;
};

export type PredictionItem = {
  slug: string;
  name_vi: string;
  name_en: string;
  confidence: number;
};

export type Macros = {
  kcal: number;
  protein_g: number;
  carb_g: number;
  fat_g: number;
};

export type Nutrition = {
  per_100g: Macros;
  serving_g: number;
  per_serving: Macros;
  verified: boolean;
  source: string;
};

export type PredictResponse = {
  status: "ok" | "unrecognized";
  model: { id: string; display_name: string };
  prediction: PredictionItem | null;
  top3: PredictionItem[];
  nutrition: Nutrition | null;
  latency_ms: number;
};
