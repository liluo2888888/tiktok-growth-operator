# Scene 15: Image Translation Brief

## Use When

- the user needs localized image-copy adaptation across languages

## Minimum Inputs

- source image text or extracted copy
- target language

## Ideal Inputs

- image
- source text
- product context
- target market
- output aspect ratio

## Workflow

1. identify which text is literal and which text is persuasive
2. translate for conversion, not word-for-word only
3. adapt tone and CTA to target market
4. output a render-ready translation brief

## Output Contract

- translated copy
- layout notes
- text hierarchy
- localization cautions

## Direct Prompt

```text
请帮我做“图片翻译执行简报”。

目标语言：<语言>
要求：
1. 不要只直译，要考虑电商转化
2. 保留主卖点层级
3. 说明哪些字适合放大，哪些适合作为辅助文案
4. 如有不适合本地市场的表达，请改写
```

## Fallback

If the user only provides the image but not extracted text, first reconstruct the likely text blocks manually.
