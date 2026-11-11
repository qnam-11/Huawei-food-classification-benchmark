"use client";

import { useRef, useState } from "react";
import Image from "next/image";
import { useLanguage } from "@/i18n/LanguageProvider";

const ACCEPTED_TYPES = ["image/jpeg", "image/png", "image/webp"];

type Props = {
  previewUrl: string | null;
  maxUploadMb: number;
  disabled?: boolean;
  onSelect: (file: File) => void;
  onError: (code: string) => void;
};

export default function ImageUploader({
  previewUrl,
  maxUploadMb,
  disabled,
  onSelect,
  onError,
}: Props) {
  const { t } = useLanguage();
  const inputRef = useRef<HTMLInputElement>(null);
  const [dragging, setDragging] = useState(false);

  function handleFile(file: File | undefined) {
    if (!file) return;
    if (!ACCEPTED_TYPES.includes(file.type)) {
      onError("unsupported_type");
      return;
    }
    if (file.size > maxUploadMb * 1024 * 1024) {
      onError("file_too_large");
      return;
    }
    onSelect(file);
  }

  return (
    <div>
      <input
        ref={inputRef}
        type="file"
        accept={ACCEPTED_TYPES.join(",")}
        hidden
        disabled={disabled}
        onChange={(event) => {
          handleFile(event.target.files?.[0]);
          event.target.value = "";
        }}
      />

      {previewUrl ? (
        <div className="overflow-hidden rounded-2xl border border-neutral-200 bg-white shadow-sm">
          <div className="relative aspect-[4/3] w-full bg-neutral-100">
            <Image
              src={previewUrl}
              alt=""
              fill
              unoptimized
              sizes="(max-width: 768px) 100vw, 768px"
              className="object-contain"
            />
          </div>
          <div className="flex justify-end border-t border-neutral-200 p-3">
            <button
              type="button"
              onClick={() => inputRef.current?.click()}
              disabled={disabled}
              className="rounded-lg border border-neutral-300 px-3 py-1.5 text-sm font-medium text-neutral-700 hover:bg-neutral-100 disabled:opacity-50"
            >
              {t("changePhoto")}
            </button>
          </div>
        </div>
      ) : (
        <button
          type="button"
          onClick={() => inputRef.current?.click()}
          onDragOver={(event) => {
            event.preventDefault();
            setDragging(true);
          }}
          onDragLeave={() => setDragging(false)}
          onDrop={(event) => {
            event.preventDefault();
            setDragging(false);
            handleFile(event.dataTransfer.files?.[0]);
          }}
          disabled={disabled}
          className={`flex w-full flex-col items-center justify-center gap-2 rounded-2xl border-2 border-dashed px-6 py-14 text-center transition-colors focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-emerald-600 disabled:opacity-50 ${
            dragging
              ? "border-emerald-500 bg-emerald-50"
              : "border-neutral-300 bg-white hover:border-neutral-400 hover:bg-neutral-50"
          }`}
        >
          <span className="text-base font-medium text-neutral-800">
            {t("uploadPrompt")}
          </span>
          <span className="text-sm text-neutral-500">
            {t("uploadHint", { mb: maxUploadMb })}
          </span>
        </button>
      )}
    </div>
  );
}
