import { router } from "expo-router";
import { Pressable, SafeAreaView, StyleSheet, Text, View } from "react-native";

const roles = [
  { id: "frontend", label: "Frontend Engineer" },
  { id: "product", label: "Product Manager" },
  { id: "sales", label: "Global Sales" }
];

export default function RoleScreen() {
  return (
    <SafeAreaView style={styles.safe}>
      <View style={styles.container}>
        <Text style={styles.kicker}>Step 1</Text>
        <Text style={styles.title}>Choose Your Target Role</Text>
        <Text style={styles.body}>
          Start with one concrete interview context instead of a generic English
          flow.
        </Text>
        <View style={styles.list}>
          {roles.map((role) => (
            <Pressable
              key={role.id}
              style={styles.item}
              onPress={() =>
                router.push({
                  pathname: "/mission",
                  params: { roleId: role.id, roleLabel: role.label }
                })
              }
            >
              <Text style={styles.itemTitle}>{role.label}</Text>
              <Text style={styles.itemMeta}>Targeted interview track</Text>
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
