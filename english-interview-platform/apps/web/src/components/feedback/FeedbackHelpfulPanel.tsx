import { useEffect, useState } from "react";

import { Button } from "@/components/ui/Button";
import { Panel } from "@/components/ui/Panel";
import { track } from "@/lib/analytics";
import {
  getFeedbackRating,
  saveFeedbackRating,
  type FeedbackRating
} from "@/lib/feedbackRating";
import { ui } from "@/lib/copy";

type Props = {
  sessionId: string;
};

export function FeedbackHelpfulPanel({ sessionId }: Props) {
  const [rating, setRating] = useState<FeedbackRating | null>(null);
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    const existing = getFeedbackRating(sessionId);
    setRating(existing);
    setSaved(Boolean(existing));
  }, [sessionId]);

  function choose(value: FeedbackRating) {
    saveFeedbackRating(sessionId, value);
    void track("feedback_helpful", {
      sessionId,
      helpful: value === "helpful"
    });
    setRating(value);
    setSaved(true);
  }

  const { feedback: copy } = ui;

  return (
    <Panel title={copy.helpfulTitle} variant="inset">
      <p className="card-body">{copy.helpfulLead}</p>
      <div className="feedback-helpful-actions">
        <Button
          type="button"
          variant={rating === "helpful" ? "primary" : "secondary"}
          onClick={() => choose("helpful")}
        >
          {copy.helpfulYes}
        </Button>
        <Button
          type="button"
          variant={rating === "not_helpful" ? "primary" : "secondary"}
          onClick={() => choose("not_helpful")}
        >
          {copy.helpfulNo}
        </Button>
      </div>
      {saved && <p className="word-count ok">{copy.helpfulThanks}</p>}
    </Panel>
  );
}
