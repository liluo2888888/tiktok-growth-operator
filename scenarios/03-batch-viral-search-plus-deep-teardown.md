# Scene 3: Batch Viral Search Plus Deep Teardown

## Use When

- the user wants to search a topic at scale and then deep-teardown only the best candidates
- the real goal is to end with creation guidance, not only a research memo

## Minimum Inputs

- one keyword or topic

## Ideal Inputs

- candidate links
- screenshots or transcript notes
- target market
- target product or niche
- explicit shortlist rule

## Workflow

1. collect and normalize the candidate pool
2. shortlist with an explicit top-sample rule
3. deeply tear down only the top few videos
4. preserve script, hook, proof rhythm, and CTA logic
5. summarize common patterns
6. output creator-ready guidance

## Output Contract

- shortlist board
- per-video teardown
- common-pattern summary
- creation guidance

## Direct Prompt

```text
按场景 03 执行：先批量搜爆款，再只深拆最强样本。
这次必须按 3 段来做：
1. 先 shortlist：明确为什么是这几条进 TOP
2. 再逐条深拆：脚本、时间轴、hook、证明、CTA、转化节奏
3. 最后沉淀共性规律和创作建议

不要把所有候选都深拆。
要明确：
- shortlist 规则
- 每条视频为什么入选
- 哪些脚本或时间轴片段最值得复用
- 最终哪些内容可直接指导新的创作
```

## Fallback

If no candidates exist yet, first run Scene 01 and then continue here with the collected shortlist.
