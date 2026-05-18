const RATING_PREFIX = "quest.feedbackRating.";

export type FeedbackRating = "helpful" | "not_helpful";

export function getFeedbackRating(sessionId: string): FeedbackRating | null {
  const value = localStorage.getItem(RATING_PREFIX + sessionId);
  if (value === "helpful" || value === "not_helpful") {
    return value;
  }
  return null;
}

export function saveFeedbackRating(sessionId: string, rating: FeedbackRating): void {
  localStorage.setItem(RATING_PREFIX + sessionId, rating);
}
