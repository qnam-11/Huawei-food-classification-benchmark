"use client";

import { useLanguage } from "@/i18n/LanguageProvider";
import type { PredictResponse } from "@/types/api";

type Props = {
  result: PredictResponse;
};

export default function ResultCard({ result }: Props) {
  const { lang, t } = useLanguage();
  const prediction = result.prediction;
  if (!prediction) return null;

  const primary = lang === "vi" ? prediction.name_vi : prediction.name_en;
  const secondary = lang === "vi" ? prediction.name_en : prediction.name_vi;
  const percent = Math.round(prediction.confidence * 100);

  return (
    <section className="rounded-2xl border border-neutral-200 bg-white p-5 shadow-sm">
      <div className="flex items-start justify-between gap-4">
        <div>
          <h2 className="text-2xl font-semibold text-neutral-900">{primary}</h2>
          <p className="text-sm text-neutral-500">{secondary}</p>
        </div>
        <span className="shrink-0 rounded-full bg-neutral-100 px-3 py-1 text-xs font-medium text-neutral-600">
          {result.model.display_name}
        </span>
      </div>

      <div className="mt-4">
        <div className="flex justify-between text-sm text-neutral-600">
          <span>{t("confidence")}</span>
          <span className="font-medium text-neutral-900">{percent}%</span>
        </div>
        <div className="mt-1.5 h-2 rounded-full bg-neutral-200">
          <div
            className="h-2 rounded-full bg-emerald-500"
            style={{ width: `${percent}%` }}
          />
        </div>
      </div>

      <div className="mt-5 border-t border-neutral-100 pt-4">
        <h3 className="text-sm font-medium text-neutral-600">{t("top3")}</h3>
        <ul className="mt-2 space-y-1.5">
          {result.top3.map((item) => (
            <li
              key={item.slug}
              className="flex justify-between gap-4 text-sm text-neutral-700"
            >
              <span>{lang === "vi" ? item.name_vi : item.name_en}</span>
              <span className="tabular-nums text-neutral-500">
                {(item.confidence * 100).toFixed(1)}%
              </span>
            </li>
          ))}
        </ul>
      </div>
    </section>
  );
}
