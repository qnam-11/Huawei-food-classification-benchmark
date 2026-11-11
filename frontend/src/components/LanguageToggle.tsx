"use client";

import { useLanguage, type Lang } from "@/i18n/LanguageProvider";

const OPTIONS: Lang[] = ["en", "vi"];

export default function LanguageToggle() {
  const { lang, setLang, t } = useLanguage();

  return (
    <div
      className="inline-flex overflow-hidden rounded-lg border border-neutral-300"
      role="group"
      aria-label={t("language")}
    >
      {OPTIONS.map((option) => (
        <button
          key={option}
          type="button"
          aria-pressed={lang === option}
          onClick={() => setLang(option)}
          className={`px-3 py-1.5 text-sm font-medium transition-colors focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-emerald-600 ${
            lang === option
              ? "bg-neutral-900 text-white"
              : "bg-white text-neutral-600 hover:bg-neutral-100"
          }`}
        >
          {option.toUpperCase()}
        </button>
      ))}
    </div>
  );
}
