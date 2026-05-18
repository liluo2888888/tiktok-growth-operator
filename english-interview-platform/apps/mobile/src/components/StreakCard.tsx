import { Pressable, StyleSheet, Text, View } from "react-native";

import type { DailyQuestSuggestion } from "@/storage/streak";
import type { StreakSummary } from "@/features/streak/streakLogic";

type StreakCardProps = {
  summary: StreakSummary;
  suggestion: DailyQuestSuggestion;
  onContinueQuest: () => void;
};

export function StreakCard({ summary, suggestion, onContinueQuest }: StreakCardProps) {
  return (
    <View style={styles.card}>
      <View style={styles.header}>
        <Text style={styles.flame}>🔥</Text>
        <View style={styles.headerText}>
          <Text style={styles.streakCount}>{summary.streakCount}</Text>
          <Text style={styles.streakLabel}>day streak</Text>
        </View>
        <View style={[styles.badge, summary.todayCompleted ? styles.badgeDone : styles.badgePending]}>
          <Text style={styles.badgeText}>
            {summary.todayCompleted ? "Today done" : "Today open"}
          </Text>
        </View>
      </View>

      <Text style={styles.taskTitle}>
        {summary.todayCompleted ? "Great work today" : "Today's quest"}
      </Text>
      <Text style={styles.taskBody}>
        {summary.todayCompleted
          ? "Come back tomorrow to extend your streak."
          : `${suggestion.missionLabel} — ${suggestion.reason}`}
      </Text>

      {!summary.todayCompleted && (
        <Pressable style={styles.button} onPress={onContinueQuest}>
          <Text style={styles.buttonText}>Continue today's quest</Text>
        </Pressable>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  card: {
    marginTop: 20,
    padding: 18,
    borderRadius: 18,
    backgroundColor: "#fff3e4",
    borderWidth: 1,
    borderColor: "#ead9c0"
  },
  header: { flexDirection: "row", alignItems: "center", gap: 12, marginBottom: 14 },
  flame: { fontSize: 28 },
  headerText: { flex: 1 },
  streakCount: { color: "#1d2a35", fontSize: 32, fontWeight: "800", lineHeight: 34 },
  streakLabel: { color: "#6a7785", fontSize: 13, fontWeight: "600" },
  badge: {
    paddingHorizontal: 10,
    paddingVertical: 6,
    borderRadius: 999
  },
  badgeDone: { backgroundColor: "#d4ead8" },
  badgePending: { backgroundColor: "#f5d9b8" },
  badgeText: { color: "#1d2a35", fontSize: 11, fontWeight: "700" },
  taskTitle: { color: "#1d2a35", fontSize: 16, fontWeight: "700", marginBottom: 6 },
  taskBody: { color: "#425466", fontSize: 14, lineHeight: 20, marginBottom: 12 },
  button: {
    alignSelf: "flex-start",
    paddingHorizontal: 14,
    paddingVertical: 10,
    borderRadius: 999,
    backgroundColor: "#8a5a2b"
  },
  buttonText: { color: "#fffaf3", fontSize: 14, fontWeight: "600" }
});
