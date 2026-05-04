# Scene 1: Viral Video Collection

## Use When

- the user wants to collect TikTok viral videos by keyword
- the goal is to build a starter board for study, scripting, or selection

## Minimum Inputs

- one keyword or product phrase

## Ideal Inputs

- keyword set
- target market
- target audience
- whether to prioritize shop-cart videos
- date window

## Workflow

1. clarify keyword, market, and what counts as “useful”
2. collect candidate videos from user links, browser search, exported sheets, or screenshots
3. rank them with the viral ranking prompt
4. extract only the fields needed for later reuse
5. output a shortlist and study board

## Output Contract

- one ranked list
- one short reason for each selected video
- one “study next” recommendation

## Direct Prompt

```text
按“爆款视频采集员”的方式工作。

关键词：<关键词>
地区：<地区>
目标：帮我从候选视频里筛出最值得研究的内容样本。

请输出：
1. Top视频清单
2. 每条视频为什么值得研究
3. 这些视频分别更适合拿来学钩子、结构、转化、还是风格
4. 下一步最应该深拆哪3条
```

## Fallback

If live results are unavailable, ask the user for:

- TikTok search screenshots
- copied titles + links
- any spreadsheet or exported candidate list
