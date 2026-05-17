from __future__ import annotations

import argparse
import copy
import json
import os
import re
import subprocess
import tempfile
from pathlib import Path

import requests
from requests import Response

from feishu_naming import build_report_title, scene_label_zh
from generate_scene_report import render_markdown_from_payload
from text_normalization import normalize_text, read_json_file, write_utf8_text


AUTH_URL = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
DOC_CREATE_URL = "https://open.feishu.cn/open-apis/docs_ai/v1/documents"
DOC_UPDATE_URL = "https://open.feishu.cn/open-apis/docs_ai/v1/documents/{document_id}"
DEFAULT_TIMEOUT = 30

DEFAULT_LARK_CLI_CANDIDATES = [
    Path(r"E:\飞书\lark-cli-bin\v1.0.25\lark-cli.exe"),
    Path(r"E:\飞书\lark-cli-bin\lark-cli.exe"),
    Path(r"E:\椋炰功\lark-cli-bin\v1.0.25\lark-cli.exe"),
    Path(r"E:\椋炰功\lark-cli-bin\lark-cli.exe"),
]

MARKDOWN_REPLACEMENTS = [
    ("## Working Context", "## 工作背景"),
    ("### Inputs", "### 输入信息"),
    ("### Minimum Evidence", "### 最低证据要求"),
    ("### Ideal Evidence", "### 理想证据"),
    ("### Constraints", "### 约束条件"),
    ("### Requested Outputs", "### 要求输出"),
    ("### Ready Checklist", "### 就绪检查清单"),
    ("## Executive Summary", "## 执行摘要"),
    ("## Operator Checklist", "## 操作检查清单"),
    ("## Common Failure Modes", "## 常见失败模式"),
    ("## Direct-Use Template", "## 直接使用模板"),
    ("### Variable Inputs", "### 变量输入"),
    ("### Codex Prompt Scaffold", "### Codex 提示词脚手架"),
    ("### Chinese Prompt Scaffold", "### 中文提示词脚手架"),
    ("### Workflow Steps", "### 工作流步骤"),
    ("### Output Checklist", "### 输出检查清单"),
    ("## Evidence", "## 证据"),
    ("### Evidence References", "### 证据引用"),
    ("## Fields To Capture Next Time", "## 下次补采字段"),
    ("## Assets", "## 资产"),
    ("## Notes", "## 备注"),
    ("## Sources", "## 来源"),
    ("## Executive Conclusion", "## 核心结论"),
    ("## Objects To Track", "## 追踪对象"),
    ("## Why They Matter", "## 重要原因"),
    ("## Fields To Capture Next Time", "## 下次补采字段"),
    ("## Next Action", "## 下一步动作"),
    ("## Structure Logic", "## 结构逻辑"),
    ("## Core Mechanism", "## 核心机制"),
    ("## Reusable Formula", "## 可复用公式"),
    ("## Risks And Adaptation Notes", "## 风险与改编说明"),
    ("## High-Level Judgment", "## 高层判断"),
    ("## Evidence Clusters", "## 证据分组"),
    ("## Recommended Action", "## 建议动作"),
    ("## Open Questions", "## 待确认问题"),
    ("## Target", "## 目标"),
    ("## Audience", "## 受众"),
    ("## Message", "## 信息主轴"),
    ("## Structure", "## 结构"),
    ("## Creative Constraints", "## 创作约束"),
    ("## Core Invariant", "## 核心不变量"),
    ("## Variable Matrix", "## 变量矩阵"),
    ("## Expected Effect", "## 预期效果"),
    ("## What To Learn", "## 学习目标"),
    ("- Scene: ", "- 场景："),
    ("- Project: ", "- 项目："),
    ("- Deliverable Type: ", "- 交付物类型："),
    ("- Generated: ", "- 生成时间："),
    ("- Status: ", "- 状态："),
    ("- Scenario File: ", "- 场景文件："),
    ("- Conclusion: ", "- 结论："),
    ("- Why It Matters: ", "- 为什么重要："),
    ("- Next Action: ", "- 下一步动作："),
    ("- Confidence: ", "- 置信度："),
    ("- Recommended Request: ", "- 推荐请求："),
    ("- Recommended Request (ZH): ", "- 推荐请求（中文）："),
    ("- Runner Args:", "- 运行参数："),
    ("| Variable | Meaning | Example | Required |", "| 变量 | 含义 | 示例 | 是否必填 |"),
    ("| Label | Detail | Source |", "| 标签 | 详情 | 来源 |"),
    ("| Source Type | Source ID | Source URL | Time Range | Excerpt | Supports |", "| 来源类型 | 来源 ID | 来源链接 | 时间范围 | 摘录 | 支撑点 |"),
]

VALUE_REPLACEMENTS = [
    ("collection_board", "采集看板"),
    ("breakdown_report", "拆解报告"),
    ("insight_report", "洞察报告"),
    ("creation_brief", "创作制作简报"),
    ("testing_matrix", "测试矩阵"),
    ("imported", "已导入"),
    ("Feishu Batch Smoke", "飞书批量冒烟"),
    ("Competitor Account Weekly Review", "竞品账号周报"),
    ("Real TikTok capture-pack import from ", "真实 TikTok capture-pack 导入自 "),
    (" for uncategorized lane. Current board size: ", "，当前用于未分类赛道。当前看板规模："),
    (" ranked / ", " 条已排序 / "),
    (" qualified with min-like threshold ", " 条达标，最低点赞阈值 "),
    ("Source profile: ", "来源账号："),
    ("session quality: ", "会话质量："),
    ("queries: ", "查询词："),
    ("topics: ", "主题："),
    ("Lead candidate: ", "首要候选："),
    (" likes, ", " 点赞，"),
    (" plays, ", " 播放，"),
    (" shares, ", " 分享，"),
    (" comments.", " 评论。"),
    (" likes=", " 点赞="),
    (" comments=", " 评论="),
    (" shares=", " 分享="),
    ("Profile: ", "账号："),
    ("Ranked video count: ", "排序视频数："),
    ("Qualified video count: ", "达标视频数："),
    ("Capture root: ", "采集根目录："),
    ("competitor accounts", "竞品账号"),
    ("One weekly batch of posts", "一周帖子样本"),
    ("Prior week notes", "上一周备注"),
    ("Per-post performance context", "逐帖表现上下文"),
    ("Target market", "目标市场"),
    ("accounts in one matrix", "个账号并排矩阵"),
    ("summary.json or aggregate_summary.json", "summary.json 或 aggregate_summary.json"),
    ("profile_summary.json or summary.json", "profile_summary.json 或 summary.json"),
    ("ranked_videos.json or aggregate_ranked_videos.json", "ranked_videos.json 或 aggregate_ranked_videos.json"),
    ("aggregate_qualified_videos.json or qualified_video_links.txt", "aggregate_qualified_videos.json 或 qualified_video_links.txt"),
    ("aggregate_report.md", "aggregate_report.md"),
    ("video_details.json", "video_details.json"),
    ("If only one week exists, mark it as baseline rather than trend.", "如果当前只有一周数据，应标记为基线周，而不是趋势结论。"),
    ("Real TikTok anonymous-session capture. Comment sampling is missing in this pack.", "当前为真实 TikTok 匿名会话采集，该包缺少评论采样。"),
    ("Conclusions should stay tied to ranked metrics, captions, and capture-pack summaries only.", "结论必须只绑定到排序指标、caption 和 capture-pack 摘要，不要外推。"),
    ("Per-account weekly summary", "分账号周度摘要"),
    ("Cross-account comparison", "跨账号横向对比"),
    ("Notable shifts", "关键变化"),
    ("Strategy-shift view", "策略变化视图"),
    ("Implications for the user", "对你的启发"),
    ("TikTok-native ranked-pattern conclusions", "TikTok 原生排序模式结论"),
    ("Reusable adaptation rules grounded in the capture pack", "基于 capture pack 的可复用改写规则"),
    ("Posts are grouped by account and week", "帖子已按账号和周维度分组"),
    ("Shift vs prior week can be stated", "可以明确说明相较上一周的变化"),
    ("Weekly response actions can be prioritized", "可以排出本周响应动作优先级"),
    ("Cross-account comparison is possible", "可以做跨账号横向对比"),
    ("Top-ranked videos are clearly identified", "已明确标出高排名视频"),
    ("Transferable pattern is separated from profile-specific brand power", "可迁移模式已与账号自身品牌势能区分"),
    ("Group posts by account and week before comparing anything.", "先按账号和周维度整理帖子，再开始比较。"),
    ("Highlight weekly shifts, not just weekly totals.", "强调每周变化，不要只罗列总量。"),
    ("Compare accounts horizontally, not as isolated mini-reports.", "按横向对比账号，不要拆成互不关联的小报告。"),
    ("Finish with actions the user should take this week.", "最后必须落到本周可执行动作。"),
    ("Listing activity without interpreting pattern changes.", "只罗列动态，不解释模式变化。"),
    ("Calling something a trend with only one baseline week.", "只有一周基线就贸然下趋势结论。"),
    ("Missing strategy-change detection because the report is too inventory-like.", "报告过于像库存清单，导致策略变化识别缺失。"),
    ("No horizontal comparison across accounts.", "没有做跨账号横向对比。"),
    ("Human-readable run or campaign name", "便于识别的运行名或项目名"),
    ("Target market or locale when the scene depends on one market", "当场景依赖单一市场时的目标市场或地区"),
    ("Links, screenshots, transcripts, exports, OCR text, or copied notes used as source evidence", "作为源证据使用的链接、截图、转写、导出文件、OCR 文本或摘录备注"),
    ("What the operator wants this scene to produce", "操作者希望该场景产出的结果"),
    ("weekly competitor report and action board", "每周竞品账号周报与动作看板"),
    ("Use scene 18 as the governing workflow.", "以场景 18 作为本次工作的主流程。"),
    ("Normalize the provided evidence into this input set before analysis: ", "分析前先把现有证据归整为以下输入："),
    ("If evidence is missing, state the gap explicitly before continuing. Minimum evidence to proceed: ", "如果证据不足，先明确缺口再继续。最低开工证据："),
    ("Produce these outputs in operator-ready form: ", "最终必须产出以下可直接给运营使用的结果："),
    ("Highlight weekly pattern shifts across accounts, not just activity counts.", "强调账号之间的周度模式变化，而不是只看活跃量。"),
    ("Translate observed shifts into action items for the current week.", "把观察到的变化转成当前周的动作项。"),
    ("Explain why a breakout happened instead of only naming the breakout post.", "解释爆发发生的原因，而不是只点名哪条爆了。"),
    ("Fill the scaffold with reusable conclusions, tables, ranking logic, and next actions instead of generic commentary.", "优先填入可复用结论、表格、排序逻辑和下一步动作，不要停留在泛泛点评。"),
    ("Posts are organized by account and week.", "帖子已按账号和周维度组织。"),
    ("The report explains shifts instead of listing raw activity.", "报告解释了变化，而不只是罗列原始动态。"),
    ("Cross-account strategy differences are explicit.", "跨账号策略差异已明确写出。"),
    ("This week's response actions are prioritized.", "本周响应动作已经排序。"),
    ("Summary", "摘要"),
    ("Profile summary", "账号摘要"),
    ("Ranked video ", "排序视频 "),
    ("Summarize what changed across the watched competitor accounts this week.", "概括本周被监控竞品账号发生了什么变化。"),
    ("This TikTok capture pack establishes a usable weekly competitor-account baseline: the account is winning with a small number of editorially packaged, emotion-first or culture-first posts.", "这份 TikTok capture pack 已经建立了一个可用的竞品账号周度基线：该账号当前主要依靠少量带编辑包装感、情绪优先或文化优先的内容取胜。"),
    ("Even one weekly baseline is enough to decide what kind of post packaging deserves continued tracking versus what is just account noise.", "即便只有一周基线，也足以判断哪些发帖包装值得持续追踪，哪些只是账号噪音。"),
    ("Use this pack as the baseline week, then compare the next capture against the same account fields to spot packaging or performance shifts.", "先把这份采集包作为基线周，下一次采集继续按同一组账号字段对比，就能识别包装或表现变化。"),
    ("Account baseline: ", "账号基线："),
    ("Top winning lane this week: ", "本周最强赛道："),
    ("Proof / authority teardown", "证明 / 权威拆解"),
    ("Breakout post cue: ", "爆发帖线索："),
    ("Treat this as a baseline-week report unless a prior capture exists for the same account set.", "在同一批账号还没有上一期 capture 前，这份报告应视为基线周报告。"),
    ("Capture each account's weekly output.", "记录每个账号这一周的输出。"),
    ("Per-Account Weekly Summary", "分账号周度摘要"),
    ("Account", "账号"),
    ("Post Volume", "发帖量"),
    ("Winning Post", "最佳帖子"),
    ("Main Theme", "主主题"),
    ("Breakout Signal", "爆发信号"),
    ("Shift vs Prior Week", "相较上周变化"),
    ("Strategy Change", "策略变化"),
    ("Top score=", "最高得分="),
    ("Baseline week only", "仅基线周"),
    ("Interpret the important changes, not just list them.", "解释关键变化，而不是只做罗列。"),
    ("Notable Weekly Shifts", "本周关键变化"),
    ("Observed Shift", "观察到的变化"),
    ("Who Changed", "变化对象"),
    ("Why It Matters", "为什么重要"),
    ("Breakout Attribution", "爆发归因"),
    ("Implication", "启发"),
    ("Proof / authority", "证明 / 权威"),
    ("Authority-led explainer", "权威型讲解"),
    ("Lean harder into trust / authority packaging.", "更明显地强化了信任 / 权威型包装。"),
    ("Leaning harder into trust / authority packaging.", "更明显地强化了信任 / 权威型包装。"),
    ("Watch for repetition, drift, or a weaker variant next week; lane: ", "下周重点观察是否重复、漂移或出现弱化版本；赛道："),
    ("Hook / emotional framing", "钩子 / 情绪框架"),
    ("Subtitle-led emotional montage", "字幕驱动的情绪蒙太奇"),
    ("Lean harder into emotional or moment-led packaging.", "更明显地强化了情绪型或时刻感包装。"),
    ("Leaning harder into emotional or moment-led packaging.", "更明显地强化了情绪型或时刻感包装。"),
    ("Topic / angle", "话题 / 角度"),
    ("Recognition-first short explainer", "识别点优先短讲解"),
    ("Testing newer topic or angle packaging.", "正在测试更新的话题或角度包装。"),
    ("account_week", "账号周记录"),
    ("account-a-week", "账号-周样本"),
    ("paste-account-or-sheet-link", "粘贴账号或表格链接"),
    ("week-window", "周时间窗"),
    ("Weekly summary showing the main content or strategy shift for account A.", "用于展示账号 A 主要内容或策略变化的周度摘要。"),
    ("Weekly shift attribution", "周度变化归因"),
    ("breakout-post-1", "爆发帖-1"),
    ("paste-video-link", "粘贴视频链接"),
    ("Representative breakout post used to explain why the account moved.", "用于解释账号为何变化的代表性爆发帖。"),
    ("Breakout attribution", "爆发归因"),
    ("List missing fields needed for stronger weekly comparison.", "列出为了做更强周对比还缺哪些字段。"),
    ("Capture a second week from the same account so shifts can be compared against a real baseline.", "补采同一账号的第二周数据，这样变化才能与真实基线比较。"),
    ("Add comment-sample availability and featured-person tags per post.", "为每条帖子补上评论采样可用性和出镜人物标签。"),
    ("Preserve cover/headline evidence if the account changes packaging style.", "如果账号更换包装风格，保留封面 / 首句证据。"),
    ("Next Capture Upgrade", "下一次采集升级"),
    ("Field", "字段"),
    ("Priority", "优先级"),
    ("Second-week snapshot", "第二周快照"),
    ("Required to tell durable packaging drift from one-week noise.", "用于判断是持续包装漂移，还是仅一周噪音。"),
    ("Comment-sample flag", "评论采样标记"),
    ("Shows whether audience language supports the ranking pattern or not.", "用于判断受众语言是否支撑当前排序模式。"),
    ("Featured-person / authority tag", "出镜人物 / 权威标签"),
    ("Separates packaging wins from celebrity or official-account lift.", "用于区分包装胜利与名人 / 官方账号带来的流量提升。"),
    ("Cover / first-frame evidence", "封面 / 首帧证据"),
    ("Lets the next compare include click packaging, not only caption-level cues.", "让下次对比能纳入点击包装，而不只看 caption 线索。"),
    ("State what the user should do this week in response.", "说明本周你应该采取什么动作。"),
    ("Weekly Operator Response", "本周运营响应"),
    ("Action Area", "动作领域"),
    ("Recommendation", "建议"),
    ("Urgency", "紧急度"),
    ("What Changed Strategically", "策略变化点"),
    ("Watch", "观察"),
    ("Track whether the same account keeps using the same winning hook family next week.", "观察同一账号下周是否继续复用同类获胜钩子。"),
    ("Test", "测试"),
    ("Try one smaller-account version with the same editorial framing but stronger owned proof.", "测试一个更适合小账号的版本，保留同类编辑框架，但补更强的自有证明。"),
    ("Portable packaging should be separated from pure distribution or authority lift.", "需要把可迁移包装与纯分发优势 / 权威势能区分开。"),
    ("Ignore", "忽略"),
    ("Do not overlearn official-account distribution effects as if they were universal.", "不要把官方账号分发优势误当成普适规律。"),
    ("Suppress if the only apparent edge is platform-scale authority rather than reusable structure.", "如果唯一优势来自平台级权威而不是可复用结构，应降低权重。"),
    ("Aggregate markdown report from the real TikTok capture pack.", "来自真实 TikTok capture pack 的聚合 Markdown 报告。"),
    ("Aggregate workbook from the real TikTok capture pack.", "来自真实 TikTok capture pack 的聚合工作簿。"),
    ("file `", "文件 `"),
    ("Ranked-video workbook from the single TikTok capture pack.", "来自单个 TikTok capture pack 的排序视频工作簿。"),
    ("Ranked-video workbook.", "排序视频工作簿。"),
    ("Qualified-video workbook.", "达标视频工作簿。"),
    ("Flattened comment export from the single TikTok capture pack.", "来自单个 TikTok capture pack 的扁平评论导出。"),
    ("teardown", "拆解"),
    ("US", "美国"),
    ("browser_same_origin_api_ok", "浏览器同源接口正常"),
    ("queries: none", "查询词：无"),
    ("topics: none", "主题：无"),
    ("caption", "标题文案"),
    ("capture-pack", "采集包"),
    ("capture pack", "采集包"),
    (" is possible", "已具备可行性"),
    ("proof. ", "证明。"),
    ("One keyword", "至少 1 个关键词"),
    ("At least 5 candidate videos, links, or screenshots", "至少提供 5 条候选视频、链接或截图"),
    ("Do not rank on views alone. Keep reuse value in the scoring logic.", "不要只按播放量排序，复用价值必须进入评分逻辑。"),
    ("If live browsing is unavailable, rely on user-provided screenshots, exports, or copied links.", "如果当前无法实时浏览，就依赖用户提供的截图、导出结果或复制链接继续分析。"),
    ("Ranked shortlist", "排序后的候选 shortlist"),
    ("Reason each selected video matters", "逐条说明每条入选视频为什么值得研究"),
    ("Study-next recommendation", "给出下一步优先深拆建议"),
    ("Candidate set is from one market", "候选集合来自同一市场"),
    ("At least basic performance signals exist", "至少具备基础表现信号"),
    ("Useful-for tags can be assigned", "可以为每条候选打上复用用途标签"),
    ("Normalize all candidates into one market before ranking.", "排序前先把所有候选统一到同一市场维度。"),
    ("Keep the rejected pool so later ranking logic can be improved.", "保留未入选池，便于后续继续优化排序逻辑。"),
    ("Ranking on views only and ignoring reuse value.", "只看播放量，不看复用价值。"),
    ("Mixing multiple markets or product intents in one shortlist.", "把多个市场或多个产品意图混进同一 shortlist。"),
    ("This capture pack already contains a usable shortlist of TikTok posts worth deeper study because the strongest rows now carry recoverable 标题文案, hook, and topic signals in addition to ranking metrics.", "这份采集包已经具备可直接深拆的 TikTok 候选 shortlist，因为高分视频除了排序指标，还保留了可恢复的标题文案、钩子和主题信号。"),
    ("Top candidate topic:", "头部候选主题："),
    ("Top candidate hook:", "头部候选钩子："),
    ("These are not just top-view posts; they are ranked candidates with reusable packaging traits and stronger recovered text evidence.", "这些视频不只是播放高，而是具备可复用包装特征和更强文本恢复证据的排序候选。"),
    ("The best shortlist items should be routed by reuse value, not only raw numbers.", "最值得优先研究的 shortlist 项，应该按复用价值分流，而不只是看原始数字。"),
    ("Topic text missing", "主题文本缺失"),
    ("Creator or brand-context authority", "创作者或品牌语境型权威证明"),
    ("Packaging-led; no strong authority cue recovered", "包装驱动型，暂未恢复到强权威线索"),
    ("Preserve the exact framing language", "保留原始表达框架"),
    ("Compare performance shape, not just views", "比较表现结构，而不只看播放量"),
    ("Separate authority from packaging", "区分权威势能与包装能力"),
    ("Route into scene 08 if present", "如有评论样本则继续分流到 Scene 08"),
    ("Yes", "是"),
    ("Comments from at least 2 products", "至少需要来自 2 个商品或对象的评论"),
    ("If comment volume is light, mark findings as provisional.", "如果评论量偏少，所有判断都要标记为暂定。"),
    ("Pain-point synthesis", "痛点归纳"),
    ("Desire synthesis", "欲望归纳"),
    ("High-frequency phrases", "高频原话"),
    ("Persona summary", "人群画像总结"),
    ("Selection and content implications", "对选品和内容的启发"),
    ("Comments stay grouped by product", "评论需要按商品或对象分组"),
    ("Repeated phrases can be quoted", "高频原话可以直接引用"),
    ("Low-volume caveats are explicit", "低样本风险要明确写出"),
    ("Keep comments grouped by product before merging category signals.", "在合并品类级信号之前，先按商品或对象对评论分组。"),
    ("Quote repeated user language, not only analyst paraphrases.", "尽量引用用户原话，而不是只给分析师转述。"),
    ("Translate pains and desires into product and script implications.", "把痛点和欲望翻译成产品调整与脚本启发。"),
    ("Mixing one-off complaints with true repeated pains.", "把偶发抱怨误当成真实高频痛点。"),
    ("Summarizing sentiment without concrete user phrases.", "只总结情绪，不给具体用户原话。"),
    ("Ignoring the difference between desire, complaint, and trust signal.", "忽略欲望、抱怨和信任信号之间的区别。"),
    ("Trust signal", "信任信号"),
    ("general reaction", "泛情绪反应"),
    ("Sampled comments exist for only part of the ranked set, so these findings are provisional rather than category-complete.", "当前只对部分高排名样本采到了评论，因此这些结论只能算暂定，不代表完整品类。"),
    ("The pack is centered on TikTok's own account, so some complaints may reflect platform-policy sentiment more than content-category demand.", "这份采集包主要围绕 TikTok 官方账号，因此部分抱怨更可能反映平台政策情绪，而不完全是内容品类需求。"),
    ("Product direction", "产品方向"),
    ("Offer / positioning", "卖点与定位"),
    ("Script language", "脚本语言"),
    ("Proof content", "证明内容"),
    ("Why", "原因"),
    ("One keyword", "1 个关键词"),
    ("At least 5 candidate videos, links, or screenshots", "至少 5 条候选视频、链接或截图"),
    ("Comments from at least 2 products", "至少 2 个商品或对象的评论"),
    ("summary.json", "summary.json"),
    ("aggregate_summary.json", "aggregate_summary.json"),
    ("profile_summary.json", "profile_summary.json"),
    ("ranked_videos.json", "ranked_videos.json"),
    ("aggregate_ranked_videos.json", "aggregate_ranked_videos.json"),
    ("Ranked shortlist", "排序后的候选清单"),
    ("Reason each selected video matters", "逐条说明每条入选视频为何值得研究"),
    ("Study-next recommendation", "下一步研究建议"),
    ("Candidate set is from one market", "候选集来自同一市场"),
    ("At least basic performance signals exist", "至少具备基础表现信号"),
    ("Useful-for tags can be assigned", "可以打上复用用途标签"),
    ("Comments stay grouped by product", "评论按商品或对象分组"),
    ("Repeated phrases can be quoted", "可以直接引用高频原话"),
    ("Low-volume caveats are explicit", "低样本限制已明确说明"),
    ("This capture pack already contains a usable shortlist of TikTok posts worth deeper study because the strongest rows now carry recoverable 标题文案, hook, and topic signals in addition to ranking metrics.", "这份采集包已经包含一份可直接深拆的 TikTok 候选清单，因为高分样本除了排序指标，还保留了可恢复的标题文案、钩子和主题信号。"),
    ("Keep comments grouped by product before merging category signals.", "在合并品类级信号之前，先按商品或对象维度整理评论。"),
    ("Quote repeated user language, not only analyst paraphrases.", "尽量直接引用重复出现的用户原话，而不是只给分析师转述。"),
    ("Translate pains and desires into product and script implications.", "把痛点和欲望翻译成产品动作与脚本启发。"),
    ("Mixing one-off complaints with true repeated pains.", "把一次性抱怨混进真正的高频痛点。"),
    ("Summarizing sentiment without concrete user phrases.", "只总结情绪，不给具体用户原话。"),
    ("Ignoring the difference between desire, complaint, and trust signal.", "忽略欲望、抱怨和信任信号之间的区别。"),
    ("Rank", "排名"),
    ("Video / Link", "视频 / 链接"),
    ("Core Topic", "核心主题"),
    ("Performance Signal", "表现信号"),
    ("Useful For", "适合复用方向"),
    ("Why Selected", "入选原因"),
    ("Video", "视频"),
    ("Hook Strength", "钩子强度"),
    ("Proof Style", "证明方式"),
    ("Conversion Signal", "转化信号"),
    ("Main Reuse Value", "主要复用价值"),
    ("Why Capture It", "为什么要补采"),
    ("Required Next Time?", "下次是否必填"),
    ("Video link", "视频链接"),
    ("Caption / hook text", "标题文案 / 钩子文本"),
    ("Likes/comments/shares", "点赞 / 评论 / 分享"),
    ("Featured person or object", "出镜人物或核心对象"),
    ("Comment sample availability", "评论样本可用性"),
    ("Top candidate topic:", "头部候选主题："),
    ("Top candidate hook:", "头部候选钩子："),
    ("Topic text missing", "主题文本缺失"),
    ("Hook text missing", "钩子文本缺失"),
    ("Creator or brand-context authority", "创作者 / 品牌语境型证明"),
    ("Packaging-led; no strong authority cue recovered", "包装驱动型，暂未恢复到强权威线索"),
    ("comments_flat.csv", "comments_flat.csv"),
    ("Sampled comments exist for only part of the ranked set, so these findings are provisional rather than category-complete.", "当前只对部分高排名样本采集到了评论，因此这些判断只能视为暂定，不代表完整品类。"),
    ("The pack is centered on TikTok's own account, so some complaints may reflect platform-policy sentiment more than content-category demand.", "这份采集包主要围绕 TikTok 官方账号，因此部分抱怨更可能反映平台政策情绪，而不完全是内容品类需求。"),
    ("One video link or storyboard summary", "1 条视频链接或一份分镜摘要"),
    ("Separate deep logic from surface style.", "把深层机制和表层风格拆开看。"),
    ("One-line judgment", "一句话判断"),
    ("Structure map", "结构地图"),
    ("Viral mechanism", "爆点机制"),
    ("Reusable formula", "可复用公式"),
    ("Adaptation advice", "改写建议"),
    ("Hook, proof, and close can be reconstructed", "钩子、证明和结尾可以被重建"),
    ("At least one adaptation target is known", "至少已知一个改写目标"),
    ("The strongest single-video breakdown target in this real TikTok pack wins by making the first frame instantly legible, then using authority, context, or a featured-person cue as compressed proof.", "这条最值得拆解的单视频之所以能跑出来，核心在于首帧一眼可懂，然后用权威、语境或人物线索完成压缩证明。"),
    ("This matters because the reusable asset is not surface polish. It is the sequence that moves from recognition to proof to a soft continuation close without over-explaining.", "真正可复用的资产不是表面包装，而是从识别到证明、再到柔性续看结尾的顺序，而不是冗长解释。"),
    ("Rebuild the reference in order, then rewrite the proof layer so an owned product, creator, or evidence object can carry the same decision logic.", "先按原顺序重建参考视频，再重写证明层，让自有产品、创作者或证据对象承接同样的决策逻辑。"),
    ("Reconstruct the video in order: hook, setup, proof, close.", "按顺序重建这条视频：钩子、铺垫、证明、结尾。"),
    ("Separate core mechanism from creator-specific surface style.", "把核心机制和创作者特有表层风格拆开。"),
    ("Write at least one adaptation path before closing the report.", "在报告结束前至少写出一条改写路径。"),
    ("Confusing visual polish with the true conversion mechanism.", "把视觉精致感误当成真正的转化机制。"),
    ("Skipping the close or CTA logic because it looks simple.", "因为结尾或 CTA 看起来简单，就忽略其逻辑。"),
    ("Giving abstract praise without reusable takeaways.", "只给抽象夸奖，不提炼可复用结论。"),
    ("Reference video:", "参考视频："),
    ("Source account baseline:", "源账号基线："),
    ("Recovered hook:", "恢复出的钩子："),
    ("Recovered topic cue:", "恢复出的主题线索："),
    ("Authority signal:", "权威信号："),
    ("Segment", "段落"),
    ("What Happens", "发生了什么"),
    ("Estimated Timestamp", "预计时间点"),
    ("Setup", "铺垫"),
    ("Close / CTA", "结尾 / CTA"),
    ("Makes the post immediately legible before explanation starts", "在解释开始前就让帖子一眼可懂"),
    ("Prevents the viewer from dropping before the premise is understood", "防止用户在理解前就划走"),
    ("Replaces long explanation with fast credibility transfer", "用快速可信度转移替代长解释"),
    ("Fits TikTok-native consumption better than a hard conversion jump", "比硬性转化跳转更符合 TikTok 原生消费节奏"),
    ("The real mechanism is recognition-first compression: the viewer understands who or what matters before the video spends attention on explanation.", "真正的机制是识别优先的压缩表达：在视频开始解释之前，用户已经明白谁或什么最重要。"),
    ("The proof layer works because the source account can borrow trust from authority, a familiar creator, or a culturally legible moment instead of spelling out every claim.", "这条视频的证明层之所以成立，是因为源账号可以借用权威、熟悉创作者或文化线索来转移信任，而不是把每个论点都解释一遍。"),
    ("Portable logic: first-frame clarity plus compressed proof.", "可迁移逻辑：首帧清晰 + 压缩证明。"),
    ("Non-portable lift: official-account authority, featured-talent recognition, or distribution advantage.", "不可直接迁移的加成：官方账号权威、熟脸人物识别度或分发优势。"),
    ("Layer", "层级"),
    ("Observed", "观察到的表现"),
    ("Reusable?", "是否可复用"),
    ("Adaptation Note", "改写备注"),
    ("Keep the instant legibility but replace the original person, object, or topic with an owned one.", "保留一眼可懂的特性，但把原人物、原物件或原主题替换成自有对象。"),
    ("Do not copy cosmetic style unless it helps the proof order.", "除非有助于证明顺序，否则不要只复制表面风格。"),
    ("Swap in owned proof, receipts, product evidence, or collaborator trust.", "替换成自有证明、凭证、产品证据或合作方信任。"),
    ("Ask for the next watch, save, or low-friction action instead of a hard sell.", "引导下一次观看、收藏或低门槛动作，而不是硬卖。"),
    ("Path", "路径"),
    ("What To Keep", "保留什么"),
    ("What To Change", "改什么"),
    ("Risk", "风险"),
    ("Safer", "更稳妥"),
    ("Keep the hook structure and proof order", "保留钩子结构和证明顺序"),
    ("Replace official-account lift with one strong owned proof object", "用一个强自有证明对象替换官方账号势能"),
    ("May feel less native if proof is weak", "如果证明弱，成品会显得不够原生"),
    ("More aggressive", "更激进"),
    ("Keep only the recognition-first shell", "只保留识别优先的外壳"),
    ("Reframe the topic, talent, and close for a new product or creator", "围绕新产品或新创作者重写主题、人物和结尾"),
    ("May lose the original trust transfer if the new cue is not instantly legible", "如果新的识别线索不够一眼可懂，就会丢失原有信任转移效果"),
    ("Use https://www.tiktok.com/@tiktok/video/7631201918366289165 as the control breakdown target.", "把 https://www.tiktok.com/@tiktok/video/7631201918366289165 作为控制组拆解样本。"),
    ("Write one owned-proof adaptation and one creator-led adaptation from the same sequence.", "基于同一顺序，分别写一版自有证明改写和一版创作者驱动改写。"),
    ("Validate whether the hook still works after removing the original authority source.", "验证去掉原始权威来源后，钩子是否仍然成立。"),
    ("One video or visual summary", "1 条视频或一份视觉摘要"),
    ("If evidence is thin, mark the prompt as low-confidence.", "如果证据薄弱，就把提示词标成低置信度。"),
    ("Do not invent hidden production details; keep uncertain fields explicit.", "不要臆造隐藏制作细节，不确定字段要明确标出。"),
    ("Inferred original brief", "反推原始制作简报"),
    ("Generator-ready schema", "可直接喂给生成器的结构"),
    ("Shot-by-shot table", "分镜逐条表"),
    ("Product-adapted brief", "面向产品改写的制作简报"),
    ("field-level confidence flags", "字段级置信度标记"),
    ("Visual evidence is sufficient to infer shot language", "视觉证据足以反推镜头语言"),
    ("Low-confidence gaps are explicit if evidence is thin", "如果证据薄弱，低置信度缺口已明确标注"),
    ("The inferred brief can be separated into original and adapted versions", "可以把反推制作简报拆成原版和改写版"),
    ("This real TikTok reference suggests a prompt or production brief built around fast recognition, minimal explanation, and one trust-bearing social cue rather than heavy narrative complexity.", "这条真实 TikTok 参考视频更像是围绕快速识别、极简解释和单一信任线索搭建出的提示词或制作简报，而不是复杂叙事。"),
    ("That makes the inferred brief reusable: the operator can preserve visual pacing and premise order while swapping the proof object or featured cue onto a different product or account.", "这让反推出的制作简报具备可复用性：在保留视觉节奏和前提顺序的同时，可以把证明对象或人物线索切换到别的产品或账号。"),
    ("Treat the inferred brief as a structured creation blueprint, then mark which parts depend on source-account authority versus portable shot and copy logic.", "把反推制作简报当成结构化创作蓝图，再标出哪些部分依赖源账号权威，哪些属于可迁移的镜头和文案逻辑。"),
    ("State the likely creative intent before writing the inferred prompt.", "在写反推提示词前，先说清这条内容的可能创作意图。"),
    ("Translate observed output into generator-ready prompt blocks, not style buzzwords.", "把观察到的成品翻译成可直接喂给生成器的提示块，而不是空泛风格词。"),
    ("Keep an inferred-original brief separate from the product-adapted brief.", "把反推原始制作简报和产品改写制作简报分开写。"),
    ("Use field-level confidence labels where evidence is thin.", "在证据薄弱的字段上使用字段级置信度标记。"),
    ("Mark low-confidence guesses when evidence is thin.", "当证据薄弱时，要把猜测明确标成低置信度。"),
    ("Inventing prompt details not justified by the video.", "臆造视频里并没有支撑的提示词细节。"),
    ("Only describing visual style without pacing, shot, and VO logic.", "只描述视觉风格，不写节奏、镜头和口播逻辑。"),
    ("Skipping shot-level structure and leaving only one generic prompt paragraph.", "跳过分镜级结构，只留下一个泛泛提示词段落。"),
    ("Forgetting to rewrite the inferred brief for the user's product.", "忘了按用户产品重写反推制作简报。"),
    ("Recovered proof lane:", "恢复出的证明路径："),
    ("Primary adaptation lane:", "主要改写路径："),
    ("Inferred Original Brief Schema", "反推原始制作简报结构"),
    ("Dimension", "维度"),
    ("Observed Evidence", "观察到的证据"),
    ("Likely Intent", "可能意图"),
    ("Confidence", "置信度"),
    ("Keep the output socially legible before detail appears", "在细节出现前先保证成品具备社交平台可读性"),
    ("Avoid clutter that hides the premise", "避免让前提被杂乱信息遮住"),
    ("Compressed setup, early proof, soft close", "快速铺垫、前置证明、柔性结尾"),
    ("Avoid explainers that delay the core promise", "避免长解释拖慢核心承诺露出"),
    ("Short premise-led beats with quick recognition framing", "用短节拍承载前提，并快速露出识别线索"),
    ("Lead with the cue that makes the viewer instantly care", "先给出让用户立刻在意的线索"),
    ("Visible and believable over polished and cinematic", "优先清晰可信，而不是过度电影感"),
    ("Keep proof clear and believable", "让证明清楚且可信"),
    ("Carry trust quickly", "快速承接信任"),
    ("Original sound or recovered social-native audio", "原始音频或恢复出的社交原生音轨"),
    ("Support the editorial mood without overpowering the cue", "支撑内容氛围，但不要盖过核心线索"),
    ("Fast cuts or compact beat changes", "快速剪切或紧凑节拍变化"),
    ("Protect clarity and momentum", "保护信息清晰度和推进感"),
    ("Creative Layer", "创作层"),
    ("Why It Likely Works", "为什么它可能有效"),
    ("What Evidence Supports It", "哪些证据支持这一点"),
    ("The first cue is instantly legible and emotionally or socially recognizable.", "第一条线索一眼可懂，并带有情绪或社交识别度。"),
    ("The proof layer leans on packaging-led; no strong authority cue recovered rather than a long argument.", "证明层更偏向包装驱动，而不是长篇论证。"),
    ("Compression matters more than cinematic complexity.", "压缩表达比电影化复杂度更重要。"),
    ("The close nudges continuation instead of forcing a hard CTA.", "结尾更像引导继续观看，而不是强推 CTA。"),
    ("Generator-Ready Brief", "可直接交给生成器的制作简报"),
    ("Block", "模块"),
    ("Prompt / Brief Content", "提示词 / 制作简报内容"),
    ("Evidence Ref", "证据引用"),
    ("Open on the clearest recognition cue, then tighten around proof", "先用最清晰的识别线索开场，再收紧到证明层"),
    ("Short beats, little dead air, no long setup before the reason to watch is clear", "节拍短、空镜少，在说明为什么值得看之前不要铺垫太久"),
    ("Shot-Level Breakdown", "分镜逐条拆解"),
    ("Shot", "镜头"),
    ("Duration", "时长"),
    ("Scene / Subject", "场景 / 主体"),
    ("Action", "动作"),
    ("Voiceover / Overlay", "口播 / 叠字"),
    ("Purpose", "目的"),
    ("Asset Need", "素材需求"),
    ("Opening recognition cue", "开场识别线索"),
    ("Make the premise legible instantly", "让前提瞬间可懂"),
    ("Recognition", "识别"),
    ("Hero cue / hook frame", "主钩子画面"),
    ("Setup / context beat", "铺垫 / 语境段"),
    ("Compress the scenario or topic", "压缩场景或主题"),
    ("Context", "语境"),
    ("Support frame or subtitle", "辅助画面或字幕"),
    ("Proof beat", "证明段"),
    ("Show packaging-led; no strong authority cue recovered with one trust cue", "展示包装驱动型证明，并补一条可信线索"),
    ("Support the promise with proof, not explanation", "用证明支撑承诺，而不是继续解释"),
    ("Trust", "信任"),
    ("Owned proof object", "自有证明对象"),
    ("Continuation close", "续看型结尾"),
    ("Return to the main cue and guide the next click or watch", "回到主线索，并引导下一次点击或观看"),
    ("Continuation CTA", "续看 CTA"),
    ("Soft conversion", "柔性转化"),
    ("CTA frame / end card", "CTA 画面 / 结尾卡"),
    ("Product-Adapted Brief", "产品改写版制作简报"),
    ("Adaptation Layer", "改写层"),
    ("Keep From Reference", "从参考里保留什么"),
    ("Rewrite For Product", "按产品改写什么"),
    ("Generator Handoff Field", "生成器交接字段"),
    ("Open Risk", "开放风险"),
    ("Recognition-first opening and compressed premise", "识别优先开场和压缩前提"),
    ("Swap the source cue for the user's product promise", "把源视频线索替换成用户产品承诺"),
    ("Hook / opening frame", "钩子 / 开场画面"),
    ("If the owned product lacks instant visual recognition, the hook needs extra proof support", "如果自有产品缺少一眼识别度，钩子就需要更强证明支撑"),
    ("Replace account authority with one owned proof object or testimonial", "用一个自有证明对象或见证替代账号权威"),
    ("Proof device", "证明装置"),
    ("Weak proof will make the brief feel copied but unsupported", "证明弱时，整份制作简报会显得像照抄却没有支撑"),
    ("Social-native editorial context", "社交原生编辑语境"),
    ("Use available talent, object, or demo footage only", "只使用实际可用的人物、物件或演示素材"),
    ("Talent / scene availability", "人物 / 场景可用性"),
    ("Do not imply unsupported scenes or creator cameos", "不要暗示并不存在的场景或创作者 cameo"),
    ("Soft continuation close", "柔性续看结尾"),
    ("Match the CTA to save, learn-more, or low-friction product curiosity", "让 CTA 对应收藏、了解更多或低门槛产品好奇心"),
    ("Close / CTA line", "结尾 / CTA 文案"),
    ("Hard-sell CTA may break the native pacing", "硬卖型 CTA 会破坏原生节奏"),
    ("One creator account or several videos from one creator", "1 个创作者账号或同一创作者的多条视频"),
    ("Separate creator-specific advantage from transferable pattern.", "把创作者特有优势和可迁移模式分开。"),
    ("Creator playbook", "创作者打法手册"),
    ("Repeatable formulas", "可重复公式"),
    ("Non-transferable advantages", "不可迁移优势"),
    ("Adaptation path", "改写路径"),
    ("Repeated patterns appear across multiple videos", "多个视频中出现了重复模式"),
    ("Creator-specific advantages are separated", "创作者专属优势已被单独拆出"),
    ("Adaptation path for user product已具备可行性", "面向用户产品的改写路径已具备可行性"),
    ("This TikTok account sample suggests a repeatable editorial formula: attach the post to a recognizable creator, story, or cultural moment, then use minimal copy to let affinity do the work.", "这组 TikTok 账号样本呈现出一套可重复的编辑公式：把帖子挂靠到可识别的创作者、故事或文化时刻，再用极简文案让熟悉感自己完成转化。"),
    ("The pattern is useful for TikTok projects that need stronger social-native packaging without long explanation-heavy intros.", "这套模式适合那些需要更强社交原生包装、又不想靠长解释开场的 TikTok 项目。"),
    ("Translate the account's strongest editorial packaging moves into a reusable creator- or community-led content brief.", "把这个账号最强的编辑包装动作翻译成一份可复用的创作者驱动或社区驱动内容制作简报。"),
    ("Use multiple creator samples before declaring a repeatable formula.", "在宣布形成可重复公式前，先至少看多个创作者样本。"),
    ("Map repeated hook, pacing, proof, and CTA patterns separately.", "把重复出现的钩子、节奏、证明和 CTA 模式分别拆出来。"),
    ("Map repeated 钩子, pacing, proof, and CTA patterns separately.", "把重复出现的钩子、节奏、证明和 CTA 模式分别拆出来。"),
    ("Explicitly separate transferable pattern from creator advantage.", "明确区分可迁移模式和创作者优势。"),
    ("Overfitting one breakout video into a full creator formula.", "把一条爆发视频过拟合成整个创作者公式。"),
    ("Ignoring trust or identity advantages unique to the creator.", "忽略只属于该创作者的信任或身份优势。"),
    ("Ending with admiration instead of adaptation rules.", "最后只剩夸赞，而没有改写规则。"),
    ("Pattern Area", "模式领域"),
    ("What Repeats", "重复出现了什么"),
    ("Example Evidence", "示例证据"),
    ("Transferable Pattern", "可迁移模式"),
    ("Why It Transfers", "为什么可迁移"),
    ("How To Adapt", "如何改写"),
    ("Creator-Specific Advantage", "创作者特有优势"),
    ("Why It Does Not Transfer Cleanly", "为什么不能直接迁移"),
    ("Official-account authority", "官方账号权威"),
    ("A large platform account has built-in distribution and credibility most projects do not have.", "大型平台账号自带分发和公信力，大多数项目并不具备。"),
    ("Featured-talent lift", "出镜人物加成"),
    ("Recognition from known creators or cultural moments may be doing part of the ranking work.", "熟悉创作者或文化时刻的识别度，可能本身就在贡献排序表现。"),
    ("Missing comments", "缺少评论"),
    ("Without sampled comments, true audience-language resonance is under-evidenced in this import.", "没有评论样本时，这次导入对真实受众语言共鸣的证据仍然不足。"),
    ("Assign one top-ranked post to a creator-led rewrite lane and one to a moment/outcome rewrite lane.", "把一条高排名帖子分到创作者驱动改写线，另一条分到时刻 / 结果驱动改写线。"),
    ("Build one smaller-account version with a stronger owned proof object before filming anything else.", "在继续拍摄前，先做一版更适合小账号、且自有证明更强的版本。"),
    ("Measure whether lighter copy plus faster recognition improves early engagement enough to justify reusing the formula.", "验证更轻的文案和更快的识别是否足以改善早期互动，从而证明这套公式值得复用。"),
    ("Operator Dispatch", "运营分发"),
    ("Lane", "分发线"),
    ("What To Do Now", "现在该做什么"),
    ("Why This Lane Exists", "为什么需要这条线"),
    ("Keep tracking which winners depend on featured-person recognition or official-account lift.", "持续追踪哪些胜出样本依赖人物识别度或官方账号势能。"),
    ("This stops the team from mistaking distribution advantage for portable format logic.", "这样可以避免团队把分发优势误认成可迁移格式逻辑。"),
    ("Run one creator-led rewrite and one proof-object-led rewrite from the top account references.", "基于头部账号参考，分别跑一版创作者驱动改写和一版证明对象驱动改写。"),
    ("This is the fastest way to learn whether the pattern survives after authority replacement.", "这是验证替换掉权威来源后模式是否仍成立的最快方式。"),
    ("Do not escalate rows whose only real edge is platform-scale authority.", "不要继续放大那些唯一优势只是平台级权威的样本。"),
    ("Those rows distort smaller-account replication planning.", "这类样本会扭曲小账号复刻规划。"),
]

MARKDOWN_REPLACEMENTS = sorted(MARKDOWN_REPLACEMENTS, key=lambda item: len(item[0]), reverse=True)
VALUE_REPLACEMENTS = sorted(VALUE_REPLACEMENTS, key=lambda item: len(item[0]), reverse=True)


def translate_text_value(text: str) -> str:
    translated = normalize_text(text, strip=False)
    for source, target in VALUE_REPLACEMENTS:
        translated = translated.replace(source, target)
    return translated


def translate_nested_value(value: object) -> object:
    if isinstance(value, str):
        return translate_text_value(value)
    if isinstance(value, list):
        return [translate_nested_value(item) for item in value]
    if isinstance(value, dict):
        return {key: translate_nested_value(item) for key, item in value.items()}
    return value


def infer_scene_id(metadata: dict) -> str:
    scene_id = normalize_text(metadata.get("scene"))
    if scene_id:
        return scene_id
    scenario_file = normalize_text(metadata.get("scenario_file"))
    match = re.search(r"(\d{2})-", scenario_file)
    if match:
        return match.group(1)
    scene_slug = normalize_text(metadata.get("scene_slug"))
    match = re.match(r"(\d{2})-", scene_slug)
    if match:
        return match.group(1)
    scene_title = normalize_text(metadata.get("scene_title"))
    for candidate, keywords in {
        "01": ["viral video collection"],
        "08": ["comment mining", "persona report"],
        "17": ["creator pattern"],
        "18": ["account weekly"],
        "19": ["account retro"],
    }.items():
        if all(keyword in scene_title.lower() for keyword in keywords):
            return candidate
    return ""


def localize_report_payload(report: dict, title: str) -> dict:
    localized = translate_nested_value(copy.deepcopy(report))
    metadata = localized.get("metadata") or {}
    scene_id = infer_scene_id(metadata)
    metadata["scene"] = scene_id
    metadata["title"] = title
    metadata["scene_title"] = scene_label_zh(scene_id)
    metadata["project"] = title
    localized["metadata"] = metadata

    # Feishu doc is a delivery surface, not an operator dev template.
    # Remove noisy English-first execution scaffolds from the body.
    localized["execution_template"] = {}

    working_context = localized.get("working_context") or {}
    working_context.pop("ideal_evidence", None)
    localized["working_context"] = working_context

    operator_guide = localized.get("operator_guide") or {}
    localized["operator_guide"] = operator_guide

    assets = localized.get("assets") or []
    filtered_assets = []
    for asset in assets:
        if not isinstance(asset, dict):
            continue
        path_text = normalize_text(asset.get("path"))
        if any(path_text.endswith(suffix) for suffix in [".xlsx", ".csv", ".json", ".md"]):
            filtered_assets.append(asset)
    localized["assets"] = filtered_assets[:6]

    return localized


def localize_markdown(markdown: str) -> str:
    localized = markdown
    for source, target in MARKDOWN_REPLACEMENTS:
        localized = localized.replace(source, target)
    filtered_lines = []
    for line in localized.splitlines():
        stripped = line.strip()
        if stripped.startswith("_") and stripped.endswith("_"):
            continue
        filtered_lines.append(line)
    localized = "\n".join(filtered_lines)
    localized = re.sub(r": file `", "：文件 `", localized)
    localized = re.sub(r": https://", "：https://", localized)
    localized = re.sub(r"\| file `", "| 文件 `", localized)
    localized = localized.replace("| Rank | Video / Link | Core Topic | Performance Signal | Useful For | Why Selected |", "| 排名 | 视频 / 链接 | 核心主题 | 表现信号 | 适合复用方向 | 入选原因 |")
    localized = localized.replace("| Video | Hook Strength | Proof Style | Conversion Signal | Main Reuse Value |", "| 视频 | 钩子强度 | 证明方式 | 转化信号 | 主要复用价值 |")
    localized = localized.replace("| Field | Why Capture It | Required Next Time? |", "| 字段 | 为什么要补采 | 下次是否必填 |")
    localized = localized.replace("| Cluster Type | Repeated Phrase / Theme | What It Suggests | Product / Content 启发 |", "| 聚类类型 | 重复短语 / 主题 | 它说明了什么 | 对产品 / 内容的启发 |")
    localized = localized.replace("| Decision Area | 建议 | Why |", "| 决策领域 | 建议 | 原因 |")
    localized = localized.replace("| Segment | What Happens | 为什么重要? | Estimated Timestamp |", "| 段落 | 发生了什么 | 为什么重要 | 预计时间点 |")
    localized = localized.replace("| Pattern Area | What Repeats | Example Evidence |", "| 模式领域 | 重复出现了什么 | 示例证据 |")
    localized = localized.replace("| Layer | Transferable Pattern | 原因 It Transfers | How To Adapt |", "| 层级 | 可迁移模式 | 为什么可迁移 | 如何改写 |")
    localized = localized.replace("| Creator-Specific Advantage | 原因 It Does Not Transfer Cleanly |", "| 创作者特有优势 | 为什么不能直接迁移 |")
    localized = localized.replace("| Lane | What To Do Now | 原因 This Lane Exists |", "| 分发线 | 现在该做什么 | 为什么需要这条线 |")
    localized = localized.replace("| Trust signal |", "| 信任信号 |")
    localized = localized.replace("| general reaction |", "| 泛情绪反应 |")
    localized = localized.replace("| Product direction |", "| 产品方向 |")
    localized = localized.replace("| Offer / positioning |", "| 卖点与定位 |")
    localized = localized.replace("| Script language |", "| 脚本语言 |")
    localized = localized.replace("| Proof content |", "| 证明内容 |")
    localized = localized.replace("shortlist", "候选清单")
    localized = localized.replace("hook", "钩子")
    localized = localized.replace("plays=", "播放=")
    localized = localized.replace("likes=", "点赞=")
    localized = localized.replace("session=", "会话=")
    localized = localized.replace("profile=", "账号=")
    localized = localized.replace("ranked=", "已排序=")
    localized = localized.replace("qualified=", "达标=")
    localized = localized.replace("min_likes=", "最低点赞阈值=")
    localized = localized.replace("medium", "中")
    localized = re.sub(r"## 字段s To Capture Next Time", "## 下次补采字段", localized)
    localized = localized.replace("### Top Candidate Board", "### 爆款候选主表")
    localized = localized.replace("### Comment Signal Clusters", "### 评论信号聚类")
    localized = localized.replace("Qualified control：", "对照样本：")
    localized = localized.replace("Target market or locale when the scene depends on one market", "当场景依赖单一市场时，需要标注目标市场或地区")
    localized = localized.replace("The board can now function as a real reusable intake layer because the shortlist is no longer only score-based; it preserves more of the source 标题文案 and packaging logic for 拆解.", "这份候选主表已经能作为可复用的爆款采集入口，因为 shortlist 不再只按分数排序，而是保留了更多源视频标题文案与包装逻辑，便于后续拆解。")
    localized = localized.replace("The board can now function as a real reusable intake layer because the 候选清单 is no longer only score-based; it preserves more of the source 标题文案 and packaging logic for 拆解.", "这份候选主表已经能作为可复用的爆款采集入口，因为候选清单不再只按分数排序，而是保留了更多源视频标题文案与包装逻辑，便于后续拆解。")
    localized = localized.replace("The strongest single-video breakdown target in this real TikTok pack wins by making the first frame instantly legible, then using authority, context, or a featured-person cue as compressed proof.", "这条最值得拆解的单视频之所以能跑出来，核心在于首帧一眼可懂，然后用权威、语境或人物线索完成压缩证明。")
    localized = localized.replace("This matters because the reusable asset is not surface polish. It is the sequence that moves from recognition to proof to a soft continuation close without over-explaining.", "真正可复用的资产不是表面包装，而是从识别到证明、再到柔性续看结尾的顺序，而不是冗长解释。")
    localized = localized.replace("Rebuild the reference in order, then rewrite the proof layer so an owned product, creator, or evidence object can carry the same decision logic.", "先按原顺序重建参考视频，再重写证明层，让自有产品、创作者或证据对象承接同样的决策逻辑。")
    localized = localized.replace("Take the top three into deeper 拆解 immediately and assign each one a clear study lane before anyone starts analyzing ad hoc.", "把前 3 条候选立刻送入深拆，并在分析前先为每条视频分配明确研究方向。")
    localized = localized.replace("Tag each selected video by best reuse purpose: hook, proof, structure, or style.", "为每条入选视频标注最适合复用的方向：钩子、证明、结构或风格。")
    localized = localized.replace("Tag each selected video by best reuse purpose: 钩子, proof, structure, or style.", "为每条入选视频标注最适合复用的方向：钩子、证明、结构或风格。")
    localized = localized.replace("Collecting links without enough hook or proof notes for later 拆解.", "只收集链接却没有补充足够的钩子或证明备注，后续无法高质量拆解。")
    localized = localized.replace("Collecting links without enough 钩子 or proof notes for later 拆解.", "只收集链接却没有补充足够的钩子或证明备注，后续无法高质量拆解。")
    localized = localized.replace("Has recoverable 标题文案/hook text; next move: Preserve the recognition-first packaging and rewrite the proof layer with owned assets.", "已恢复可用的标题文案与钩子文本；下一步应保留其识别度优先的包装方式，再用自有素材重写证明层。")
    localized = localized.replace("Has recoverable 标题文案/钩子 text; next move: Preserve the recognition-first packaging and rewrite the proof layer with owned assets.", "已恢复可用的标题文案与钩子文本；下一步应保留其识别度优先的包装方式，再用自有素材重写证明层。")
    localized = localized.replace("Strong score and reusable packaging potential; next move: Preserve the recognition-first packaging and rewrite the proof layer with owned assets.", "分数表现强，且具备可复用的包装潜力；下一步应保留其识别度优先的包装方式，再用自有素材重写证明层。")
    localized = localized.replace("Route to Hook / packaging 拆解", "进入钩子 / 包装拆解")
    localized = localized.replace("Hook / packaging 拆解", "钩子 / 包装拆解")
    localized = localized.replace("Traceability into later 拆解", "便于后续继续追踪到拆解环节")
    localized = localized.replace("Send shortlist rank 1 to Hook / packaging 拆解 first and capture a full 拆解 note.", "优先把 shortlist 第 1 名送入钩子 / 包装拆解，并补齐完整拆解记录。")
    localized = localized.replace("Use shortlist rank 2 as the backup study lane for Hook / packaging 拆解.", "把 shortlist 第 2 名作为钩子 / 包装拆解的第二研究位。")
    localized = localized.replace("Keep shortlist rank 3 as the contrast reference, then preserve the whole board as the intake baseline for the next collection round.", "保留 shortlist 第 3 名作为对照样本，并把整份主表沉淀为下一轮采集的基线。")
    localized = localized.replace("The strongest repeated user language in this TikTok comment pack is not purchase desire but control, trust, and feature-friction concern, especially around AI remix settings.", "这批 TikTok 评论里最强的重复语言并不是购买欲，而是对控制权、信任感和功能摩擦的担忧，尤其集中在 AI remix 设置上。")
    localized = localized.replace("This matters because live moderation and content framing need to answer user-control anxiety directly instead of only promoting the post theme.", "这意味着直播回复和内容包装都需要正面回应用户的控制权焦虑，而不是只继续强调帖子主题。")
    localized = localized.replace("Use the repeated complaint language to build moderator replies, host clarification prompts, and a cleaner user-control explanation path.", "把这些高频抱怨语句转成运营回复、主播澄清提示词，以及更清晰的用户控制权解释路径。")
    localized = localized.replace("Comment samples were captured from 1 TikTok videos in this pack.", "当前评论样本来自这份包内的 1 条 TikTok 视频。")
    localized = localized.replace("The dominant live-ops lesson is that users surface platform-control complaints in public comment threads even when the post itself is not primarily about that feature.", "当前最重要的运营启发是：即便帖子主题并不直接围绕该功能，用户仍会在公开评论区集中表达对平台控制权的抱怨。")
    localized = localized.replace("Most repeated pain: inability to easily disable or opt out of AI remix behavior.", "最高频痛点：用户无法轻松关闭或退出 AI remix 行为。")
    localized = localized.replace("Most repeated trigger: visible mismatch between what users think they consented to and what the platform enabled by default.", "最高频触发因素：用户自认为的授权范围，与平台默认启用状态之间存在明显错位。")
    localized = localized.replace("Treat as weak signal unless repeated with stronger specificity.", "如果没有更多高具体度重复出现，应只视作弱信号。")
    localized = localized.replace("Explain feature control in plainer language and reduce opt-out friction in user-facing guidance.", "用更直白的话解释功能控制方式，并降低用户侧退出流程的理解门槛。")
    localized = localized.replace("Repeated comments ask how to disable or remove AI remix.", "高频评论都在追问如何关闭或移除 AI remix。")
    localized = localized.replace("Lead with control and transparency before reassurance.", "先讲清控制权与透明度，再做安抚说明。")
    localized = localized.replace("Trust is weakened when users feel settings changed without consent.", "当用户感觉设置在未获同意时被改变，信任会明显下降。")
    localized = localized.replace("Reuse user phrases like 'turn off', 'opt out', and 'remove AI remix'.", "直接复用用户原话，例如“turn off”“opt out”“remove AI remix”等表达。")
    localized = localized.replace("Direct language will match what users are already typing.", "直接语言更贴近用户已经在评论区输入的表达方式。")
    localized = localized.replace("Show exact steps or visible UI proof when answering control questions.", "在回答控制权问题时，尽量展示明确步骤或可见的 UI 证明。")
    localized = localized.replace("Trust objections need concrete resolution, not only tone.", "信任类异议需要具体解决方案，不能只靠安抚语气。")
    localized = localized.replace("Send shortlist rank 1 to 钩子 / 包装拆解 first and capture a full 拆解 note.", "优先把候选清单第 1 名送入钩子 / 包装拆解，并补齐完整拆解记录。")
    localized = localized.replace("Use shortlist rank 2 as the backup study lane for 钩子 / 包装拆解.", "把候选清单第 2 名作为钩子 / 包装拆解的第二研究位。")
    localized = localized.replace("Keep 候选清单 rank 3 as the contrast reference, then preserve the whole board as the intake baseline for the next collection round.", "保留候选清单第 3 名作为对照样本，并把整份主表沉淀为下一轮采集的基线。")
    localized = localized.replace("Send 候选清单 rank 1 to 钩子 / 包装拆解 first and capture a full 拆解 note.", "优先把候选清单第 1 名送入钩子 / 包装拆解，并补齐完整拆解记录。")
    localized = localized.replace("Use 候选清单 rank 2 as the backup study lane for 钩子 / 包装拆解.", "把候选清单第 2 名作为钩子 / 包装拆解的第二研究位。")
    localized = localized.replace("This 采集包 already contains a usable 候选清单 of TikTok posts worth deeper study because the strongest rows now carry recoverable 标题文案, 钩子, and topic signals in addition to ranking metrics.", "这份采集包已经包含一份可直接深拆的 TikTok 候选清单，因为高分样本除了排序指标，还保留了可恢复的标题文案、钩子和主题信号。")
    localized = localized.replace("This real TikTok reference suggests a prompt or production brief built around fast recognition, minimal explanation, and one trust-bearing social cue rather than heavy narrative complexity.", "这条真实 TikTok 参考视频更像是围绕快速识别、极简解释和单一信任线索搭建出的提示词或制作简报，而不是复杂叙事。")
    localized = localized.replace("That makes the inferred brief reusable: the operator can preserve visual pacing and premise order while swapping the proof object or featured cue onto a different product or account.", "这让反推出的制作简报具备可复用性：在保留视觉节奏和前提顺序的同时，可以把证明对象或人物线索切换到别的产品或账号。")
    localized = localized.replace("Treat the inferred brief as a structured creation blueprint, then mark which parts depend on source-account authority versus portable shot and copy logic.", "把反推制作简报当成结构化创作蓝图，再标出哪些部分依赖源账号权威，哪些属于可迁移的镜头和文案逻辑。")
    localized = localized.replace("This TikTok account sample suggests a repeatable editorial formula: attach the post to a recognizable creator, story, or cultural moment, then use minimal copy to let affinity do the work.", "这组 TikTok 账号样本呈现出一套可重复的编辑公式：把帖子挂靠到可识别的创作者、故事或文化时刻，再用极简文案让熟悉感自己完成转化。")
    localized = localized.replace("The pattern is useful for TikTok projects that need stronger social-native packaging without long explanation-heavy intros.", "这套模式适合那些需要更强社交原生包装、又不想靠长解释开场的 TikTok 项目。")
    localized = localized.replace("Translate the account's strongest editorial packaging moves into a reusable creator- or community-led content brief.", "把这个账号最强的编辑包装动作翻译成一份可复用的创作者驱动或社区驱动内容制作简报。")
    localized = localized.replace("Reference video:", "参考视频：")
    localized = localized.replace("Source account baseline:", "源账号基线：")
    localized = localized.replace("Profile session quality:", "账号会话质量：")
    localized = localized.replace("### 结构 Map", "### 结构地图")
    localized = localized.replace("One-line judgment", "一句话判断")
    localized = localized.replace("Structure map", "结构地图")
    localized = localized.replace("Viral mechanism", "爆点机制")
    localized = localized.replace("Reusable formula", "可复用公式")
    localized = localized.replace("Adaptation advice", "改写建议")
    localized = localized.replace("Inferred original brief", "反推原始制作简报")
    localized = localized.replace("Generator-ready schema", "可直接喂给生成器的结构")
    localized = localized.replace("Shot-by-shot table", "分镜逐条表")
    localized = localized.replace("Product-adapted brief", "产品改写版制作简报")
    localized = localized.replace("field-level confidence flags", "字段级置信度标记")
    localized = localized.replace("Recommended 动作", "建议动作")
    localized = localized.replace("Creator playbook", "创作者打法手册")
    localized = localized.replace("Repeatable formulas", "可重复公式")
    localized = localized.replace("Non-transferable advantages", "不可迁移优势")
    localized = localized.replace("Adaptation path", "改写路径")
    localized = localized.replace("改写路径 for user product已具备可行性", "针对用户产品的改写路径已具备可行性")
    localized = localized.replace("## 原因 They Matter", "## 重要原因")
    localized = localized.replace("| Decision Area | 建议 | 原因 |", "| 决策领域 | 建议 | 原因 |")
    localized = localized.replace("| video | 爆发帖-1 | 粘贴视频链接 | 00:00-00:05 | 用于解释账号为何变化的代表性爆发帖。 | 爆发归因 |", "| 视频 | 爆发帖-1 | 粘贴视频链接 | 00:00-00:05 | 用于解释账号为何变化的代表性爆发帖。 | 爆发归因 |")
    localized = localized.replace("Scene 08", "场景 08")
    localized = localized.replace("min_点赞", "最低点赞阈值")
    localized = localized.replace("## Next 动作", "## 下一步动作")
    localized = localized.replace("## 风险s And 改写备注s", "## 风险与改写备注")
    localized = localized.replace("字段-level confidence flags", "字段级置信度标记")
    localized = localized.replace("with one dominant recognition cue", "并以一个主识别线索为核心")
    localized = localized.replace("Human-first, emotion-first, or culture-first 标题文案 packaging", "以人物优先、情绪优先或文化时刻优先的标题文案包装")
    localized = localized.replace("Likely dependent on featured creator/performance clip rather than explanation-led structure", "更依赖出镜创作者或表演片段，而不是解释驱动结构")
    localized = localized.replace("信任 rides on official account authority, featured people, and recognizable context", "信任更多建立在官方账号权威、出镜人物和可识别语境上")
    localized = localized.replace("Soft teaser or continuation toward more content", "用柔性预告或续看方式引向更多内容")
    localized = localized.replace("The account does not need to over-explain. It packages a familiar person or cultural cue and relies on fast recognition plus account trust.", "这个账号不需要过度解释，它把熟悉人物或文化线索打包进去，并依赖快速识别和账号信任完成推进。")
    localized = localized.replace("The transferable lesson is not 'be TikTok'. It is to reduce friction between first-frame recognition and the emotional reason to keep watching.", "可迁移的经验不是“像 TikTok 一样”，而是降低首帧识别与继续看下去的情绪理由之间的摩擦。")
    localized = localized.replace("Open with immediate recognition or emotional clarity", "用即时识别或情绪清晰度开场")
    localized = localized.replace("识别 compresses decision time on TikTok", "识别优先能压缩用户决策时间")
    localized = localized.replace("Swap in a figure, object, or cue your audience already cares about", "替换成你的受众已经在意的人物、对象或线索")
    localized = localized.replace("Stay short and premise-led", "保持短小，并由前提驱动")
    localized = localized.replace("The format works because it does not over-teach", "这种格式有效，是因为它不过度讲解")
    localized = localized.replace("Strip excess setup before the main cue lands", "在主线索落地前，剥掉多余铺垫")
    localized = localized.replace("信任-building", "信任构建")
    localized = localized.replace("Borrow trust from the account, featured talent, or event context", "从账号、出镜人物或事件语境借用信任")
    localized = localized.replace("信任 can be transferred via stronger proof objects", "信任可以通过更强证明对象被转移")
    localized = localized.replace("Use receipts, social proof, or known collaborators if account authority is weaker", "如果账号权威较弱，就用凭证、社会证明或已知合作方来补强")
    localized = localized.replace("Use continuation energy instead of hard closing", "用续看感代替硬收尾")
    localized = localized.replace("Soft progression fits social-native viewing better", "柔性推进更适合社交原生观看节奏")
    localized = localized.replace("Route toward next watch, next profile action, or soft save/share", "引导到下一次观看、主页动作或柔性收藏 / 分享")
    localized = localized.replace("Profile 会话质量：", "账号会话质量：")
    localized = localized.replace("If multiple markets are mixed together, split the board before drawing conclusions.", "如果混入了多个市场，请先拆分主表，再分别下结论。")
    localized = localized.replace("- Recent post list", "- 最近帖子清单")
    localized = localized.replace("- Some performance signal per post", "- 每条帖子的基础表现信号")
    localized = localized.replace("- If metrics are incomplete, keep weak conclusions explicitly labeled.", "- 如果指标不完整，弱结论必须显式标注。")
    localized = localized.replace("- High vs low performance grouping", "- 高表现与低表现分组")
    localized = localized.replace("- Performance pattern summary", "- 表现模式总结")
    localized = localized.replace("- Winning traits", "- 高表现特征")
    localized = localized.replace("- Losing traits", "- 低表现特征")
    localized = localized.replace("- Next-cycle plan", "- 下一轮测试计划")
    localized = localized.replace("- Posts can be clustered by pattern", "- 可以按内容模式对帖子聚类")
    localized = localized.replace("- Winners and losers are distinguishable", "- 高低表现样本可以明确区分")
    localized = localized.replace("- Next-cycle test rules can be written", "- 可以写出下一轮测试规则")
    localized = localized.replace("- High- and low-performance groups can be compared directly", "- 高表现与低表现组可以直接对照")
    localized = localized.replace("Within this TikTok account sample, the likely winning pattern is short, editorially framed posts that attach to a recognizable person, story, or moment instead of leading with heavy explanation.", "在这组 TikTok 账号样本里，更可能跑赢的是那种短、编辑包装感强，并且挂靠到可识别人、故事或时刻的内容，而不是一上来就重解释。")
    localized = localized.replace("This is useful as a retro template because it converts raw ranked-post data into do-more, do-less, and next-test rules for the next cycle.", "这份复盘模板的价值在于：它能把原始排序帖子数据转成“多做什么、少做什么、下一轮测什么”的明确规则。")
    localized = localized.replace("Cluster the next account batch around people-led, moment-led, and explanation-led posts to confirm which packaging family deserves more volume.", "下一轮账号内容请围绕人物驱动、时刻驱动、解释驱动三类内容分组，验证哪一类包装方式最值得继续放量。")
    localized = localized.replace("- Cluster posts by pattern, not just by publish date.", "- 帖子要按内容模式聚类，而不只是按发布时间排序。")
    localized = localized.replace("- Compare high-performing and low-performing groups explicitly.", "- 明确对比高表现组与低表现组。")
    localized = localized.replace("- Write explicit do-more, do-less, and stop rules.", "- 写出明确的多做、少做、停止规则。")
    localized = localized.replace("- Turn the retro into one next-cycle testing plan.", "- 把复盘结果转成一份下一轮测试计划。")
    localized = localized.replace("- Reading metrics row by row with no pattern grouping.", "- 逐行看指标，却没有做模式聚类。")
    localized = localized.replace("- Stopping at retrospective summary without turning it into a next-cycle test plan.", "- 停留在复盘摘要，没有转成下一轮测试计划。")
    localized = localized.replace("- Blaming outcomes on vague quality judgments.", "- 用模糊的“质量高低”来归因结果。")
    localized = localized.replace("- Ending the retro without a concrete next test cycle.", "- 复盘结束时没有给出明确的下一轮测试周期。")
    localized = localized.replace("Current ranked post count in pack:", "当前采集包内排序帖子数：")
    localized = localized.replace("- High-performer control:", "- 高表现对照样本：")
    localized = localized.replace("- Low-performer contrast:", "- 低表现对照样本：")
    localized = localized.replace("- Use this retro as a next-cycle dispatch, not as a passive recap.", "- 把这份复盘当成下一轮派单依据，而不是被动总结。")
    localized = localized.replace("| Performance Group | Pattern | 原因 It Likely Happened | Growth / ROI Relevance |", "| 表现分组 | 模式 | 可能原因 | 对增长 / ROI 的意义 |")
    localized = localized.replace("| High-performing |", "| 高表现 |")
    localized = localized.replace("| Low-performing |", "| 低表现 |")
    localized = localized.replace("| Unclear |", "| 待确认 |")
    localized = localized.replace("Higher-ranked posts lean on immediate recognition and lighter copy.", "高排名帖子更依赖即时识别和更轻量的文案。")
    localized = localized.replace("Most relevant when growth depends on trust transfer, receipts, or credible proof.", "当增长依赖信任迁移、凭证展示或可信证明时，这类模式最值得优先放大。")
    localized = localized.replace("Lower-ranked posts appear to rely more on weaker proof or less legible opening cues.", "低排名帖子往往更依赖较弱证明，或者开场识别度不够。")
    localized = localized.replace("Most relevant when the account needs fresher angles without rebuilding the full content engine.", "如果账号需要在不重建整套内容引擎的前提下测试新角度，这类问题最值得优先修正。")
    localized = localized.replace("Whether comment-heavy posts outperform because of controversy or because of account trust", "高评论帖子表现更强，到底是因为争议性，还是因为账号信任势能")
    localized = localized.replace("Needs more weeks and more comment-linked evidence", "需要更多周样本和更多与评论联动的证据")
    localized = localized.replace("Do not over-attribute ROI effects without owned conversion or retention context.", "如果没有自有转化或留存上下文，不要过度归因 ROI 效果。")
    localized = localized.replace("### Performance Clusters", "### 表现聚类")
    localized = localized.replace("| Cluster | Content Mode | Representative Posts | Shared Traits | Signal Strength |", "| 聚类 | 内容模式 | 代表帖子 | 共性特征 | 信号强度 |")
    localized = localized.replace("| video | self-top-cluster | 粘贴视频链接 | cluster-window | Representative winning post set for the strongest-performing pattern. | Winning-pattern cluster |", "| 视频 | self-top-cluster | 粘贴视频链接 | cluster-window | 用于代表当前最强表现模式的一组胜出帖子。 | 胜出模式聚类 |")
    localized = localized.replace("| video | self-low-cluster | 粘贴视频链接 | cluster-window | Representative weak post set showing the low-performing pattern. | Losing-pattern cluster |", "| 视频 | self-low-cluster | 粘贴视频链接 | cluster-window | 用于代表当前低表现模式的一组弱势帖子。 | 低表现模式聚类 |")
    localized = localized.replace("| Rule Type | 建议 | Reason | Next-Cycle Owner / Check |", "| 规则类型 | 建议 | 原因 | 下一轮负责人 / 检查项 |")
    localized = localized.replace("| Do more |", "| 多做 |")
    localized = localized.replace("| Do less |", "| 少做 |")
    localized = localized.replace("| Stop |", "| 停止 |")
    localized = localized.replace("| 测试 next |", "| 下一轮测试 |")
    localized = localized.replace("Lead with quicker recognition and lighter 标题文案 packaging.", "优先使用更快识别、文案更轻的内容包装。")
    localized = localized.replace("This is the clearest shared trait across the stronger posts.", "这是高表现帖子里最清晰、最稳定的共同特征。")
    localized = localized.replace("Operator / next content sprint", "运营负责人 / 下一轮内容冲刺")
    localized = localized.replace("Reduce explanation-heavy intros that delay the emotional or social cue.", "减少解释过重、拖慢情绪或社交线索露出的开场。")
    localized = localized.replace("Do not let the next test cycle open with setup before the cue lands.", "下一轮测试不要再让铺垫先于核心线索落地。")
    localized = localized.replace("Script reviewer / editor", "脚本审核 / 剪辑负责人")
    localized = localized.replace("Stop assuming platform-account authority will transfer unchanged to smaller accounts.", "不要再默认平台级账号权威可以原样迁移到小账号。")
    localized = localized.replace("Remove copied authority shells when writing the next smaller-account versions.", "在写下一轮小账号版本时，要去掉生搬硬套的权威外壳。")
    localized = localized.replace("Strategy owner", "策略负责人")
    localized = localized.replace("Run a controlled comparison between person-led and proof-object-led versions.", "对人物驱动版和证明物驱动版做一组受控对比测试。")
    localized = localized.replace("This should decide which lane gets more volume next cycle.", "用这组测试决定下一轮应该给哪条内容线更多量。")
    localized = localized.replace("Growth + content lead", "增长负责人 + 内容负责人")
    localized = localized.replace("A true retro on the user's own account would need multiple internal batches, not only competitor data.", "如果要做真正的自家账号复盘，还需要多批内部账号数据，而不能只依赖竞品样本。")
    localized = localized.replace("This 已导入 retro is best treated as a pattern template, not as a final verdict on a different account's strategy.", "这份已导入复盘更适合作为模式模板，而不是对另一账号策略下最终结论。")
    localized = localized.replace("### Next-Cycle 测试 Plan", "### 下一轮测试计划")
    localized = localized.replace("| Next 测试 | Hypothesis | What Changes | Success Signal |", "| 下一轮测试 | 假设 | 调整内容 | 成功信号 |")
    localized = localized.replace("The account will grow faster if the opening cue lands before any heavy setup.", "如果核心线索先于重铺垫出现，账号增长速度会更快。")
    localized = localized.replace("Rewrite two posts so the premise is visible in the first beat.", "重写两条帖子，让核心前提在第一拍就可见。")
    localized = localized.replace("Higher hold, stronger 点赞，or stronger saves on the recognition-first variant.", "如果识别优先版本的停留、更强点赞或收藏更高，就说明假设成立。")
    localized = localized.replace("Owned proof can replace borrowed authority without losing performance.", "自有证明对象可以替代借来的权威外壳，而不显著损失表现。")
    localized = localized.replace("Swap official-account or trust-shell cues for one stronger owned proof object.", "把官方账号或信任外壳线索替换成一个更强的自有证明对象。")
    localized = localized.replace("The proof-object version narrows the gap in interaction quality.", "如果证明对象版本缩小互动质量差距，就说明替换方向正确。")
    localized = localized.replace("One content mode deserves more weekly volume than the others.", "有一种内容模式应该获得比其他模式更多的周度产量。")
    localized = localized.replace("Split the next cycle by content mode and hold the publishing window roughly stable.", "下一轮按内容模式拆分测试，并尽量保持发布时间窗口稳定。")
    localized = localized.replace("One mode consistently wins on ranked interaction or owned conversion proxy.", "如果某一模式在排序互动或自有转化代理指标上持续胜出，就应继续放量。")
    localized = localized.replace("| Style |", "| 风格 |")
    localized = localized.replace("| Environment |", "| 场景环境 |")
    localized = localized.replace("| Tone & Pacing |", "| 语气与节奏 |")
    localized = localized.replace("| Camera |", "| 镜头 |")
    localized = localized.replace("| Lighting |", "| 光线 |")
    localized = localized.replace("| Character |", "| 人物 |")
    localized = localized.replace("| Background Sound |", "| 背景声音 |")
    localized = localized.replace("| Transition / Editing |", "| 转场 / 剪辑 |")
    localized = localized.replace("| Hook design |", "| 钩子设计 |")
    localized = localized.replace("| Proof design |", "| 证明设计 |")
    localized = localized.replace("| Pacing design |", "| 节奏设计 |")
    localized = localized.replace("| Conversion design |", "| 转化设计 |")
    localized = localized.replace("Social-native, single-premise scene order", "社交原生、单前提驱动的场景顺序")
    localized = localized.replace("Fast recognition, minimal explanation, early proof", "快速识别、少解释、早证明")
    localized = localized.replace("| Hook |", "| 钩子 |")
    localized = localized.replace("| Proof |", "| 证明 |")
    localized = localized.replace("| Hook logic |", "| 钩子逻辑 |")
    localized = localized.replace("| Visual style |", "| 视觉风格 |")
    localized = localized.replace("| Proof logic |", "| 证明逻辑 |")
    localized = localized.replace("| CTA style |", "| CTA 风格 |")
    localized = localized.replace("| Hook formula |", "| 钩子公式 |")
    localized = localized.replace("| Visual rhythm |", "| 视觉节奏 |")
    localized = localized.replace("| Proof style |", "| 证明风格 |")
    localized = localized.replace("| Conversion move |", "| 转化动作 |")
    localized = localized.replace("| Pacing |", "| 节奏 |")
    localized = localized.replace("| Suppress |", "| 抑制规则 |")
    localized = localized.replace("| Scene / talent |", "| 场景 / 人物 |")
    localized = localized.replace("信任 is weakened when users feel settings changed without consent.", "当用户感觉设置在未获同意时被改变，信任会明显下降。")
    localized = localized.replace("信任 objections need concrete resolution, not only tone.", "信任类异议需要具体解决方案，不能只靠安抚语气。")
    return localized


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Push a structured TikTok Growth Operator scene report JSON into a Feishu Doc."
    )
    parser.add_argument("--input", required=True, help="Structured scene report JSON path.")
    parser.add_argument(
        "--backend",
        choices=["auto", "api", "lark-cli"],
        default="auto",
        help="Preferred Feishu doc backend. auto currently prefers the direct OpenAPI path.",
    )
    parser.add_argument("--app-id", default=os.environ.get("FEISHU_APP_ID", ""), help="Feishu app ID for API mode.")
    parser.add_argument(
        "--app-secret",
        default=os.environ.get("FEISHU_APP_SECRET", ""),
        help="Feishu app secret for API mode.",
    )
    parser.add_argument(
        "--mode",
        choices=["create", "append", "overwrite"],
        default="create",
        help="Create a new Feishu doc, or append/overwrite an existing one.",
    )
    parser.add_argument("--doc", default="", help="Existing Feishu doc URL or token for append/overwrite.")
    parser.add_argument("--title", default="", help="Optional explicit Feishu doc title.")
    parser.add_argument("--parent-token", default="", help="Optional target parent folder or wiki node token for create mode.")
    parser.add_argument(
        "--parent-position",
        default="",
        help="Optional parent position for create mode, for example my_library.",
    )
    parser.add_argument(
        "--identity",
        choices=["bot", "user"],
        default="bot",
        help="Used only by lark-cli backend. bot is the safer default.",
    )
    parser.add_argument(
        "--lark-cli",
        default=os.environ.get("LARK_CLI_BIN", ""),
        help="Path to lark-cli.exe. Can also come from LARK_CLI_BIN.",
    )
    parser.add_argument(
        "--keep-markdown",
        action="store_true",
        help="Keep the intermediate rendered Markdown file for inspection.",
    )
    parser.add_argument(
        "--markdown-output",
        default="",
        help="Optional explicit path for the rendered Markdown handoff file.",
    )
    return parser.parse_args()


def require(value: str, label: str) -> str:
    text = normalize_text(value)
    if not text:
        raise SystemExit(f"Missing required {label}.")
    return text


def load_report(path: Path) -> dict:
    payload = read_json_file(path)
    if not isinstance(payload, dict):
        raise SystemExit(f"Expected a structured scene report JSON object: {path}")
    return payload


def infer_title(report: dict, explicit_title: str) -> str:
    if normalize_text(explicit_title):
        return normalize_text(explicit_title)
    metadata = report.get("metadata") or {}
    return build_report_title(
        metadata.get("project") or metadata.get("title"),
        metadata.get("scene"),
        metadata.get("scene_title"),
    )


def render_doc_markdown(report: dict, title: str) -> str:
    localized_report = localize_report_payload(report, title)
    raw = render_markdown_from_payload(localized_report)
    raw = localize_markdown(raw)
    lines = raw.splitlines()
    body_lines = lines[:]
    if body_lines and body_lines[0].startswith("# "):
        body_lines = body_lines[1:]
        while body_lines and not body_lines[0].strip():
            body_lines.pop(0)
    body = "\n".join(body_lines).strip()
    if not body:
        body = "_No content rendered from report payload._"
    return f"# {title}\n\n{body}\n"


def write_markdown_handoff(markdown: str, explicit_output: str) -> Path:
    if normalize_text(explicit_output):
        path = Path(explicit_output)
        path.parent.mkdir(parents=True, exist_ok=True)
        write_utf8_text(path, markdown)
        return path
    temp_dir = Path(tempfile.mkdtemp(prefix="tgo-feishu-doc-"))
    path = temp_dir / "report.md"
    write_utf8_text(path, markdown)
    return path


def auth_headers(token: str) -> dict[str, str]:
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json; charset=utf-8",
    }


def parse_error_response(response: Response) -> dict:
    try:
        body = response.json()
    except ValueError:
        body = {
            "code": response.status_code,
            "msg": normalize_text(response.text, strip=False) or f"HTTP {response.status_code}",
        }
    if not isinstance(body, dict):
        body = {
            "code": response.status_code,
            "msg": normalize_text(str(body), strip=False) or f"HTTP {response.status_code}",
        }
    return body


def raise_feishu_api_error(url: str, body: dict) -> None:
    violations = []
    for item in ((body.get("error") or {}).get("permission_violations") or []):
        subject = normalize_text((item or {}).get("subject"))
        if subject:
            violations.append(subject)

    hints = []
    if violations:
        hints.append(f"required_scopes={', '.join(violations)}")

    message = normalize_text(body.get("msg"), strip=False)
    auth_link = ""
    if "https://open.feishu.cn/app/" in message:
        start = message.find("https://open.feishu.cn/app/")
        auth_link = message[start:].split()[0]
    if auth_link:
        hints.append(f"auth_link={auth_link}")

    log_id = normalize_text(((body.get("error") or {}).get("log_id")))
    if log_id:
        hints.append(f"log_id={log_id}")

    suffix = f" ({'; '.join(hints)})" if hints else ""
    raise SystemExit(f"Feishu API error at {url}: code={body.get('code')} msg={body.get('msg')}{suffix}")


def post_json(url: str, payload: dict, *, headers: dict[str, str] | None = None) -> dict:
    response = requests.post(
        url,
        headers=headers or {"Content-Type": "application/json; charset=utf-8"},
        json=payload,
        timeout=DEFAULT_TIMEOUT,
    )
    body = parse_error_response(response)
    if response.status_code >= 400 or body.get("code") not in (0, None):
        raise_feishu_api_error(url, body)
    return body


def put_json(url: str, payload: dict, *, headers: dict[str, str]) -> dict:
    response = requests.put(url, headers=headers, json=payload, timeout=DEFAULT_TIMEOUT)
    body = parse_error_response(response)
    if response.status_code >= 400 or body.get("code") not in (0, None):
        raise_feishu_api_error(url, body)
    return body


def get_tenant_access_token(app_id: str, app_secret: str) -> str:
    body = post_json(AUTH_URL, {"app_id": app_id, "app_secret": app_secret})
    token = normalize_text(body.get("tenant_access_token"))
    if not token:
        raise SystemExit("Feishu auth succeeded but no tenant_access_token was returned.")
    return token


def parse_document_ref(value: str) -> str:
    raw = require(value, "doc")
    for marker in ("/wiki/", "/docx/", "/doc/"):
        index = raw.find(marker)
        if index >= 0:
            token = raw[index + len(marker) :]
            for splitter in ("/", "?", "#"):
                split_index = token.find(splitter)
                if split_index >= 0:
                    token = token[:split_index]
            token = normalize_text(token)
            if token:
                return token
    if "://" in raw:
        raise SystemExit(f"Unsupported --doc input: {raw}")
    if any(char in raw for char in "/?#"):
        raise SystemExit(f"Unsupported --doc input: {raw}")
    return raw


def run_api_backend(args: argparse.Namespace, title: str, markdown: str) -> dict:
    app_id = require(args.app_id, "app_id")
    app_secret = require(args.app_secret, "app_secret")
    token = get_tenant_access_token(app_id, app_secret)
    headers = auth_headers(token)

    if args.mode == "create":
        payload = {
            "format": "markdown",
            "content": markdown,
        }
        if normalize_text(args.parent_token):
            payload["parent_token"] = normalize_text(args.parent_token)
        if normalize_text(args.parent_position):
            payload["parent_position"] = normalize_text(args.parent_position)
        body = post_json(DOC_CREATE_URL, payload, headers=headers)
        data = body.get("data") or {}
        document = data.get("document") or {}
        doc_id = normalize_text(document.get("document_id"))
        return {
            "status": "ok",
            "backend": "api",
            "mode": args.mode,
            "title": title,
            "document_id": doc_id,
            "document_url": normalize_text(document.get("url")) or (f"https://www.feishu.cn/docx/{doc_id}" if doc_id else ""),
            "response": data,
        }

    document_id = parse_document_ref(args.doc)
    payload = {
        "format": "markdown",
        "command": "overwrite" if args.mode == "overwrite" else "block_insert_after",
        "content": markdown,
    }
    if args.mode == "append":
        payload["block_id"] = "-1"
    body = put_json(DOC_UPDATE_URL.format(document_id=document_id), payload, headers=headers)
    data = body.get("data") or {}
    return {
        "status": "ok",
        "backend": "api",
        "mode": args.mode,
        "title": title,
        "document_id": document_id,
        "document_url": f"https://www.feishu.cn/docx/{document_id}",
        "response": data,
    }


def resolve_lark_cli(candidate: str) -> Path:
    if normalize_text(candidate):
        path = Path(candidate)
        if path.exists():
            return path
        raise SystemExit(f"lark-cli not found at: {path}")
    for path in DEFAULT_LARK_CLI_CANDIDATES:
        if path.exists():
            return path
    for root in (Path(r"E:\飞书\lark-cli-bin"), Path(r"E:\椋炰功\lark-cli-bin")):
        if root.exists():
            matches = sorted(root.glob("**/lark-cli.exe"))
            if matches:
                return matches[-1]
    raise SystemExit("Could not find lark-cli.exe. Pass --lark-cli or set LARK_CLI_BIN.")


def run_lark_cli(cli_path: Path, args: list[str], cwd: Path | None = None) -> tuple[int, str, str]:
    completed = subprocess.run(
        [str(cli_path), *args],
        cwd=str(cwd) if cwd else None,
        text=True,
        capture_output=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    return completed.returncode, completed.stdout, completed.stderr


def parse_json_output(stdout: str) -> dict:
    text = normalize_text(stdout, strip=False)
    if not text.strip():
        return {}
    try:
        payload = json.loads(text)
    except json.JSONDecodeError:
        return {"raw_stdout": text}
    return payload if isinstance(payload, dict) else {"raw_stdout": text}


def build_lark_cli_args(args: argparse.Namespace, markdown_path: Path) -> list[str]:
    identity = normalize_text(args.identity) or "bot"
    markdown_arg = f"@{markdown_path.name}"
    if args.mode == "create":
        command = [
            "docs",
            "+create",
            "--api-version",
            "v2",
            "--as",
            identity,
            "--content",
            markdown_arg,
            "--doc-format",
            "markdown",
        ]
        if normalize_text(args.parent_token):
            command.extend(["--parent-token", normalize_text(args.parent_token)])
        if normalize_text(args.parent_position):
            command.extend(["--parent-position", normalize_text(args.parent_position)])
        return command

    return [
        "docs",
        "+update",
        "--api-version",
        "v2",
        "--as",
        identity,
        "--doc",
        require(args.doc, "doc"),
        "--mode",
        args.mode,
        "--content",
        markdown_arg,
        "--doc-format",
        "markdown",
    ]


def build_lark_next_steps(stderr: str, json_body: dict) -> list[str]:
    hint = normalize_text(((json_body.get("error") or {}).get("hint", "")) or stderr)
    next_steps: list[str] = []
    if "FEISHU_APP_ID not found" in hint or "FEISHU_APP_SECRET not found" in hint:
        next_steps.append("先把 FEISHU_APP_ID 和 FEISHU_APP_SECRET 写入 D:\\hermes\\.env。")
        next_steps.append("可直接运行：python scripts/setup_hermes_feishu_env.py")
    if "config bind" in hint:
        next_steps.append('& "E:\\飞书\\lark-cli-bin\\v1.0.25\\lark-cli.exe" config bind --identity bot-only')
    if "auth login" in hint:
        next_steps.append('& "E:\\飞书\\lark-cli-bin\\v1.0.25\\lark-cli.exe" auth login --recommend')
    if "app secret invalid" in hint:
        next_steps.append("本地 lark-cli 的 Hermes 凭证链路已过期或不匹配，直接改用 --backend api 会更稳。")
    if not next_steps:
        next_steps.append('& "E:\\飞书\\lark-cli-bin\\v1.0.25\\lark-cli.exe" doctor --offline')
    return next_steps


def run_lark_cli_backend(args: argparse.Namespace, title: str, markdown_path: Path) -> dict:
    cli_path = resolve_lark_cli(args.lark_cli)
    command = build_lark_cli_args(args, markdown_path)
    exit_code, stdout, stderr = run_lark_cli(cli_path, command, cwd=markdown_path.parent)
    json_body = parse_json_output(stdout)

    payload = {
        "status": "ok" if exit_code == 0 else "error",
        "backend": "lark-cli",
        "mode": args.mode,
        "lark_cli": str(cli_path),
        "identity": args.identity,
        "title": title,
        "markdown_handoff": str(markdown_path),
        "command": " ".join(command),
        "stdout": json_body,
        "stderr": normalize_text(stderr, strip=False),
    }
    if exit_code != 0:
        payload["next_steps"] = build_lark_next_steps(stderr, json_body)
        raise SystemExit(json.dumps(payload, ensure_ascii=False, indent=2))
    return payload


def cleanup_markdown_temp(args: argparse.Namespace, markdown_path: Path) -> str:
    if args.keep_markdown or normalize_text(args.markdown_output):
        return str(markdown_path)
    try:
        markdown_path.unlink(missing_ok=True)
        markdown_path.parent.rmdir()
    except OSError:
        pass
    return "<temp cleaned>"


def main() -> None:
    args = parse_args()
    report = load_report(Path(args.input))
    title = infer_title(report, args.title)
    markdown = render_doc_markdown(report, title)
    markdown_path = write_markdown_handoff(markdown, args.markdown_output)

    backend = args.backend
    if backend == "auto":
        backend = "api"

    try:
        if backend == "api":
            payload = run_api_backend(args, title, markdown)
            payload["markdown_handoff"] = cleanup_markdown_temp(args, markdown_path)
            payload["next_steps"] = [
                "当前飞书文档链路已走直连 OpenAPI，不再依赖不稳定的本地 lark-cli Hermes 凭证路径。",
                "如果还想把结构化表格同步到飞书多维表格，再运行 push_report_to_feishu.py。",
            ]
            print(json.dumps(payload, ensure_ascii=False, indent=2))
            return

        payload = run_lark_cli_backend(args, title, markdown_path)
        payload["markdown_handoff"] = cleanup_markdown_temp(args, markdown_path)
        payload["next_steps"] = [
            "如果还想把结构化场景表同步到飞书多维表格，再运行 push_report_to_feishu.py。",
        ]
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    except SystemExit as exc:
        if not args.keep_markdown and not normalize_text(args.markdown_output):
            cleanup_markdown_temp(args, markdown_path)
        raise exc


if __name__ == "__main__":
    main()
