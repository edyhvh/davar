import { View, StyleSheet } from "react-native";

import { Skeleton } from "@/src/components/ui/Skeleton";
import { spacing, radii } from "@/src/theme";

const WORD_WIDTHS = [58, 44, 72, 52, 66, 48];
const WORD_HEIGHT = 36;
const STAGGER_MS = 80;

type VerseCardSkeletonProps = {
  pageHeight: number;
};

export const VerseCardSkeleton = ({ pageHeight }: VerseCardSkeletonProps) => {
  return (
    <View style={[styles.container, { height: pageHeight }]}>
      {/* Hebrew word row */}
      <View style={styles.hebrewRow}>
        {WORD_WIDTHS.map((w, i) => (
          <Skeleton
            key={i}
            width={w}
            height={WORD_HEIGHT}
            borderRadius={radii.sm}
            delay={i * STAGGER_MS}
          />
        ))}
      </View>

      {/* Translation lines */}
      <View style={styles.translationArea}>
        <Skeleton
          width="70%"
          height={14}
          borderRadius={radii.sm}
          delay={WORD_WIDTHS.length * STAGGER_MS}
        />
        <Skeleton
          width="45%"
          height={14}
          borderRadius={radii.sm}
          delay={(WORD_WIDTHS.length + 1) * STAGGER_MS}
        />
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    alignItems: "center",
    justifyContent: "center",
    paddingHorizontal: spacing[4],
  },
  hebrewRow: {
    flexDirection: "row-reverse",
    flexWrap: "wrap",
    justifyContent: "center",
    columnGap: spacing[2],
    rowGap: spacing[2],
  },
  translationArea: {
    alignItems: "center",
    marginTop: spacing[6],
    gap: spacing[2],
  },
});
