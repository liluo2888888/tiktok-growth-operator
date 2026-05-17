# Scene 4: Single Video Breakdown

## Use When

- the user gives one TikTok or Douyin video and wants the full mechanism rebuilt
- the next step depends on understanding one video's hook, proof rhythm, and adaptation path

## Minimum Inputs

- one video link or storyboard summary

## Ideal Inputs

- video link
- video download JSON or capture detail when available
- transcript or subtitle notes
- screenshots by beat
- BGM or audio cue
- basic performance context

## Workflow

1. classify the video type first
2. decide whether it is voiceover-led, subtitle-led, or no-voiceover-led
3. rebuild the video beat by beat with a stable timeline table
4. extract hook, conversion rhythm, and visual-style logic separately
5. analyze BGM, subtitle density, and transition rhythm
6. separate transferable mechanism from creator-specific polish
7. write one safer and one more aggressive adaptation path

## Output Contract

- executive judgment
- timeline breakdown table
- video-type classification
- BGM and sensory analysis
- standard view:
  `Time Range | Scene Type | Visual Content | Spoken / On-Screen Script | Role In Conversion | Evidence Ref`
- viral interpretation:
  opening hook, conversion rhythm, visual style
- reusable mechanism
- adaptation paths

## Standard Timeline View

- `Time Range | Scene Type | Visual Content | Spoken / On-Screen Script | Role In Conversion | Evidence Ref`

## Direct Prompt

```text
按场景 04 执行：完整拆一条短视频。
先判断它属于哪种视频类型，再按时间顺序重建：
1. 每个时间段发生了什么
2. 画面、口播或字幕分别承担什么转化作用
3. 背景音乐、节奏和转场如何放大效果
4. 开头钩子、转化节奏、画面风格这三层分别为什么成立
5. 哪些机制可迁移，哪些只是创作者表层风格
最后给我一条保守改编路径和一条激进改编路径。
如果是无口播视频，不要因为没台词就弱化拆解，要重点看字幕、动作、镜头和节奏。
标准表格优先使用：
Time Range | Scene Type | Visual Content | Spoken / On-Screen Script | Role In Conversion | Evidence Ref
```

## Fallback

If only the link exists but no accessible content, ask for screenshots, subtitles, or a short manual reconstruction before judging the mechanism.
