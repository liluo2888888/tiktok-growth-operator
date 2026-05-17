# Scene 5: Reverse-Engineer Video Prompt

## Use When

- the user wants the likely prompt, production brief, or generator-ready structure behind a video
- the next step is to adapt the winning logic onto a new product

## Minimum Inputs

- one video link or multi-frame visual summary

## Ideal Inputs

- video link
- transcript or subtitle notes
- screenshots by shot
- pacing notes
- target product to adapt onto

## Workflow

1. infer the original creative intent
2. map the piece into structured brief blocks
3. produce a shot-level breakdown
4. separate inferred-original brief from product-adapted brief
5. mark low-confidence inferences field by field
6. output generator-ready handoff fields when product context exists

## Output Contract

- executive summary of likely creative intent
- inferred original brief
- generator-ready schema:
  `Style`, `Environment`, `Tone & Pacing`, `Camera`, `Lighting`, `Character`, `Shots`, `Background Sound`, `Transition / Editing`
- shot-level table:
  `Shot | Duration | Scene / Subject | Action | Voiceover / Overlay | Purpose | Asset Need`
- product-adapted brief
- generator handoff fields
- field-level confidence labels

## Direct Prompt

```text
按场景 05 执行：反推这条视频背后的提示词或制作 brief。
不要只写风格词，要分成两层输出：
第一层是原视频的 inferred brief：
1. Style
2. Environment
3. Tone & Pacing
4. Camera
5. Lighting
6. Character
7. Shots
8. Background Sound
9. Transition / Editing

第二层是 shot 级拆解：
- 每个 shot 的时长、主体、动作、口播或字幕、作用

如果我提供了产品信息，再给我一版 product-adapted brief。
还要把结果做成 generator-ready handoff，不要只停留在分析笔记。
所有证据不足的字段都要单独标低置信度，不要假装确定。
```

## Fallback

If visual evidence is too thin, output a low-confidence brief plus a missing-evidence checklist instead of fabricating hidden production details.
