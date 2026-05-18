import AsyncStorage from "@react-native-async-storage/async-storage";

const RATING_PREFIX = "quest.feedbackRating.";

export type FeedbackRating = "helpful" | "not_helpful";

export async function getFeedbackRating(sessionId: string): Promise<FeedbackRating | null> {
  const value = await AsyncStorage.getItem(RATING_PREFIX + sessionId);
  if (value === "helpful" || value === "not_helpful") {
    return value;
  }

  return null;
}

export async function saveFeedbackRating(
  sessionId: string,
  rating: FeedbackRating
): Promise<void> {
  await AsyncStorage.setItem(RATING_PREFIX + sessionId, rating);
}
