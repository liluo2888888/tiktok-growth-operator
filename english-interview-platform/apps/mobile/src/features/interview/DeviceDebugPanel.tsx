import { useEffect, useState } from "react";
import { Pressable, StyleSheet, Text, View } from "react-native";

import { apiBaseUrl } from "@/services/api";
import { checkApiHealth, type ApiHealthResult } from "@/services/health";
import { hasOpenAiApiKey } from "@/services/asr";

type DeviceDebugPanelProps = {
  onRetryBootstrap?: () => void;
};

export function DeviceDebugPanel({ onRetryBootstrap }: DeviceDebugPanelProps) {
  const [health, setHealth] = useState<ApiHealthResult | null>(null);
  const [checking, setChecking] = useState(false);

  async function runCheck() {
    setChecking(true);
    const result = await checkApiHealth();
    setHealth(result);
    setChecking(false);
  }

  useEffect(() => {
    void runCheck();
  }, []);

  const apiLooksLocal =
    apiBaseUrl.includes("localhost") || apiBaseUrl.includes("127.0.0.1");

  return (
    <View style={styles.panel}>
      <Text style={styles.title}>Device debug</Text>
      <Text style={styles.line}>API: {apiBaseUrl}</Text>
      <Text style={styles.line}>ASR key: {hasOpenAiApiKey() ? "set" : "missing"}</Text>
      {apiLooksLocal && (
        <Text style={styles.warn}>
          Phone cannot use localhost. Set EXPO_PUBLIC_API_BASE_URL to your PC LAN IP in
          apps/mobile/.env, then restart Expo (press r).
        </Text>
      )}
      <Text style={styles.line}>
        Health:{" "}
        {checking
          ? "checking..."
          : health?.ok
            ? `OK (${health.status})`
            : health?.error ?? "unknown"}
      </Text>
      <View style={styles.actions}>
        <Pressable style={styles.button} onPress={() => void runCheck()}>
          <Text style={styles.buttonText}>Ping API</Text>
        </Pressable>
        {onRetryBootstrap && (
          <Pressable style={styles.button} onPress={onRetryBootstrap}>
            <Text style={styles.buttonText}>Retry session</Text>
          </Pressable>
        )}
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  panel: {
    marginTop: 16,
    padding: 12,
    borderRadius: 12,
    backgroundColor: "#eef3f8",
    borderWidth: 1,
    borderColor: "#c5d4e3"
  },
  title: { color: "#1d2a35", fontSize: 13, fontWeight: "700", marginBottom: 6 },
  line: { color: "#425466", fontSize: 12, lineHeight: 18, marginBottom: 4 },
  warn: { color: "#9b2c2c", fontSize: 12, lineHeight: 18, marginBottom: 6 },
  actions: { flexDirection: "row", gap: 8, marginTop: 8, flexWrap: "wrap" },
  button: {
    paddingHorizontal: 10,
    paddingVertical: 6,
    borderRadius: 999,
    backgroundColor: "#5c6f82"
  },
  buttonText: { color: "#fff", fontSize: 12, fontWeight: "600" }
});
