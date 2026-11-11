"use client";

import { useLanguage } from "@/i18n/LanguageProvider";
import type { ModelSummary } from "@/types/api";

type Props = {
  models: ModelSummary[];
  value: string;
  disabled?: boolean;
  onChange: (modelId: string) => void;
};

export default function ModelSelect({
  models,
  value,
  disabled,
  onChange,
}: Props) {
  const { t } = useLanguage();

  return (
    <label className="block">
      <span className="mb-1.5 block text-sm font-medium text-neutral-700">
        {t("chooseModel")}
      </span>
      <select
        value={value}
        disabled={disabled || models.length === 0}
        onChange={(event) => onChange(event.target.value)}
        className="w-full rounded-lg border border-neutral-300 bg-white px-3 py-2.5 text-sm text-neutral-900 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-emerald-600 disabled:opacity-50"
      >
        <option value="" disabled>
          {models.length === 0 ? t("loadingModels") : t("chooseModel")}
        </option>
        {models.map((model) => (
          <option key={model.id} value={model.id}>
            {model.display_name} · {t("f1Label")}{" "}
            {(model.val_macro_f1 * 100).toFixed(1)}%
          </option>
        ))}
      </select>
    </label>
  );
}
