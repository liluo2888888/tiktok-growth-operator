import { router, useFocusEffect } from "expo-router";
import { useCallback, useState } from "react";
import {
  Pressable,
  SafeAreaView,
  ScrollView,
  StyleSheet,
  Text,
  View
} from "react-native";

import { LoadingOverlay } from "@/components/LoadingOverlay";
import { MISSIONS, QUEST_PACK } from "@/content/quests";
import { missionStatusLabel } from "@/features/quest/missionStatusLabel";
import {
  getMissionStatus,
  getUserProfile,
  type MissionStatus,
  type UserProfile
} from "@/storage/userProfile";

export default function QuestMapScreen() {
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [statuses, setStatuses] = useState<Record<string, MissionStatus>>({});
  const [loading, setLoading] = useState(true);

  const load = useCallback(async () => {
    setLoading(true);
    const userProfile = await getUserProfile();
    if (!userProfile) {
      router.replace("/onboarding");
      return;
    }

    setProfile(userProfile);
    const nextStatuses: Record<string, MissionStatus> = {};
    for (const mission of MISSIONS) {
      nextStatuses[mission.id] = await getMissionStatus(mission.id);
    }
    setStatuses(nextStatuses);
    setLoading(false);
  }, []);

  useFocusEffect(
    useCallback(() => {
      void load();
    }, [load])
  );

  function openMission(missionId: string, missionLabel: string) {
    if (!profile) {
      return;
    }

    router.push({
      pathname: "/quest-start",
      params: {
        roleId: profile.roleId,
        roleLabel: profile.roleLabel,
        missionId,
        missionLabel
      }
    });
  }

  return (
    <SafeAreaView style={styles.safe}>
      <ScrollView contentContainerStyle={styles.container}>
        <Text style={styles.kicker}>Quest Map</Text>
        <Text style={styles.title}>{QUEST_PACK.title}</Text>
        <Text style={styles.body}>{QUEST_PACK.description}</Text>
        {!!profile && (
          <Text style={styles.meta}>
            Track: {profile.roleLabel} · Goal: Job Interview
          </Text>
        )}

        <LoadingOverlay visible={loading} message="Loading quest map…" />

        {!loading && (
          <View style={styles.list}>
            {MISSIONS.map((mission) => {
              const status = statuses[mission.id] ?? "not_started";
              return (
                <Pressable
                  key={mission.id}
                  style={styles.missionCard}
                  onPress={() => openMission(mission.id, mission.label)}
                >
                  <View style={styles.missionHeader}>
                    <Text style={styles.missionTitle}>{mission.label}</Text>
                    <Text style={styles.statusPill}>{missionStatusLabel(status)}</Text>
                  </View>
                  <Text style={styles.missionSubtitle}>{mission.subtitle}</Text>
                  <Text style={styles.missionMeta}>~{mission.durationMinutes} min · Voice practice</Text>
                </Pressable>
              );
            })}
          </View>
        )}

        <View style={styles.footerActions}>
          <Pressable style={styles.secondaryButton} onPress={() => router.push("/passport")}>
            <Text style={styles.secondaryButtonText}>Passport</Text>
          </Pressable>
          <Pressable style={styles.secondaryButton} onPress={() => router.push("/")}>
            <Text style={styles.secondaryButtonText}>Home</Text>
          </Pressable>
        </View>
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
  title: { color: "#1d2a35", fontSize: 32, fontWeight: "700", marginBottom: 10 },
  body: { color: "#425466", fontSize: 16, lineHeight: 24, marginBottom: 8 },
  meta: { color: "#6b7c8f", fontSize: 14, marginBottom: 20 },
  loading: { paddingVertical: 32 },
  list: { gap: 14, marginBottom: 24 },
  missionCard: {
    padding: 18,
    borderRadius: 18,
    backgroundColor: "#fff8ef"
  },
  missionHeader: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "flex-start",
    gap: 10,
    marginBottom: 8
  },
  missionTitle: { color: "#1d2a35", fontSize: 20, fontWeight: "700", flex: 1 },
  statusPill: {
    color: "#8a5a2b",
    fontSize: 11,
    fontWeight: "700",
    textTransform: "uppercase",
    letterSpacing: 0.6
  },
  missionSubtitle: { color: "#425466", fontSize: 15, lineHeight: 22, marginBottom: 6 },
  missionMeta: { color: "#6a7785", fontSize: 13 },
  footerActions: { flexDirection: "row", gap: 10, flexWrap: "wrap" },
  secondaryButton: {
    paddingHorizontal: 14,
    paddingVertical: 10,
    borderRadius: 999,
    backgroundColor: "#d9c2a2"
  },
  secondaryButtonText: { color: "#1d2a35", fontSize: 14, fontWeight: "600" }
});
