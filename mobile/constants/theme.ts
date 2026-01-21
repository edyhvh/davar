import { getColors, typography } from "@/src/theme";

export const Colors = {
  light: {
    ...getColors("light"),
    tint: getColors("light").primary,
    icon: getColors("light").textSecondary,
    tabIconDefault: getColors("light").textSecondary,
    tabIconSelected: getColors("light").primary,
    text: getColors("light").textPrimary,
  },
  dark: {
    ...getColors("dark"),
    tint: getColors("dark").primary,
    icon: getColors("dark").textSecondary,
    tabIconDefault: getColors("dark").textSecondary,
    tabIconSelected: getColors("dark").primary,
    text: getColors("dark").textPrimary,
  },
};

export const Fonts = {
  sans: typography.families.latinUI,
  serif: typography.families.hebrewScripture,
  rounded: typography.families.latinUI,
  mono: typography.families.latinUI,
};
