import { Modal, Pressable, StyleSheet, Text, View } from "react-native";

import { PassportStampCard } from "@/components/PassportStampCard";
import type { PassportStamp } from "@/storage/passportStamps";

type StampEarnedModalProps = {
  visible: boolean;
  stamp: PassportStamp | null;
  onViewPassport: () => void;
  onDismiss: () => void;
};

export function StampEarnedModal({
  visible,
  stamp,
  onViewPassport,
  onDismiss
}: StampEarnedModalProps) {
  if (!stamp) {
    return null;
  }

  return (
    <Modal visible={visible} transparent animationType="fade" onRequestClose={onDismiss}>
      <View style={styles.backdrop}>
        <View style={styles.sheet}>
          <Text style={styles.kicker}>New stamp</Text>
          <Text style={styles.title}>Passport updated</Text>
          <Text style={styles.body}>
            You earned a progress stamp for completing this interview round.
          </Text>
          <PassportStampCard stamp={stamp} />
          <View style={styles.actions}>
            <Pressable style={styles.button} onPress={onViewPassport}>
              <Text style={styles.buttonText}>View Passport</Text>
            </Pressable>
            <Pressable style={styles.secondaryButton} onPress={onDismiss}>
              <Text style={styles.secondaryButtonText}>Continue</Text>
            </Pressable>
          </View>
        </View>
      </View>
    </Modal>
  );
}

const styles = StyleSheet.create({
  backdrop: {
    flex: 1,
    backgroundColor: "rgba(29, 42, 53, 0.45)",
    justifyContent: "center",
    paddingHorizontal: 24
  },
  sheet: {
    borderRadius: 22,
    backgroundColor: "#f6f1e8",
    padding: 22,
    gap: 12
  },
  kicker: {
    color: "#8a5a2b",
    fontSize: 12,
    textTransform: "uppercase",
    letterSpacing: 1.2,
    fontWeight: "700"
  },
  title: { color: "#1d2a35", fontSize: 26, fontWeight: "700" },
  body: { color: "#425466", fontSize: 15, lineHeight: 22 },
  actions: { gap: 10, marginTop: 4 },
  button: {
    paddingVertical: 12,
    borderRadius: 999,
    backgroundColor: "#8a5a2b",
    alignItems: "center"
  },
  buttonText: { color: "#fffaf3", fontSize: 15, fontWeight: "600" },
  secondaryButton: {
    paddingVertical: 12,
    borderRadius: 999,
    backgroundColor: "#d9c2a2",
    alignItems: "center"
  },
  secondaryButtonText: { color: "#1d2a35", fontSize: 15, fontWeight: "600" }
});
