# Scene 2: Daily Category Patrol

## Use When

- the user wants a repeatable daily patrol workflow for one category

## Minimum Inputs

- one category
- one primary market

## Ideal Inputs

- 3-10 keywords
- patrol cadence
- desired fields
- alert conditions

## Workflow

1. define the patrol keyword set
2. define the data fields to record every day
3. define the ranking rule
4. define what counts as a meaningful change
5. output a patrol SOP and report template

## Output Contract

- daily patrol checklist
- patrol table schema
- alert logic
- ready-to-reuse daily summary template

## Direct Prompt

```text
帮我设计一个“TikTok 品类爆款视频每日巡检”流程。

品类：<品类>
地区：<地区>
关键词：<关键词列表>

请输出：
1. 每天要采哪些字段
2. 如何筛出真正值得注意的新视频
3. 哪些信号算异常或机会
4. 每日巡检报告模板
```

## Fallback

If the user has no existing data source, convert this into a manual patrol SOP instead of claiming automation.
