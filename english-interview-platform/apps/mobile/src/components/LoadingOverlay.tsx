import { ActivityIndicator, Modal, StyleSheet, Text, View } from "react-native";

type LoadingOverlayProps = {
  visible: boolean;
  message?: string;
  /** card = inline section; fullscreen = modal overlay for blocking actions */
  mode?: "card" | "fullscreen";
};

export function LoadingOverlay({
  visible,
  message = "Loading…",
  mode = "card"
}: LoadingOverlayProps) {
  if (!visible) {
    return null;
  }

  if (mode === "fullscreen") {
    return (
      <Modal visible transparent animationType="fade" statusBarTranslucent>
        <View style={styles.fullscreenBackdrop}>
          <View style={styles.fullscreenCard}>
            <ActivityIndicator color="#8a5a2b" size="large" />
            <Text style={styles.fullscreenMessage}>{message}</Text>
          </View>
        </View>
      </Modal>
    );
  }

  return (
    <View style={styles.card} accessibilityRole="progressbar">
      <ActivityIndicator color="#8a5a2b" />
      <Text style={styles.cardMessage}>{message}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  card: {
    padding: 18,
    borderRadius: 18,
    backgroundColor: "#fff8ef",
    alignItems: "center",
    gap: 12
  },
  cardMessage: { color: "#425466", fontSize: 14, textAlign: "center" },
  fullscreenBackdrop: {
    flex: 1,
    backgroundColor: "rgba(29, 42, 53, 0.35)",
    alignItems: "center",
    justifyContent: "center",
    padding: 24
  },
  fullscreenCard: {
    minWidth: 220,
    paddingVertical: 28,
    paddingHorizontal: 24,
    borderRadius: 20,
    backgroundColor: "#fffaf3",
    alignItems: "center",
    gap: 14,
    borderWidth: 1,
    borderColor: "#ead9c0"
  },
  fullscreenMessage: {
    color: "#1d2a35",
    fontSize: 15,
    fontWeight: "600",
    textAlign: "center"
  }
});
