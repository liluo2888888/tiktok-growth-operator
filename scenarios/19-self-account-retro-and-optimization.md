# Scene 19: Self-Account Retro And Optimization

## Use When

- the user wants to review their own account performance and decide what to do next

## Minimum Inputs

- a list of recent posts with some performance signal

## Ideal Inputs

- titles
- publish times
- views
- likes
- comments
- saves or shares
- content type labels

## Workflow

1. group posts by content pattern
2. identify winners and losers
3. infer the variables that matter most
4. write clear do-more / do-less / stop rules
5. design the next test cycle

## Output Contract

- performance pattern summary
- winning traits
- losing traits
- next-cycle plan

## Direct Prompt

```text
请帮我做“自有账号内容复盘与优化建议”。

不要只看数据高低，我要你回答：
1. 什么内容模式赢了
2. 为什么赢
3. 什么内容模式输了
4. 为什么输
5. 接下来我该多做什么、少做什么、停止什么
```

## Fallback

If performance data is incomplete, use a qualitative retro and explicitly note which conclusions are weak.
