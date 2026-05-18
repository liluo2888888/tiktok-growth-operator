import { router } from "expo-router";
import { useState } from "react";
import {
  Pressable,
  SafeAreaView,
  ScrollView,
  StyleSheet,
  Text,
  View
} from "react-native";

import { SelectableCard } from "@/components/SelectableCard";
import { GOALS, ROLES, type QuestGoal } from "@/content/quests";
import { track } from "@/services/analytics";
import { saveOnboardingProfile } from "@/storage/userProfile";

export default function OnboardingScreen() {
  const [step, setStep] = useState<1 | 2>(1);
  const [goal, setGoal] = useState<QuestGoal>("job_interview");
  const [roleId, setRoleId] = useState<"product" | "general">("product");
  const [saving, setSaving] = useState(false);

  async function finishOnboarding() {
    setSaving(true);
    try {
      await saveOnboardingProfile({ goal, roleId });
      await track("onboarding_complete", { goal, roleId });
      router.replace("/quest-map");
    } finally {
      setSaving(false);
    }
  }

  return (
    <SafeAreaView style={styles.safe}>
      <ScrollView contentContainerStyle={styles.container}>
        <Text style={styles.kicker}>Welcome</Text>
        <Text style={styles.title}>Set up your interview quest</Text>
        <Text style={styles.body}>
          Step {step} of 2 — we will tailor missions to your goal and role.
        </Text>

        {step === 1 && (
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>What are you preparing for?</Text>
            {GOALS.map((item) => (
              <SelectableCard
                key={item.id}
                title={item.label}
                description={item.description}
                selected={goal === item.id}
                badge="MVP"
                onPress={() => setGoal(item.id)}
              />
            ))}
            <Pressable style={styles.button} onPress={() => setStep(2)}>
              <Text style={styles.buttonText}>Next</Text>
            </Pressable>
          </View>
        )}

        {step === 2 && (
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Which role track fits you?</Text>
            {ROLES.map((role) => (
              <SelectableCard
                key={role.id}
                title={role.label}
                description={role.description}
                selected={roleId === role.id}
                onPress={() => setRoleId(role.id)}
              />
            ))}
            <Pressable style={styles.legalLink} onPress={() => router.push("/legal")}>
              <Text style={styles.legalLinkText}>Privacy & voice data</Text>
            </Pressable>
            <View style={styles.actions}>
              <Pressable style={styles.secondaryButton} onPress={() => setStep(1)}>
                <Text style={styles.secondaryButtonText}>Back</Text>
              </Pressable>
              <Pressable
                style={[styles.button, saving && styles.buttonDisabled]}
                disabled={saving}
                onPress={() => void finishOnboarding()}
              >
                <Text style={styles.buttonText}>
                  {saving ? "Saving..." : "Continue to Quest Map"}
                </Text>
              </Pressable>
            </View>
          </View>
        )}
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
  title: { color: "#1d2a35", fontSize: 32, fontWeight: "700", marginBottom: 12 },
  body: { color: "#425466", fontSize: 16, lineHeight: 24, marginBottom: 24 },
  section: { gap: 14 },
  sectionTitle: { color: "#1d2a35", fontSize: 18, fontWeight: "600", marginBottom: 4 },
  actions: { flexDirection: "row", gap: 10, flexWrap: "wrap", marginTop: 8 },
  button: {
    alignSelf: "flex-start",
    paddingHorizontal: 16,
    paddingVertical: 12,
    borderRadius: 999,
    backgroundColor: "#8a5a2b"
  },
  buttonDisabled: { opacity: 0.6 },
  buttonText: { color: "#fffaf3", fontSize: 14, fontWeight: "600" },
  secondaryButton: {
    paddingHorizontal: 16,
    paddingVertical: 12,
    borderRadius: 999,
    backgroundColor: "#d9c2a2"
  },
  secondaryButtonText: { color: "#1d2a35", fontSize: 14, fontWeight: "600" },
  legalLink: { marginTop: 8 },
  legalLinkText: { color: "#6b7c8f", fontSize: 13, textDecorationLine: "underline" }
});
