import { useEffect, useState } from "react";
import { Pressable, StyleSheet, Text, View } from "react-native";

import { track } from "@/services/analytics";
import {
  getFeedbackRating,
  saveFeedbackRating,
  type FeedbackRating
} from "@/storage/feedbackRating";

type FeedbackHelpfulPanelProps = {
  sessionId: string;
};

export function FeedbackHelpfulPanel({ sessionId }: FeedbackHelpfulPanelProps) {
  const [rating, setRating] = useState<FeedbackRating | null>(null);
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    void getFeedbackRating(sessionId).then((value) => {
      setRating(value);
      setSaved(Boolean(value));
    });
  }, [sessionId]);

  async function choose(value: FeedbackRating) {
    await saveFeedbackRating(sessionId, value);
    await track("feedback_helpful", {
      sessionId,
      helpful: value === "helpful"
    });
    setRating(value);
    setSaved(true);
  }

  return (
    <View style={styles.card}>
      <Text style={styles.title}>Was this feedback helpful?</Text>
      <View style={styles.actions}>
        <Pressable
          style={[styles.chip, rating === "helpful" && styles.chipSelected]}
          onPress={() => void choose("helpful")}
        >
          <Text style={[styles.chipText, rating === "helpful" && styles.chipTextSelected]}>
            Helpful
          </Text>
        </Pressable>
        <Pressable
          style={[styles.chip, rating === "not_helpful" && styles.chipSelected]}
          onPress={() => void choose("not_helpful")}
        >
          <Text
            style={[styles.chipText, rating === "not_helpful" && styles.chipTextSelected]}
          >
            Not helpful
          </Text>
        </Pressable>
      </View>
      {saved && (
        <Text style={styles.thanks}>Thanks — your rating helps us improve.</Text>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  card: {
    padding: 18,
    borderRadius: 18,
    backgroundColor: "#fff8ef"
  },
  title: { color: "#1d2a35", fontSize: 16, fontWeight: "600", marginBottom: 12 },
  actions: { flexDirection: "row", gap: 10 },
  chip: {
    paddingHorizontal: 16,
    paddingVertical: 10,
    borderRadius: 999,
    backgroundColor: "#ead9c0"
  },
  chipSelected: { backgroundColor: "#8a5a2b" },
  chipText: { color: "#1d2a35", fontSize: 14, fontWeight: "600" },
  chipTextSelected: { color: "#fffaf3" },
  thanks: { marginTop: 10, color: "#6a7785", fontSize: 13 }
});
