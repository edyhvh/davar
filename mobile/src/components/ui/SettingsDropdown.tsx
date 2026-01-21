import { useMemo, useState } from "react";
import { Modal, Pressable, StyleSheet, Text, View } from "react-native";
import { Ionicons } from "@expo/vector-icons";

import { getColors, radii, spacing, typography } from "@/src/theme";
import { useAppStore, type AppState } from "@/src/store/useAppStore";

type SettingsDropdownOption<T extends string> = {
  label: string;
  value: T;
};

type SettingsDropdownProps<T extends string> = {
  label?: string;
  value: T;
  options: SettingsDropdownOption<T>[];
  onChange: (value: T) => void;
};

const createStyles = (colors: ReturnType<typeof getColors>) =>
  StyleSheet.create({
    trigger: {
      borderWidth: 1,
      borderColor: colors.border,
      borderRadius: radii.full,
      backgroundColor: colors.surface,
      paddingHorizontal: spacing[4],
      paddingVertical: spacing[3],
      flexDirection: "row",
      alignItems: "center",
      gap: spacing[2],
      minWidth: 120,
    },
    triggerLabel: {
      fontFamily: typography.families.latinUI,
      fontSize: typography.sizes.body,
      color: colors.textPrimary,
    },
    modalOverlay: {
      flex: 1,
      backgroundColor: "rgba(0,0,0,0.3)",
      justifyContent: "center",
      alignItems: "center",
    },
    optionsContainer: {
      backgroundColor: colors.surface,
      borderRadius: radii.lg,
      minWidth: 200,
      overflow: "hidden",
      shadowColor: "#000",
      shadowOffset: { width: 0, height: 4 },
      shadowOpacity: 0.15,
      shadowRadius: 12,
      elevation: 8,
    },
    option: {
      paddingHorizontal: spacing[5],
      paddingVertical: spacing[4],
      borderBottomWidth: StyleSheet.hairlineWidth,
      borderBottomColor: colors.border,
    },
    optionLast: {
      borderBottomWidth: 0,
    },
    optionText: {
      fontFamily: typography.families.latinUI,
      fontSize: typography.sizes.body,
      color: colors.textPrimary,
      textAlign: "center",
    },
    optionActive: {
      backgroundColor: colors.primaryLight,
    },
    optionTextActive: {
      color: colors.primaryDark,
      fontWeight: typography.weights.medium,
    },
  });

export const SettingsDropdown = <T extends string>({
  value,
  options,
  onChange,
}: SettingsDropdownProps<T>) => {
  const themeMode = useAppStore((state: AppState) => state.themeMode);
  const colors = getColors(themeMode);
  const styles = useMemo(() => createStyles(colors), [colors]);
  const [open, setOpen] = useState(false);
  const selected = options.find((option) => option.value === value);

  return (
    <>
      <Pressable style={styles.trigger} onPress={() => setOpen(true)}>
        <Text style={styles.triggerLabel}>{selected?.label ?? ""}</Text>
        <Ionicons name="chevron-down" size={16} color={colors.textSecondary} />
      </Pressable>
      <Modal
        visible={open}
        transparent
        animationType="fade"
        onRequestClose={() => setOpen(false)}
      >
        <Pressable style={styles.modalOverlay} onPress={() => setOpen(false)}>
          <View style={styles.optionsContainer}>
            {options.map((option, index) => {
              const isActive = option.value === value;
              return (
                <Pressable
                  key={option.value}
                  onPress={() => {
                    onChange(option.value);
                    setOpen(false);
                  }}
                  style={[
                    styles.option,
                    index === options.length - 1 && styles.optionLast,
                    isActive && styles.optionActive,
                  ]}
                >
                  <Text
                    style={[
                      styles.optionText,
                      isActive && styles.optionTextActive,
                    ]}
                  >
                    {option.label}
                  </Text>
                </Pressable>
              );
            })}
          </View>
        </Pressable>
      </Modal>
    </>
  );
};
