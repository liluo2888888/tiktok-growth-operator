import { StyleSheet, Text, View } from "react-native";

type StageNextPanelProps = {
  stage: string;
  currentQuestion: string;
  status: string;
};

export function StageNextPanel({ stage, currentQuestion, status }: StageNextPanelProps) {
  const sessionEnded = status === "completed" || stage === "closing";

  return (
    <View style={styles.card}>
      <Text style={styles.title}>{sessionEnded ? "Round complete" : "Keep going"}</Text>
      <Text style={styles.meta}>Stage: {stage}</Text>
      {!sessionEnded && (
        <>
          <Text style={styles.label}>Suggested next question</Text>
          <Text style={styles.question}>{currentQuestion}</Text>
        </>
      )}
      {sessionEnded && (
        <Text style={styles.body}>
          You finished this practice round. Review your scores below or start another mission from
          the Quest Map.
        </Text>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  card: {
    padding: 18,
    borderRadius: 18,
    backgroundColor: "#eef6f0",
    borderWidth: 1,
    borderColor: "#c5dcc9"
  },
  title: { color: "#1d2a35", fontSize: 17, fontWeight: "700", marginBottom: 8 },
  meta: { color: "#6a7785", fontSize: 13, marginBottom: 10 },
  label: {
    color: "#8a5a2b",
    fontSize: 12,
    textTransform: "uppercase",
    letterSpacing: 1,
    marginBottom: 6
  },
  question: { color: "#1d2a35", fontSize: 16, lineHeight: 24, fontWeight: "600" },
  body: { color: "#425466", fontSize: 14, lineHeight: 22 }
});
