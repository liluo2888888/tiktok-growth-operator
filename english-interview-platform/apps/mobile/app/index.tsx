import { router, useFocusEffect } from "expo-router";
import { useCallback, useEffect, useState } from "react";
import {
  Pressable,
  SafeAreaView,
  ScrollView,
  StyleSheet,
  Text,
  View
} from "react-native";

import { LoadingOverlay } from "@/components/LoadingOverlay";
import { StreakCard } from "@/components/StreakCard";
import { QUEST_PACK } from "@/content/quests";
import type { StreakSummary } from "@/features/streak/streakLogic";
import {
  getDailyQuestSuggestion,
  getStreakSummary,
  openSuggestedQuest,
  type DailyQuestSuggestion
} from "@/storage/streak";
import {
  clearUserData,
  getUserProfile,
  hasCompletedOnboarding,
  type UserProfile
} from "@/storage/userProfile";

export default function HomeScreen() {
  const [loading, setLoading] = useState(true);
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [streak, setStreak] = useState<StreakSummary | null>(null);
  const [suggestion, setSuggestion] = useState<DailyQuestSuggestion | null>(null);

  const refreshHome = useCallback(async () => {
    const [nextProfile, nextStreak, nextSuggestion] = await Promise.all([
      getUserProfile(),
      getStreakSummary(),
      getDailyQuestSuggestion()
    ]);
    setProfile(nextProfile);
    setStreak(nextStreak);
    setSuggestion(nextSuggestion);
  }, []);

  useEffect(() => {
    void (async () => {
      const done = await hasCompletedOnboarding();
      if (!done) {
        router.replace("/onboarding");
        return;
      }

      await refreshHome();
      setLoading(false);
    })();
  }, [refreshHome]);

  useFocusEffect(
    useCallback(() => {
      if (!loading) {
        void refreshHome();
      }
    }, [loading, refreshHome])
  );

  if (loading) {
    return (
      <SafeAreaView style={styles.safe}>
        <View style={[styles.container, styles.centered]}>
          <LoadingOverlay visible message="Loading home…" />
        </View>
      </SafeAreaView>
    );
  }

  async function handleContinueQuest() {
    const target = await openSuggestedQuest();
    router.push(target);
  }

  return (
    <SafeAreaView style={styles.safe}>
      <ScrollView contentContainerStyle={styles.container}>
        <Text style={styles.kicker}>Quest English</Text>
        <Text style={styles.title}>Interview Quest Pack</Text>
        <Text style={styles.body}>
          Practice spoken answers for real interviews — not generic vocabulary drills.
        </Text>
        {!!profile && (
          <Text style={styles.meta}>
            {profile.roleLabel} · Job Interview
          </Text>
        )}

        {!!streak && !!suggestion && (
          <StreakCard
            summary={streak}
            suggestion={suggestion}
            onContinueQuest={() => void handleContinueQuest()}
          />
        )}

        <View style={styles.card}>
          <Text style={styles.cardTitle}>{QUEST_PACK.title}</Text>
          <Text style={styles.cardBody}>{QUEST_PACK.description}</Text>
          <Pressable style={styles.button} onPress={() => router.push("/quest-map")}>
            <Text style={styles.buttonText}>Open Quest Map</Text>
          </Pressable>
        </View>

        <View style={styles.card}>
          <Text style={styles.cardTitle}>Quick links</Text>
          <Pressable style={styles.linkButton} onPress={() => router.push("/passport")}>
            <Text style={styles.linkText}>Open Passport</Text>
          </Pressable>
          <Pressable style={styles.linkButton} onPress={() => router.push("/onboarding")}>
            <Text style={styles.linkText}>Change goal / role</Text>
          </Pressable>
          <Pressable style={styles.linkButton} onPress={() => router.push("/legal")}>
            <Text style={styles.linkText}>Privacy & voice data</Text>
          </Pressable>
        </View>

        {__DEV__ && (
          <Pressable
            style={styles.devButton}
            onPress={() => void clearUserData().then(() => router.replace("/onboarding"))}
          >
            <Text style={styles.devButtonText}>Reset onboarding (dev)</Text>
          </Pressable>
        )}
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safe: { flex: 1, backgroundColor: "#f6f1e8" },
  container: { flexGrow: 1, paddingHorizontal: 24, paddingVertical: 32 },
  centered: { alignItems: "center" },
  kicker: {
    color: "#8a5a2b",
    fontSize: 14,
    marginBottom: 12,
    textTransform: "uppercase",
    letterSpacing: 1.2
  },
  title: { color: "#1d2a35", fontSize: 34, fontWeight: "700", marginBottom: 16 },
  body: { color: "#425466", fontSize: 16, lineHeight: 24 },
  meta: { color: "#6b7c8f", fontSize: 14, marginTop: 8, marginBottom: 4 },
  card: {
    marginTop: 24,
    padding: 18,
    borderRadius: 18,
    backgroundColor: "#fff8ef"
  },
  cardTitle: { color: "#1d2a35", fontSize: 18, fontWeight: "600", marginBottom: 10 },
  cardBody: { color: "#425466", fontSize: 14, lineHeight: 20, marginBottom: 14 },
  button: {
    alignSelf: "flex-start",
    paddingHorizontal: 14,
    paddingVertical: 10,
    borderRadius: 999,
    backgroundColor: "#8a5a2b"
  },
  buttonText: { color: "#fffaf3", fontSize: 14, fontWeight: "600" },
  linkButton: { paddingVertical: 6 },
  linkText: { color: "#8a5a2b", fontSize: 14, fontWeight: "600" },
  devButton: { marginTop: 20, alignSelf: "flex-start" },
  devButtonText: { color: "#6b7c8f", fontSize: 12 }
});
