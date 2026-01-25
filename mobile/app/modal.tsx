import { useCallback, useMemo, useRef, useEffect } from "react";
import { StyleSheet, View } from "react-native";
import { router } from "expo-router";
import BottomSheet from "@gorhom/bottom-sheet";

import { getColors } from "@/src/theme";
import { mockVerses } from "@/src/constants/mockData";
import { useAppStore, type AppState } from "@/src/store/useAppStore";
import { BookSelectorSheet } from "@/src/components/BookSelectorSheet";
import { fetchMetadata } from "@/src/services/metadata";

const createStyles = (colors: ReturnType<typeof getColors>) =>
  StyleSheet.create({
    container: {
      flex: 1,
      backgroundColor: "transparent",
    },
  });

export default function ModalScreen() {
  const themeMode = useAppStore((state: AppState) => state.themeMode);
  const setCurrentVerseId = useAppStore(
    (state: AppState) => state.setCurrentVerseId,
  );
  const currentVerseId = useAppStore((state: AppState) => state.currentVerseId);
  const colors = getColors(themeMode);
  const styles = useMemo(() => createStyles(colors), [colors]);
  const sheetRef = useRef<BottomSheet>(null);

  const currentBookId = useMemo(
    () => mockVerses.find((verse) => verse.id === currentVerseId)?.bookId,
    [currentVerseId],
  );

  useEffect(() => {
    // Open the sheet when the modal mounts
    const timer = setTimeout(() => {
      sheetRef.current?.snapToIndex(0);
    }, 100);
    return () => clearTimeout(timer);
  }, []);

  const handleSelectBook = useCallback(
    async (bookId: string) => {
      try {
        const metadata = await fetchMetadata();
        const chapters = metadata?.chapter_counts?.[bookId];
        const firstChapter = chapters && chapters.length > 0 ? chapters[0] : 1;
        console.debug("Modal: handleSelectBook", { bookId, firstChapter });
        setCurrentVerseId(`${bookId}-${firstChapter}-1`);
      } catch (err) {
        console.debug("Modal: handleSelectBook failed, using fallback firstChapter=1", { bookId, err });
        // Fallback if metadata fetch fails or book not found
        setCurrentVerseId(`${bookId}-1-1`);
      } finally {
        router.back();
      }
    },
    [setCurrentVerseId],
  );

  const handleClose = useCallback(() => {
    router.back();
  }, []);

  return (
    <View style={styles.container}>
      <BookSelectorSheet
        sheetRef={sheetRef}
        currentBookId={currentBookId}
        onSelectBook={handleSelectBook}
        onClose={handleClose}
      />
    </View>
  );
}
