import { Pressable, StyleSheet, Text, View } from "react-native";

type SelectableCardProps = {
  title: string;
  description: string;
  selected: boolean;
  onPress: () => void;
  badge?: string;
};

export function SelectableCard({
  title,
  description,
  selected,
  onPress,
  badge
}: SelectableCardProps) {
  return (
    <Pressable
      style={[styles.card, selected && styles.cardSelected]}
      onPress={onPress}
    >
      <View style={styles.header}>
        <Text style={styles.title}>{title}</Text>
        {!!badge && <Text style={styles.badge}>{badge}</Text>}
      </View>
      <Text style={styles.description}>{description}</Text>
    </Pressable>
  );
}

const styles = StyleSheet.create({
  card: {
    padding: 18,
    borderRadius: 18,
    backgroundColor: "#fff8ef",
    borderWidth: 2,
    borderColor: "transparent"
  },
  cardSelected: {
    borderColor: "#8a5a2b",
    backgroundColor: "#fffdf9"
  },
  header: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "flex-start",
    gap: 8,
    marginBottom: 6
  },
  title: { color: "#1d2a35", fontSize: 18, fontWeight: "600", flex: 1 },
  badge: {
    color: "#8a5a2b",
    fontSize: 11,
    fontWeight: "700",
    textTransform: "uppercase",
    letterSpacing: 0.8
  },
  description: { color: "#6a7785", fontSize: 14, lineHeight: 20 }
});
