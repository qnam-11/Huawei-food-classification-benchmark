"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import ErrorBanner from "@/components/ErrorBanner";
import ImageUploader from "@/components/ImageUploader";
import LanguageToggle from "@/components/LanguageToggle";
import ModelSelect from "@/components/ModelSelect";
import NutritionTable from "@/components/NutritionTable";
import ResultCard from "@/components/ResultCard";
import UnrecognizedNotice from "@/components/UnrecognizedNotice";
import { useLanguage } from "@/i18n/LanguageProvider";
import { ApiError, fetchModels, predict } from "@/lib/api";
import type { ModelsResponse, ModelSummary, PredictResponse } from "@/types/api";

export default function Home() {
  const { t } = useLanguage();
  const [models, setModels] = useState<ModelSummary[]>([]);
  const [modelsLoading, setModelsLoading] = useState(true);
  const [modelsError, setModelsError] = useState<string | null>(null);
  const [modelId, setModelId] = useState("");
  const [maxUploadMb, setMaxUploadMb] = useState(10);
  const [file, setFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<PredictResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const abortRef = useRef<AbortController | null>(null);

  const applyModels = useCallback((data: ModelsResponse) => {
    setModels(data.models);
    setMaxUploadMb(data.max_upload_mb);
    setModelId((current) => current || data.models[0]?.id || "");
    setModelsLoading(false);
    setModelsError(null);
  }, []);

  const loadModels = useCallback(async () => {
    setModelsLoading(true);
    setModelsError(null);
    try {
      applyModels(await fetchModels());
    } catch (err) {
      setModelsLoading(false);
      setModelsError(err instanceof ApiError ? err.code : "inference_failed");
    }
  }, [applyModels]);

  useEffect(() => {
    fetchModels()
      .then(applyModels)
      .catch((err) => {
        setModelsLoading(false);
        setModelsError(err instanceof ApiError ? err.code : "inference_failed");
      });
  }, [applyModels]);

  useEffect(() => {
    return () => {
      if (previewUrl) URL.revokeObjectURL(previewUrl);
    };
  }, [previewUrl]);

  function handleSelect(next: File) {
    setResult(null);
    setError(null);
    setFile(next);
    setPreviewUrl(URL.createObjectURL(next));
  }

  async function handleAnalyze() {
    if (!file || !modelId) return;
    abortRef.current?.abort();
    const controller = new AbortController();
    abortRef.current = controller;
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const data = await predict(file, modelId, controller.signal);
      setResult(data);
    } catch (err) {
      if (err instanceof DOMException && err.name === "AbortError") return;
      setError(err instanceof ApiError ? err.code : "inference_failed");
    } finally {
      if (abortRef.current === controller) setLoading(false);
    }
  }

  const canAnalyze = Boolean(file && modelId) && !loading;

  return (
    <main className="mx-auto w-full max-w-3xl px-4 py-10">
      <header className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <h1 className="text-3xl font-semibold tracking-tight text-neutral-900">
            {t("appTitle")}
          </h1>
          <p className="mt-1 max-w-xl text-sm text-neutral-600">
            {t("appSubtitle")}
          </p>
        </div>
        <LanguageToggle />
      </header>

      <section className="mt-8 space-y-5">
        <ImageUploader
          previewUrl={previewUrl}
          maxUploadMb={maxUploadMb}
          disabled={loading}
          onSelect={handleSelect}
          onError={(code) => {
            setResult(null);
            setError(code);
          }}
        />

        <ModelSelect
          models={models}
          value={modelId}
          disabled={loading || modelsLoading}
          onChange={(id) => {
            setModelId(id);
            setResult(null);
          }}
        />

        {modelsLoading ? (
          <p className="text-sm text-neutral-500">{t("loadingModels")}</p>
        ) : null}

        {modelsError ? (
          <ErrorBanner
            code={modelsError}
            maxUploadMb={maxUploadMb}
            onRetry={loadModels}
          />
        ) : null}

        <button
          type="button"
          onClick={handleAnalyze}
          disabled={!canAnalyze}
          className="w-full rounded-xl bg-emerald-600 px-4 py-3 text-base font-medium text-white transition-colors hover:bg-emerald-700 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-emerald-600 disabled:cursor-not-allowed disabled:opacity-50"
        >
          {loading ? t("analyzing") : t("analyze")}
        </button>

        {error ? <ErrorBanner code={error} maxUploadMb={maxUploadMb} /> : null}

        {result?.status === "ok" ? <ResultCard result={result} /> : null}
        {result?.status === "ok" && result.nutrition ? (
          <NutritionTable nutrition={result.nutrition} />
        ) : null}
        {result?.status === "unrecognized" ? (
          <UnrecognizedNotice top3={result.top3} />
        ) : null}
      </section>

      <footer className="mt-10 text-xs text-neutral-500">
        {t("footerNote")}
      </footer>
    </main>
  );
}
