import { StyleSheet, Text, View } from "react-native";

type ScoreBarProps = {
  label: string;
  value: number;
  highlight?: boolean;
};

export function ScoreBar({ label, value, highlight }: ScoreBarProps) {
  const clamped = Math.max(0, Math.min(100, value));

  return (
    <View style={styles.row}>
      <Text style={[styles.label, highlight && styles.labelHighlight]}>{label}</Text>
      <View style={styles.trackWrap}>
        <View style={styles.track}>
          <View style={[styles.fill, { width: `${clamped}%` }, highlight && styles.fillHighlight]} />
        </View>
        <Text style={[styles.value, highlight && styles.valueHighlight]}>{clamped}</Text>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  row: { marginBottom: 12 },
  label: { color: "#425466", fontSize: 13, marginBottom: 6, fontWeight: "500" },
  labelHighlight: { color: "#1d2a35", fontWeight: "700" },
  trackWrap: { flexDirection: "row", alignItems: "center", gap: 10 },
  track: {
    flex: 1,
    height: 10,
    borderRadius: 999,
    backgroundColor: "#ead9c0",
    overflow: "hidden"
  },
  fill: { height: "100%", borderRadius: 999, backgroundColor: "#c9b8a4" },
  fillHighlight: { backgroundColor: "#8a5a2b" },
  value: { color: "#6a7785", fontSize: 13, fontWeight: "600", minWidth: 28, textAlign: "right" },
  valueHighlight: { color: "#8a5a2b", fontSize: 16, fontWeight: "800" }
});
