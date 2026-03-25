import { createClient } from "@supabase/supabase-js";
import Constants from "expo-constants";

const supabaseUrl = Constants.expoConfig?.extra?.supabaseUrl;
const supabaseAnonKey = Constants.expoConfig?.extra?.supabaseAnonKey;

const validateSupabaseConfig = (value: unknown, name: string): string => {
  if (typeof value !== "string") {
    throw new Error(
      `Invalid Supabase configuration: ${name} must be a non-empty string`,
    );
  }

  const trimmed = value.trim();
  if (trimmed.length === 0) {
    throw new Error(
      `Missing Supabase configuration: ${name} is empty or whitespace`,
    );
  }

  return trimmed;
};

const validatedSupabaseUrl = validateSupabaseConfig(supabaseUrl, "supabaseUrl");
const validatedSupabaseAnonKey = validateSupabaseConfig(
  supabaseAnonKey,
  "supabaseAnonKey",
);

export const supabase = createClient(
  validatedSupabaseUrl,
  validatedSupabaseAnonKey,
);
export const fetchTs2009Translation = async (
  book: string,
  chapter: number,
  verse: number,
): Promise<string | null> => {
  try {
    const fileName = `${book}/${chapter}/${verse}.json`;
    const { data, error } = await supabase.storage
      .from("ts2009")
      .download(fileName);

    if (error) {
      console.warn(
        `TS2009 not available for ${book} ${chapter}:${verse}:`,
        error,
      );
      return null;
    }

    const content = await data.text();
    const json = JSON.parse(content);
    return json.translation || null;
  } catch (error) {
    console.warn(
      `Failed to fetch TS2009 for ${book} ${chapter}:${verse}:`,
      error,
    );
    return null;
  }
};
