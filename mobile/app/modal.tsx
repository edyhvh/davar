import { useCallback, useMemo, useRef, useEffect } from "react";
import { StyleSheet, View } from "react-native";
import { router } from "expo-router";
import BottomSheet from "@gorhom/bottom-sheet";

import { getColors } from "@/src/theme";
import { mockVerses } from "@/src/constants/mockData";
import { useAppStore, type AppState } from "@/src/store/useAppStore";
import { BookSelectorSheet } from "@/src/components/BookSelectorSheet";

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
    (bookId: string) => {
      const nextVerse = mockVerses.find((verse) => verse.bookId === bookId);
      if (nextVerse) {
        setCurrentVerseId(nextVerse.id);
      }
      router.back();
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
