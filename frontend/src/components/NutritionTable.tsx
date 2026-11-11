"use client";

import { useLanguage } from "@/i18n/LanguageProvider";
import type { Dict } from "@/i18n/en";
import type { Macros, Nutrition } from "@/types/api";

const ROWS: { key: keyof Macros; label: keyof Dict }[] = [
  { key: "kcal", label: "kcal" },
  { key: "protein_g", label: "protein" },
  { key: "carb_g", label: "carb" },
  { key: "fat_g", label: "fat" },
];

function format(key: keyof Macros, value: number) {
  return key === "kcal" ? String(Math.round(value)) : value.toFixed(1);
}

export default function NutritionTable({ nutrition }: { nutrition: Nutrition }) {
  const { t } = useLanguage();
  const { per_100g: per100, per_serving: perServing } = nutrition;

  return (
    <section className="rounded-2xl border border-neutral-200 bg-white p-5 shadow-sm">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <h2 className="text-lg font-semibold text-neutral-900">
          {t("per_100g")} / {t("per_serving")}
        </h2>
        <span className="text-xs text-neutral-500">
          {t("serving")}: {nutrition.serving_g} g
        </span>
      </div>

      {!nutrition.verified ? (
        <p className="mt-3 inline-block rounded-full bg-amber-100 px-3 py-1 text-xs font-medium text-amber-800">
          {t("draft_badge")}
        </p>
      ) : null}

      <table className="mt-4 w-full text-sm">
        <thead>
          <tr className="text-left text-xs uppercase tracking-wide text-neutral-500">
            <th className="pb-2 font-medium" />
            <th className="pb-2 text-right font-medium">{t("per_100g")}</th>
            <th className="pb-2 text-right font-medium">{t("per_serving")}</th>
          </tr>
        </thead>
        <tbody>
          {ROWS.map((row) => {
            const a = per100[row.key];
            const b = perServing[row.key];
            const max = Math.max(a, b, 0.0001);
            return (
              <tr key={row.key} className="border-t border-neutral-100">
                <th className="py-2.5 text-left font-medium text-neutral-700">
                  {t(row.label)}
                </th>
                <td className="py-2.5 text-right tabular-nums text-neutral-900">
                  {format(row.key, a)}
                  <div className="ml-auto mt-1 h-1.5 w-16 rounded-full bg-neutral-200">
                    <div
                      className="h-1.5 rounded-full bg-emerald-500"
                      style={{ width: `${(a / max) * 100}%` }}
                    />
                  </div>
                </td>
                <td className="py-2.5 text-right tabular-nums text-neutral-900">
                  {format(row.key, b)}
                  <div className="ml-auto mt-1 h-1.5 w-16 rounded-full bg-neutral-200">
                    <div
                      className="h-1.5 rounded-full bg-emerald-500"
                      style={{ width: `${(b / max) * 100}%` }}
                    />
                  </div>
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </section>
  );
}
