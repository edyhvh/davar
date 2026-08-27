import { Fragment, useCallback, useMemo, type ReactNode } from "react";
import { Alert, ScrollView, StyleSheet, Text, View } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";

import { AppIcon } from "@/src/components/ui/AppIcon";
import { PillToggle } from "@/src/components/ui/PillToggle";
import { OnOffButton } from "@/src/components/ui/OnOffButton";
import { SettingsDropdown } from "@/src/components/ui/SettingsDropdown";
import { getColors, radii, spacing, typography } from "@/src/theme";
import { useAppStore, type AppState } from "@/src/store/useAppStore";
import { clearStorage } from "@/src/services/storage";
import { useTranslation } from "@/src/i18n/useTranslation";
import {
  SHARED_SETTINGS_ORDER,
  canUseSeferStyle,
  isSeferStyleVisible,
  type SharedSettingId,
} from "@davar/shared/settingsOrder";
