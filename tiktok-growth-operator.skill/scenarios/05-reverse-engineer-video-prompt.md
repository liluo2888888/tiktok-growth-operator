# Scene 5: Reverse-Engineer Video Prompt

## Use When

- the user wants the likely generation prompt, shot brief, or production brief behind a video

## Minimum Inputs

- one video link or multi-frame visual summary

## Ideal Inputs

- video
- transcript
- screenshots
- target product to adapt onto

## Workflow

1. infer the likely creative intent
2. describe the visual style, shot language, pacing, and voiceover logic
3. turn that into a structured prompt or brief
4. optionally rewrite it for the user’s product

## Output Contract

- reverse-engineered prompt
- shot/scene brief
- optional product-adapted version

## Direct Prompt

```text
请反推这条视频背后的生成提示词或创作简报。

不要只写风格词。请输出：
1. 画面风格
2. 镜头语言
3. 叙事节奏
4. 口播逻辑
5. 一版通用提示词
6. 一版适配我产品的改写版
```

## Fallback

If visual evidence is too thin, output a low-confidence prompt plus the missing evidence checklist.
