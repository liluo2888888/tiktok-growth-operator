import { forwardRef } from "react";
import { StyleSheet, Text, View, type View as ViewType } from "react-native";

import {
  missionStampEmoji,
  readinessTier
} from "@/features/passport/stampPresentation";
import type { PassportStamp } from "@/storage/passportStamps";
import { formatStampDate } from "@/utils/formatDate";

type ShareStampPosterProps = {
  stamp: PassportStamp;
};

export const SHARE_POSTER_SIZE = 360;

export const ShareStampPoster = forwardRef<ViewType, ShareStampPosterProps>(function ShareStampPoster(
  { stamp },
  ref
) {
  return (
    <View ref={ref} style={styles.poster} collapsable={false}>
      <Text style={styles.brand}>Quest English</Text>
      <Text style={styles.subbrand}>Interview Quest Pack</Text>
      <Text style={styles.emoji}>{missionStampEmoji(stamp.missionId)}</Text>
      <Text style={styles.mission}>{stamp.missionLabel}</Text>
      <Text style={styles.role}>{stamp.roleLabel}</Text>
      <View style={styles.readinessBlock}>
        <Text style={styles.readinessValue}>{stamp.readiness}</Text>
        <Text style={styles.readinessLabel}>Readiness</Text>
      </View>
      <Text style={styles.tier}>{readinessTier(stamp.readiness)}</Text>
      <Text style={styles.earned}>Earned {formatStampDate(stamp.earnedAt)}</Text>
    </View>
  );
});

const styles = StyleSheet.create({
  poster: {
    width: SHARE_POSTER_SIZE,
    height: SHARE_POSTER_SIZE,
    padding: 28,
    borderRadius: 24,
    backgroundColor: "#fff8ef",
    borderWidth: 2,
    borderColor: "#c9a574",
    alignItems: "center",
    justifyContent: "center"
  },
  brand: {
    color: "#8a5a2b",
    fontSize: 13,
    fontWeight: "800",
    letterSpacing: 1.4,
    textTransform: "uppercase"
  },
  subbrand: { color: "#6a7785", fontSize: 11, marginBottom: 10 },
  emoji: { fontSize: 40, marginBottom: 6 },
  mission: {
    color: "#1d2a35",
    fontSize: 22,
    fontWeight: "800",
    textAlign: "center",
    marginBottom: 4
  },
  role: { color: "#425466", fontSize: 13, marginBottom: 12 },
  readinessBlock: { alignItems: "center", marginBottom: 4 },
  readinessValue: { color: "#8a5a2b", fontSize: 48, fontWeight: "800", lineHeight: 52 },
  readinessLabel: { color: "#6a7785", fontSize: 12, fontWeight: "600" },
  tier: { color: "#1d2a35", fontSize: 14, fontWeight: "600", marginBottom: 8 },
  earned: { color: "#6a7785", fontSize: 11 }
});
