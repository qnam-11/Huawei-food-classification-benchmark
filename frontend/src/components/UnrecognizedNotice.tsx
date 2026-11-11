"use client";

import { useLanguage } from "@/i18n/LanguageProvider";
import type { PredictionItem } from "@/types/api";

export default function UnrecognizedNotice({ top3 }: { top3: PredictionItem[] }) {
  const { lang, t } = useLanguage();

  return (
    <section
      role="status"
      className="rounded-2xl border border-amber-200 bg-amber-50 p-5 text-amber-900 shadow-sm"
    >
      <p className="font-medium">{t("unrecognized")}</p>
      {top3.length > 1 ? (
        <div className="mt-4">
          <h3 className="text-sm font-medium text-amber-800">{t("top3")}</h3>
          <ul className="mt-1.5 space-y-1">
            {top3.slice(1).map((item) => (
              <li
                key={item.slug}
                className="flex justify-between gap-4 text-sm text-amber-900/80"
              >
                <span>{lang === "vi" ? item.name_vi : item.name_en}</span>
                <span className="tabular-nums">
                  {(item.confidence * 100).toFixed(1)}%
                </span>
              </li>
            ))}
          </ul>
        </div>
      ) : null}
    </section>
  );
}
