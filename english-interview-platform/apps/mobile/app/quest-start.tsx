import { router, useLocalSearchParams } from "expo-router";
import { Pressable, SafeAreaView, StyleSheet, Text, View } from "react-native";

import { QUEST_PACK, getMissionById } from "@/content/quests";
import { track } from "@/services/analytics";
import { markMissionInProgress } from "@/storage/userProfile";

export default function QuestStartScreen() {
  const { roleId, roleLabel, missionId, missionLabel } = useLocalSearchParams<{
    roleId: string;
    roleLabel: string;
    missionId: string;
    missionLabel: string;
  }>();

  const mission = getMissionById(missionId);

  async function beginPractice() {
    await markMissionInProgress(missionId);
    await track("quest_start", {
      questPackId: QUEST_PACK.id,
      missionId
    });
    router.push({
      pathname: "/interview",
      params: { roleId, roleLabel, missionId, missionLabel }
    });
  }

  return (
    <SafeAreaView style={styles.safe}>
      <View style={styles.container}>
        <Text style={styles.kicker}>Quest Start</Text>
        <Text style={styles.title}>{missionLabel}</Text>
        <Text style={styles.body}>Role track: {roleLabel}</Text>

        <View style={styles.card}>
          <Text style={styles.cardTitle}>This round</Text>
          <Text style={styles.cardBody}>
            {mission?.subtitle ??
              "Practice one spoken answer, review the transcript, then submit for feedback."}
          </Text>
          <Text style={styles.cardMeta}>~{mission?.durationMinutes ?? 3} minutes · Voice answer</Text>
        </View>

        <View style={styles.card}>
          <Text style={styles.cardTitle}>Interviewer</Text>
          <Text style={styles.quote}>
            “{mission?.interviewerLine ?? "Tell me about yourself and your fit for this role."}”
          </Text>
        </View>

        <View style={styles.actions}>
          <Pressable style={styles.button} onPress={() => void beginPractice()}>
            <Text style={styles.buttonText}>Begin Practice</Text>
          </Pressable>
          <Pressable style={styles.secondaryButton} onPress={() => router.back()}>
            <Text style={styles.secondaryButtonText}>Back to Map</Text>
          </Pressable>
        </View>
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safe: { flex: 1, backgroundColor: "#f6f1e8" },
  container: { flex: 1, paddingHorizontal: 24, paddingTop: 48 },
  kicker: {
    color: "#8a5a2b",
    fontSize: 14,
    marginBottom: 10,
    textTransform: "uppercase",
    letterSpacing: 1.2
  },
  title: { color: "#1d2a35", fontSize: 32, fontWeight: "700", marginBottom: 12 },
  body: { color: "#425466", fontSize: 16, lineHeight: 24, marginBottom: 24 },
  card: {
    marginBottom: 16,
    padding: 18,
    borderRadius: 18,
    backgroundColor: "#fff8ef"
  },
  cardTitle: { color: "#1d2a35", fontSize: 18, fontWeight: "600", marginBottom: 10 },
  cardBody: { color: "#425466", fontSize: 15, lineHeight: 22, marginBottom: 8 },
  cardMeta: { color: "#6a7785", fontSize: 13 },
  quote: {
    color: "#1d2a35",
    fontSize: 17,
    lineHeight: 26,
    fontStyle: "italic"
  },
  actions: { marginTop: 12, gap: 12 },
  button: {
    alignSelf: "flex-start",
    paddingHorizontal: 16,
    paddingVertical: 12,
    borderRadius: 999,
    backgroundColor: "#8a5a2b"
  },
  buttonText: { color: "#fffaf3", fontSize: 14, fontWeight: "600" },
  secondaryButton: {
    alignSelf: "flex-start",
    paddingHorizontal: 16,
    paddingVertical: 12,
    borderRadius: 999,
    backgroundColor: "#d9c2a2"
  },
  secondaryButtonText: { color: "#1d2a35", fontSize: 14, fontWeight: "600" }
});
