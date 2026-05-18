import assert from "node:assert/strict";
import test from "node:test";

import { canSubmitVoiceAnswer, countWords } from "./voiceValidation";

test("countWords ignores extra whitespace", () => {
  assert.equal(countWords("  hello   world  "), 2);
});

test("canSubmitVoiceAnswer requires min duration and three words", () => {
  assert.equal(canSubmitVoiceAnswer("one two three", 10), true);
  assert.equal(canSubmitVoiceAnswer("one two", 10), false);
  assert.equal(canSubmitVoiceAnswer("one two three", 9), false);
});
