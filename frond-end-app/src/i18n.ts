// I18n store reativo para o UI Svelte.
// Uso em templates: {$t('chave')} ou {$t('chave', { nome: 'X' })}.
// Persiste a escolha em localStorage; default detecta navigator.language.
//
// API:
//   locale         - store writable, valores 'pt-BR' | 'en-US'
//   setLocale(c)   - troca e persiste
//   t              - store derivado: ($t)(key, params?) => string
//   localeForCore  - store derivado: 'pt' | 'en' (formato curto para CLI)

import { derived, get, writable } from "svelte/store";
import { messages as ptBR } from "./messages/pt-BR";
import { messages as enUS } from "./messages/en-US";

export type Locale = "pt-BR" | "en-US";

const LOCALE_STORAGE_KEY = "bi-doc-maker-lang";

const CATALOGS: Record<Locale, Record<string, string>> = {
  "pt-BR": ptBR,
  "en-US": enUS,
};

function detectInitialLocale(): Locale {
  if (typeof localStorage !== "undefined") {
    const stored = localStorage.getItem(LOCALE_STORAGE_KEY);
    if (stored === "pt-BR" || stored === "en-US") {
      return stored;
    }
  }
  if (typeof navigator !== "undefined") {
    const sys = navigator.language?.toLowerCase() ?? "";
    if (sys.startsWith("en")) return "en-US";
  }
  return "pt-BR";
}

export const locale = writable<Locale>(detectInitialLocale());

export function setLocale(next: Locale): void {
  locale.set(next);
  if (typeof localStorage !== "undefined") {
    localStorage.setItem(LOCALE_STORAGE_KEY, next);
  }
}

function interpolate(template: string, params?: Record<string, string | number>): string {
  if (!params) return template;
  let out = template;
  for (const [k, v] of Object.entries(params)) {
    // Replace {key} occurrences (sem regex pra evitar escape de chars)
    out = out.split(`{${k}}`).join(String(v));
  }
  return out;
}

/**
 * Translator store reativo. Usar como `$t("chave")` em templates Svelte.
 * Fallback: locale ativo -> pt-BR -> `[?key]`.
 */
export const t = derived(locale, ($locale) => {
  return (key: string, params?: Record<string, string | number>): string => {
    const primary = CATALOGS[$locale][key];
    const fallback = CATALOGS["pt-BR"][key];
    const template = primary ?? fallback ?? `[?${key}]`;
    return interpolate(template, params);
  };
});

/**
 * Codigo curto do locale (pt/en) para passar ao backend Rust/Python.
 */
export const localeForCore = derived(locale, ($locale) =>
  $locale === "en-US" ? "en" : "pt"
);

/**
 * Versao nao-reativa do t() para uso fora do template Svelte (ex: handlers).
 */
export function translate(key: string, params?: Record<string, string | number>): string {
  const current = get(locale);
  const primary = CATALOGS[current][key];
  const fallback = CATALOGS["pt-BR"][key];
  const template = primary ?? fallback ?? `[?${key}]`;
  return interpolate(template, params);
}
