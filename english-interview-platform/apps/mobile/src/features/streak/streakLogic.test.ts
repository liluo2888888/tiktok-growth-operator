import assert from "node:assert/strict";
import test from "node:test";

import {
  applyQuestCompletion,
  readStreakSummary,
  type StreakState
} from "./streakLogic";

test("first completion starts streak at 1", () => {
  const result = applyQuestCompletion({ streakCount: 0, lastCompletedDate: null }, "2026-05-17");
  assert.equal(result.streakCount, 1);
  assert.equal(result.todayCompleted, true);
});

test("consecutive day increments streak", () => {
  const result = applyQuestCompletion(
    { streakCount: 2, lastCompletedDate: "2026-05-16" },
    "2026-05-17"
  );
  assert.equal(result.streakCount, 3);
});

test("gap resets streak to 1 on new completion", () => {
  const result = applyQuestCompletion(
    { streakCount: 5, lastCompletedDate: "2026-05-14" },
    "2026-05-17"
  );
  assert.equal(result.streakCount, 1);
});

test("readStreakSummary zeroes streak after missed day", () => {
  const summary = readStreakSummary(
    { streakCount: 4, lastCompletedDate: "2026-05-14" },
    "2026-05-17"
  );
  assert.equal(summary.streakCount, 0);
  assert.equal(summary.todayCompleted, false);
});
