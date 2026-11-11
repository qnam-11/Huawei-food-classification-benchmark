"use client";

import { useLanguage } from "@/i18n/LanguageProvider";

type Props = {
  code: string;
  maxUploadMb?: number;
  onRetry?: () => void;
};

export default function ErrorBanner({ code, maxUploadMb, onRetry }: Props) {
  const { t, tError } = useLanguage();

  return (
    <div
      role="alert"
      className="flex items-start justify-between gap-4 rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-800"
    >
      <p>{tError(code, maxUploadMb ? { mb: maxUploadMb } : undefined)}</p>
      {onRetry ? (
        <button
          type="button"
          onClick={onRetry}
          className="shrink-0 rounded-md border border-red-300 px-2.5 py-1 font-medium hover:bg-red-100"
        >
          {t("retry")}
        </button>
      ) : null}
    </div>
  );
}
