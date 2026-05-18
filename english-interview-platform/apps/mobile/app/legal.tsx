import { router } from "expo-router";
import { Pressable, SafeAreaView, ScrollView, StyleSheet, Text, View } from "react-native";

export default function LegalScreen() {
  return (
    <SafeAreaView style={styles.safe}>
      <ScrollView contentContainerStyle={styles.container}>
        <Text style={styles.kicker}>Legal</Text>
        <Text style={styles.title}>Privacy & voice data</Text>
        <Text style={styles.updated}>Last updated: 2026-05-17 · MVP beta</Text>

        <View style={styles.card}>
          <Text style={styles.sectionTitle}>What we collect</Text>
          <Text style={styles.body}>
            Quest English stores your interview practice sessions, text answers (including
            speech-to-text transcripts), and progress stamps. We use an anonymous device
            identifier (`X-Device-Id`) to associate passport stamps with your device.
          </Text>
        </View>

        <View style={styles.card}>
          <Text style={styles.sectionTitle}>Voice & third-party ASR</Text>
          <Text style={styles.body}>
            When you enable automatic transcription, audio may be sent to OpenAI Whisper for
            speech-to-text. Do not enable this feature with an API key you do not trust. You can
            always type your answer manually instead.
          </Text>
          <Text style={styles.body}>
            Audio files are kept on your device temporarily during practice and are deleted after
            submit or re-record. We do not store raw audio on our servers in this MVP.
          </Text>
        </View>

        <View style={styles.card}>
          <Text style={styles.sectionTitle}>How long we keep data</Text>
          <Text style={styles.body}>
            Session records and passport stamps are retained for product improvement during the
            beta. You may request deletion by contacting the team running this beta build.
          </Text>
        </View>

        <View style={styles.card}>
          <Text style={styles.sectionTitle}>Not for children</Text>
          <Text style={styles.body}>
            This app is not intended for users under 13. By continuing, you confirm you meet this
            requirement.
          </Text>
        </View>

        <Pressable style={styles.button} onPress={() => router.back()}>
          <Text style={styles.buttonText}>Back</Text>
        </Pressable>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safe: { flex: 1, backgroundColor: "#f6f1e8" },
  container: { paddingHorizontal: 24, paddingTop: 48, paddingBottom: 40 },
  kicker: {
    color: "#8a5a2b",
    fontSize: 14,
    marginBottom: 10,
    textTransform: "uppercase",
    letterSpacing: 1.2
  },
  title: { color: "#1d2a35", fontSize: 30, fontWeight: "700", marginBottom: 8 },
  updated: { color: "#6b7c8f", fontSize: 13, marginBottom: 20 },
  card: {
    padding: 18,
    borderRadius: 18,
    backgroundColor: "#fff8ef",
    marginBottom: 14
  },
  sectionTitle: { color: "#1d2a35", fontSize: 17, fontWeight: "600", marginBottom: 8 },
  body: { color: "#425466", fontSize: 15, lineHeight: 22, marginBottom: 10 },
  button: {
    alignSelf: "flex-start",
    marginTop: 8,
    paddingHorizontal: 16,
    paddingVertical: 12,
    borderRadius: 999,
    backgroundColor: "#8a5a2b"
  },
  buttonText: { color: "#fffaf3", fontSize: 14, fontWeight: "600" }
});
