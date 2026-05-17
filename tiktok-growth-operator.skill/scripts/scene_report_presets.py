from __future__ import annotations

from copy import deepcopy


def blank_table(headers: list[str], rows: list[list[str]] | None = None, title: str = "") -> dict:
    return {
        "title": title,
        "headers": headers,
        "rows": rows or [],
    }


def blank_evidence_refs(rows: list[dict] | None = None) -> list[dict]:
    return rows or []


def evidence_ref(
    source_type: str,
    source_id: str,
    source_url: str,
    time_range: str,
    excerpt: str,
    supports: str,
) -> dict:
    return {
        "source_type": source_type,
        "source_id": source_id,
        "source_url": source_url,
        "time_range": time_range,
        "excerpt": excerpt,
        "supports": supports,
    }


def section(
    heading: str,
    instruction: str,
    paragraphs: list[str] | None = None,
    bullets: list[str] | None = None,
    numbered: list[str] | None = None,
    table: dict | None = None,
    evidence_refs: list[dict] | None = None,
) -> dict:
    return {
        "heading": heading,
        "instruction": instruction,
        "paragraphs": paragraphs or [],
        "bullets": bullets or [],
        "numbered": numbered or [],
        "table": table or blank_table([]),
        "evidence_refs": blank_evidence_refs(evidence_refs),
    }


SCENE_EXECUTION_PROFILES = {
    "01": {
        "runner_slug": "viral-video-collection",
        "project_example": "美国口红组合爆款采集",
        "evidence_example": "15 条 TikTok 搜索结果，含链接、基础指标与首拍钩子笔记",
        "success_goal": "排序短名单与深拆优先级",
        "recommended_request": "按场景 01 执行：围绕一个关键词或品类和单一市场，采集并排序最值得研究的爆款视频。把发布时间窗口、地区、排序方式和是否只看带购物车视频作为明确输入，不要只按播放量排序，而是按复用价值排序，最后给出可直接进入场景 03 的 shortlist。",
        "extra_prompt_lines": [
            "先完成候选池排序，再进入任何深层分析。",
            "给每条 shortlist 视频标注最适合复用的用途：hook、证明、结构或风格。",
            "把购买意图与 TikTok Shop 信号单独列出，不要埋在备注里。",
        ],
        "output_checklist": [
            "短名单已经排序，并限制在最强样本内。",
            "每条入选视频都有明确的入选原因。",
            "每条 shortlisted 视频都明确写出商业置信度与复用用途。",
            "操作者知道哪些视频应该立即进入下一步深拆流程。",
        ],
    },
    "02": {
        "runner_slug": "daily-category-patrol",
        "project_example": "美妆品类日常巡检",
        "evidence_example": "当前关键词集合、巡检入口、历史巡检备注与同表追加规则",
        "success_goal": "可重复运行的巡检 SOP、主表结构、日报模板与 Scene 03 升级规则",
        "recommended_request": "按场景 02 执行：设计一个 TikTok 品类日常巡检体系。固定巡检频率、固定巡检时间、同表追加策略、采集日期字段、多关键词 watchlist 组织方式、预警逻辑和日报模板，让它像产品一样可持续运行，而不是一份一次性研究建议。",
        "extra_prompt_lines": [
            "把例行追踪字段与预警触发字段分开。",
            "没有自动化时，也要保留一个单人可执行的手工 SOP。",
            "日报默认突出新增、上升与异常，不要重复抄老内容。",
            "明确哪些结果自动进入场景 03，哪些只沉淀进 patrol 历史库。",
        ],
        "output_checklist": [
            "巡检频率与固定巡检时间已明确。",
            "主表字段与预警字段可长期维护。",
            "日报已明确区分新增、上升、异常与弱信号。",
            "已给出可复用日报模板与 Scene 03 升级规则。",
        ],
    },
    "03": {
        "runner_slug": "batch-search-teardown",
        "project_example": "晨间美妆钩子批量深拆",
        "evidence_example": "10 条候选 TikTok 链接，附截图与转写笔记",
        "success_goal": "短名单、逐条深拆与创作规则",
        "recommended_request": "Run scene 03 to shortlist the strongest viral candidates for one topic, then deeply tear down only the top set using an explicit top-sample rule. End with three stable deliverables: per-video teardown, common-pattern summary, and creation guidance that can be used immediately for new scripts.",
        "extra_prompt_lines": [
            "Use the same teardown lens across all shortlisted videos so the pattern summary is comparable.",
            "Do not deep-analyze weak candidates that should have been filtered out earlier.",
            "Preserve full script, hook, proof rhythm, and time-axis conversion notes whenever evidence allows.",
        ],
        "output_checklist": [
            "The top set is explicitly shortlisted before deep teardown.",
            "Each chosen video is analyzed with the same fields.",
            "The output includes both per-video detail and common-pattern synthesis.",
            "The report ends with reusable creation rules, not only observations.",
        ],
    },
    "04": {
        "runner_slug": "single-video-breakdown",
        "project_example": "口红爆款单视频拆解",
        "evidence_example": "视频链接、下载 JSON / capture detail、转写笔记、逐拍截图与 BGM 线索",
        "success_goal": "单视频机制拆解、标准时间轴表与改编路径",
        "recommended_request": "按场景 04 执行：完整拆解 1 条 TikTok 或抖音视频。先判断视频类型与有无口播，再按时间轴逐拍重建画面、字幕 / 口播、BGM、hook、证明段与收口段，最后分离核心机制与表层风格，并给出保守 / 激进两条改编路径。",
        "extra_prompt_lines": [
            "先按顺序重建视频，再下结论。",
            "明确区分创作者个人化包装与可迁移的转化逻辑。",
            "同时支持有口播与无口播视频，必要时用字幕、动作与运动证明链补齐分析。",
            "优先使用标准表格：Time Range | Scene Type | Visual Content | Spoken / On-Screen Script | Role In Conversion | Evidence Ref。",
        ],
        "output_checklist": [
            "时间轴已按顺序重建，且每一拍都有证据支撑。",
            "hook、证明段与收口段已按顺序复原。",
            "BGM、视频类型与转化节奏已明确写出。",
            "核心机制与表层风格已分离。",
            "至少有 1 条改编路径具体到可以直接继续产出。",
        ],
    },
    "05": {
        "runner_slug": "reverse-engineer-prompt",
        "project_example": "创作者制作简报反推",
        "evidence_example": "参考视频画面、转写片段与节奏笔记",
        "success_goal": "反推原始 brief、产品适配 brief 与 generator-ready handoff",
        "recommended_request": "按场景 05 执行：反推 1 条视频背后的提示词或制作简报。先推断原始创意意图，再拆成可直接交给生成器的模块，如风格、环境、镜头、灯光、角色与分镜级结构；然后分开输出反推原版、产品适配版和 generator-ready handoff，并给字段级低置信度标记。",
        "extra_prompt_lines": [
            "把观测结果翻译成生成器可直接消费的提示词模块，如风格、环境、节奏、镜头、灯光、角色、镜头段落、背景声音与转场剪辑。",
            "交付结果必须拆成“反推原版”和“产品适配版”两层。",
            "shot 级结构至少要落到时长、主体、动作、口播 / 字幕、作用与素材需求。",
            "若证据偏薄，最终制作简报中要保留低置信度标记。",
        ],
        "output_checklist": [
            "反推制作简报已拆成生成器可用的结构化模块。",
            "存在分镜级行，而不只是 1 段泛 prompt。",
            "当存在产品上下文时，已附带用户产品适配版。",
            "已额外给出生成器交接字段，而不是停在分析笔记。",
            "证据薄弱的推断已清楚标记。",
            "无需从零重做分析，就能继续改写为用户产品版本。",
        ],
    },
    "06": {
        "runner_slug": "competitor-product-dashboard",
        "project_example": "Weekly Competitor Product Dashboard",
        "evidence_example": "3 competitor listings with price, rating, and offer snapshots",
        "success_goal": "competitor tracking dashboard and signal rules",
        "recommended_request": "Run scene 06 to build a competitor product dashboard that can be reused weekly. If no TikTok Shop API exists, fall back to listing snapshots, PDP screenshots, review evidence, and manual tracker rows while keeping the same schema and signal rules.",
        "extra_prompt_lines": [
            "Use stable product identifiers so later tracking does not drift.",
            "Interpret changes commercially instead of logging raw changes only.",
            "When Shop API data is missing, switch to fallback evidence capture instead of leaving the workflow blank.",
        ],
        "output_checklist": [
            "The dashboard schema is stable enough for repeated use.",
            "Signal changes have follow-up actions attached.",
            "The board stays minimal enough for one operator to maintain.",
        ],
    },
    "07": {
        "runner_slug": "category-market-insight",
        "project_example": "US Beauty Category Opportunity Read",
        "evidence_example": "Category examples, competitor set, and top content references",
        "success_goal": "category opportunity judgment and next move",
        "recommended_request": "Run scene 07 to judge a category or product theme for demand, saturation, and opportunity. Extract hot keywords from titles and hashtags, evaluate each keyword by content heat and product-side proof, and end with a do, do-not-do, and priority-do decision surface.",
        "extra_prompt_lines": [
            "Separate hot demand signals from crowded angle saturation.",
            "Match recommendation strength to evidence depth instead of overstating certainty.",
            "Keep content heat and product performance as separate evaluation axes.",
        ],
        "output_checklist": [
            "Demand, saturation, and whitespace are all addressed.",
            "Conclusions are backed by visible examples, not hype alone.",
            "The output includes keyword-level decisions rather than one vague category opinion.",
            "The operator gets one prioritized next move.",
        ],
    },
    "08": {
        "runner_slug": "comment-mining-persona",
        "project_example": "口红品类评论挖掘与人群画像报告",
        "evidence_example": "来自 3-5 个商品的评论样本，已标出物流、包装、真假、退货、before-after、色号 / 尺码适配等购买型语言",
        "success_goal": "买家语言提炼、基础价值 / 改进机会分离与人群画像启发",
        "recommended_request": "按场景 08 执行：把多个商品的评论做成品类级人群洞察。先按来源商品分组，再提炼购买因素、好评关键词、差评痛点、价位差异，并保留重复用户原话与来源商品标签，最后回到人群画像、定位与脚本话术建议。",
        "extra_prompt_lines": [
            "合并品类信号前，先按商品维度保留评论分组。",
            "优先保留重复用户原话，不要只做抽象情绪总结。",
            "把品类级基础价值与品类级改进机会明确分开。",
            "尽量突出物流、包装、真假、退货、before-after、尺码 / 色号适配等购买型语言。",
        ],
        "output_checklist": [
            "Repeated pain, desire, and trust signals are separated clearly.",
            "Real user-language evidence is preserved.",
            "Source products remain visible through the merged analysis.",
            "基础价值与改进机会已明确分开。",
            "Persona and messaging implications follow directly from the mined comments.",
        ],
    },
    "09": {
        "runner_slug": "reference-replication-brief",
        "project_example": "对标视频复刻制作简报",
        "evidence_example": "参考视频逻辑、用户产品基础信息与现有素材",
        "success_goal": "适配新产品的复刻制作简报与镜头顺序",
        "recommended_request": "Run scene 09 to turn one reference video into an adapted replication plan for a new product. Lock the invariant winning logic first, then rewrite the hook, proof, and close for the user's product.",
        "extra_prompt_lines": [
            "Keep the winning mechanism, but replace product-specific proof and offer layers one at a time.",
            "End with a filmable shot order or prompt-ready scene structure.",
        ],
        "output_checklist": [
            "Invariant reference logic is clearly separated from adapted layers.",
            "The adapted production brief is specific enough to produce from.",
            "Literal-copy risks are called out explicitly.",
        ],
    },
    "10": {
        "runner_slug": "product-image-to-video-brief",
        "project_example": "产品图转视频制作简报",
        "evidence_example": "Product images, selling points, audience note, and desired style",
        "success_goal": "基于静态素材的可生产短视频制作简报",
        "recommended_request": "Run scene 10 to design a short-form video production brief from product images only. Choose the video type, build proof beats around available assets, and note any visual gaps that would block production.",
        "extra_prompt_lines": [
            "Design proof beats from the assets that actually exist, not from imaginary footage.",
            "Keep CTA and conversion intent visible even if the input is image-only.",
        ],
        "output_checklist": [
            "The production brief is compatible with the available asset set.",
            "Hook, proof beats, and CTA are all defined.",
            "Any visual gaps are explicit instead of hidden inside optimistic wording.",
        ],
    },
    "11": {
        "runner_slug": "hot-video-replication-pipeline",
        "project_example": "Hot Video Replication Pipeline",
        "evidence_example": "Discovery inputs, shortlist rules, and weekly operator cadence",
        "success_goal": "repeatable discovery-to-replication pipeline",
        "recommended_request": "Run scene 11 to build a repeatable hot-video replication pipeline from discovery through ranking, teardown, and creative queueing. Make the decision gates explicit so the workflow can run every week.",
        "extra_prompt_lines": [
            "Separate discovery, teardown, queue-entry, and production handoff into distinct stages.",
            "Define what makes a hot video worth entering the replication queue.",
        ],
        "output_checklist": [
            "Pipeline stages and gates are explicit.",
            "The replication queue has ranking logic, not only intake logic.",
            "The workflow is light enough to repeat on a real cadence.",
        ],
    },
    "12": {
        "runner_slug": "multi-style-testing-matrix",
        "project_example": "One Product Multi-Style Test Matrix",
        "evidence_example": "One product, one core message, and style directions to test",
        "success_goal": "multi-style variant matrix with learning agenda",
        "recommended_request": "Run scene 12 to create a multi-style testing matrix for one product. Lock the invariant message first, then define meaningfully different style variants and what each row is meant to teach.",
        "extra_prompt_lines": [
            "Do not create cosmetic variants that only change wording slightly.",
            "Define success signals and the learning objective for each variant.",
        ],
        "output_checklist": [
            "The invariant message stays fixed across rows.",
            "Variants differ in a meaningful strategic way.",
            "Each row has a clear learning goal and test priority.",
        ],
    },
    "13": {
        "runner_slug": "multi-market-localization-pack",
        "project_example": "Beauty Multi-Market Localization Pack",
        "evidence_example": "Source concept, 2-3 target markets, and local audience notes",
        "success_goal": "多市场本地化制作简报包",
        "recommended_request": "Run scene 13 to localize one product concept across multiple markets. Separate shared product truth from market-specific hooks, tone, and avoid-lists, and keep localization tied to conversion context rather than literal translation.",
        "extra_prompt_lines": [
            "Write each market's hook, tone, and risk notes separately.",
            "Treat localization as adaptation of message, talent, and scene logic, not copy translation only.",
        ],
        "output_checklist": [
            "Shared invariant logic is separated from local layers.",
            "Each target market has a concrete hook direction.",
            "Avoid-lists or local-risk notes are visible where relevant.",
        ],
    },
    "14": {
        "runner_slug": "launch-asset-family-pack",
        "project_example": "Launch Asset Family Blueprint",
        "evidence_example": "Product description, selling points, and platform launch constraints",
        "success_goal": "coordinated launch asset family blueprint",
        "recommended_request": "Run scene 14 to design a coordinated launch asset family. Define the minimum viable asset family first, assign one conversion job to each asset, and prioritize production order by launch leverage.",
        "extra_prompt_lines": [
            "Keep message logic coherent across the full asset family.",
            "Do not treat all assets as equally important or equally urgent.",
        ],
        "output_checklist": [
            "Each asset has one explicit job in the launch system.",
            "Production order is prioritized.",
            "The family shares one coherent creative direction.",
        ],
    },
    "15": {
        "runner_slug": "image-translation-brief",
        "project_example": "图片文案本地化制作简报",
        "evidence_example": "Image OCR text, layout notes, target language, and conversion goal",
        "success_goal": "兼容原布局的图片文案本地化制作简报",
        "recommended_request": "Run scene 15 to translate and localize image copy for conversion. Separate literal information from persuasive copy blocks, preserve hierarchy, and include layout notes so the localized copy can actually fit.",
        "extra_prompt_lines": [
            "Do not stop at literal translation when the image is meant to convert.",
            "Call out where copy length or emphasis must shift to preserve layout hierarchy.",
        ],
        "output_checklist": [
            "Headline, support copy, and literal information are separated.",
            "Localized copy is compatible with the original layout constraints.",
            "Conversion tone is adapted for the target market instead of translated blindly.",
        ],
    },
    "16": {
        "runner_slug": "main-image-benchmark",
        "project_example": "竞品主图超车制作简报",
        "evidence_example": "2-5 competitor images plus the user's current image or product",
        "success_goal": "主图超车方向与设计制作简报",
        "recommended_request": "Run scene 16 to benchmark competitor main images and define a stronger direction. Describe the click context first, then identify category norms, gaps, and a sharper outperform production brief.",
        "extra_prompt_lines": [
            "Judge likely click behavior in context instead of giving generic visual design notes.",
            "End with an outperform strategy, not just a critique list.",
        ],
        "output_checklist": [
            "The benchmark is grounded in comparable category context.",
            "Likely click drivers are identified explicitly.",
            "The final production brief is sharper than generic advice such as make it cleaner.",
        ],
    },
    "17": {
        "runner_slug": "creator-distillation",
        "project_example": "创作者公式蒸馏报告",
        "evidence_example": "Several top creator videos with transcript and performance notes",
        "success_goal": "可重复创作者公式与改编规则",
        "recommended_request": "按场景 17 执行：从同一创作者的多条视频里蒸馏可重复的内容公式。先做账号概览，再比较高互动与低互动样本，提炼可复用的 hook 与节奏公式，最后把可迁移逻辑和创作者专属优势拆开，并桥接成新脚本方向。",
        "extra_prompt_lines": [
            "在宣告公式前，至少使用多条创作者样本。",
            "不要把“喜欢这个创作者”误判为“可复用的制作规则”。",
            "把 hook 公式、视觉风格、BGM、hashtag 习惯与发布时间线索拆成独立提取层。",
        ],
        "output_checklist": [
            "在提出公式前，账号概览与内容基线已经明确。",
            "重复模式由多条创作者样本支撑。",
            "高互动与低互动差异已直接对比。",
            "hook 与节奏公式足够可复用，可直接作为新脚本种子。",
            "可迁移规则与创作者专属优势已分开。",
            "报告最终落到新的产品或账号适配建议。",
        ],
    },
    "18": {
        "runner_slug": "competitor-account-weekly-report",
        "project_example": "竞品账号周报",
        "evidence_example": "2-5 个竞品账号的周度帖子批次、上周备注与多周快照",
        "success_goal": "竞品周报、爆款归因、策略变化判断与动作看板",
        "recommended_request": "按场景 18 执行：输出竞品账号周报。把 3-5 个账号视为同一个矩阵，按账号与周维度比较发帖、爆点内容、爆款归因与策略变化；如果只有 1 周数据，要明确标成 baseline week，最后写清本周该跟进什么动作。",
        "extra_prompt_lines": [
            "重点突出跨账号的周度模式变化，而不是只列活动量。",
            "把观察到的变化翻译成本周可执行动作。",
            "解释为什么会爆，而不是只点名哪条爆了。",
            "只有单周数据时，不要假装有长期趋势判断。",
        ],
        "output_checklist": [
            "帖子已经按账号与周维度整理。",
            "报告解释了变化，而不是只罗列原始活动量。",
            "跨账号策略差异已经说清楚。",
            "已经区分 baseline week 与多周趋势判断。",
            "本周响应动作已经排优先级。",
        ],
    },
    "19": {
        "runner_slug": "self-account-retro",
        "project_example": "自家账号复盘优化",
        "evidence_example": "最近多批帖子表，包含指标、钩子、内容类型标签与可选 ROI 线索",
        "success_goal": "表现复盘、多做 / 少做 / 停止规则与下轮测试计划",
        "recommended_request": "按场景 19 执行：复盘一个账号最近一批内容并定义下一轮优化周期。先按内容模式聚类，再直接比较高表现组和低表现组；如果只有 1 个时间窗口的数据，要明确写成本轮观察，最后输出多做、少做、停止和下轮测试规则，并尽量挂到 ROI 或增长目标。",
        "extra_prompt_lines": [
            "按可重复模式聚类帖子，不要只逐条读表。",
            "把复盘落成一份下轮测试计划，而不是停留在被动总结。",
            "只要证据允许，就把内容特征挂到增长或 ROI 相关性上，而不是停留在审美判断。",
            "区分单窗口观察与多周重复模式，不要把一周表现写成长期规律。",
        ],
        "output_checklist": [
            "高低表现组已经直接对比。",
            "赢法与输法已经清楚分开。",
            "建议写成操作规则，而不是模糊观察。",
            "如有 ROI 线索，已挂到增长目标上。",
            "下轮测试计划已经具体到可以直接执行。",
        ],
    },
}


SCENE_TITLES_ZH = {
    "01": "\u7206\u6b3e\u89c6\u9891\u91c7\u96c6",
    "02": "\u54c1\u7c7b\u65e5\u5e38\u5de1\u68c0",
    "03": "\u6279\u91cf\u7206\u6b3e\u68c0\u7d22\u4e0e\u6df1\u62c6",
    "04": "\u5355\u6761\u89c6\u9891\u62c6\u89e3",
    "05": "\u53cd\u63a8\u63d0\u793a\u8bcd\u4e0e\u5236\u4f5c\u7b80\u62a5",
    "06": "\u7ade\u54c1\u5546\u54c1\u770b\u677f",
    "07": "\u54c1\u7c7b\u5e02\u573a\u5224\u65ad",
    "08": "\u591a\u4ea7\u54c1\u8bc4\u8bba\u6316\u6398\u4e0e\u4eba\u7fa4\u62a5\u544a",
    "09": "\u5bf9\u6807\u89c6\u9891\u590d\u523b\u5236\u4f5c\u7b80\u62a5",
    "10": "\u4ea7\u54c1\u56fe\u8f6c\u89c6\u9891\u5236\u4f5c\u7b80\u62a5",
    "11": "\u70ed\u70b9\u89c6\u9891\u590d\u5236 Pipeline",
    "12": "\u5355\u54c1\u591a\u98ce\u683c\u6d4b\u8bd5\u77e9\u9635",
    "13": "\u591a\u5e02\u573a\u672c\u5730\u5316\u5305",
    "14": "\u4e0a\u65b0\u7d20\u6750\u5bb6\u65cf\u5305",
    "15": "\u56fe\u7247\u6587\u6848\u7ffb\u8bd1\u5236\u4f5c\u7b80\u62a5",
    "16": "\u7ade\u54c1\u4e3b\u56fe Benchmark",
    "17": "\u521b\u4f5c\u8005\u516c\u5f0f\u84b8\u998f",
    "18": "\u7ade\u54c1\u8d26\u53f7\u5468\u62a5",
    "19": "\u81ea\u6709\u8d26\u53f7\u590d\u76d8\u4f18\u5316",
}

SCENE_REQUESTS_ZH = {
    "01": "\u6309\u573a\u666f 01 \u6267\u884c\uff1a\u56f4\u7ed5\u4e00\u4e2a\u5173\u952e\u8bcd\u6216\u54c1\u7c7b\u548c\u5355\u4e00\u5e02\u573a\uff0c\u5148\u6536\u96c6\u5019\u9009\u7206\u6b3e\uff0c\u518d\u6309\u590d\u7528\u4ef7\u503c\u800c\u4e0d\u662f\u5355\u770b\u64ad\u653e\u91cf\u6392\u5e8f\uff0c\u6700\u540e\u544a\u8bc9\u6211\u54ea\u4e9b\u89c6\u9891\u6700\u503c\u5f97\u8fdb\u5165\u4e0b\u4e00\u6b65\u62c6\u89e3\u3002",
    "02": "\u6309\u573a\u666f 02 \u6267\u884c\uff1a\u4e3a\u4e00\u4e2a\u54c1\u7c7b\u642d\u5efa\u65e5\u5e38\u5de1\u68c0 SOP\uff0c\u8f93\u51fa\u53ef\u91cd\u590d\u4f7f\u7528\u7684\u5de1\u68c0\u8868\u3001\u9884\u8b66\u903b\u8f91\u548c\u65e5\u62a5\u6a21\u677f\uff0c\u4e0d\u8981\u53ea\u7ed9\u7814\u7a76\u7ed3\u8bba\u3002",
    "03": "\u6309\u573a\u666f 03 \u6267\u884c\uff1a\u5148\u5bf9\u540c\u4e00\u4e3b\u9898\u7684\u5019\u9009\u70ed\u89c6\u9891\u505a shortlist\uff0c\u518d\u53ea\u6df1\u62c6\u524d\u51e0\u6761\u5f3a\u6837\u672c\uff0c\u6700\u540e\u6c89\u6dc0\u5171\u7528\u7206\u70b9\u89c4\u5f8b\u548c\u53ef\u76f4\u63a5\u6539\u5199\u6210\u65b0\u811a\u672c\u7684\u521b\u4f5c\u89c4\u5219\u3002",
    "04": "\u6309\u573a\u666f 04 \u6267\u884c\uff1a\u5b8c\u6574\u62c6\u4e00\u6761\u77ed\u89c6\u9891\uff0c\u6309 hook\u3001\u94fa\u57ab\u3001\u8bc1\u660e\u3001\u6536\u53e3\u91cd\u5efa\u7ed3\u6784\uff0c\u518d\u5206\u79bb\u771f\u6b63\u6709\u6548\u7684\u673a\u5236\u548c\u8868\u5c42\u98ce\u683c\uff0c\u5e76\u7ed9\u51fa\u4e00\u4e2a\u53ef\u6539\u7f16\u65b9\u5411\u3002",
    "05": "\u6309\u573a\u666f 05 \u6267\u884c\uff1a\u53cd\u5411\u63a8\u65ad\u8fd9\u6761\u89c6\u9891\u80cc\u540e\u7684\u63d0\u793a\u8bcd\u6216\u5236\u4f5c\u7b80\u62a5\uff0c\u628a\u521b\u4f5c\u610f\u56fe\u62c6\u6210\u89c6\u89c9\u3001\u955c\u5934\u3001\u65c1\u767d\u3001\u8282\u594f\u6a21\u5757\uff0c\u5e76\u628a\u4f4e\u7f6e\u4fe1\u5ea6\u731c\u6d4b\u6807\u51fa\u6765\u3002",
    "06": "\u6309\u573a\u666f 06 \u6267\u884c\uff1a\u642d\u5efa\u53ef\u6bcf\u5468\u590d\u7528\u7684\u7ade\u54c1\u5546\u54c1\u770b\u677f\uff0c\u5b9a\u4e49\u6700\u5c0f\u8ffd\u8e2a\u5b57\u6bb5\u3001\u4fe1\u53f7\u89e3\u91ca\u903b\u8f91\u548c\u53d8\u5316\u540e\u7684\u8fd0\u8425\u52a8\u4f5c\uff1b\u5982\u679c\u6ca1\u6709 TikTok Shop API\uff0c\u5c31\u8d70 listing/PDP/\u8bc4\u8bba\u622a\u56fe\u964d\u7ea7\u6a21\u5f0f\u3002",
    "07": "\u6309\u573a\u666f 07 \u6267\u884c\uff1a\u5224\u65ad\u4e00\u4e2a\u54c1\u7c7b\u6216\u4e3b\u9898\u662f\u5426\u503c\u5f97\u505a\uff0c\u8981\u540c\u65f6\u770b\u5185\u5bb9\u70ed\u5ea6\u3001\u4f9b\u7ed9\u9971\u548c\u5ea6\u548c\u53ef\u5207\u5165\u7a7a\u4f4d\uff0c\u6700\u540e\u7ed9\u51fa\u5f3a\u5f31\u5206\u7ea7\u5efa\u8bae\u3002",
    "08": "\u6309\u573a\u666f 08 \u6267\u884c\uff1a\u628a\u591a\u4e2a\u4ea7\u54c1\u7684\u8bc4\u8bba\u505a\u5408\u5e76\u6316\u6398\uff0c\u5206\u5f00\u63d0\u70bc\u75db\u70b9\u3001\u6b32\u671b\u548c\u4fe1\u4efb\u4fe1\u53f7\uff0c\u5e76\u4fdd\u7559\u539f\u8bdd\uff0c\u6700\u540e\u8f6c\u6210\u4eba\u7fa4\u548c\u8bdd\u672f\u542f\u53d1\u3002",
    "09": "\u6309\u573a\u666f 09 \u6267\u884c\uff1a\u628a\u4e00\u6761\u5bf9\u6807\u89c6\u9891\u6539\u9020\u6210\u9002\u5408\u65b0\u4ea7\u54c1\u7684\u590d\u523b\u5236\u4f5c\u7b80\u62a5\uff0c\u5148\u9501\u5b9a\u4e0d\u8be5\u6539\u7684 winning logic\uff0c\u518d\u91cd\u5199 hook\u3001\u8bc1\u660e\u548c\u6536\u53e3\u3002",
    "10": "\u6309\u573a\u666f 10 \u6267\u884c\uff1a\u4ec5\u57fa\u4e8e\u4ea7\u54c1\u56fe\u8bbe\u8ba1\u4e00\u7248\u77ed\u89c6\u9891\u5236\u4f5c\u7b80\u62a5\uff0c\u660e\u786e\u89c6\u9891\u7c7b\u578b\u3001\u8bc1\u660e\u955c\u5934\u3001CTA \u548c\u8d44\u4ea7\u7f3a\u53e3\uff0c\u4e0d\u8981\u5047\u8bbe\u7528\u6237\u5df2\u7ecf\u6709\u989d\u5916\u7d20\u6750\u3002",
    "11": "\u6309\u573a\u666f 11 \u6267\u884c\uff1a\u642d\u4e00\u4e2a\u53ef\u91cd\u590d\u8dd1\u7684\u70ed\u70b9\u89c6\u9891\u590d\u5236 pipeline\uff0c\u628a\u53d1\u73b0\u3001\u7b5b\u9009\u3001\u6df1\u62c6\u3001\u5165\u6c60\u548c\u751f\u4ea7\u4ea4\u63a5\u62c6\u6210\u660e\u786e\u9636\u6bb5\u548c\u95e8\u69db\u3002",
    "12": "\u6309\u573a\u666f 12 \u6267\u884c\uff1a\u4e3a\u4e00\u4e2a\u4ea7\u54c1\u505a\u591a\u98ce\u683c\u6d4b\u8bd5\u77e9\u9635\uff0c\u5148\u9501 invariant message\uff0c\u518d\u8bbe\u8ba1\u771f\u6b63\u6709\u5dee\u5f02\u7684\u6d4b\u8bd5\u98ce\u683c\uff0c\u5e76\u5199\u51fa\u6bcf\u4e2a\u53d8\u4f53\u8981\u5b66\u4ec0\u4e48\u3002",
    "13": "\u6309\u573a\u666f 13 \u6267\u884c\uff1a\u628a\u4e00\u4e2a\u4ea7\u54c1\u6982\u5ff5\u505a\u6210\u591a\u5e02\u573a\u672c\u5730\u5316\u5305\uff0c\u62c6\u6e05\u5171\u4eab\u4ea7\u54c1\u771f\u76f8\u548c\u5404\u5e02\u573a\u7684 hook\u3001\u8bed\u6c14\u3001\u7981\u533a\uff0c\u4e0d\u8981\u53ea\u505a\u76f4\u8bd1\u3002",
    "14": "\u6309\u573a\u666f 14 \u6267\u884c\uff1a\u8bbe\u8ba1\u4e00\u5957\u4e0a\u65b0\u7d20\u6750\u5bb6\u65cf\uff0c\u5148\u5b9a\u4e49\u6700\u5c0f\u53ef\u4e0a\u7ebf\u8d44\u4ea7\u96c6\uff0c\u518d\u7ed9\u6bcf\u4e2a\u7d20\u6750\u5206\u914d\u4e00\u4e2a\u8f6c\u5316\u804c\u8d23\uff0c\u5e76\u6392\u51fa\u5236\u4f5c\u4f18\u5148\u7ea7\u3002",
    "15": "\u6309\u573a\u666f 15 \u6267\u884c\uff1a\u505a\u56fe\u7247\u6587\u6848\u7ffb\u8bd1\u4e0e\u672c\u5730\u5316\u5236\u4f5c\u7b80\u62a5\uff0c\u533a\u5206\u4fe1\u606f\u6027\u6587\u6848\u548c\u8f6c\u5316\u578b\u6587\u6848\uff0c\u4fdd\u7559\u5c42\u7ea7\u5173\u7cfb\uff0c\u5e76\u8bf4\u660e\u65b0\u6587\u6848\u5982\u4f55\u9002\u914d\u539f\u5e03\u5c40\u3002",
    "16": "\u6309\u573a\u666f 16 \u6267\u884c\uff1a\u5bf9\u6807\u7ade\u54c1\u4e3b\u56fe\u5e76\u5b9a\u4e49\u66f4\u5f3a\u65b9\u5411\uff0c\u5148\u8bf4\u6e05\u70b9\u51fb\u573a\u666f\uff0c\u518d\u603b\u7ed3\u7c7b\u76ee\u5171\u6027\u3001\u5dee\u5f02\u673a\u4f1a\u548c\u4e00\u7248\u53ef\u6267\u884c\u7684\u8d85\u8f66\u5236\u4f5c\u7b80\u62a5\u3002",
    "17": "\u6309\u573a\u666f 17 \u6267\u884c\uff1a\u63d0\u70bc\u4e00\u4e2a\u521b\u4f5c\u8005\u5728\u591a\u6761\u89c6\u9891\u91cc\u91cd\u590d\u51fa\u73b0\u7684\u5185\u5bb9\u516c\u5f0f\uff0c\u62c6\u5f00 hook\u3001\u8282\u594f\u3001\u8bc1\u660e\u548c CTA\uff0c\u5e76\u533a\u5206\u53ef\u8fc1\u79fb\u89c4\u5219\u4e0e\u521b\u4f5c\u8005\u72ec\u6709\u4f18\u52bf\u3002",
    "18": "\u6309\u573a\u666f 18 \u6267\u884c\uff1a\u8f93\u51fa\u7ade\u54c1\u8d26\u53f7\u5468\u62a5\uff0c\u8981\u6309\u8d26\u53f7\u548c\u5468\u7ef4\u5ea6\u6bd4\u8f83\u5185\u5bb9\u53d8\u5316\uff0c\u4e0d\u53ea\u770b\u603b\u91cf\uff0c\u5e76\u660e\u786e\u672c\u5468\u8be5\u8ddf\u8fdb\u7684\u52a8\u4f5c\u3002",
    "19": "\u6309\u573a\u666f 19 \u6267\u884c\uff1a\u590d\u76d8\u4e00\u4e2a\u8d26\u53f7\u6700\u8fd1\u4e00\u6279\u5185\u5bb9\uff0c\u628a\u5e16\u5b50\u6309\u6a21\u5f0f\u5206\u7ec4\uff0c\u62c6\u51fa\u8d62\u6cd5\u548c\u8f93\u6cd5\uff0c\u6700\u540e\u5199\u6210\u591a\u505a\u4ec0\u4e48\u3001\u5c11\u505a\u4ec0\u4e48\u3001\u505c\u6b62\u4ec0\u4e48\u548c\u4e0b\u4e00\u8f6e\u6d4b\u8bd5\u8ba1\u5212\u3002",
}

def _build_default_variable_inputs(
    project_example: str,
    evidence_example: str,
    success_goal: str,
) -> list[dict]:
    return [
        {
            "name": "project_name",
            "meaning": "便于识别的运行名或项目名",
            "example": project_example,
            "required": "是",
        },
        {
            "name": "market",
            "meaning": "当场景依赖单一市场时的目标市场或地区",
            "example": "美国",
            "required": "建议",
        },
        {
            "name": "evidence_pack",
            "meaning": "作为源证据使用的链接、截图、转写、导出文件、OCR 文本或摘录备注",
            "example": evidence_example,
            "required": "是",
        },
        {
            "name": "success_goal",
            "meaning": "操作者希望该场景产出的结果",
            "example": success_goal,
            "required": "建议",
        },
    ]


def _build_prompt_scaffold_zh(
    scene_id: str,
    inputs: list[str],
    minimum_evidence: list[str],
    requested_outputs: list[str],
) -> list[str]:
    scene_title_zh = SCENE_TITLES_ZH.get(scene_id, f"\u573a\u666f {scene_id}")
    default_inputs = "\u573a\u666f\u6240\u9700\u8bc1\u636e\u96c6"
    default_minimum = "\u8bf7\u5148\u8bf4\u660e\u6700\u4f4e\u53ef\u5f00\u5de5\u8bc1\u636e"
    default_outputs = "\u573a\u666f\u4ea4\u4ed8\u7269\u548c\u4e0b\u4e00\u6b65\u52a8\u4f5c"
    inputs_text = ", ".join(inputs) if inputs else default_inputs
    minimum_text = ", ".join(minimum_evidence) if minimum_evidence else default_minimum
    outputs_text = ", ".join(requested_outputs) if requested_outputs else default_outputs
    return [
        SCENE_REQUESTS_ZH.get(scene_id, f"\u6309\u573a\u666f {scene_id}\u300a{scene_title_zh}\u300b\u6267\u884c\u3002"),
        f"\u5148\u628a\u6211\u63d0\u4f9b\u7684\u6750\u6599\u6574\u7406\u6210\u8fd9\u7ec4\u8f93\u5165\uff1a{inputs_text}\u3002",
        f"\u5982\u679c\u8bc1\u636e\u4e0d\u8db3\uff0c\u5148\u660e\u786e\u7f3a\u53e3\u518d\u7ee7\u7eed\u3002\u6700\u4f4e\u5f00\u5de5\u8bc1\u636e\uff1a{minimum_text}\u3002",
        f"\u6700\u7ec8\u5fc5\u987b\u4ea7\u51fa\uff1a{outputs_text}\u3002",
        "\u8f93\u51fa\u5fc5\u987b\u53ef\u76f4\u63a5\u7ed9\u8fd0\u8425\u3001\u62c6\u89e3\u3001\u811a\u672c\u3001\u6d4b\u8bd5\u6216\u4ea4\u4ed8\u4f7f\u7528\uff0c\u4f18\u5148\u7ed9\u8868\u683c\u3001\u6392\u5e8f\u903b\u8f91\u3001\u590d\u7528\u89c4\u5219\u548c\u4e0b\u4e00\u6b65\u52a8\u4f5c\u3002",
    ]


def build_execution_template(scene_id: str, preset: dict) -> dict:
    working_context = preset.get("working_context", {})
    requested_outputs = [str(item).strip() for item in working_context.get("requested_outputs", []) if str(item).strip()]
    inputs = [str(item).strip() for item in working_context.get("inputs", []) if str(item).strip()]
    minimum_evidence = [str(item).strip() for item in working_context.get("minimum_evidence", []) if str(item).strip()]
    operator_guide = preset.get("operator_guide", {})
    operator_checklist = [str(item).strip() for item in operator_guide.get("operator_checklist", []) if str(item).strip()]
    profile = SCENE_EXECUTION_PROFILES.get(scene_id, {})
    project_example = profile.get("project_example", "Beauty US Daily Ops")
    evidence_example = profile.get("evidence_example", "Links, screenshots, transcripts, and operator notes")
    success_goal = profile.get(
        "success_goal",
        ", ".join(requested_outputs[:2]) if requested_outputs else "Reusable operator deliverable",
    )
    runner_slug = profile.get("runner_slug", f"scene-{scene_id}-run")
    workflow_steps = profile.get("workflow_steps", operator_checklist) or [
        "先归整证据与工作范围。",
        "按章节补全场景脚手架。",
        "最后落到 1 个明确的下一步动作。",
    ]
    prompt_scaffold = [
        f"以场景 {scene_id} 作为本次工作的主流程。",
        f"分析前先把现有证据归整为以下输入：{', '.join(inputs) if inputs else '场景特定证据集合'}。",
        f"如果证据不足，先明确缺口再继续。最低开工证据：{', '.join(minimum_evidence) if minimum_evidence else '请明确最低开工证据'}。",
        f"最终必须产出以下可直接给运营使用的结果：{', '.join(requested_outputs) if requested_outputs else '场景交付章节与下一步动作'}。",
    ]
    prompt_scaffold.extend(profile.get("extra_prompt_lines", []))
    prompt_scaffold.append("优先填入可复用结论、表格、排序逻辑和下一步动作，不要停留在泛泛点评。")

    return {
        "recommended_request": profile.get(
            "recommended_request",
            f"按场景 {scene_id} 执行，并输出完整可复用交付物，不要只给摘要。",
        ),
        "recommended_request_zh": SCENE_REQUESTS_ZH.get(
            scene_id,
            f"\u6309\u573a\u666f {scene_id} \u6267\u884c\uff0c\u5e76\u8f93\u51fa\u5b8c\u6574\u53ef\u590d\u7528\u4ea4\u4ed8\u7269\uff0c\u4e0d\u8981\u53ea\u7ed9\u6458\u8981\u3002",
        ),
        "recommended_runner_args": [
            f'python scripts/run_operator_workflow.py --mode scene --scene {scene_id} --project "<project-name>" --output-root ".\\tmp\\{runner_slug}"',
            f'python scripts/generate_scene_report.py --scene {scene_id} --project "<project-name>" --output ".\\tmp\\{runner_slug}.json" --format json',
        ],
        "variable_inputs": _build_default_variable_inputs(project_example, evidence_example, success_goal),
        "codex_prompt_scaffold": prompt_scaffold,
        "codex_prompt_scaffold_zh": _build_prompt_scaffold_zh(
            scene_id,
            inputs,
            minimum_evidence,
            requested_outputs,
        ),
        "workflow_steps": workflow_steps,
        "output_checklist": profile.get("output_checklist", []) or [
            "交付结果已绑定到真实证据。",
            "操作者无需额外解释就能继续下一步。",
        ],
    }
SCENE_PRESETS = {
    "01": {
        "working_context": {
            "inputs": [
                "核心关键词或产品短语",
                "目标市场",
                "目标人群",
                "发布时间窗口或时效要求",
                "排序方式",
                "是否仅保留 TikTok Shop 购物车视频",
            ],
            "constraints": [
                "不要只按播放量排序，排序逻辑里必须保留复用价值判断。",
                "如果当前无法实时浏览，就依赖用户提供的截图、导出文件或复制链接。",
            ],
            "requested_outputs": [
                "排序短名单",
                "结构化采集主表",
                "每条入选视频为什么值得研究",
                "Scene 03 交接短名单",
            ],
        },
        "evidence": [
            {"label": "候选导出", "detail": "粘贴标题、链接、播放、点赞、发布时间和首拍钩子笔记。", "source": ""},
            {"label": "搜索截图集", "detail": "如果没有结构化导出，就附上搜索结果截图。", "source": ""},
        ],
        "sections": [
            section(
                "Executive Conclusion",
                "说明在这个关键词和市场下，最值得研究的是哪类视频。",
                bullets=[
                    "短名单里最强的子模式是什么？",
                    "操作者应该优先研究 hook、结构、证明还是风格？",
                ],
            ),
            section(
                "Objects To Track",
                "先搭好短名单主表。",
                table=blank_table(
                    ["Rank", "Video / Link", "Core Topic", "Performance Signal", "Publish Window", "TikTok Shop Signal", "Commerce Confidence", "Useful For", "Why Selected", "Best Next Scene"],
                    [
                        ["1", "", "", "", "", "", "", "", "", ""],
                        ["2", "", "", "", "", "", "", "", "", ""],
                        ["3", "", "", "", "", "", "", "", "", ""],
                        ["4", "", "", "", "", "", "", "", "", ""],
                        ["5", "", "", "", "", "", "", "", "", ""],
                    ],
                    "Top Candidate Board",
                ),
            ),
            section(
                "Why They Matter",
                "解释为什么每条入选视频值得被优先关注。",
                table=blank_table(
                    ["Video", "Hook Strength", "Proof Style", "Conversion Signal", "Why Worth Studying", "Suitable Product / Niche"],
                    [["", "", "", "", "", ""], ["", "", "", "", "", ""], ["", "", "", "", "", ""]],
                ),
            ),
            section(
                "Fields To Capture Next Time",
                "定义下一轮采集至少要补齐哪些字段。",
                table=blank_table(
                    ["Field", "Why Capture It", "Required Next Time?"],
                    [
                        ["视频链接", "便于追溯到后续深拆", "是"],
                        ["地区", "确保只看单一市场", "是"],
                        ["排序方式", "保证采集轮次可复现", "是"],
                        ["购物车 / 店铺信号", "判断商业意图", "是"],
                        ["发布时间", "判断新鲜度", "是"],
                        ["播放 / 点赞 / 评论", "保留基础表现形态", "是"],
                        ["钩子摘要", "供后续拆解使用", "是"],
                        ["复用用途标签", "决定进入哪条下游流程", "是"],
                    ],
                ),
            ),
            section(
                "Next Action",
                "明确采集完成后立刻要做什么。",
                table=blank_table(
                    ["Priority", "Video", "Why It Should Move Now", "Scene 03 Role", "Open Evidence Gap"],
                    [["1", "", "", "", ""], ["2", "", "", "", ""], ["3", "", "", "", ""]],
                    "Scene 03 Handoff Shortlist",
                ),
            ),
        ],
        "assets": [
            {"label": "候选截图", "path": "", "note": "可选的搜索结果或头部帖子截图。"},
        ],
        "notes": [
            "如果多个市场混在一起，先拆分看板，再下结论。",
        ],
    },
    "02": {
        "working_context": {
            "inputs": [
                "品类名称",
                "主市场",
                "关键词集合",
                "巡检频率",
                "追加策略",
                "预警条件偏好",
            ],
            "constraints": [
                "如果没有自动化数据源，就输出可手工执行的 SOP，不要伪造自动化。",
            ],
            "requested_outputs": [
                "日常巡检清单",
                "巡检主表结构",
                "预警逻辑",
                "日报模板",
            ],
        },
        "evidence": [
            {"label": "当前巡检来源", "detail": "列出现有搜索入口、导出来源或手工采集来源。", "source": ""},
        ],
        "sections": [
            section(
                "Executive Conclusion",
                "用一段面向运营的结论说明这套巡检设计是什么、为什么要这么做。",
                bullets=[
                    "每个巡检周期到底检查什么？",
                    "什么才算值得处理的有效变化？",
                ],
            ),
            section(
                "Objects To Track",
                "定义日常巡检主表结构。",
                table=blank_table(
                    ["Field", "Description", "Why It Matters", "Daily / Weekly", "Append Every Run?"],
                    [
                        ["采集日期", "", "", "Daily", "Yes"],
                        ["关键词", "", "", "Daily", "Yes"],
                        ["视频链接", "", "", "Daily", "Yes"],
                        ["表现信号", "", "", "Daily", "Yes"],
                        ["新角度观察", "", "", "Daily", "Yes"],
                        ["预警标记", "", "", "Daily", "Yes"],
                    ],
                    "Patrol Board Schema",
                ),
            ),
            section(
                "Why They Matter",
                "解释这些变化该如何理解，而不是只做记录。",
                table=blank_table(
                    ["Signal Type", "What It Might Mean", "Follow-up Action", "Escalate To Scene 03?"],
                    [
                        ["今日新增爆点", "", "", ""],
                        ["今日上升模式", "", "", ""],
                        ["异常内容变化", "", "", ""],
                        ["弱信号 / 仅观察", "", "", ""],
                    ],
                ),
            ),
            section(
                "Capture Gaps Next Round",
                "如果当前巡检还偏浅，明确下次必须补采哪些字段。",
                bullets=[
                    "今天还缺哪些字段？",
                    "哪些字段能让后续排序更快？",
                ],
            ),
            section(
                "Next Action",
                "给运营留下一套可以直接执行的巡检日报例行流程。",
                table=blank_table(
                    ["Daily Summary Block", "Template", "Must Include"],
                    [
                        ["今天变了什么", "", ""],
                        ["今天新跑出的内容", "", ""],
                        ["哪些需要进入场景 03 深拆", "", ""],
                        ["哪些继续留在 watchlist", "", ""],
                    ],
                    "Reusable Daily Summary Template",
                ),
            ),
        ],
    },
    "03": {
        "working_context": {
            "inputs": [
                "Keyword or topic",
                "Target market",
                "Candidate links or search results",
                "Desired sample size",
                "Shortlist rule",
            ],
            "constraints": [
                "Shortlist before tearing down.",
                "Conclusions must be grounded in evidence from the chosen top videos.",
            ],
            "requested_outputs": [
                "Shortlist",
                "Per-video teardown",
                "Shared pattern summary",
                "Creation rules",
            ],
        },
        "evidence": [
            {"label": "Candidate pool", "detail": "Paste all initial candidates before ranking.", "source": ""},
            {"label": "Top-video evidence", "detail": "Add screenshots, transcript notes, and links for each chosen video.", "source": ""},
        ],
        "sections": [
            section(
                "Executive Conclusion",
                "State the core winning pattern shared by the top videos.",
                bullets=[
                    "What is the dominant hook type?",
                    "What is the main proof or conversion rhythm?",
                ],
            ),
            section(
                "Structure Logic",
                "Show how the top candidates were ranked and selected.",
                table=blank_table(
                    ["Rank", "Video", "Hook", "Proof", "Conversion Signal", "Commerce Signal", "Why It Made Top Set"],
                    [["1", "", "", "", "", "", ""], ["2", "", "", "", "", "", ""], ["3", "", "", "", "", "", ""]],
                    "Shortlist",
                ),
            ),
            section(
                "Core Mechanism",
                "Break down each selected video using the same lens.",
                table=blank_table(
                    ["Video", "Opening Hook", "Full Script / Key Lines", "Time-Axis Rhythm", "Proof Device", "CTA / Close", "Main Reuse Value"],
                    [["", "", "", "", "", "", ""], ["", "", "", "", "", "", ""], ["", "", "", "", "", "", ""]],
                    "Per-Video Breakdown Grid",
                ),
                evidence_refs=[
                    evidence_ref("video", "candidate-1", "paste-video-link", "00:00-00:03", "Hook and first proof beat from the top-ranked video.", "Per-video hook breakdown"),
                    evidence_ref("transcript", "candidate-1-script", "paste-transcript-source", "00:00-00:12", "Recovered caption or subtitle lines supporting the time-axis rhythm.", "Full script / key lines"),
                ],
            ),
            section(
                "Reusable Formula",
                "Turn the shared pattern into direct creation guidance.",
                table=blank_table(
                    ["Element", "Observed Pattern", "How To Reuse It", "What Not To Copy Blindly", "Evidence Ref"],
                    [
                        ["Hook", "", "", "", ""],
                        ["Proof", "", "", "", ""],
                        ["Shot rhythm", "", "", "", ""],
                        ["CTA", "", "", "", ""],
                    ],
                    "Creation Rules",
                ),
                evidence_refs=[
                    evidence_ref("video", "candidate-1", "paste-video-link", "00:00-00:02", "Opening reveal pattern reused across the strongest shortlisted videos.", "Hook formula"),
                    evidence_ref("video", "candidate-2", "paste-video-link", "00:03-00:08", "Proof-beat structure that repeats without relying on the same product.", "Proof formula"),
                ],
            ),
            section(
                "Risks And Adaptation Notes",
                "Explain where false copying would fail.",
                table=blank_table(
                    ["Risk Area", "Why It Can Mislead", "What To Check Before Reuse"],
                    [["Creator-specific advantage", "", ""], ["Market-specific angle", "", ""], ["Product-proof mismatch", "", ""]],
                ),
            ),
            section(
                "Next Action",
                "Leave a concrete next production move.",
                table=blank_table(
                    ["Output Block", "What Must Be Delivered", "Who Uses It Next"],
                    [["Per-video teardown", "", ""], ["Common-pattern summary", "", ""], ["Creation guidance", "", ""]],
                ),
            ),
        ],
    },
    "04": {
        "working_context": {
            "inputs": [
                "One video link or storyboard",
                "Transcript or subtitle notes",
                "Frame notes or screenshots",
                "Optional basic performance context",
            ],
            "constraints": [
                "Separate deep logic from surface style.",
                "If there is no voiceover, reconstruct the logic from subtitles, actions, cuts, and visual proof.",
            ],
            "requested_outputs": [
                "时间轴拆解表",
                "视频类型判断",
                "BGM 分析",
                "三段式爆点解读",
                "可复用机制",
                "改编建议",
            ],
        },
        "evidence": [
            {"label": "视频证据", "detail": "链接、截图、转写笔记，或人工重建笔记。", "source": ""},
            {"label": "音频证据", "detail": "如果没有完整转写，至少补 BGM 名称、音频风格或字幕线索。", "source": ""},
        ],
        "sections": [
            section(
                "Executive Conclusion",
                "明确判断这条单视频为什么成立，或为什么没有成立。",
            ),
            section(
                "Structure Logic",
                "按节拍重建视频从开头到结尾的结构。",
                table=blank_table(
                    ["Time Range", "Scene Type", "Visual Content", "Spoken / On-Screen Script", "Role In Conversion", "Asset / Talent Needed", "Evidence Ref"],
                    [
                        ["00:00-00:02", "钩子", "", "", "", "", ""],
                        ["00:02-00:06", "铺垫", "", "", "", "", ""],
                        ["00:06-00:14", "证明", "", "", "", "", ""],
                        ["00:14-00:20", "收口 / CTA", "", "", "", "", ""],
                    ],
                    "时间轴拆解",
                ),
                evidence_refs=[
                    evidence_ref("video", "primary-video", "待补视频链接", "00:00-00:02", "展示首个钩子瞬间或第一视觉回报的片段。", "时间轴行：钩子"),
                    evidence_ref("screenshot", "frame-setup", "待补截图路径或链接", "00:02-00:06", "支撑铺垫到证明转折的截图组。", "时间轴行：铺垫"),
                    evidence_ref("transcript", "subtitle-pass", "待补转写来源", "00:06-00:14", "支撑证明段的字幕或口播证据。", "时间轴行：证明"),
                ],
            ),
            section(
                "Core Mechanism",
                "描述真正起作用的底层机制，而不是只写表层风格。",
                table=blank_table(
                    ["Mechanism Layer", "Observed Pattern", "Why It Works", "Failure Mode If Removed", "Evidence Ref"],
                    [
                        ["视频类型", "", "", "", ""],
                        ["注意力张力", "", "", "", ""],
                        ["证明装置", "", "", "", ""],
                        ["无口播补位方式", "", "", "", ""],
                    ],
                    "机制拆解",
                ),
                evidence_refs=[
                    evidence_ref("video", "primary-video", "待补视频链接", "full-video", "用整条视频区分底层机制与表面包装。", "机制拆解"),
                ],
            ),
            section(
                "可复用公式",
                "只抽取能迁移复用的部分。",
                table=blank_table(
                    ["层级", "观察结果", "是否可复用", "改编说明", "置信度"],
                    [
                        ["钩子逻辑", "", "", "", ""],
                        ["视觉风格", "", "", "", ""],
                        ["证明逻辑", "", "", "", ""],
                        ["CTA 风格", "", "", "", ""],
                    ],
                ),
            ),
            section(
                "Risks And Adaptation Notes",
                "用最实战的三个视角解释爆点逻辑。",
                table=blank_table(
                    ["Lens", "Observed Pattern", "Why It Works", "Adaptation Guardrail", "Evidence Ref"],
                    [
                        ["开头钩子", "", "", "", ""],
                        ["转化节奏", "", "", "", ""],
                        ["视觉风格", "", "", "", ""],
                    ],
                    "爆点解读",
                ),
                evidence_refs=[
                    evidence_ref("video", "primary-video", "待补视频链接", "00:00-00:03", "支撑开头钩子判断的首个视觉回报片段。", "开头钩子解读"),
                    evidence_ref("video", "primary-video", "待补视频链接", "00:03-00:14", "覆盖铺垫、证明与抬升的转化节奏证据。", "转化节奏解读"),
                    evidence_ref("screenshot", "style-board", "待补截图路径或链接", "visual-layer", "展示可复用视觉风格与剪辑处理的截图组。", "视觉风格解读"),
                ],
            ),
            section(
                "BGM And Sensory Layer",
                "说明音频、BGM、字幕密度和剪辑节奏如何影响表现。",
                table=blank_table(
                    ["Element", "Observed", "Strategic Role", "Adaptation Note", "Evidence Ref"],
                    [
                        ["BGM / 音频氛围", "", "", "", ""],
                        ["字幕风格", "", "", "", ""],
                        ["转场节奏", "", "", "", ""],
                        ["停顿 / 留白用法", "", "", "", ""],
                    ],
                ),
                evidence_refs=[
                    evidence_ref("video", "primary-video-audio", "待补视频链接", "audio-layer", "支撑感官层判断的音频、字幕与节奏证据。", "BGM 与感官层"),
                ],
            ),
            section(
                "Production-Spec Handoff",
                "把拆解结果转成可直接复刻或剪辑的蓝图。",
                table=blank_table(
                    ["Beat / Shot", "What Must Happen", "Purpose", "Subtitle / VO Beat", "Proof Block", "Asset / Talent Needed", "Confidence"],
                    [
                        ["1", "", "", "", "", "", ""],
                        ["2", "", "", "", "", "", ""],
                        ["3", "", "", "", "", "", ""],
                        ["4", "", "", "", "", "", ""],
                    ],
                    "复刻镜头顺序",
                ),
            ),
            section(
                "Next Action",
                "给出一条稳妥版和一条激进版改编路径。",
                table=blank_table(
                    ["Path", "What To Keep", "What To Change", "Primary Asset Need", "Primary Risk"],
                    [["稳妥版", "", "", "", ""], ["激进版", "", "", "", ""]],
                ),
            ),
        ],
    },
    "05": {
        "working_context": {
            "inputs": [
                "参考视频",
                "截图或分镜摘要",
                "转写笔记",
                "可选的用户产品信息",
            ],
            "constraints": [
                "如果证据偏薄，必须显式标记为低置信度。",
                "不要臆造隐藏制作细节；不确定字段必须明说。",
            ],
            "requested_outputs": [
                "反推原始制作简报",
                "可生成结构",
                "分镜逐条表",
                "产品适配制作简报",
                "字段级置信度标记",
            ],
        },
        "evidence": [
            {"label": "视觉证据", "detail": "附上画面截图或描述场景顺序。", "source": ""},
            {"label": "音频 / 转写证据", "detail": "粘贴关键口播内容或字幕笔记。", "source": ""},
        ],
        "sections": [
            section(
                "Executive Conclusion",
                "概括这条内容背后的高概率创作意图。",
            ),
            section(
                "Structure Logic",
                "从观察到的成片反推出可直接交给生成器的制作简报结构。",
                table=blank_table(
                    ["Dimension", "Observed Evidence", "Likely Intent", "Generator Handoff", "Confidence"],
                    [
                        ["风格", "", "", "", ""],
                        ["环境", "", "", "", ""],
                        ["语气与节奏", "", "", "", ""],
                        ["镜头", "", "", "", ""],
                        ["灯光", "", "", "", ""],
                        ["角色", "", "", "", ""],
                        ["背景声音", "", "", "", ""],
                        ["转场 / 剪辑", "", "", "", ""],
                    ],
                    "反推原始制作简报结构",
                ),
            ),
            section(
                "Core Mechanism",
                "说明这份反推简报为什么可能有效，以及哪些部分仍是推断。",
                table=blank_table(
                    ["Creative Layer", "Why It Likely Works", "What Evidence Supports It", "Asset Dependency", "Confidence"],
                    [
                        ["钩子设计", "", "", "", ""],
                        ["证明设计", "", "", "", ""],
                        ["节奏设计", "", "", "", ""],
                        ["转化设计", "", "", "", ""],
                    ],
                ),
            ),
            section(
                "Reusable Formula",
                "把反推原版 prompt 或制作简报写成生成器可直接消费的结构。",
                table=blank_table(
                    ["Block", "Prompt / Brief Content", "Generator Handoff Field", "Confidence", "Evidence Ref"],
                    [
                        ["风格", "", "", "", ""],
                        ["环境", "", "", "", ""],
                        ["语气与节奏", "", "", "", ""],
                        ["镜头", "", "", "", ""],
                        ["灯光", "", "", "", ""],
                        ["角色", "", "", "", ""],
                        ["背景声音", "", "", "", ""],
                        ["转场 / 剪辑", "", "", "", ""],
                    ],
                    "可直接生成的制作简报",
                ),
            ),
            section(
                "Risks And Adaptation Notes",
                "按分镜描述结构，并指出哪些推断仍然偏弱。",
                table=blank_table(
                    ["Shot", "Duration", "Scene / Subject", "Action", "Voiceover / Overlay", "Purpose", "Asset Need", "Generator Handoff", "Confidence"],
                    [
                        ["1", "", "", "", "", "", "", "", ""],
                        ["2", "", "", "", "", "", "", "", ""],
                        ["3", "", "", "", "", "", "", "", ""],
                        ["4", "", "", "", "", "", "", "", ""],
                    ],
                    "分镜逐条表",
                ),
            ),
            section(
                "Next Action",
                "如果已有用户产品，就明确这份简报该如何改写到该产品上。",
                table=blank_table(
                    ["Adaptation Layer", "Keep From Reference", "Rewrite For Product", "Generator Handoff Field", "Asset / Talent Dependency", "Open Risk"],
                    [
                        ["钩子", "", "", "", "", ""],
                        ["证明", "", "", "", "", ""],
                        ["场景 / 人物", "", "", "", "", ""],
                        ["CTA", "", "", "", "", ""],
                    ],
                    "产品适配制作简报",
                ),
            ),
            section(
                "Production-Spec Handoff",
                "让这份简报无需再做二次分析，就能直接给生成器或剪辑执行。",
                table=blank_table(
                    ["Delivery Block", "What Must Be Finalized", "Who Uses It", "Blocking Gap", "Next Owner"],
                    [
                        ["原始制作简报结构", "", "", "", ""],
                        ["分镜逐条表", "", "", "", ""],
                        ["产品适配简报", "", "", "", ""],
                        ["素材 / 人员清单", "", "", "", ""],
                    ],
                    "生成器 / 剪辑交接表",
                ),
            ),
        ],
    },
    "06": {
        "working_context": {
            "inputs": [
                "Competitor product list",
                "Links, IDs, or screenshots",
                "Optional price / rating / sales signals",
                "Fallback evidence when no TikTok Shop API exists: listing screenshots, PDP snapshots, review exports, or manual notes",
            ],
            "constraints": [
                "If structured data is incomplete, define the schema first and flag missing fields.",
                "Do not leave the scene empty just because Shop API data is unavailable; switch to a fallback snapshot workflow.",
            ],
            "requested_outputs": [
                "Competitor board schema",
                "Daily / weekly review checklist",
                "Anomaly interpretation guide",
                "Fallback evidence capture SOP",
            ],
        },
        "evidence": [
            {"label": "Competitor list", "detail": "Paste every tracked product and its platform / marketplace context.", "source": ""},
        ],
        "sections": [
            section(
                "Executive Conclusion",
                "Summarize what the dashboard should help the operator notice.",
            ),
            section(
                "Objects To Track",
                "Build the competitor dashboard schema.",
                table=blank_table(
                    ["Competitor Product", "Platform", "Core Offer", "Price", "Rating Signal", "Review Cadence"],
                    [["", "", "", "", "", ""], ["", "", "", "", "", ""], ["", "", "", "", "", ""]],
                    "Competitor Board Schema",
                ),
            ),
            section(
                "Why They Matter",
                "Explain which changes deserve attention.",
                table=blank_table(
                    ["Change Type", "What It Might Mean", "Commercial Importance", "Follow-up"],
                    [
                        ["Price drop", "", "", ""],
                        ["Rating shift", "", "", ""],
                        ["Creative update", "", "", ""],
                        ["Offer / bundle change", "", "", ""],
                    ],
                ),
            ),
            section(
                "Fields To Capture Next Time",
                "Define missing fields to improve future monitoring.",
                bullets=[
                    "What fields are mandatory from the next tracking cycle onward?",
                    "Which optional fields create stronger competitor context?",
                    "Which fields can be recovered manually when TikTok Shop API data is missing?",
                ],
            ),
            section(
                "Fallback Mode",
                "Explain how to run the board without TikTok Shop API access.",
                table=blank_table(
                    ["Evidence Source", "Minimum Field Set", "Operator Effort", "When To Use"],
                    [
                        ["Listing screenshot", "Title, price, promo badge", "Low", "Fast weekly scan"],
                        ["Product detail page snapshot", "Variant, rating, review count", "Medium", "Deeper audit"],
                        ["Review export or screenshots", "Complaint themes, trust cues", "Medium", "Message or quality shift check"],
                        ["Manual note row", "Observed change and date", "Low", "When platform fields are unavailable"],
                    ],
                    "No-API Fallback Sources",
                ),
            ),
            section(
                "Next Action",
                "Leave a reusable review routine.",
                numbered=[
                    "Refresh each tracked product on the chosen cadence.",
                    "Separate noise from meaningful commercial changes.",
                    "Escalate only when the change alters pricing, trust, or message position.",
                ],
            ),
        ],
    },
    "07": {
        "working_context": {
            "inputs": [
                "Category or product theme",
                "Market",
                "Top content examples",
                "Competitor observations",
                "Title / hashtag set",
            ],
            "constraints": [
                "If evidence is incomplete, avoid a hard go / no-go claim.",
            ],
            "requested_outputs": [
                "Category judgment",
                "Keyword decision table",
                "Hot angle map",
                "Saturation notes",
                "Opportunity notes",
                "Recommendation",
            ],
        },
        "evidence": [
            {"label": "Category evidence set", "detail": "Collect top videos, product examples, and search observations.", "source": ""},
        ],
        "sections": [
            section(
                "Executive Conclusion",
                "State whether the category looks attractive and why.",
            ),
            section(
                "High-Level Judgment",
                "Turn the category read into an operator judgment.",
                table=blank_table(
                    ["Dimension", "Judgment", "Evidence", "Decision Strength"],
                    [
                        ["Demand visibility", "", "", ""],
                        ["Angle saturation", "", "", ""],
                        ["Commercial seriousness", "", "", ""],
                        ["Entry attractiveness", "", "", ""],
                    ],
                ),
            ),
            section(
                "Evidence Clusters",
                "Group the strongest patterns in the market.",
                table=blank_table(
                    ["Keyword", "Content Heat", "Product Performance", "Decision", "Why"],
                    [["", "", "", "", ""], ["", "", "", "", ""], ["", "", "", "", ""]],
                    "Keyword Decision Table",
                ),
            ),
            section(
                "Recommended Action",
                "Turn the category read into a decision.",
                table=blank_table(
                    ["Cluster", "What Repeats", "Implication"],
                    [
                        ["Hot angles", "", ""],
                        ["Overused angles", "", ""],
                        ["Underserved need", "", ""],
                        ["Audience cue", "", ""],
                    ],
                    "Category Pattern Clusters",
                ),
            ),
            section(
                "Open Questions",
                "List what still needs verification before stronger commitment.",
                table=blank_table(
                    ["Decision Surface", "Answer", "Why"],
                    [["Do", "", ""], ["Do Not Do", "", ""], ["Priority Do", "", ""]],
                    "Actionable Decision Surface",
                ),
            ),
        ],
    },
    "08": {
        "working_context": {
            "inputs": [
                "Comments from 2+ products",
                "Market",
                "Product positioning goal",
                "Optional price-band notes",
            ],
            "constraints": [
                "If comment volume is light, mark findings as provisional.",
            ],
            "requested_outputs": [
                "购买因素提炼",
                "Praise keyword synthesis",
                "Complaint pain-point synthesis",
                "Price-band difference view",
                "Persona summary",
                "Selection and content implications",
            ],
        },
        "evidence": [
            {"label": "Comment pool", "detail": "Paste comments by product, not mixed together.", "source": ""},
        ],
        "sections": [
            section(
                "Executive Conclusion",
                "Summarize what these comments reveal about the category buyer.",
            ),
            section(
                "High-Level Judgment",
                "State the strongest demand-side insight.",
                table=blank_table(
                    ["Source Product", "Price Band", "Volume", "Primary Purchase Trigger", "Primary Complaint"],
                    [["", "", "", "", ""], ["", "", "", "", ""], ["", "", "", "", ""]],
                    "Source Product Summary",
                ),
            ),
            section(
                "Evidence Clusters",
                "Cluster repeated user language across products.",
                table=blank_table(
                    ["Cluster Type", "Repeated Phrase / Theme", "Source Product", "What It Suggests", "Product / Content Implication"],
                    [
                        ["购买因素", "", "", "", ""],
                        ["好评关键词", "", "", "", ""],
                        ["差评痛点", "", "", "", ""],
                        ["信任信号", "", "", "", ""],
                    ],
                    "Comment Signal Clusters",
                ),
                evidence_refs=[
                    evidence_ref("comment", "product-a-thread-1", "paste-comment-source", "comment-thread", "Repeated buyer phrase from one product's comment thread.", "Purchase-factor cluster"),
                    evidence_ref("comment", "product-b-thread-2", "paste-comment-source", "comment-thread", "Negative or complaint phrasing repeated across multiple comments.", "Complaint cluster"),
                    evidence_ref("comment", "product-c-reply-1", "paste-comment-source", "reply-chain", "Reply-chain pattern revealing trust or objection handling.", "Trust-signal cluster"),
                ],
            ),
            section(
                "Recommended Action",
                "Turn the user language into next decisions.",
                table=blank_table(
                    ["Decision Area", "Recommendation", "Why", "Base Value Or Improvement Opportunity?"],
                    [
                        ["产品方向", "", "", ""],
                        ["卖点与定位", "", "", ""],
                        ["脚本语言", "", "", ""],
                        ["证明内容", "", "", ""],
                    ],
                ),
            ),
            section(
                "Open Questions",
                "List missing evidence or weak conclusions.",
                table=blank_table(
                    ["Price Band", "Repeated Driver", "Repeated Complaint", "Implication"],
                    [["", "", "", ""], ["", "", "", ""], ["", "", "", ""]],
                    "价格带差异",
                ),
            ),
        ],
    },
    "09": {
        "working_context": {
            "inputs": [
                "Reference video or breakdown",
                "User product details",
                "Selling points",
                "Target audience / market",
            ],
            "constraints": [
                "Keep the underlying logic, not literal copying.",
                "Do not reuse branded phrasing, proof claims, or signature creator cues without rewriting them for the new product.",
            ],
            "requested_outputs": [
                "Replication brief",
                "Adapted hook",
                "Adapted proof sequence",
                "Shot order",
                "Optional voiceover draft",
                "Production handoff",
            ],
        },
        "evidence": [
            {"label": "Reference logic", "detail": "Paste the reference video link or teardown notes.", "source": ""},
            {"label": "User product facts", "detail": "Add product offer, selling points, and constraints.", "source": ""},
            {"label": "Available asset / talent reality", "detail": "List whether the user has founder footage, UGC talent, product close-ups, before-after proof, or only still assets.", "source": ""},
        ],
        "sections": [
            section(
                "Executive Conclusion",
                "Summarize the strongest transferable logic from the reference.",
            ),
            section(
                "Target",
                "Define the goal of the adapted version.",
                table=blank_table(
                    ["Field", "Answer", "Why It Matters"],
                    [
                        ["Target audience", "", ""],
                        ["Conversion goal", "", ""],
                        ["Reference asset", "", ""],
                        ["User product", "", ""],
                    ],
                ),
            ),
            section(
                "Audience",
                "Describe the audience and what they need to believe.",
                bullets=[
                    "What belief from the reference still needs to be created for the new product?",
                    "What objection or doubt must the adapted version remove faster than the original?",
                ],
            ),
            section(
                "Message",
                "Rewrite the hook and proof logic for the user's product.",
                table=blank_table(
                    ["Layer", "Reference Logic", "Adapted Version", "Required Product Evidence"],
                    [
                        ["Hook", "", "", ""],
                        ["Problem framing", "", "", ""],
                        ["Proof device", "", "", ""],
                        ["Close / CTA", "", "", ""],
                    ],
                ),
            ),
            section(
                "Structure",
                "给出可以直接执行的镜头顺序。",
                table=blank_table(
                    ["Shot / Beat", "What Happens", "Purpose", "Asset / Talent Needed", "Line / Overlay", "Dependency / Risk"],
                    [["1", "", "", "", "", ""], ["2", "", "", "", "", ""], ["3", "", "", "", "", ""], ["4", "", "", "", "", ""]],
                    "Replication Shot Order",
                ),
            ),
            section(
                "Creative Constraints",
                "列出哪些不能照抄，哪些必须按用户产品重写。",
                table=blank_table(
                    ["Constraint", "Keep / Change", "Reason", "Owner / Check"],
                    [
                        ["Visual identity", "", "", ""],
                        ["Claim language", "", "", ""],
                        ["Proof style", "", "", ""],
                        ["CTA wording", "", "", ""],
                    ],
                    "Adaptation Guardrails",
                ),
            ),
            section(
                "Production Handoff",
                "给拍摄或提示词执行方留下一张清晰交接表。",
                table=blank_table(
                    ["Handoff Item", "Locked Decision", "Owner", "Blocking Risk"],
                    [
                        ["Hook direction", "", "", ""],
                        ["Proof asset", "", "", ""],
                        ["On-screen line / overlay", "", "", ""],
                        ["CTA execution", "", "", ""],
                    ],
                ),
            ),
            section(
                "Next Action",
                "State whether this brief is ready for scripting, filming, or prompting.",
                numbered=[
                    "Confirm the product proof that will replace the reference proof.",
                    "Lock the adapted shot order and overlay copy.",
                    "Move this brief into scripting, filming, or prompt generation.",
                ],
            ),
        ],
    },
    "10": {
        "working_context": {
            "inputs": [
                "Product images or product description",
                "Selling points",
                "Target audience",
                "Market language",
            ],
            "constraints": [
                "If images are missing, mark visual sections as pending.",
                "Do not invent footage, talent, or usage scenes the current asset set cannot support.",
            ],
            "requested_outputs": [
                "Video concept",
                "Shot structure",
                "Voiceover structure",
                "Style keywords",
                "Test variables",
                "Production handoff",
            ],
        },
        "evidence": [
            {"label": "Product asset set", "detail": "List the available images, angles, or missing visual gaps.", "source": ""},
            {"label": "Missing visual gaps", "detail": "Call out which claims, demos, or scene transitions cannot be supported by the current asset set.", "source": ""},
        ],
        "sections": [
            section(
                "Executive Conclusion",
                "State the best video concept to pursue from image-only inputs.",
            ),
            section(
                "Target",
                "Clarify the video goal and context.",
                table=blank_table(
                    ["Field", "Answer", "Why It Matters"],
                    [
                        ["Audience", "", ""],
                        ["Market", "", ""],
                        ["Conversion goal", "", ""],
                        ["Video type", "", ""],
                    ],
                ),
            ),
            section(
                "Audience",
                "Describe what the audience must feel or understand quickly.",
                bullets=[
                    "What should the viewer understand in the first 2 seconds?",
                    "What trust signal must the image-only asset set communicate?",
                ],
            ),
            section(
                "Message",
                "Define the core promise and proof path.",
                table=blank_table(
                    ["Layer", "Draft", "Supported By Which Asset", "Missing Proof?"],
                    [
                        ["Core promise", "", "", ""],
                        ["Primary proof", "", "", ""],
                        ["Secondary proof", "", "", ""],
                        ["CTA", "", "", ""],
                    ],
                    "Image-Only Messaging Brief",
                ),
            ),
            section(
                "Structure",
                "Map the shot flow from opening to close.",
                table=blank_table(
                    ["Beat", "Visual Use", "Voiceover / Overlay", "Purpose", "Asset / Talent Source", "Missing Asset?"],
                    [["Hook", "", "", "", "", ""], ["Proof 1", "", "", "", "", ""], ["Proof 2", "", "", "", "", ""], ["Close", "", "", "", "", ""]],
                ),
            ),
            section(
                "Creative Constraints",
                "Specify style keywords, rendering guardrails, and what to avoid.",
                table=blank_table(
                    ["Constraint Type", "Detail", "Risk If Ignored", "Fix Path"],
                    [["Visual style", "", "", ""], ["Tone", "", "", ""], ["Must show", "", "", ""], ["Must avoid", "", "", ""]],
                    "Render Guardrails",
                ),
            ),
            section(
                "Production Handoff",
                "State what the editing, design, or prompt-render team can execute now.",
                table=blank_table(
                    ["Handoff Item", "Locked Decision", "Open Gap", "Owner"],
                    [
                        ["Hook frame", "", "", ""],
                        ["Primary proof beat", "", "", ""],
                        ["VO / overlay draft", "", "", ""],
                        ["CTA treatment", "", "", ""],
                    ],
                ),
            ),
            section(
                "Next Action",
                "List the next two test variables to try.",
                table=blank_table(
                    ["Test Variable", "Why Test It First", "What Asset Change Is Needed"],
                    [["Hook framing", "", ""], ["Proof order", "", ""], ["CTA treatment", "", ""]],
                ),
            ),
        ],
    },
    "11": {
        "working_context": {
            "inputs": [
                "Category or product",
                "Keyword set",
                "Target market",
                "Testing goal",
            ],
            "constraints": [
                "If no live candidates exist, output the pipeline and intake checklist anyway.",
            ],
            "requested_outputs": [
                "Candidate ladder",
                "Replication brief bank",
                "Production queue",
                "Testing recommendation",
                "Weekly runbook",
            ],
        },
        "evidence": [
            {"label": "Discovery pool", "detail": "Paste the hot-video shortlist feeding the pipeline.", "source": ""},
        ],
        "sections": [
            section(
                "Executive Conclusion",
                "State what this replication pipeline should optimize for.",
            ),
            section(
                "Core Invariant",
                "Define the operating principle that stays constant.",
                table=blank_table(
                    ["Invariant", "Rule", "Why It Cannot Drift"],
                    [
                        ["Entry threshold", "", ""],
                        ["Teardown lens", "", ""],
                        ["Queue standard", "", ""],
                    ],
                ),
            ),
            section(
                "Variable Matrix",
                "Map the pipeline from discovery to production.",
                table=blank_table(
                    ["Stage", "Input", "Decision Rule", "Asset Need", "Owner", "Output", "SLA / Cadence"],
                    [
                        ["Discovery", "", "", "", "", "", ""],
                        ["Shortlist", "", "", "", "", "", ""],
                        ["Teardown", "", "", "", "", "", ""],
                        ["Replication brief", "", "", "", "", "", ""],
                        ["Production queue", "", "", "", "", "", ""],
                    ],
                    "Pipeline Stages",
                ),
            ),
            section(
                "Expected Effect",
                "Explain what this pipeline should improve operationally.",
                bullets=[
                    "Which step becomes faster or more selective after this pipeline exists?",
                    "Where should weak candidates get filtered out before wasting production time?",
                ],
            ),
            section(
                "What To Learn",
                "State what each cycle should teach the operator.",
                table=blank_table(
                    ["Cycle Question", "Why It Matters", "How To Measure", "What Decision It Changes", "If Confirmed", "If Rejected"],
                    [["", "", "", "", "", ""], ["", "", "", "", "", ""], ["", "", "", "", "", ""]],
                ),
            ),
            section(
                "Execution Handoff",
                "Define the artifacts and owners needed to keep the pipeline moving each week.",
                table=blank_table(
                    ["Queue Artifact", "Who Owns It", "Ready When", "Blocking Risk"],
                    [
                        ["Discovery shortlist", "", "", ""],
                        ["Teardown packet", "", "", ""],
                        ["Replication brief bank", "", "", ""],
                        ["Production queue", "", "", ""],
                    ],
                ),
            ),
            section(
                "Next Action",
                "Give the first weekly implementation sequence.",
                numbered=[
                    "Run one discovery pass and force-rank candidates with the entry rule.",
                    "Deep-teardown only the shortlisted videos.",
                    "Move only the strongest replication briefs into the production queue.",
                ],
            ),
        ],
    },
    "12": {
        "working_context": {
            "inputs": [
                "One product",
                "One target market",
                "Product images or selling points",
            ],
            "constraints": [
                "Keep one invariant message while varying style.",
            ],
            "requested_outputs": [
                "Style matrix",
                "Hook variants",
                "Proof variants",
                "Testing order",
                "Variant handoff",
            ],
        },
        "evidence": [
            {"label": "Product brief", "detail": "Include key selling points, constraints, and available assets.", "source": ""},
        ],
        "sections": [
            section(
                "Executive Conclusion",
                "State which style family should likely win first and why.",
            ),
            section(
                "Core Invariant",
                "Describe the one thing that must stay constant across all variants.",
                table=blank_table(
                    ["Invariant Type", "Locked Element", "Why It Must Stay Fixed"],
                    [["Core message", "", ""], ["Product truth", "", ""], ["Target outcome", "", ""]],
                ),
            ),
            section(
                "Variable Matrix",
                "Build the full testing matrix.",
                table=blank_table(
                    ["Style", "Audience Lens", "Hook", "Proof Device", "Visual Style", "CTA", "Asset Need", "Production Complexity", "Primary Hypothesis", "Why Test It"],
                    [
                        ["Style 1", "", "", "", "", "", "", "", "", ""],
                        ["Style 2", "", "", "", "", "", "", "", "", ""],
                        ["Style 3", "", "", "", "", "", "", "", "", ""],
                        ["Style 4", "", "", "", "", "", "", "", "", ""],
                    ],
                    "Multi-Style Testing Matrix",
                ),
            ),
            section(
                "Expected Effect",
                "Explain what each style variation is expected to change.",
                table=blank_table(
                    ["Variant", "Expected Attention Shift", "Expected Conversion Shift", "Main Risk"],
                    [["Style 1", "", "", ""], ["Style 2", "", "", ""], ["Style 3", "", "", ""], ["Style 4", "", "", ""]],
                ),
            ),
            section(
                "What To Learn",
                "Define the learning agenda from the matrix.",
                table=blank_table(
                    ["Variant", "Main Hypothesis", "Success Signal", "What It Teaches", "If Confirmed", "If Rejected"],
                    [["Style 1", "", "", "", "", ""], ["Style 2", "", "", "", "", ""], ["Style 3", "", "", "", "", ""], ["Style 4", "", "", "", "", ""]],
                ),
            ),
            section(
                "Execution Handoff",
                "State what each first-wave variant needs before it can go live.",
                table=blank_table(
                    ["Variant", "First Asset Need", "Owner", "Ready For Test When"],
                    [["Style 1", "", "", ""], ["Style 2", "", "", ""], ["Style 3", "", "", ""], ["Style 4", "", "", ""]],
                ),
            ),
            section(
                "Next Action",
                "Rank the order of testing and explain why.",
                table=blank_table(
                    ["Priority", "Variant", "Why It Goes Now"],
                    [["1", "", ""], ["2", "", ""], ["3", "", ""], ["4", "", ""]],
                ),
            ),
        ],
    },
    "13": {
        "working_context": {
            "inputs": [
                "One product",
                "2+ target markets",
                "Source concept or script",
                "Local audience notes",
            ],
            "constraints": [
                "Localize for conversion, not only literal translation.",
                "Do not localize into a market without stating what evidence supports the adaptation.",
            ],
            "requested_outputs": [
                "Shared invariant",
                "Per-market notes",
                "Per-market hook and script direction",
                "Per-market visual cues",
                "Market handoff",
            ],
        },
        "evidence": [
            {"label": "Source concept", "detail": "Add the original script, product concept, or winning angle.", "source": ""},
            {"label": "Local reviewer context", "detail": "Add any native-speaker, creator, or market-review notes that can validate localization choices.", "source": ""},
        ],
        "sections": [
            section(
                "Executive Conclusion",
                "Summarize the localization strategy across markets.",
            ),
            section(
                "Target",
                "State what remains fixed versus what changes by market.",
                table=blank_table(
                    ["Layer", "Invariant", "Needs Localization?", "Why"],
                    [
                        ["Core product promise", "", "No", ""],
                        ["Hook wording", "", "Yes", ""],
                        ["Talent / scene cue", "", "Yes", ""],
                        ["CTA tone", "", "Yes", ""],
                    ],
                ),
            ),
            section(
                "Audience",
                "Describe how audience expectation changes across markets.",
                table=blank_table(
                    ["Market", "Viewer Expectation", "Key Trigger", "Key Risk"],
                    [["", "", "", ""], ["", "", "", ""], ["", "", "", ""]],
                ),
            ),
            section(
                "Message",
                "Adapt the hook and message by market.",
                table=blank_table(
                    ["Market", "Audience Cue", "Hook Direction", "Language / Tone", "Proof Angle", "Avoid"],
                    [["", "", "", "", "", ""], ["", "", "", "", "", ""], ["", "", "", "", "", ""]],
                    "Per-Market Localization Grid",
                ),
            ),
            section(
                "Structure",
                "Describe any structural changes by market if needed.",
                table=blank_table(
                    ["Market", "Opening Beat", "Middle Proof", "Close / CTA", "Visual Cue", "Talent / Asset Need", "Localization Dependency"],
                    [["", "", "", "", "", "", ""], ["", "", "", "", "", "", ""], ["", "", "", "", "", "", ""]],
                ),
            ),
            section(
                "Creative Constraints",
                "List cultural, visual, or language cautions per market.",
                table=blank_table(
                    ["Market", "Do Not Use", "Must Adapt", "Open Risk", "Review Owner"],
                    [["", "", "", "", ""], ["", "", "", "", ""], ["", "", "", "", ""]],
                ),
            ),
            section(
                "Production Handoff",
                "State which markets are ready for scripting and which still need validation.",
                table=blank_table(
                    ["Market", "What Is Ready To Script", "What Still Needs Native Review", "Owner"],
                    [["", "", "", ""], ["", "", "", ""], ["", "", "", ""]],
                ),
            ),
            section(
                "Next Action",
                "State what is ready for localized scripting versus what still needs research.",
                numbered=[
                    "Lock the invariant product truth once for all markets.",
                    "Write each market's hook and proof angle separately.",
                    "Move only the markets with enough local evidence into scripting.",
                ],
            ),
        ],
    },
    "14": {
        "working_context": {
            "inputs": [
                "Product description",
                "Optional product images",
                "Selling points",
                "Target market",
            ],
            "constraints": [
                "If images are missing, keep this as blueprint plus asset requirements.",
                "Flag which assets depend on unavailable footage, design time, or product proof before sequencing production.",
            ],
            "requested_outputs": [
                "Asset list",
                "Purpose of each asset",
                "Creative direction",
                "Production priority",
                "Production handoff",
            ],
        },
        "evidence": [
            {"label": "Launch context", "detail": "Add platform, market, and current asset gaps.", "source": ""},
        ],
        "sections": [
            section(
                "Executive Conclusion",
                "State the minimum viable asset family for launch.",
            ),
            section(
                "Core Invariant",
                "Define the shared creative direction across all assets.",
                table=blank_table(
                    ["Invariant", "Definition", "Why It Must Stay Consistent"],
                    [["Core promise", "", ""], ["Visual code", "", ""], ["Offer logic", "", ""]],
                ),
            ),
            section(
                "Variable Matrix",
                "Map each asset to its job.",
                table=blank_table(
                    ["Asset", "Purpose", "Primary Message", "Format / Ratio", "Owner / Tool", "Dependency / Blocking Risk", "Priority"],
                    [
                        ["Main image", "", "", "", "", "", ""],
                        ["Scene image", "", "", "", "", "", ""],
                        ["Benefit image", "", "", "", "", "", ""],
                        ["Detail image", "", "", "", "", "", ""],
                        ["Short video", "", "", "", "", "", ""],
                    ],
                    "Launch Asset Family",
                ),
            ),
            section(
                "Expected Effect",
                "Explain how the asset set works together.",
                bullets=[
                    "Which asset should create first click?",
                    "Which asset should deepen understanding or remove objections?",
                    "Which asset should close the conversion gap?",
                ],
            ),
            section(
                "What To Learn",
                "State what should be learned from launch testing.",
                table=blank_table(
                    ["Asset", "Question", "Success Signal", "What It Changes Next", "If It Wins"],
                    [["Main image", "", "", "", ""], ["Benefit image", "", "", "", ""], ["Short video", "", "", "", ""]],
                ),
            ),
            section(
                "Production Handoff",
                "Leave a concrete asset-family handoff for design and production owners.",
                table=blank_table(
                    ["Asset Family Item", "Ready Spec", "Missing Input", "Owner"],
                    [["Main image", "", "", ""], ["Scene image", "", "", ""], ["Benefit image", "", "", ""], ["Short video", "", "", ""]],
                ),
            ),
            section(
                "Next Action",
                "Give the production order and handoff notes.",
                table=blank_table(
                    ["Priority", "Asset", "Why It Goes First", "Dependency", "Owner"],
                    [["1", "", "", "", ""], ["2", "", "", "", ""], ["3", "", "", "", ""], ["4", "", "", "", ""], ["5", "", "", "", ""]],
                ),
            ),
        ],
    },
    "15": {
        "working_context": {
            "inputs": [
                "Source image text or OCR",
                "Target language",
                "Product context",
                "Target market",
            ],
            "constraints": [
                "Translate for conversion, not literal fidelity alone.",
            ],
            "requested_outputs": [
                "Translated copy",
                "Layout notes",
                "Text hierarchy",
                "Localization cautions",
                "Render handoff",
            ],
        },
        "evidence": [
            {"label": "Source copy blocks", "detail": "List each text block in reading order.", "source": ""},
            {"label": "Layout capture", "detail": "Attach the current image layout or a block map so the localized copy can be sized correctly.", "source": ""},
        ],
        "sections": [
            section(
                "Executive Conclusion",
                "Summarize the localization approach for this image asset.",
            ),
            section(
                "Target",
                "Clarify market, language, and conversion goal.",
                table=blank_table(
                    ["Field", "Answer", "Why It Matters"],
                    [["Target market", "", ""], ["Target language", "", ""], ["Conversion goal", "", ""], ["Asset type", "", ""]],
                ),
            ),
            section(
                "Audience",
                "Describe what the target viewer needs from the copy.",
                bullets=[
                    "What must remain literally accurate?",
                    "What should become more persuasive in the localized version?",
                ],
            ),
            section(
                "Message",
                "Translate each block with hierarchy preserved.",
                table=blank_table(
                    ["Source Block", "Function", "Localized Copy", "Length Risk", "Layout Fit", "Native Review Needed?", "Notes"],
                    [["", "", "", "", "", "", ""], ["", "", "", "", "", "", ""], ["", "", "", "", "", "", ""]],
                    "Localized Copy Grid",
                ),
            ),
            section(
                "Structure",
                "Describe text hierarchy and placement logic.",
                table=blank_table(
                    ["Text Layer", "Priority", "Placement Note", "Can Be Shortened?", "Design Action"],
                    [["Headline", "", "", "", ""], ["Support line", "", "", "", ""], ["CTA", "", "", "", ""]],
                ),
            ),
            section(
                "Creative Constraints",
                "List localization cautions, banned phrasing, and readability notes.",
                table=blank_table(
                    ["Constraint", "Localized Rule", "Reason", "Review Owner"],
                    [["Banned phrasing", "", "", ""], ["Tone guardrail", "", "", ""], ["Layout limit", "", "", ""], ["Readability note", "", "", ""]],
                ),
            ),
            section(
                "Production Handoff",
                "State what the design or rendering team can execute immediately.",
                table=blank_table(
                    ["Handoff Item", "Localized Decision", "Needs Review?", "Owner"],
                    [["Headline block", "", "", ""], ["Support copy", "", "", ""], ["CTA line", "", "", ""], ["Final layout check", "", "", ""]],
                ),
            ),
            section(
                "Next Action",
                "State whether the asset is ready for rendering or needs copy review.",
                numbered=[
                    "Review localized copy against layout length and hierarchy.",
                    "Flag any line that still needs legal or native-speaker review.",
                    "Move the asset into rendering only after the hierarchy is stable.",
                ],
            ),
        ],
    },
    "16": {
        "working_context": {
            "inputs": [
                "Competitor main images",
                "User image or product",
                "Platform and category context",
            ],
            "constraints": [
                "Benchmark what actually influences click, not generic design taste.",
            ],
            "requested_outputs": [
                "Competitor comparison",
                "Design weakness map",
                "Outperform strategy",
                "Revised main-image brief",
                "Design handoff",
            ],
        },
        "evidence": [
            {"label": "Competitor image set", "detail": "Attach each image with basic context if possible.", "source": ""},
            {"label": "User image or product", "detail": "Attach current main image or describe current direction.", "source": ""},
        ],
        "sections": [
            section(
                "Executive Conclusion",
                "State the strongest opportunity to outperform the current competitor set.",
            ),
            section(
                "Target",
                "Clarify the benchmark context.",
                table=blank_table(
                    ["Field", "Answer", "Why It Matters"],
                    [["Platform", "", ""], ["Category", "", ""], ["User asset", "", ""], ["Competitor count", "", ""]],
                ),
            ),
            section(
                "Audience",
                "Describe the click context and viewer expectation.",
                bullets=[
                    "What is the viewer scanning for in this category before they click?",
                    "What category visual code is overused and therefore less likely to win attention?",
                ],
            ),
            section(
                "Message",
                "Compare the competitor approaches.",
                table=blank_table(
                    ["Image / Brand", "Dominant Visual Code", "Likely Click Driver", "Weakness", "What To Keep", "What To Avoid", "Execution Note"],
                    [["", "", "", "", "", "", ""], ["", "", "", "", "", "", ""], ["", "", "", "", "", "", ""]],
                    "Competitor Comparison",
                ),
            ),
            section(
                "Structure",
                "Convert the benchmark into a revised main-image direction.",
                table=blank_table(
                    ["Layer", "New Direction", "Purpose", "Must Be Visible?", "Asset Need"],
                    [["Hero visual", "", "", "", ""], ["Text treatment", "", "", "", ""], ["Offer cue", "", "", "", ""], ["Trust cue", "", "", "", ""]],
                ),
            ),
            section(
                "Creative Constraints",
                "State what the new main image must avoid and what it must emphasize.",
                table=blank_table(
                    ["Constraint", "Emphasize / Avoid", "Reason", "Owner / Check"],
                    [["Category cliche", "", "", ""], ["Clutter risk", "", "", ""], ["Trust risk", "", "", ""], ["Readability risk", "", "", ""]],
                ),
            ),
            section(
                "Production Handoff",
                "Translate the benchmark into a concrete design or image-generation brief.",
                table=blank_table(
                    ["Handoff Item", "Decision", "Owner", "Risk Before Design"],
                    [["Hero concept", "", "", ""], ["Text hierarchy", "", "", ""], ["Offer / trust cue", "", "", ""], ["Final QA lens", "", "", ""]],
                ),
            ),
            section(
                "Next Action",
                "Leave an execution-ready brief for design or generation.",
                numbered=[
                    "Choose the one competitor pattern to borrow and the one to reject.",
                    "Lock the new hero visual and text hierarchy.",
                    "Hand off one outperform brief to design or image generation.",
                ],
            ),
        ],
    },
    "17": {
        "working_context": {
            "inputs": [
                "1 个创作者账号，或同一创作者的多条视频",
                "高表现视频",
                "转写稿",
                "表现备注",
                "可选的发布时间与 hashtag 备注",
            ],
            "constraints": [
                "把创作者个人加成和可迁移公式拆开看。",
            ],
            "requested_outputs": [
                "账号概览",
                "高低互动对比",
                "可重复公式",
                "不可迁移优势",
                "新脚本桥接",
            ],
        },
        "evidence": [
            {"label": "创作者样本集", "detail": "列出该创作者的高表现或代表性视频。", "source": ""},
        ],
        "sections": [
            section(
                "Executive Conclusion",
                "概括这个创作者最稳定、最可复用的赢法。",
            ),
            section(
                "Structure Logic",
                "先做账号速览，再提炼公式。",
                table=blank_table(
                    ["Overview Field", "Observation", "Evidence Ref"],
                    [
                        ["一句话定位", "", ""],
                        ["平均播放", "", ""],
                        ["平均点赞", "", ""],
                        ["平均评论", "", ""],
                        ["平均分享", "", ""],
                        ["爆款率", "", ""],
                        ["更新频率", "", ""],
                    ],
                    "账号速览",
                ),
                evidence_refs=[
                    evidence_ref("creator", "account-summary", "待补账号链接", "账号样本时间窗", "基于样本帖子的账号级基线，包括互动和更新节奏。", "账号速览"),
                ],
            ),
            section(
                "Core Mechanism",
                "先比较高互动与低互动内容，再下公式结论。",
                table=blank_table(
                    ["Comparison Lens", "High-Interaction Pattern", "Low-Interaction Pattern", "Implication", "Evidence Ref"],
                    [
                        ["钩子", "", "", "", ""],
                        ["节奏", "", "", "", ""],
                        ["证明方式", "", "", "", ""],
                        ["CTA 风格", "", "", "", ""],
                        ["视频类型", "", "", "", ""],
                    ],
                    "高低互动对比",
                ),
                evidence_refs=[
                    evidence_ref("video", "creator-top-1", "待补视频链接", "00:00-00:05", "作为正样本对照的高互动视频。", "高互动对比"),
                    evidence_ref("video", "creator-low-1", "待补视频链接", "00:00-00:05", "用于隔离差异的低互动样本。", "低互动对比"),
                ],
            ),
            section(
                "Reusable Formula",
                "提炼可迁移到其他账号或产品上的模式。",
                table=blank_table(
                    ["Layer", "Transferable Pattern", "Why It Transfers", "How To Adapt", "Evidence Ref"],
                    [
                        ["钩子", "", "", "", ""],
                        ["节奏", "", "", "", ""],
                        ["信任建立", "", "", "", ""],
                        ["转化动作", "", "", "", ""],
                    ],
                ),
            ),
            section(
                "Risks And Adaptation Notes",
                "列出依赖创作者个人特质的部分，以及真正值得抄走的公式。",
                table=blank_table(
                    ["Formula Type", "Original Example", "Reusable Template", "Where It Works Best"],
                    [
                        ["钩子公式", "", "", ""],
                        ["钩子公式", "", "", ""],
                        ["节奏模型", "", "", ""],
                        ["CTA 公式", "", "", ""],
                    ],
                    "公式库",
                ),
            ),
            section(
                "Visual And Distribution Signature",
                "记录那些不属于脚本但仍明显影响表现的重复模式。",
                table=blank_table(
                    ["Dimension", "Observed Pattern", "Why It Matters", "Evidence Ref"],
                    [
                        ["视觉风格", "", "", ""],
                        ["BGM / 音频", "", "", ""],
                        ["Hashtag 习惯", "", "", ""],
                        ["发布时间", "", "", ""],
                    ],
                ),
                evidence_refs=[
                    evidence_ref("creator", "distribution-pattern", "待补账号链接", "账号样本时间窗", "在样本集中重复出现的发布时间、hashtag 和音频习惯。", "分发特征"),
                ],
            ),
            section(
                "Next Action",
                "说明如何把这套模式迁移到用户自己的产品或账号。",
                table=blank_table(
                    ["Bridge Step", "What To Borrow", "What To Rewrite", "Risk / Caveat"],
                    [
                        ["新钩子草稿", "", "", ""],
                        ["脚本节奏", "", "", ""],
                        ["证明形式", "", "", ""],
                        ["发布实验", "", "", ""],
                    ],
                    "新脚本承接表",
                ),
            ),
        ],
    },
    "18": {
        "working_context": {
            "inputs": [
                "2 个以上竞品账号",
                "最近帖子或周度帖子清单",
                "如有则附上上周备注",
                "目标市场",
                "周度监控窗口",
            ],
            "constraints": [
                "如果目前只有 1 周数据，应标记为基线周，而不是趋势判断。",
            ],
            "requested_outputs": [
                "分账号周度总结",
                "跨账号横向对比",
                "关键变化",
                "策略变化视角",
                "对用户的影响",
            ],
        },
        "evidence": [
            {"label": "账号周度帖子清单", "detail": "先把帖子按账号和周维度分组。", "source": ""},
        ],
        "sections": [
            section(
                "Executive Conclusion",
                "总结本周被监控竞品账号到底发生了哪些变化。",
            ),
            section(
                "Objects To Track",
                "按账号记录每周产出表现。",
                table=blank_table(
                    ["账号", "发帖量", "本周胜出帖子", "主主题", "爆点信号", "相对上周变化", "策略变化"],
                    [["", "", "", "", "", "", ""], ["", "", "", "", "", "", ""], ["", "", "", "", "", "", ""]],
                    "分账号周度总结",
                ),
            ),
            section(
                "Why They Matter",
                "解释这些变化为什么重要，而不是只罗列现象。",
                table=blank_table(
                    ["观察到的变化", "是谁变了", "为什么重要", "爆点归因", "启发"],
                    [["", "", "", "", ""], ["", "", "", "", ""], ["", "", "", "", ""]],
                    "关键周度变化",
                ),
                evidence_refs=[
                    evidence_ref("account_week", "account-a-week", "待补账号或表格链接", "周观察窗口", "展示账号 A 在该周主要内容或策略变化的周总结。", "周度变化归因"),
                    evidence_ref("video", "breakout-post-1", "待补视频链接", "00:00-00:05", "用于解释账号为什么发生变化的代表性爆点帖子。", "爆点归因"),
                ],
            ),
            section(
                "Fields To Capture Next Time",
                "列出为了更强周对比还缺哪些字段。",
                table=blank_table(
                    ["比较维度", "账号 A", "账号 B", "账号 C", "运营结论"],
                    [["Hook 风格", "", "", "", ""], ["证明方式", "", "", "", ""], ["发帖模式", "", "", "", ""]],
                    "跨账号对比",
                ),
            ),
            section(
                "Next Action",
                "明确本周运营应该做什么响应动作。",
                table=blank_table(
                    ["动作领域", "建议", "紧急度", "策略变化点"],
                    [["继续观察", "", "", ""], ["验证测试", "", "", ""], ["先忽略", "", "", ""]],
                    "本周运营响应",
                ),
            ),
        ],
    },
    "19": {
        "working_context": {
            "inputs": [
                "最近帖子列表",
                "播放、点赞、评论、收藏或分享",
                "帖子标题 / hook",
                "内容类型标签",
                "可选的转化或 ROI 上下文",
            ],
            "constraints": [
                "如果指标不完整，必须把弱结论显式标记出来。",
            ],
            "requested_outputs": [
                "高低表现分组",
                "表现模式总结",
                "高表现特征",
                "低表现特征",
                "下一轮计划",
            ],
        },
        "evidence": [
            {"label": "最近帖子表", "detail": "粘贴最近帖子及其所有可用表现信号。", "source": ""},
        ],
        "sections": [
            section(
                "Executive Conclusion",
                "写出这次账号复盘最重要的一条教训。",
            ),
            section(
                "High-Level Judgment",
                "总结什么在起作用，什么没起作用。",
                table=blank_table(
                    ["表现分组", "模式", "可能原因", "对增长 / ROI 的意义"],
                    [["高表现组", "", "", ""], ["低表现组", "", "", ""], ["暂不下结论", "", "", ""]],
                ),
            ),
            section(
                "Evidence Clusters",
                "按表现模式聚类内容，而不是只按日期排列。",
                table=blank_table(
                    ["聚类", "内容模式", "代表帖子", "共同特征", "信号强度"],
                    [["", "", "", "", ""], ["", "", "", "", ""], ["", "", "", "", ""]],
                    "表现模式聚类",
                ),
                evidence_refs=[
                    evidence_ref("video", "self-top-cluster", "待补视频链接", "聚类观察窗口", "代表最强表现模式的一组样本帖子。", "高表现模式聚类"),
                    evidence_ref("video", "self-low-cluster", "待补视频链接", "聚类观察窗口", "展示低表现模式的一组代表性弱样本帖子。", "低表现模式聚类"),
                ],
            ),
            section(
                "Recommended Action",
                "把复盘翻译成多做 / 少做 / 停止规则。",
                table=blank_table(
                    ["规则类型", "建议", "原因", "下轮负责人 / 检查项"],
                    [["多做", "", "", ""], ["少做", "", "", ""], ["停止", "", "", ""], ["下轮测试", "", "", ""]],
                ),
            ),
            section(
                "Open Questions",
                "列出哪些缺失数据阻碍了更强的优化判断。",
                table=blank_table(
                    ["下轮测试", "假设", "具体改什么", "成功信号"],
                    [["", "", "", ""], ["", "", "", ""], ["", "", "", ""]],
                    "下轮测试计划",
                ),
            ),
        ],
    },
}


SCENE_INTAKE = {
    "01": {
        "minimum_evidence": ["One keyword", "At least 5 candidate videos, links, or screenshots"],
        "ideal_evidence": ["15-30 candidates with basic metrics", "Search-result screenshots", "Market and audience note", "Sort order and shop-cart filter state"],
        "ready_checklist": ["Candidate set is from one market", "At least basic performance signals exist", "Useful-for tags can be assigned", "Publish window and sort rule are explicit"],
    },
    "02": {
        "minimum_evidence": ["One category", "One market", "Initial keyword set"],
        "ideal_evidence": ["3-10 patrol keywords", "Prior daily notes", "Preferred alert conditions", "Append-to-history rule", "Fixed patrol time", "Whether rows append into one long-lived sheet"],
        "ready_checklist": ["Cadence is defined", "Tracked fields are agreed", "Manual vs automated patrol mode is explicit", "New / rising / abnormal signals are separated", "Scene 03 escalation rules are explicit"],
    },
    "03": {
        "minimum_evidence": ["One keyword or topic", "A candidate pool to rank"],
        "ideal_evidence": ["10+ candidate videos", "Links plus screenshots or transcript notes", "Target product or niche", "Explicit top-sample rule"],
        "ready_checklist": ["Shortlist criteria are clear", "Top 3-5 videos have enough evidence for teardown", "Market is not mixed", "Per-video and common-pattern deliverables are both expected"],
    },
    "04": {
        "minimum_evidence": ["One video link or storyboard summary"],
        "ideal_evidence": ["下载 JSON 或 capture detail", "转写稿或字幕笔记", "按节拍截图", "基础表现上下文", "音频或 BGM 线索"],
        "ready_checklist": ["能够重建 hook、证明段与收口段", "至少已知 1 个改编目标", "时间轴表可以在不臆造缺失段落的前提下补完", "有口播 / 无口播路径已明确"],
    },
    "05": {
        "minimum_evidence": ["1 条视频或 1 份视觉摘要"],
        "ideal_evidence": ["转写稿", "逐帧笔记", "待适配的用户产品", "场景或人物备注", "镜头时长与节奏备注"],
        "ready_checklist": ["视觉证据足以推断镜头语言", "若证据偏薄，低置信度缺口已显式标出", "反推 brief 可以明确拆成原版与适配版", "generator-ready handoff 字段可输出"],
    },
    "06": {
        "minimum_evidence": ["3+ competitor products or listings"],
        "ideal_evidence": ["Price, rating, and offer snapshots", "Past tracking notes", "Desired review cadence", "Listing or PDP screenshots when API access is absent"],
        "ready_checklist": ["Each product has a stable identifier", "Fields to track are defined", "Change interpretation rules are explicit", "Fallback evidence path is explicit if Shop API data is unavailable"],
    },
    "07": {
        "minimum_evidence": ["One category or product theme", "Some visible market examples"],
        "ideal_evidence": ["Top content examples", "Competitor product set", "Keyword map by market", "Title and hashtag clues"],
        "ready_checklist": ["Demand evidence exists", "Saturation read is backed by examples", "Recommendation strength matches evidence depth", "Keyword-level decisioning is possible"],
    },
    "08": {
        "minimum_evidence": ["Comments from at least 2 products"],
        "ideal_evidence": ["20-40 comments per product", "Market context", "Positioning goal", "Price-band context", "购买型评论语言样本"],
        "ready_checklist": ["Comments stay grouped by product", "Repeated phrases can be quoted", "Low-volume caveats are explicit", "Source product labels survive the merge", "基础价值与改进机会可以分开"],
    },
    "09": {
        "minimum_evidence": ["Reference video logic", "User product basics"],
        "ideal_evidence": ["产品图片", "卖点", "目标人群与市场备注"],
        "ready_checklist": ["核心不变量已识别", "照抄风险已列出", "适配后的 hook 与镜头路径已经可写"],
    },
    "10": {
        "minimum_evidence": ["Product description or product images"],
        "ideal_evidence": ["多角度素材", "卖点", "目标人群", "期望风格"],
        "ready_checklist": ["视频目标清楚", "视觉缺口已标出", "可以基于现有素材设计 hook 与证明段"],
    },
    "11": {
        "minimum_evidence": ["One category or product and a testing goal"],
        "ideal_evidence": ["Hot-video shortlist", "Product assets", "Weekly operating cadence"],
        "ready_checklist": ["Discovery and shortlist stages are separated", "Replication gate is defined", "Output queue can be prioritized"],
    },
    "12": {
        "minimum_evidence": ["One product", "One market", "One core message"],
        "ideal_evidence": ["Product images", "Selling points", "Audience segments", "Style constraints"],
        "ready_checklist": ["Invariant is locked", "At least 4 distinct styles can be tested", "Success signals are defined per variant"],
    },
    "13": {
        "minimum_evidence": ["One product", "At least 2 target markets"],
        "ideal_evidence": ["源脚本或创意概念", "本地受众备注", "视觉素材集"],
        "ready_checklist": ["核心不变量已与本地化层分开", "每个市场都有清晰的 hook 方向", "如有需要，每个市场都已有 avoid-list"],
    },
    "14": {
        "minimum_evidence": ["Product description"],
        "ideal_evidence": ["Product images", "Selling points", "Platform constraints", "Launch priority"],
        "ready_checklist": ["Asset family scope is fixed", "Each asset has one job", "Production priority order is explicit"],
    },
    "15": {
        "minimum_evidence": ["Source image text or OCR", "Target language"],
        "ideal_evidence": ["Image layout", "Product context", "Market note", "Conversion goal"],
        "ready_checklist": ["Text hierarchy is recoverable", "Literal vs persuasive text is separated", "Layout notes exist for rendering"],
    },
    "16": {
        "minimum_evidence": ["2+ competitor images", "User image or product"],
        "ideal_evidence": ["Platform click context", "Category norms", "Known strengths or weaknesses"],
        "ready_checklist": ["Competitor set is comparable", "Likely click drivers are described", "Outperform brief is sharper than generic design feedback"],
    },
    "17": {
        "minimum_evidence": ["1 个创作者账号，或同一创作者的多条视频"],
        "ideal_evidence": ["高表现视频", "转写稿", "表现备注", "发布时间或 hashtag 备注"],
        "ready_checklist": ["重复模式已在多条视频中出现", "高互动与低互动样本可以对比", "创作者专属优势已被分离", "能够给出面向用户产品的适配路径"],
    },
    "18": {
        "minimum_evidence": ["2 个以上竞品账号", "1 周帖子批次"],
        "ideal_evidence": ["上周备注", "逐帖表现上下文", "目标市场", "1 个矩阵里包含 3-5 个账号", "2 周以上周度快照"],
        "ready_checklist": ["帖子已按账号与周维度分组", "可以明确写出相对上周的变化", "可以给每周响应动作排优先级", "可以进行跨账号横向对比", "baseline week 与多周趋势可以区分"],
    },
    "19": {
        "minimum_evidence": ["最近帖子列表", "每条帖子至少有部分表现信号"],
        "ideal_evidence": ["播放、点赞、评论、收藏、分享", "hook / 标题备注", "内容类型标签", "可选的转化或 ROI 上下文", "2 个以上时间窗口"],
        "ready_checklist": ["帖子可以按模式聚类", "高低表现内容可区分", "下一轮测试规则可以写出来", "高低表现组可以直接对比", "单窗口观察与多周模式可以区分"],
    },
}


SCENE_OPERATOR_GUIDE = {
    "01": {
        "operator_checklist": [
            "排序前先把所有候选样本统一到同一市场。",
            "采集前先锁定发布时间窗口、地区、排序规则与购物车视频范围。",
            "给每条入选视频标记最佳复用用途：hook、证明、结构或风格。",
            "保留未入选池，方便后续迭代排序逻辑。",
        ],
        "common_failure_modes": [
            "只按播放量排序，忽略复用价值。",
            "把偏自然流量的爆款和强带货内容混在一起，却没标清差异。",
            "在同一 shortlist 里混入多个市场或多个产品意图。",
            "只收集链接，没有为后续拆解保留足够的 hook 或证明笔记。",
        ],
    },
    "02": {
        "operator_checklist": [
            "Lock the patrol cadence before defining the table.",
            "Separate routine fields from alert-trigger fields.",
            "Highlight only new, rising, and abnormal signals in the daily surface.",
            "Write the daily summary template before claiming the patrol is reusable.",
            "Define which rows auto-escalate into scene 03 and which stay as patrol history.",
        ],
        "common_failure_modes": [
            "Trying to automate before the manual SOP is stable.",
            "Tracking too many fields to sustain daily use.",
            "Appending rows with inconsistent headers or no capture date.",
            "No clear threshold for what counts as a meaningful change.",
        ],
    },
    "03": {
        "operator_checklist": [
            "Shortlist first, then deep-teardown only the top set.",
            "Use an explicit top-sample rule before teardown begins.",
            "Use the same lens across all chosen videos so patterns are comparable.",
            "End with creation rules, not only observations.",
        ],
        "common_failure_modes": [
            "Deep-analyzing weak candidates that should have been filtered out earlier.",
            "Skipping script or time-axis extraction and therefore flattening the teardown.",
            "Using different teardown criteria across videos.",
            "Summarizing patterns without enough per-video evidence.",
        ],
    },
    "04": {
        "operator_checklist": [
            "用带时间范围的节拍表按顺序重建视频。",
            "在过度泛化结论前，先判断视频类型。",
            "把核心机制与创作者个人化表层风格分开。",
            "显式记录 BGM、字幕表现与转场节奏。",
            "在收尾前至少写出 1 条改编路径。",
            "无口播视频也要按字幕、动作、镜头与节奏完整拆解。",
        ],
        "common_failure_modes": [
            "把视觉精致度误当成真正的转化机制。",
            "因为转写稿稀疏，就忽略无口播视频的成立逻辑。",
            "因为收口或 CTA 看起来简单，就直接跳过。",
            "只给抽象夸赞，没有可复用结论。",
        ],
    },
    "05": {
        "operator_checklist": [
            "在写反推 prompt 前，先说明可能的创作意图。",
            "把观测结果翻译成生成器可用模块，而不是空泛风格词。",
            "反推原版 brief 与产品适配版 brief 必须分开。",
            "证据偏薄的字段要用字段级置信度标识。",
            "低置信度猜测必须显式写出来。",
            "至少给出 generator-ready handoff 字段，不要停留在分析语句。",
        ],
        "common_failure_modes": [
            "臆造视频无法支撑的 prompt 细节。",
            "只描述视觉风格，不写节奏、镜头和口播逻辑。",
            "跳过 shot 级结构，只剩 1 段泛 prompt。",
            "忘记把反推 brief 改写成用户产品版本。",
        ],
    },
    "06": {
        "operator_checklist": [
            "Fix the product identifiers before tracking changes over time.",
            "Define what counts as a commercial signal, not only a data change.",
            "Keep the dashboard schema minimal enough to maintain weekly.",
            "If Shop API data is missing, switch to listing/PDP snapshot intake instead of leaving holes in the board.",
        ],
        "common_failure_modes": [
            "Tracking products with inconsistent naming and duplicate rows.",
            "Collecting raw data without interpretation rules.",
            "Watching too many fields and never using the board in practice.",
            "Treating missing API access as a blocker instead of running the fallback evidence mode.",
        ],
    },
    "07": {
        "operator_checklist": [
            "Use both content evidence and product evidence before judging the category.",
            "Extract keyword clues from titles and hashtags before jumping to market judgment.",
            "Separate hot angles from overcrowded angles.",
            "Match recommendation strength to evidence depth.",
        ],
        "common_failure_modes": [
            "Calling a category attractive based on a few flashy videos.",
            "Treating attention heat as proof of durable commercial demand.",
            "Skipping keyword-level decisions and leaving only one fuzzy recommendation.",
            "Missing whitespace because angle saturation was not mapped explicitly.",
        ],
    },
    "08": {
        "operator_checklist": [
            "合并品类信号前，先按商品维度保留评论分组。",
            "来源商品标签要一路保留到洞察层。",
            "优先引用重复出现的用户原话，而不只是分析师转述。",
            "把痛点与欲望翻译成产品决策和脚本启发。",
            "优先突出物流、包装、真假、退货、before-after、尺码 / 色号适配这类购买型语言。",
        ],
        "common_failure_modes": [
            "把一次性抱怨和真正重复出现的痛点混为一谈。",
            "只做情绪总结，没有具体用户原话。",
            "过早抹平来源商品差异，丢掉价格带洞察。",
            "忽略欲望、抱怨和信任信号之间的区别。",
        ],
    },
    "09": {
        "operator_checklist": [
            "Lock the invariant logic from the reference before adapting anything.",
            "Swap product-specific pieces one layer at a time: hook, proof, close.",
            "End with a filmable or promptable shot order.",
        ],
        "common_failure_modes": [
            "Copying the reference too literally.",
            "Changing so much that the winning logic is lost.",
            "Leaving the brief too abstract for production.",
        ],
    },
    "10": {
        "operator_checklist": [
            "Choose the video type before writing scenes.",
            "Use the available images to design proof beats, not just beauty shots.",
            "Leave explicit visual-gap notes when the asset set is weak.",
        ],
        "common_failure_modes": [
            "Writing a concept that depends on footage the user does not have.",
            "Filling the brief with style words and no proof structure.",
            "Ignoring CTA and conversion intent because the input is image-only.",
        ],
    },
    "11": {
        "operator_checklist": [
            "Define the pipeline stages and decision gates clearly.",
            "Decide what makes a hot video worth entering the replication queue.",
            "Tie the workflow to a repeatable daily or weekly cadence.",
        ],
        "common_failure_modes": [
            "Blurring discovery, teardown, and production into one vague step.",
            "Queueing too many candidates with no ranking gate.",
            "Building a pipeline that cannot be run repeatedly by one operator.",
        ],
    },
    "12": {
        "operator_checklist": [
            "Lock the invariant message before varying style.",
            "Ensure each style meaningfully changes hook, proof, or audience lens.",
            "Define success signals before recommending test order.",
        ],
        "common_failure_modes": [
            "Creating cosmetic variants that are not meaningfully different.",
            "Changing the core message across rows and ruining comparability.",
            "No stated learning objective for each variant.",
        ],
    },
    "13": {
        "operator_checklist": [
            "Separate shared product truth from market-specific adaptation layers.",
            "Write each market's hook, tone, and avoid-list explicitly.",
            "Keep localization tied to conversion context, not literal translation.",
        ],
        "common_failure_modes": [
            "Using one English-first script across all markets.",
            "Localizing copy but not talent, scene, or tone cues.",
            "Ignoring culturally awkward phrasing until render time.",
        ],
    },
    "14": {
        "operator_checklist": [
            "Define the minimum viable asset family before adding nice-to-have assets.",
            "Assign one conversion job to each asset.",
            "Order production by launch leverage, not by creative preference.",
        ],
        "common_failure_modes": [
            "Treating all assets as equally important.",
            "No coherent creative direction across the family.",
            "Producing images and video separately with no shared message logic.",
        ],
    },
    "15": {
        "operator_checklist": [
            "Separate literal information from persuasive copy blocks.",
            "Preserve hierarchy while adapting for local conversion language.",
            "Add layout notes so the localized copy can actually fit.",
        ],
        "common_failure_modes": [
            "Direct translation that breaks persuasion or tone.",
            "Localized copy that no longer fits the original layout.",
            "Failing to note which lines should be headline versus support text.",
        ],
    },
    "16": {
        "operator_checklist": [
            "Describe the click context before judging the images.",
            "Identify both category norms and sharp opportunities to differ.",
            "End with a more useful brief than generic 'make it cleaner' advice.",
        ],
        "common_failure_modes": [
            "Comparing images with no category or platform context.",
            "Mistaking visual novelty for likely click improvement.",
            "Giving weak benchmark commentary with no outperform strategy.",
        ],
    },
    "17": {
        "operator_checklist": [
            "在宣告可复用公式前，先使用多条创作者样本。",
            "提炼公式前先总结账号基线。",
            "直接比较高表现与低表现样本。",
            "把重复出现的 hook、节奏、证明与 CTA 模式拆开整理。",
            "明确区分可迁移模式与创作者专属优势。",
        ],
        "common_failure_modes": [
            "用 1 条爆款过拟合出整套创作者公式。",
            "忽略低表现样本，导致没有对照。",
            "忽略创作者独有的信任或身份优势。",
            "最后停留在夸赞，而不是适配规则。",
        ],
    },
    "18": {
        "operator_checklist": [
            "开始比较前，先按账号和周维度整理帖子。",
            "重点标出周度变化，而不是只列周度总量。",
            "横向比较账号，而不是拆成互不相干的小报告。",
            "最后必须落到本周用户该采取的动作。",
            "如果只有单周数据，就标成 baseline week，不要假装长期趋势。",
        ],
        "common_failure_modes": [
            "只列活动量，没有解释模式变化。",
            "只有 1 个基线周却直接下趋势判断。",
            "报告太像库存清单，导致漏掉策略变化检测。",
            "没有真正做跨账号横向比较。",
        ],
    },
    "19": {
        "operator_checklist": [
            "按模式聚类帖子，不要只按发布时间排列。",
            "明确比较高表现组和低表现组。",
            "写出明确的多做、少做和停止规则。",
            "把复盘落实成一份下轮测试计划。",
            "只有单窗口数据时，把结论写成本轮观察，不要写成长期规律。",
        ],
        "common_failure_modes": [
            "逐条读指标，却没有模式聚类。",
            "停在复盘总结，没有落成下轮测试计划。",
            "用模糊质量判断解释结果。",
            "复盘结束时没有具体的下一轮测试周期。",
        ],
    },
}


def get_scene_preset(scene_id: str) -> dict:
    preset = deepcopy(SCENE_PRESETS.get(scene_id, {}))
    if not preset:
        return {}
    working_context = preset.setdefault("working_context", {})
    for key, value in SCENE_INTAKE.get(scene_id, {}).items():
        working_context.setdefault(key, value)
    preset.setdefault("operator_guide", {})
    for key, value in SCENE_OPERATOR_GUIDE.get(scene_id, {}).items():
        preset["operator_guide"].setdefault(key, value)
    preset["execution_template"] = build_execution_template(scene_id, preset)
    return preset


