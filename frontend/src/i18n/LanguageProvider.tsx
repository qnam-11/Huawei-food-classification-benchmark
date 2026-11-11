"use client";

import {
  createContext,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";
import { en, type Dict } from "./en";
import { vi } from "./vi";

export type Lang = "en" | "vi";

const dictionaries: Record<Lang, Dict> = { en, vi };

type Vars = Record<string, string | number>;

type LanguageContextValue = {
  lang: Lang;
  setLang: (lang: Lang) => void;
  t: (key: keyof Dict, vars?: Vars) => string;
  tError: (code: string, vars?: Vars) => string;
};

const LanguageContext = createContext<LanguageContextValue | null>(null);

export function LanguageProvider({ children }: { children: ReactNode }) {
  const [lang, setLangState] = useState<Lang>("en");

  useEffect(() => {
    // localStorage and navigator are only readable after hydration
    const saved = window.localStorage.getItem("lang");
    const preferred =
      saved === "en" || saved === "vi"
        ? saved
        : navigator.language.toLowerCase().startsWith("vi")
          ? "vi"
          : "en";
    // eslint-disable-next-line react-hooks/set-state-in-effect -- browser-only preference
    setLangState(preferred);
  }, []);

  useEffect(() => {
    document.documentElement.lang = lang;
  }, [lang]);

  const value = useMemo<LanguageContextValue>(() => {
    const dict = dictionaries[lang];
    const format = (text: string, vars?: Vars) => {
      if (!vars) return text;
      return Object.entries(vars).reduce(
        (result, [key, value]) =>
          result.replaceAll(`{${key}}`, String(value)),
        text,
      );
    };
    return {
      lang,
      setLang: (next) => {
        setLangState(next);
        window.localStorage.setItem("lang", next);
      },
      t: (key, vars) => format(dict[key], vars),
      tError: (code, vars) =>
        format(dict[code as keyof Dict] ?? dict.inference_failed, vars),
    };
  }, [lang]);

  return (
    <LanguageContext.Provider value={value}>{children}</LanguageContext.Provider>
  );
}

export function useLanguage() {
  const context = useContext(LanguageContext);
  if (!context) {
    throw new Error("useLanguage must be used inside LanguageProvider");
  }
  return context;
}
