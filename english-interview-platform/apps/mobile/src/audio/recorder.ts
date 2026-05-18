import { Audio } from "expo-av";
import * as FileSystem from "expo-file-system";

import type { RecordingResult } from "@/audio/types";

let activeRecording: Audio.Recording | null = null;

export async function requestMicrophonePermission(): Promise<boolean> {
  const permission = await Audio.requestPermissionsAsync();
  return permission.granted;
}

export async function startRecording(): Promise<void> {
  if (activeRecording) {
    await discardRecording();
  }

  await Audio.setAudioModeAsync({
    allowsRecordingIOS: true,
    playsInSilentModeIOS: true
  });

  const recording = new Audio.Recording();
  await recording.prepareToRecordAsync(Audio.RecordingOptionsPresets.HIGH_QUALITY);
  await recording.startAsync();
  activeRecording = recording;
}

export async function stopRecording(): Promise<RecordingResult> {
  if (!activeRecording) {
    throw new Error("No active recording");
  }

  const recording = activeRecording;
  activeRecording = null;

  await recording.stopAndUnloadAsync();
  const uri = recording.getURI();
  const status = await recording.getStatusAsync();

  if (!uri) {
    throw new Error("Recording file is missing");
  }

  const cacheUri = `${FileSystem.cacheDirectory}quest-recording-${Date.now()}.m4a`;
  await FileSystem.copyAsync({ from: uri, to: cacheUri });
  await FileSystem.deleteAsync(uri, { idempotent: true });

  return {
    uri: cacheUri,
    durationMs: status.durationMillis ?? 0
  };
}

export async function discardRecording(): Promise<void> {
  if (!activeRecording) {
    return;
  }

  try {
    await activeRecording.stopAndUnloadAsync();
    const uri = activeRecording.getURI();
    if (uri) {
      await FileSystem.deleteAsync(uri, { idempotent: true });
    }
  } finally {
    activeRecording = null;
  }
}

export async function deleteRecordingFile(uri: string): Promise<void> {
  await FileSystem.deleteAsync(uri, { idempotent: true });
}

export async function playRecording(uri: string): Promise<Audio.Sound> {
  await Audio.setAudioModeAsync({
    allowsRecordingIOS: false,
    playsInSilentModeIOS: true
  });

  const { sound } = await Audio.Sound.createAsync({ uri });
  await sound.playAsync();
  return sound;
}

export function isRecordingActive(): boolean {
  return activeRecording !== null;
}
