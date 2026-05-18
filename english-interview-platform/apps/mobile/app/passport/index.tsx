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
import { PassportStampCard } from "@/components/PassportStampCard";
import { listPassportStamps, type PassportStamp } from "@/storage/passportStamps";

export default function PassportListScreen() {
  const [stamps, setStamps] = useState<PassportStamp[]>([]);
  const [loading, setLoading] = useState(true);

  const load = useCallback(async () => {
    setLoading(true);
    setStamps(await listPassportStamps());
    setLoading(false);
  }, []);

  useFocusEffect(
    useCallback(() => {
      void load();
    }, [load])
  );

  return (
    <SafeAreaView style={styles.safe}>
      <ScrollView contentContainerStyle={styles.container}>
        <Text style={styles.kicker}>Progress</Text>
        <Text style={styles.title}>Passport</Text>
        <Text style={styles.body}>
          Every completed interview round earns a stamp with your readiness score.
        </Text>

        <LoadingOverlay visible={loading} message="Loading passport…" />

        {!loading && stamps.length === 0 && (
          <View style={styles.emptyCard}>
            <Text style={styles.emptyEmoji}>🛂</Text>
            <Text style={styles.emptyTitle}>No stamps yet</Text>
            <Text style={styles.emptyBody}>
              Finish your first voice interview round to unlock your first passport stamp.
            </Text>
            <Pressable style={styles.button} onPress={() => router.replace("/quest-map")}>
              <Text style={styles.buttonText}>Start first quest</Text>
            </Pressable>
          </View>
        )}

        {!loading && stamps.length > 0 && (
          <View style={styles.list}>
            <Text style={styles.count}>{stamps.length} stamp{stamps.length === 1 ? "" : "s"}</Text>
            {stamps.map((stamp) => (
              <PassportStampCard
                key={stamp.id}
                stamp={stamp}
                onPress={() =>
                  router.push({
                    pathname: "/passport/[id]",
                    params: { id: stamp.id }
                  })
                }
              />
            ))}
          </View>
        )}

        <Pressable style={styles.secondaryButton} onPress={() => router.push("/")}>
          <Text style={styles.secondaryButtonText}>Home</Text>
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
  title: { color: "#1d2a35", fontSize: 32, fontWeight: "700", marginBottom: 10 },
  body: { color: "#425466", fontSize: 16, lineHeight: 24, marginBottom: 20 },
  loading: { paddingVertical: 32 },
  emptyCard: {
    padding: 24,
    borderRadius: 18,
    backgroundColor: "#fff8ef",
    alignItems: "center",
    marginBottom: 20
  },
  emptyEmoji: { fontSize: 40, marginBottom: 12 },
  emptyTitle: { color: "#1d2a35", fontSize: 20, fontWeight: "700", marginBottom: 8 },
  emptyBody: {
    color: "#425466",
    fontSize: 15,
    lineHeight: 22,
    textAlign: "center",
    marginBottom: 16
  },
  list: { gap: 14, marginBottom: 20 },
  count: { color: "#6b7c8f", fontSize: 13, marginBottom: 4 },
  button: {
    paddingHorizontal: 16,
    paddingVertical: 12,
    borderRadius: 999,
    backgroundColor: "#8a5a2b"
  },
  buttonText: { color: "#fffaf3", fontSize: 14, fontWeight: "600" },
  secondaryButton: {
    alignSelf: "flex-start",
    paddingHorizontal: 14,
    paddingVertical: 10,
    borderRadius: 999,
    backgroundColor: "#d9c2a2"
  },
  secondaryButtonText: { color: "#1d2a35", fontSize: 14, fontWeight: "600" }
});
