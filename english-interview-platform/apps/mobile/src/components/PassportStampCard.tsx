import { Pressable, StyleSheet, Text, View } from "react-native";

import {
  missionStampEmoji,
  readinessTier
} from "@/features/passport/stampPresentation";
import type { PassportStamp } from "@/storage/passportStamps";
import { formatStampDate } from "@/utils/formatDate";

type PassportStampCardProps = {
  stamp: PassportStamp;
  onPress?: () => void;
  compact?: boolean;
};

export function PassportStampCard({ stamp, onPress, compact }: PassportStampCardProps) {
  const content = (
    <>
      <View style={styles.header}>
        <Text style={styles.emoji}>{missionStampEmoji(stamp.missionId)}</Text>
        <View style={styles.headerText}>
          <Text style={styles.title}>{stamp.missionLabel}</Text>
          <Text style={styles.meta}>
            {stamp.roleLabel} · {formatStampDate(stamp.earnedAt)}
          </Text>
        </View>
        <Text style={styles.readiness}>{stamp.readiness}</Text>
      </View>
      {!compact && (
        <Text style={styles.tier}>{readinessTier(stamp.readiness)}</Text>
      )}
    </>
  );

  if (!onPress) {
    return <View style={styles.card}>{content}</View>;
  }

  return (
    <Pressable style={styles.card} onPress={onPress}>
      {content}
    </Pressable>
  );
}

const styles = StyleSheet.create({
  card: {
    padding: 18,
    borderRadius: 18,
    backgroundColor: "#fff8ef",
    borderWidth: 1,
    borderColor: "#ead9c0"
  },
  header: { flexDirection: "row", alignItems: "center", gap: 12 },
  emoji: { fontSize: 32 },
  headerText: { flex: 1 },
  title: { color: "#1d2a35", fontSize: 18, fontWeight: "700", marginBottom: 4 },
  meta: { color: "#6a7785", fontSize: 13 },
  readiness: {
    color: "#8a5a2b",
    fontSize: 28,
    fontWeight: "800"
  },
  tier: {
    marginTop: 10,
    color: "#425466",
    fontSize: 13,
    fontWeight: "600"
  }
});
