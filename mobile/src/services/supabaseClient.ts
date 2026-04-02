import AsyncStorage from "@react-native-async-storage/async-storage";
import { createClient } from "@supabase/supabase-js";
import Constants from "expo-constants";

const PLACEHOLDER_SUPABASE_URL = "your-project-ref.supabase.co";
const PLACEHOLDER_SUPABASE_KEY = "your-supabase-key";
const PLACEHOLDER_SUPABASE_PUBLISHABLE_KEY = "your-supabase-publishable-key";
const PLACEHOLDER_SUPABASE_ANON_KEY = "your-supabase-anon-key";

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
    normalized.includes(PLACEHOLDER_SUPABASE_KEY) ||
    normalized.includes(PLACEHOLDER_SUPABASE_PUBLISHABLE_KEY) ||
    normalized.includes(PLACEHOLDER_SUPABASE_ANON_KEY)
  );
};

const resolveSupabaseConfig = (): { url: string; key: string } | null => {
  const envUrl = sanitizeConfigValue(process.env.EXPO_PUBLIC_SUPABASE_URL);
  const envKey = sanitizeConfigValue(process.env.EXPO_PUBLIC_SUPABASE_KEY);
  const envAnonKey = sanitizeConfigValue(
    process.env.EXPO_PUBLIC_SUPABASE_ANON_KEY,
  );

  const extraUrl = sanitizeConfigValue(Constants.expoConfig?.extra?.supabaseUrl);
  const extraKey = sanitizeConfigValue(Constants.expoConfig?.extra?.supabaseKey);
  const extraAnonKey = sanitizeConfigValue(
    Constants.expoConfig?.extra?.supabaseAnonKey,
  );

  const url = envUrl ?? extraUrl;
  const key = envKey ?? envAnonKey ?? extraKey ?? extraAnonKey;

  if (!url || !key) {
    return null;
  }

  if (looksLikePlaceholder(url) || looksLikePlaceholder(key)) {
    return null;
  }

  return { url, key };
};

const supabaseConfig = resolveSupabaseConfig();
export const supabase = supabaseConfig
  ? createClient(supabaseConfig.url, supabaseConfig.key, {
      auth: {
        storage: AsyncStorage,
        autoRefreshToken: true,
        persistSession: true,
        detectSessionInUrl: false,
      },
    })
  : null;
