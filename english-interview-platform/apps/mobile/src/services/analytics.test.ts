import assert from "node:assert/strict";
import test from "node:test";

import { ANALYTICS_EVENTS } from "./analytics";

test("analytics event catalog matches PRD funnel", () => {
  assert.deepEqual([...ANALYTICS_EVENTS], [
    "onboarding_complete",
    "quest_start",
    "session_bootstrap",
    "turn_submit",
    "feedback_view",
    "feedback_helpful",
    "passport_stamp_earned",
    "passport_share"
  ]);
});
