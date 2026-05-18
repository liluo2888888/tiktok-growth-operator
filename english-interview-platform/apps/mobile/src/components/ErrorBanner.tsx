import { Pressable, StyleSheet, Text, View } from "react-native";

type ErrorBannerProps = {
  title?: string;
  message: string;
  onRetry?: () => void;
  retryLabel?: string;
};

export function ErrorBanner({ title, message, onRetry, retryLabel = "Retry" }: ErrorBannerProps) {
  return (
    <View style={styles.banner} accessibilityRole="alert">
      {!!title && <Text style={styles.title}>{title}</Text>}
      <Text style={styles.message}>{message}</Text>
      {!!onRetry && (
        <Pressable style={styles.button} onPress={onRetry}>
          <Text style={styles.buttonText}>{retryLabel}</Text>
        </Pressable>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  banner: {
    padding: 18,
    borderRadius: 18,
    backgroundColor: "#fff1f0",
    borderWidth: 1,
    borderColor: "#f0c4c0"
  },
  title: { color: "#7a1f1f", fontSize: 15, fontWeight: "700", marginBottom: 6 },
  message: { color: "#9b2c2c", fontSize: 14, lineHeight: 20, marginBottom: 12 },
  button: {
    alignSelf: "flex-start",
    paddingHorizontal: 14,
    paddingVertical: 10,
    borderRadius: 999,
    backgroundColor: "#8a5a2b"
  },
  buttonText: { color: "#fffaf3", fontSize: 14, fontWeight: "600" }
});
