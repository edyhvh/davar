import { createClient } from "@supabase/supabase-js";

// Prefer import.meta.env in browser and allow process.env fallback when inlined by bundlers.
const importMetaEnv = (import.meta as any).env || {};
const processEnv =
  typeof process !== "undefined" && (process as any).env
    ? (process as any).env
    : {};

const getPublicEnv = (key: string): string => {
  const value = importMetaEnv[key] ?? processEnv[key];
  return typeof value === "string" ? value : "";
};

const supabaseUrl = getPublicEnv("PUBLIC_SUPABASE_URL");
const supabaseAnonKey = getPublicEnv("PUBLIC_SUPABASE_ANON_KEY");

let supabase: ReturnType<typeof createClient> | null = null;

if (supabaseUrl && supabaseAnonKey) {
  try {
    new URL(supabaseUrl);
    supabase = createClient(supabaseUrl, supabaseAnonKey);
  } catch {
    console.warn("Skipping Supabase initialization: PUBLIC_SUPABASE_URL must be a valid URL");
  }
} else {
  console.warn(
    "Skipping Supabase initialization: missing PUBLIC_SUPABASE_URL or PUBLIC_SUPABASE_ANON_KEY",
  );
}

export { supabase };

export const fetchTs2009Translation = async (
  book: string,
  chapter: number,
  verse: number,
): Promise<string | null> => {
  if (!supabase) {
    return null;
  }

  try {
    const fileName = `${book}/${chapter}/${verse}.json`;
    const { data, error } = await supabase.storage
      .from("ts2009")
      .download(fileName);

    if (error) {
      console.warn(`TS2009 not available for ${book} ${chapter}:${verse}:`, error);
      return null;
    }

    const content = await data.text();
    const json = JSON.parse(content);
    return json.translation || null;
  } catch (error) {
    console.warn(`Failed to fetch TS2009 for ${book} ${chapter}:${verse}:`, error);
    return null;
  }
};