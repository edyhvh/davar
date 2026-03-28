import { createClient } from "@supabase/supabase-js";
import Constants from "expo-constants";

const PLACEHOLDER_SUPABASE_URL = "your-project-ref.supabase.co";
const PLACEHOLDER_SUPABASE_KEY = "your-supabase-anon-key";

const sanitizeConfigValue = (value: unknown): string | null => {
  if (typeof value !== "string") {
    return null;
  }

  const trimmed = value.trim();
  if (trimmed.length === 0) {
    return null;
  }

  return trimmed;
};

const looksLikePlaceholder = (value: string): boolean => {
  const normalized = value.toLowerCase();
  return (
    normalized.includes(PLACEHOLDER_SUPABASE_URL) ||
    normalized.includes(PLACEHOLDER_SUPABASE_KEY)
  );
};

const resolveSupabaseConfig = (): { url: string; anonKey: string } | null => {
  const envUrl = sanitizeConfigValue(process.env.EXPO_PUBLIC_SUPABASE_URL);
  const envAnonKey = sanitizeConfigValue(
    process.env.EXPO_PUBLIC_SUPABASE_ANON_KEY,
  );

  const extraUrl = sanitizeConfigValue(Constants.expoConfig?.extra?.supabaseUrl);
  const extraAnonKey = sanitizeConfigValue(
    Constants.expoConfig?.extra?.supabaseAnonKey,
  );

  const url = envUrl ?? extraUrl;
  const anonKey = envAnonKey ?? extraAnonKey;

  if (!url || !anonKey) {
    return null;
  }

  if (looksLikePlaceholder(url) || looksLikePlaceholder(anonKey)) {
    return null;
  }

  return { url, anonKey };
};

const supabaseConfig = resolveSupabaseConfig();
export const supabase = supabaseConfig
  ? createClient(supabaseConfig.url, supabaseConfig.anonKey)
  : null;
