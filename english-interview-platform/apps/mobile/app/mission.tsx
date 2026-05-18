import { router, useLocalSearchParams } from "expo-router";
import { Pressable, SafeAreaView, StyleSheet, Text, View } from "react-native";

const missions = [
  { id: "self_intro", label: "Self Introduction" },
  { id: "behavioral", label: "Behavioral Interview" },
  { id: "case_round", label: "Case / Problem Solving" }
];

export default function MissionScreen() {
  const { roleId, roleLabel } = useLocalSearchParams<{
    roleId: string;
    roleLabel: string;
  }>();

  return (
    <SafeAreaView style={styles.safe}>
      <View style={styles.container}>
        <Text style={styles.kicker}>Step 2</Text>
        <Text style={styles.title}>Choose A Mission</Text>
        <Text style={styles.body}>Role: {roleLabel ?? roleId}</Text>
        <View style={styles.list}>
          {missions.map((mission) => (
            <Pressable
              key={mission.id}
              style={styles.item}
              onPress={() =>
                router.push({
                  pathname: "/interview",
                  params: {
                    roleId,
                    roleLabel,
                    missionId: mission.id,
                    missionLabel: mission.label
                  }
                })
              }
            >
              <Text style={styles.itemTitle}>{mission.label}</Text>
              <Text style={styles.itemMeta}>Structured English interview practice</Text>
            </Pressable>
          ))}
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
  list: { gap: 14 },
  item: {
    padding: 18,
    borderRadius: 18,
    backgroundColor: "#fff8ef"
  },
  itemTitle: { color: "#1d2a35", fontSize: 18, fontWeight: "600", marginBottom: 6 },
  itemMeta: { color: "#6a7785", fontSize: 14 }
});
