from __future__ import annotations

from copy import deepcopy


def blank_table(headers: list[str], rows: list[list[str]] | None = None, title: str = "") -> dict:
    return {
        "title": title,
        "headers": headers,
        "rows": rows or [],
    }


def section(
    heading: str,
    instruction: str,
    paragraphs: list[str] | None = None,
    bullets: list[str] | None = None,
    numbered: list[str] | None = None,
    table: dict | None = None,
) -> dict:
    return {
        "heading": heading,
        "instruction": instruction,
        "paragraphs": paragraphs or [],
        "bullets": bullets or [],
        "numbered": numbered or [],
        "table": table or blank_table([]),
    }


SCENE_EXECUTION_PROFILES = {
    "01": {
        "runner_slug": "viral-video-collection",
        "project_example": "US Lip Combo Viral Collection",
        "evidence_example": "15 TikTok search results with links, metrics, and first-hook notes",
        "success_goal": "ranked shortlist plus teardown priority",
        "recommended_request": "Run scene 01 to collect and rank the best viral videos for one keyword and market. Score for reuse value, not just views, and finish with which videos should move into teardown next.",
        "extra_prompt_lines": [
            "Rank the candidate pool before doing any deeper analysis.",
            "Tag each shortlisted video by best reuse purpose: hook, proof, structure, or style.",
        ],
        "output_checklist": [
            "The shortlist is ranked and limited to the strongest candidates.",
            "Each selected video has a concrete why-selected reason.",
            "The operator knows which videos should move into the next teardown workflow.",
        ],
    },
    "02": {
        "runner_slug": "daily-category-patrol",
        "project_example": "Daily Beauty Category Patrol",
        "evidence_example": "Current keyword set, patrol entry points, and existing manual notes",
        "success_goal": "repeatable patrol SOP and alert schema",
        "recommended_request": "Run scene 02 to design a daily category patrol workflow. Build a repeatable patrol table, alert logic, and one daily summary template instead of a vague research memo.",
        "extra_prompt_lines": [
            "Separate routine tracking fields from alert-trigger fields.",
            "If automation is unavailable, keep the workflow as a manual SOP that one operator can actually run.",
        ],
        "output_checklist": [
            "The patrol cadence is explicit.",
            "Tracked fields and alert conditions are practical to maintain.",
            "A reusable daily summary template is included.",
        ],
    },
    "03": {
        "runner_slug": "batch-search-teardown",
        "project_example": "Morning Makeup Hook Teardown",
        "evidence_example": "10 candidate TikTok links with screenshots and transcript notes",
        "success_goal": "shortlist plus per-video teardown and creation rules",
        "recommended_request": "Run scene 03 to shortlist the strongest viral candidates for one topic, then deeply tear down only the top set. Finish with shared creation rules that can be used immediately for new scripts.",
        "extra_prompt_lines": [
            "Use the same teardown lens across all shortlisted videos so the pattern summary is comparable.",
            "Do not deep-analyze weak candidates that should have been filtered out earlier.",
        ],
        "output_checklist": [
            "The top set is explicitly shortlisted before deep teardown.",
            "Each chosen video is analyzed with the same fields.",
            "The report ends with reusable creation rules, not only observations.",
        ],
    },
    "04": {
        "runner_slug": "single-video-breakdown",
        "project_example": "One Viral Concealer Breakdown",
        "evidence_example": "One video link, transcript notes, and screenshots by beat",
        "success_goal": "single-video mechanism breakdown and adaptation path",
        "recommended_request": "Run scene 04 to fully break down one TikTok or Douyin video. Reconstruct the hook, setup, proof, and close, then separate the true mechanism from surface style and recommend one concrete adaptation path.",
        "extra_prompt_lines": [
            "Rebuild the video in sequence before drawing any conclusions.",
            "Explicitly separate creator-specific polish from transferable conversion logic.",
        ],
        "output_checklist": [
            "The hook, proof, and close are reconstructed in order.",
            "The core mechanism is distinguished from surface style.",
            "At least one adaptation path is concrete enough to produce from.",
        ],
    },
    "05": {
        "runner_slug": "reverse-engineer-prompt",
        "project_example": "Creator Brief Reconstruction",
        "evidence_example": "Reference video frames, transcript snippets, and pacing notes",
        "success_goal": "reverse-engineered prompt or production brief",
        "recommended_request": "Run scene 05 to reverse-engineer the likely prompt or production brief behind one video. Infer the creative intent, translate it into brief blocks, and mark low-confidence guesses instead of inventing certainty.",
        "extra_prompt_lines": [
            "Translate observed output into prompt blocks such as visual direction, shot plan, voiceover logic, and editing rhythm.",
            "If evidence is thin, keep low-confidence labels visible in the final brief.",
        ],
        "output_checklist": [
            "The inferred brief is structured into reusable creation blocks.",
            "Weakly supported inferences are clearly labeled.",
            "The output can be adapted to a user product without redoing the analysis from zero.",
        ],
    },
    "06": {
        "runner_slug": "competitor-product-dashboard",
        "project_example": "Weekly Competitor Product Dashboard",
        "evidence_example": "3 competitor listings with price, rating, and offer snapshots",
        "success_goal": "competitor tracking dashboard and signal rules",
        "recommended_request": "Run scene 06 to build a competitor product dashboard that can be reused weekly. Define the minimum trackable schema, signal interpretation rules, and the operator response to changes.",
        "extra_prompt_lines": [
            "Use stable product identifiers so later tracking does not drift.",
            "Interpret changes commercially instead of logging raw changes only.",
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
        "recommended_request": "Run scene 07 to judge a category or product theme for demand, saturation, and opportunity. Use both content evidence and product evidence, and end with a strength-rated recommendation.",
        "extra_prompt_lines": [
            "Separate hot demand signals from crowded angle saturation.",
            "Match recommendation strength to evidence depth instead of overstating certainty.",
        ],
        "output_checklist": [
            "Demand, saturation, and whitespace are all addressed.",
            "Conclusions are backed by visible examples, not hype alone.",
            "The operator gets one prioritized next move.",
        ],
    },
    "08": {
        "runner_slug": "comment-mining-persona",
        "project_example": "Lip Product Comment Mining Persona Report",
        "evidence_example": "Comments from 3 products with repeated phrases highlighted",
        "success_goal": "pain-language synthesis and persona guidance",
        "recommended_request": "Run scene 08 to mine repeated customer language from multiple product comment sets. Separate pain, desire, and trust signals, quote real phrases, and translate them into persona and messaging implications.",
        "extra_prompt_lines": [
            "Keep comments grouped by product before merging category-level signals.",
            "Prefer repeated user phrases over abstract sentiment summaries.",
        ],
        "output_checklist": [
            "Repeated pain, desire, and trust signals are separated clearly.",
            "Real user-language evidence is preserved.",
            "Persona and messaging implications follow directly from the mined comments.",
        ],
    },
    "09": {
        "runner_slug": "reference-replication-brief",
        "project_example": "Reference Video Adaptation Brief",
        "evidence_example": "Reference video logic plus user product basics and assets",
        "success_goal": "adapted replication brief with shot order",
        "recommended_request": "Run scene 09 to turn one reference video into an adapted replication brief for a new product. Lock the invariant winning logic first, then rewrite the hook, proof, and close for the user's product.",
        "extra_prompt_lines": [
            "Keep the winning mechanism, but replace product-specific proof and offer layers one at a time.",
            "End with a filmable shot order or prompt-ready scene structure.",
        ],
        "output_checklist": [
            "Invariant reference logic is clearly separated from adapted layers.",
            "The adapted brief is specific enough to produce from.",
            "Literal-copy risks are called out explicitly.",
        ],
    },
    "10": {
        "runner_slug": "product-image-to-video-brief",
        "project_example": "Image-To-Video Product Brief",
        "evidence_example": "Product images, selling points, audience note, and desired style",
        "success_goal": "production-ready video brief from still assets",
        "recommended_request": "Run scene 10 to design a short-form video brief from product images only. Choose the video type, build proof beats around available assets, and note any visual gaps that would block production.",
        "extra_prompt_lines": [
            "Design proof beats from the assets that actually exist, not from imaginary footage.",
            "Keep CTA and conversion intent visible even if the input is image-only.",
        ],
        "output_checklist": [
            "The brief is compatible with the available asset set.",
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
        "success_goal": "localized brief pack across multiple markets",
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
        "project_example": "Localized Image Copy Brief",
        "evidence_example": "Image OCR text, layout notes, target language, and conversion goal",
        "success_goal": "localized image-copy brief that still fits the layout",
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
        "project_example": "Competitor Main Image Benchmark",
        "evidence_example": "2-5 competitor images plus the user's current image or product",
        "success_goal": "outperform direction for main image creative",
        "recommended_request": "Run scene 16 to benchmark competitor main images and define a stronger direction. Describe the click context first, then identify category norms, gaps, and a sharper outperform brief.",
        "extra_prompt_lines": [
            "Judge likely click behavior in context instead of giving generic visual design notes.",
            "End with an outperform strategy, not just a critique list.",
        ],
        "output_checklist": [
            "The benchmark is grounded in comparable category context.",
            "Likely click drivers are identified explicitly.",
            "The final brief is sharper than generic advice such as make it cleaner.",
        ],
    },
    "17": {
        "runner_slug": "creator-distillation",
        "project_example": "Creator Formula Distillation",
        "evidence_example": "Several top creator videos with transcript and performance notes",
        "success_goal": "repeatable creator formula and adaptation rules",
        "recommended_request": "Run scene 17 to distill one creator's repeatable content formula across multiple videos. Map repeated hook, pacing, proof, and CTA patterns, then separate transferable logic from creator-specific advantage.",
        "extra_prompt_lines": [
            "Use several creator samples before declaring a formula.",
            "Do not confuse admiration for the creator with reusable production rules.",
        ],
        "output_checklist": [
            "Repeated patterns are supported by multiple creator samples.",
            "Transferable rules are separated from creator-only advantages.",
            "The report ends with adaptation guidance for a new product or account.",
        ],
    },
    "18": {
        "runner_slug": "competitor-account-weekly-report",
        "project_example": "Weekly Competitor Account Review",
        "evidence_example": "2+ competitor accounts with one week's posts and performance notes",
        "success_goal": "weekly competitor report and action board",
        "recommended_request": "Run scene 18 to produce a weekly competitor account review. Group posts by account and week, compare shifts rather than totals only, and finish with what the operator should react to this week.",
        "extra_prompt_lines": [
            "Highlight weekly pattern shifts across accounts, not just activity counts.",
            "Translate observed shifts into action items for the current week.",
        ],
        "output_checklist": [
            "Posts are organized by account and week.",
            "The report explains shifts instead of listing raw activity.",
            "This week's response actions are prioritized.",
        ],
    },
    "19": {
        "runner_slug": "self-account-retro",
        "project_example": "Self Account Retro And Optimization",
        "evidence_example": "Recent post table with metrics, hooks, and content-type labels",
        "success_goal": "performance retro and next-cycle test plan",
        "recommended_request": "Run scene 19 to review a recent batch of posts from one account and define the next optimization cycle. Cluster posts by pattern, separate winning and losing traits, and end with do-more, do-less, stop, and test-next rules.",
        "extra_prompt_lines": [
            "Group posts by repeatable pattern instead of analyzing row by row only.",
            "Turn the retro into one next-cycle testing plan rather than a passive recap.",
        ],
        "output_checklist": [
            "Winning and losing patterns are clearly separated.",
            "Recommendations are phrased as operating rules, not vague observations.",
            "The next-cycle test plan is concrete enough to run immediately.",
        ],
    },
}


SCENE_TITLES_ZH = {
    "01": "爆款视频采集",
    "02": "品类日常巡检",
    "03": "批量爆款检索与深拆",
    "04": "单条视频拆解",
    "05": "视频提示词反推",
    "06": "竞品商品看板",
    "07": "品类市场判断",
    "08": "多产品评论挖掘与人群报告",
    "09": "对标视频复刻 Brief",
    "10": "产品图转视频 Brief",
    "11": "热点视频复制 Pipeline",
    "12": "单品多风格测试矩阵",
    "13": "多市场本地化包",
    "14": "上新素材家族包",
    "15": "图片文案翻译 Brief",
    "16": "竞品主图 Benchmark",
    "17": "创作者公式蒸馏",
    "18": "竞品账号周报",
    "19": "自有账号复盘优化",
}

SCENE_REQUESTS_ZH = {
    "01": "按场景 01 执行：围绕一个关键词或品类和单一市场，先收集候选爆款，再按复用价值而不是单看播放量排序，最后告诉我哪些视频最值得进入下一步拆解。",
    "02": "按场景 02 执行：为一个品类搭建日常巡检 SOP，输出可重复使用的巡检表、预警逻辑和日报模板，不要只给研究结论。",
    "03": "按场景 03 执行：先对同一主题的候选热视频做 shortlist，再只深拆前几条强样本，最后沉淀共享爆点规律和可直接改写成新脚本的创作规则。",
    "04": "按场景 04 执行：完整拆一条短视频，按 hook、铺垫、证明、收口重建结构，再分离真正有效的机制和表层风格，并给出一个可改编方向。",
    "05": "按场景 05 执行：反向推断这条视频背后的提示词或制作 brief，把创作意图拆成视觉、镜头、旁白、节奏模块，并把低置信度猜测标出来。",
    "06": "按场景 06 执行：搭建可每周复用的竞品商品看板，定义最小追踪字段、信号解释逻辑和变化后的运营动作。",
    "07": "按场景 07 执行：判断一个品类或主题是否值得做，要同时看内容热度、供给饱和度和可切入空位，最后给出强弱分级建议。",
    "08": "按场景 08 执行：把多个产品的评论做合并挖掘，分开提炼痛点、欲望和信任信号，并保留原话，最后转成人群和话术启发。",
    "09": "按场景 09 执行：把一条对标视频改造成适合新产品的复刻 brief，先锁定不该改的 winning logic，再重写 hook、证明和收口。",
    "10": "按场景 10 执行：仅基于产品图设计一版短视频 brief，明确视频类型、证明镜头、CTA 和资产缺口，不要假设用户已经有额外素材。",
    "11": "按场景 11 执行：搭一个可重复跑的热点视频复制 pipeline，把发现、筛选、深拆、入池和生产交接拆成明确阶段和门槛。",
    "12": "按场景 12 执行：为一个产品做多风格测试矩阵，先锁 invariant message，再设计真正有差异的测试风格，并写出每个变体要学什么。",
    "13": "按场景 13 执行：把一个产品概念做成多市场本地化包，拆清共享产品真相和各市场的 hook、语气、禁区，不要只做直译。",
    "14": "按场景 14 执行：设计一套上新素材家族，先定义最小可上线资产集，再给每个素材分配一个转化职责，并排出制作优先级。",
    "15": "按场景 15 执行：做图片文案翻译与本地化 brief，区分信息性文案和转化型文案，保留层级关系，并说明新文案如何适配原布局。",
    "16": "按场景 16 执行：对标竞品主图并定义更强方向，先说清点击场景，再总结类目共性、差异机会和一版可执行的超越 brief。",
    "17": "按场景 17 执行：提炼一个创作者在多条视频里重复出现的内容公式，拆开 hook、节奏、证明和 CTA，并区分可迁移规则与创作者独有优势。",
    "18": "按场景 18 执行：输出竞品账号周报，要按账号和周维度比较内容变化，不只看总量，并明确本周该跟进的动作。",
    "19": "按场景 19 执行：复盘一个账号最近一批内容，把帖子按模式分组，拆出赢法和输法，最后写成 do more、do less、stop 和下一轮测试计划。",
}

def _build_default_variable_inputs(
    project_example: str,
    evidence_example: str,
    success_goal: str,
) -> list[dict]:
    return [
        {
            "name": "project_name",
            "meaning": "Human-readable run or campaign name",
            "example": project_example,
            "required": "yes",
        },
        {
            "name": "market",
            "meaning": "Target market or locale when the scene depends on one market",
            "example": "US",
            "required": "recommended",
        },
        {
            "name": "evidence_pack",
            "meaning": "Links, screenshots, transcripts, exports, OCR text, or copied notes used as source evidence",
            "example": evidence_example,
            "required": "yes",
        },
        {
            "name": "success_goal",
            "meaning": "What the operator wants this scene to produce",
            "example": success_goal,
            "required": "recommended",
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
        f"\u5148\u628a\u6211\u63d0\u4f9b\u7684\u6750\u6599\u6574\u7406\u6210\u8fd9\u7ec4\u8f93\u5165：{inputs_text}\u3002",
        f"\u5982\u679c\u8bc1\u636e\u4e0d\u8db3，\u5148\u660e\u786e\u7f3a\u53e3\u518d\u7ee7\u7eed\u3002\u6700\u4f4e\u5f00\u5de5\u8bc1\u636e：{minimum_text}\u3002",
        f"\u6700\u7ec8\u5fc5\u987b\u4ea7\u51fa：{outputs_text}\u3002",
        "\u8f93\u51fa\u5fc5\u987b\u53ef\u76f4\u63a5\u7ed9\u8fd0\u8425\u3001\u62c6\u89e3\u3001\u811a\u672c\u3001\u6d4b\u8bd5\u6216\u4ea4\u4ed8\u4f7f\u7528，\u4f18\u5148\u7ed9\u8868\u683c\u3001\u6392\u5e8f\u903b\u8f91\u3001\u590d\u7528\u89c4\u5219\u548c\u4e0b\u4e00\u6b65\u52a8\u4f5c\u3002",
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
        "Normalize the evidence and scope first.",
        "Fill the scene scaffold section by section.",
        "End with one concrete next operator move.",
    ]
    prompt_scaffold = [
        f"Use scene {scene_id} as the governing workflow.",
        f"Normalize the provided evidence into this input set before analysis: {', '.join(inputs) if inputs else 'scene-specific evidence set'}.",
        f"If evidence is missing, state the gap explicitly before continuing. Minimum evidence to proceed: {', '.join(minimum_evidence) if minimum_evidence else 'state the minimum evidence explicitly'}.",
        f"Produce these outputs in operator-ready form: {', '.join(requested_outputs) if requested_outputs else 'scene deliverable sections plus one next action'}.",
    ]
    prompt_scaffold.extend(profile.get("extra_prompt_lines", []))
    prompt_scaffold.append("Fill the scaffold with reusable conclusions, tables, ranking logic, and next actions instead of generic commentary.")

    return {
        "recommended_request": profile.get(
            "recommended_request",
            f"Run scene {scene_id} and produce the full reusable deliverable, not a brief summary.",
        ),
        "recommended_request_zh": SCENE_REQUESTS_ZH.get(
            scene_id,
            f"按场景 {scene_id} 执行，并输出完整可复用交付物，不要只给摘要。",
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
            "The deliverable is grounded in evidence.",
            "The operator can run the next step without extra interpretation.",
        ],
    }
SCENE_PRESETS = {
    "01": {
        "working_context": {
            "inputs": [
                "Primary keyword or product phrase",
                "Target market",
                "Target audience",
                "Date window or freshness requirement",
            ],
            "constraints": [
                "Do not rank on views alone. Keep reuse value in the scoring logic.",
                "If live browsing is unavailable, rely on user-provided screenshots, exports, or copied links.",
            ],
            "requested_outputs": [
                "Ranked shortlist",
                "Reason each selected video matters",
                "Study-next recommendation",
            ],
        },
        "evidence": [
            {"label": "Candidate export", "detail": "Paste titles, links, views, likes, dates, and first-hook notes.", "source": ""},
            {"label": "Search screenshot set", "detail": "Attach screenshots if no structured export exists.", "source": ""},
        ],
        "sections": [
            section(
                "Executive Conclusion",
                "State what kind of videos are most worth studying for this keyword and market.",
                bullets=[
                    "Which sub-pattern dominates the shortlist?",
                    "What should the operator study first: hook, structure, proof, or style?",
                ],
            ),
            section(
                "Objects To Track",
                "Build the shortlist table first.",
                table=blank_table(
                    ["Rank", "Video / Link", "Core Topic", "Performance Signal", "Useful For", "Why Selected"],
                    [
                        ["1", "", "", "", "", ""],
                        ["2", "", "", "", "", ""],
                        ["3", "", "", "", "", ""],
                        ["4", "", "", "", "", ""],
                        ["5", "", "", "", "", ""],
                    ],
                    "Top Candidate Board",
                ),
            ),
            section(
                "Why They Matter",
                "Explain why each selected item deserves operator attention.",
                table=blank_table(
                    ["Video", "Hook Strength", "Proof Style", "Conversion Signal", "Main Reuse Value"],
                    [["", "", "", "", ""], ["", "", "", "", ""], ["", "", "", "", ""]],
                ),
            ),
            section(
                "Fields To Capture Next Time",
                "Define the minimum schema for future collection rounds.",
                table=blank_table(
                    ["Field", "Why Capture It", "Required Next Time?"],
                    [
                        ["Video link", "Traceability", "Yes"],
                        ["Post date", "Freshness", "Yes"],
                        ["Views / likes / comments", "Basic performance", "Yes"],
                        ["Hook summary", "Later breakdown", "Yes"],
                        ["Useful-for tag", "Routing to next workflow", "Yes"],
                    ],
                ),
            ),
            section(
                "Next Action",
                "Recommend what to do immediately after collection.",
                numbered=[
                    "Choose 1-3 videos for deep teardown.",
                    "Tag each shortlisted video by best reuse purpose.",
                    "Archive the full candidate set so later comparisons remain possible.",
                ],
            ),
        ],
        "assets": [
            {"label": "Candidate screenshots", "path": "", "note": "Optional screenshots of search results or top posts."},
        ],
        "notes": [
            "If multiple markets are mixed together, split the board before drawing conclusions.",
        ],
    },
    "02": {
        "working_context": {
            "inputs": [
                "Category name",
                "Primary market",
                "Keyword set",
                "Patrol cadence",
            ],
            "constraints": [
                "If no automation source exists, keep the output as a manual SOP instead of fake automation.",
            ],
            "requested_outputs": [
                "Daily patrol checklist",
                "Patrol table schema",
                "Alert logic",
                "Daily summary template",
            ],
        },
        "evidence": [
            {"label": "Current patrol source", "detail": "List current search entry points, exports, or manual sources.", "source": ""},
        ],
        "sections": [
            section(
                "Executive Conclusion",
                "Summarize the patrol design and its purpose in one operator-facing paragraph.",
                bullets=[
                    "What exactly gets checked each cycle?",
                    "What counts as a meaningful change?",
                ],
            ),
            section(
                "Objects To Track",
                "Define the daily patrol schema.",
                table=blank_table(
                    ["Field", "Description", "Why It Matters", "Daily / Weekly"],
                    [
                        ["Keyword", "", "", "Daily"],
                        ["Video link", "", "", "Daily"],
                        ["Performance signal", "", "", "Daily"],
                        ["New angle observed", "", "", "Daily"],
                        ["Alert flag", "", "", "Daily"],
                    ],
                    "Patrol Table Schema",
                ),
            ),
            section(
                "Why They Matter",
                "Explain how to interpret changes rather than just record them.",
                table=blank_table(
                    ["Signal", "What It Might Mean", "Follow-up Action"],
                    [
                        ["Sudden high-view new post", "", ""],
                        ["Repeated hook across accounts", "", ""],
                        ["Price / offer shift", "", ""],
                        ["New creator archetype", "", ""],
                    ],
                ),
            ),
            section(
                "Fields To Capture Next Time",
                "Specify what must be added if the current patrol is too shallow.",
                bullets=[
                    "Which fields are missing today?",
                    "Which fields unlock faster ranking later?",
                ],
            ),
            section(
                "Next Action",
                "Leave the operator with a ready-to-run patrol routine.",
                numbered=[
                    "Run the patrol at the chosen cadence.",
                    "Compare against the prior snapshot, not only today's raw numbers.",
                    "Escalate only when an alert condition is triggered.",
                ],
                table=blank_table(
                    ["Daily Summary Block", "Template"],
                    [
                        ["What changed", ""],
                        ["What broke out", ""],
                        ["What needs deeper teardown", ""],
                        ["What to watch tomorrow", ""],
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
                    ["Rank", "Video", "Hook", "Proof", "Conversion Signal", "Why It Made Top Set"],
                    [["1", "", "", "", "", ""], ["2", "", "", "", "", ""], ["3", "", "", "", "", ""]],
                    "Shortlist",
                ),
            ),
            section(
                "Core Mechanism",
                "Break down each selected video using the same lens.",
                table=blank_table(
                    ["Video", "Opening Hook", "Structure", "Proof Device", "CTA / Close", "Main Reuse Value"],
                    [["", "", "", "", "", ""], ["", "", "", "", "", ""], ["", "", "", "", "", ""]],
                    "Per-Video Breakdown Grid",
                ),
            ),
            section(
                "Reusable Formula",
                "Turn the shared pattern into direct creation guidance.",
                table=blank_table(
                    ["Element", "Observed Pattern", "How To Reuse It", "What Not To Copy Blindly"],
                    [
                        ["Hook", "", "", ""],
                        ["Proof", "", "", ""],
                        ["Shot rhythm", "", "", ""],
                        ["CTA", "", "", ""],
                    ],
                    "Creation Rules",
                ),
            ),
            section(
                "Risks And Adaptation Notes",
                "Explain where false copying would fail.",
                bullets=[
                    "Which strengths depend on creator-specific advantage?",
                    "Which parts are likely market- or product-specific?",
                ],
            ),
            section(
                "Next Action",
                "Leave a concrete next production move.",
                numbered=[
                    "Pick the best candidate to replicate first.",
                    "Write 2-3 new directions using the shared formula.",
                    "Decide what should be tested immediately versus archived.",
                ],
            ),
        ],
    },
    "04": {
        "working_context": {
            "inputs": [
                "One video link or storyboard",
                "Transcript or subtitle notes",
                "Frame notes or screenshots",
            ],
            "constraints": [
                "Separate deep logic from surface style.",
            ],
            "requested_outputs": [
                "One-line judgment",
                "Structure map",
                "Viral mechanism",
                "Reusable formula",
                "Adaptation advice",
            ],
        },
        "evidence": [
            {"label": "Video evidence", "detail": "Link, screenshots, transcript notes, or manual reconstruction.", "source": ""},
        ],
        "sections": [
            section(
                "Executive Conclusion",
                "Make a sharp judgment about why this single video works or fails.",
            ),
            section(
                "Structure Logic",
                "Map the video from open to close.",
                table=blank_table(
                    ["Segment", "What Happens", "Why It Matters", "Estimated Timestamp"],
                    [
                        ["Hook", "", "", ""],
                        ["Setup", "", "", ""],
                        ["Proof", "", "", ""],
                        ["Close / CTA", "", "", ""],
                    ],
                    "Structure Map",
                ),
            ),
            section(
                "Core Mechanism",
                "Describe the underlying mechanism, not just the visible style.",
                bullets=[
                    "What tension or curiosity keeps attention?",
                    "How does the video establish proof or credibility?",
                ],
            ),
            section(
                "Reusable Formula",
                "Extract only the transferable parts.",
                table=blank_table(
                    ["Layer", "Observed", "Reusable?", "Adaptation Note"],
                    [
                        ["Hook logic", "", "", ""],
                        ["Visual style", "", "", ""],
                        ["Proof logic", "", "", ""],
                        ["CTA style", "", "", ""],
                    ],
                ),
            ),
            section(
                "Risks And Adaptation Notes",
                "Give one safer and one more aggressive adaptation path.",
                table=blank_table(
                    ["Path", "What To Keep", "What To Change", "Risk"],
                    [["Safer", "", "", ""], ["More aggressive", "", "", ""]],
                ),
            ),
            section(
                "Next Action",
                "Recommend the single best next move for the operator.",
            ),
        ],
    },
    "05": {
        "working_context": {
            "inputs": [
                "Reference video",
                "Screenshots or frame summary",
                "Transcript notes",
                "Optional user product to adapt onto",
            ],
            "constraints": [
                "If evidence is thin, mark the prompt as low-confidence.",
            ],
            "requested_outputs": [
                "Reverse-engineered prompt",
                "Shot / scene brief",
                "Optional product-adapted version",
            ],
        },
        "evidence": [
            {"label": "Visual evidence", "detail": "Attach frames or describe the scene order.", "source": ""},
            {"label": "Audio / transcript evidence", "detail": "Paste key spoken lines or subtitle notes.", "source": ""},
        ],
        "sections": [
            section(
                "Executive Conclusion",
                "Summarize the likely creative intent behind the piece.",
            ),
            section(
                "Structure Logic",
                "Reconstruct the brief from observed output.",
                table=blank_table(
                    ["Dimension", "Observed Evidence", "Likely Intent"],
                    [
                        ["Visual style", "", ""],
                        ["Shot language", "", ""],
                        ["Narrative pacing", "", ""],
                        ["Voiceover logic", "", ""],
                    ],
                ),
            ),
            section(
                "Core Mechanism",
                "State what makes the reconstructed brief effective.",
            ),
            section(
                "Reusable Formula",
                "Write the inferred prompt or creation brief.",
                table=blank_table(
                    ["Block", "Prompt / Brief Content"],
                    [
                        ["Visual direction", ""],
                        ["Shot plan", ""],
                        ["Voiceover logic", ""],
                        ["Editing / pacing", ""],
                    ],
                    "Reverse-Engineered Brief",
                ),
            ),
            section(
                "Risks And Adaptation Notes",
                "Describe where the inference is weak or where adaptation is needed.",
            ),
            section(
                "Next Action",
                "If a user product exists, state how to rewrite the brief for it.",
            ),
        ],
    },
    "06": {
        "working_context": {
            "inputs": [
                "Competitor product list",
                "Links, IDs, or screenshots",
                "Optional price / rating / sales signals",
            ],
            "constraints": [
                "If structured data is incomplete, define the schema first and flag missing fields.",
            ],
            "requested_outputs": [
                "Competitor board schema",
                "Daily / weekly review checklist",
                "Anomaly interpretation guide",
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
                ],
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
            ],
            "constraints": [
                "If evidence is incomplete, avoid a hard go / no-go claim.",
            ],
            "requested_outputs": [
                "Category judgment",
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
                    ["Dimension", "Judgment", "Evidence"],
                    [
                        ["Demand visibility", "", ""],
                        ["Angle saturation", "", ""],
                        ["Commercial seriousness", "", ""],
                        ["Entry attractiveness", "", ""],
                    ],
                ),
            ),
            section(
                "Evidence Clusters",
                "Group the strongest patterns in the market.",
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
                "Recommended Action",
                "Translate the category read into a decision.",
                bullets=[
                    "Go / no-go / watch-only",
                    "What angle should be prioritized first?",
                    "What should be avoided because the market is crowded?",
                ],
            ),
            section(
                "Open Questions",
                "List what still needs verification before stronger commitment.",
            ),
        ],
    },
    "08": {
        "working_context": {
            "inputs": [
                "Comments from 2+ products",
                "Market",
                "Product positioning goal",
            ],
            "constraints": [
                "If comment volume is light, mark findings as provisional.",
            ],
            "requested_outputs": [
                "Pain-point synthesis",
                "Desire synthesis",
                "High-frequency phrases",
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
                bullets=[
                    "What pain repeats most often?",
                    "What buying trigger appears most often?",
                ],
            ),
            section(
                "Evidence Clusters",
                "Cluster repeated user language across products.",
                table=blank_table(
                    ["Cluster Type", "Repeated Phrase / Theme", "What It Suggests", "Product / Content Implication"],
                    [
                        ["Pain point", "", "", ""],
                        ["Desired outcome", "", "", ""],
                        ["Complaint", "", "", ""],
                        ["Trust signal", "", "", ""],
                    ],
                    "Comment Signal Clusters",
                ),
            ),
            section(
                "Recommended Action",
                "Turn the user language into next decisions.",
                table=blank_table(
                    ["Decision Area", "Recommendation", "Why"],
                    [
                        ["Product direction", "", ""],
                        ["Offer / positioning", "", ""],
                        ["Script language", "", ""],
                        ["Proof content", "", ""],
                    ],
                ),
            ),
            section(
                "Open Questions",
                "List missing evidence or weak conclusions.",
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
            ],
            "requested_outputs": [
                "Replication brief",
                "Adapted hook",
                "Adapted proof sequence",
                "Shot order",
                "Optional voiceover draft",
            ],
        },
        "evidence": [
            {"label": "Reference logic", "detail": "Paste the reference video link or teardown notes.", "source": ""},
            {"label": "User product facts", "detail": "Add product offer, selling points, and constraints.", "source": ""},
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
                "Give an execution-ready shot order.",
                table=blank_table(
                    ["Shot / Beat", "What Happens", "Purpose", "Asset / Talent Needed", "Line / Overlay"],
                    [["1", "", "", "", ""], ["2", "", "", "", ""], ["3", "", "", "", ""], ["4", "", "", "", ""]],
                    "Replication Shot Order",
                ),
            ),
            section(
                "Creative Constraints",
                "List what cannot be copied literally and what must change for the user product.",
                table=blank_table(
                    ["Constraint", "Keep / Change", "Reason"],
                    [
                        ["Visual identity", "", ""],
                        ["Claim language", "", ""],
                        ["Proof style", "", ""],
                        ["CTA wording", "", ""],
                    ],
                    "Adaptation Guardrails",
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
            ],
            "requested_outputs": [
                "Video concept",
                "Shot structure",
                "Voiceover structure",
                "Style keywords",
                "Test variables",
            ],
        },
        "evidence": [
            {"label": "Product asset set", "detail": "List the available images, angles, or missing visual gaps.", "source": ""},
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
                    ["Layer", "Draft", "Supported By Which Asset"],
                    [
                        ["Core promise", "", ""],
                        ["Primary proof", "", ""],
                        ["Secondary proof", "", ""],
                        ["CTA", "", ""],
                    ],
                    "Image-Only Messaging Brief",
                ),
            ),
            section(
                "Structure",
                "Map the shot flow from opening to close.",
                table=blank_table(
                    ["Beat", "Visual Use", "Voiceover / Overlay", "Purpose", "Missing Asset?"],
                    [["Hook", "", "", "", ""], ["Proof 1", "", "", "", ""], ["Proof 2", "", "", "", ""], ["Close", "", "", "", ""]],
                ),
            ),
            section(
                "Creative Constraints",
                "Specify style keywords, rendering guardrails, and what to avoid.",
                table=blank_table(
                    ["Constraint Type", "Detail", "Risk If Ignored"],
                    [["Visual style", "", ""], ["Tone", "", ""], ["Must show", "", ""], ["Must avoid", "", ""]],
                    "Render Guardrails",
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
                    ["Stage", "Input", "Decision Rule", "Owner", "Output", "SLA / Cadence"],
                    [
                        ["Discovery", "", "", "", "", ""],
                        ["Shortlist", "", "", "", "", ""],
                        ["Teardown", "", "", "", "", ""],
                        ["Replication brief", "", "", "", "", ""],
                        ["Production queue", "", "", "", "", ""],
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
                    ["Cycle Question", "Why It Matters", "How To Measure", "What Decision It Changes"],
                    [["", "", "", ""], ["", "", "", ""], ["", "", "", ""]],
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
                    ["Style", "Audience Lens", "Hook", "Proof Device", "Visual Style", "CTA", "Primary Hypothesis", "Why Test It"],
                    [
                        ["Style 1", "", "", "", "", "", "", ""],
                        ["Style 2", "", "", "", "", "", "", ""],
                        ["Style 3", "", "", "", "", "", "", ""],
                        ["Style 4", "", "", "", "", "", "", ""],
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
                    ["Variant", "Main Hypothesis", "Success Signal", "What It Teaches"],
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
            ],
            "requested_outputs": [
                "Shared invariant",
                "Per-market notes",
                "Per-market hook and script direction",
                "Per-market visual cues",
            ],
        },
        "evidence": [
            {"label": "Source concept", "detail": "Add the original script, product concept, or winning angle.", "source": ""},
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
                    ["Market", "Opening Beat", "Middle Proof", "Close / CTA", "Visual Cue"],
                    [["", "", "", "", ""], ["", "", "", "", ""], ["", "", "", "", ""]],
                ),
            ),
            section(
                "Creative Constraints",
                "List cultural, visual, or language cautions per market.",
                table=blank_table(
                    ["Market", "Do Not Use", "Must Adapt", "Open Risk"],
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
            ],
            "requested_outputs": [
                "Asset list",
                "Purpose of each asset",
                "Creative direction",
                "Production priority",
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
                    ["Asset", "Purpose", "Primary Message", "Format / Ratio", "Owner / Tool", "Priority"],
                    [
                        ["Main image", "", "", "", "", ""],
                        ["Scene image", "", "", "", "", ""],
                        ["Benefit image", "", "", "", "", ""],
                        ["Detail image", "", "", "", "", ""],
                        ["Short video", "", "", "", "", ""],
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
                    ["Asset", "Question", "Success Signal", "What It Changes Next"],
                    [["Main image", "", "", ""], ["Benefit image", "", "", ""], ["Short video", "", "", ""]],
                ),
            ),
            section(
                "Next Action",
                "Give the production order and handoff notes.",
                table=blank_table(
                    ["Priority", "Asset", "Why It Goes First", "Dependency"],
                    [["1", "", "", ""], ["2", "", "", ""], ["3", "", "", ""], ["4", "", "", ""], ["5", "", "", ""]],
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
            ],
        },
        "evidence": [
            {"label": "Source copy blocks", "detail": "List each text block in reading order.", "source": ""},
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
                    ["Source Block", "Function", "Localized Copy", "Length Risk", "Notes"],
                    [["", "", "", "", ""], ["", "", "", "", ""], ["", "", "", "", ""]],
                    "Localized Copy Grid",
                ),
            ),
            section(
                "Structure",
                "Describe text hierarchy and placement logic.",
                table=blank_table(
                    ["Text Layer", "Priority", "Placement Note", "Can Be Shortened?"],
                    [["Headline", "", "", ""], ["Support line", "", "", ""], ["CTA", "", "", ""]],
                ),
            ),
            section(
                "Creative Constraints",
                "List localization cautions, banned phrasing, and readability notes.",
                table=blank_table(
                    ["Constraint", "Localized Rule", "Reason"],
                    [["Banned phrasing", "", ""], ["Tone guardrail", "", ""], ["Layout limit", "", ""], ["Readability note", "", ""]],
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
                    ["Image / Brand", "Dominant Visual Code", "Likely Click Driver", "Weakness", "What To Keep", "What To Avoid"],
                    [["", "", "", "", "", ""], ["", "", "", "", "", ""], ["", "", "", "", "", ""]],
                    "Competitor Comparison",
                ),
            ),
            section(
                "Structure",
                "Convert the benchmark into a revised main-image direction.",
                table=blank_table(
                    ["Layer", "New Direction", "Purpose", "Must Be Visible?"],
                    [["Hero visual", "", "", ""], ["Text treatment", "", "", ""], ["Offer cue", "", "", ""], ["Trust cue", "", "", ""]],
                ),
            ),
            section(
                "Creative Constraints",
                "State what the new main image must avoid and what it must emphasize.",
                table=blank_table(
                    ["Constraint", "Emphasize / Avoid", "Reason"],
                    [["Category cliche", "", ""], ["Clutter risk", "", ""], ["Trust risk", "", ""], ["Readability risk", "", ""]],
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
                "One creator account or several videos from one creator",
                "Top videos",
                "Transcripts",
                "Performance notes",
            ],
            "constraints": [
                "Separate creator-specific advantage from transferable pattern.",
            ],
            "requested_outputs": [
                "Creator playbook",
                "Repeatable formulas",
                "Non-transferable advantages",
                "Adaptation path",
            ],
        },
        "evidence": [
            {"label": "Creator sample set", "detail": "List the creator's top or representative videos.", "source": ""},
        ],
        "sections": [
            section(
                "Executive Conclusion",
                "Summarize the creator's repeatable winning pattern.",
            ),
            section(
                "Structure Logic",
                "Map the creator's recurring content structure.",
                table=blank_table(
                    ["Pattern Area", "What Repeats", "Example Evidence"],
                    [
                        ["Hook formula", "", ""],
                        ["Visual rhythm", "", ""],
                        ["Proof style", "", ""],
                        ["CTA style", "", ""],
                    ],
                ),
            ),
            section(
                "Core Mechanism",
                "Describe why the creator's pattern works.",
            ),
            section(
                "Reusable Formula",
                "Extract what can transfer to another account or product.",
                table=blank_table(
                    ["Layer", "Transferable Pattern", "Why It Transfers", "How To Adapt"],
                    [
                        ["Hook", "", "", ""],
                        ["Pacing", "", "", ""],
                        ["Trust-building", "", "", ""],
                        ["Conversion move", "", "", ""],
                    ],
                ),
            ),
            section(
                "Risks And Adaptation Notes",
                "List the parts that depend on this specific creator.",
                table=blank_table(
                    ["Creator-Specific Advantage", "Why It Does Not Transfer Cleanly"],
                    [["", ""], ["", ""]],
                ),
            ),
            section(
                "Next Action",
                "Describe how to migrate the pattern to the user's product.",
            ),
        ],
    },
    "18": {
        "working_context": {
            "inputs": [
                "2+ competitor accounts",
                "Latest posts or weekly post list",
                "Previous notes if available",
                "Target market",
            ],
            "constraints": [
                "If only one week exists, mark it as baseline rather than trend.",
            ],
            "requested_outputs": [
                "Per-account weekly summary",
                "Cross-account comparison",
                "Notable shifts",
                "Implications for the user",
            ],
        },
        "evidence": [
            {"label": "Account weekly post list", "detail": "Group posts by account and week.", "source": ""},
        ],
        "sections": [
            section(
                "Executive Conclusion",
                "Summarize what changed across the watched competitor accounts this week.",
            ),
            section(
                "Objects To Track",
                "Capture each account's weekly output.",
                table=blank_table(
                    ["Account", "Post Volume", "Winning Post", "Main Theme", "Breakout Signal", "Shift vs Prior Week"],
                    [["", "", "", "", "", ""], ["", "", "", "", "", ""], ["", "", "", "", "", ""]],
                    "Per-Account Weekly Summary",
                ),
            ),
            section(
                "Why They Matter",
                "Interpret the important changes, not just list them.",
                table=blank_table(
                    ["Observed Shift", "Who Changed", "Why It Matters", "Implication"],
                    [["", "", "", ""], ["", "", "", ""], ["", "", "", ""]],
                    "Notable Weekly Shifts",
                ),
            ),
            section(
                "Fields To Capture Next Time",
                "List missing fields needed for stronger weekly comparison.",
            ),
            section(
                "Next Action",
                "State what the user should do this week in response.",
                table=blank_table(
                    ["Action Area", "Recommendation", "Urgency"],
                    [["Watch", "", ""], ["Test", "", ""], ["Ignore", "", ""]],
                    "Weekly Operator Response",
                ),
            ),
        ],
    },
    "19": {
        "working_context": {
            "inputs": [
                "Recent post list",
                "Views, likes, comments, saves, or shares",
                "Post titles / hooks",
                "Content type labels",
            ],
            "constraints": [
                "If metrics are incomplete, keep weak conclusions explicitly labeled.",
            ],
            "requested_outputs": [
                "Performance pattern summary",
                "Winning traits",
                "Losing traits",
                "Next-cycle plan",
            ],
        },
        "evidence": [
            {"label": "Recent post table", "detail": "Paste recent posts with all available performance signals.", "source": ""},
        ],
        "sections": [
            section(
                "Executive Conclusion",
                "State the biggest lesson from the account retro.",
            ),
            section(
                "High-Level Judgment",
                "Summarize what is working and what is not.",
                table=blank_table(
                    ["Pattern", "Result", "Why It Likely Happened"],
                    [["Winning pattern", "", ""], ["Losing pattern", "", ""], ["Unclear pattern", "", ""]],
                ),
            ),
            section(
                "Evidence Clusters",
                "Group content by performance pattern rather than by date alone.",
                table=blank_table(
                    ["Cluster", "Representative Posts", "Shared Traits", "Signal Strength"],
                    [["", "", "", ""], ["", "", "", ""], ["", "", "", ""]],
                    "Performance Clusters",
                ),
            ),
            section(
                "Recommended Action",
                "Translate the retro into do-more / do-less / stop rules.",
                table=blank_table(
                    ["Rule Type", "Recommendation", "Reason"],
                    [["Do more", "", ""], ["Do less", "", ""], ["Stop", "", ""], ["Test next", "", ""]],
                ),
            ),
            section(
                "Open Questions",
                "List which missing data blocks stronger optimization decisions.",
            ),
        ],
    },
}


SCENE_INTAKE = {
    "01": {
        "minimum_evidence": ["One keyword", "At least 5 candidate videos, links, or screenshots"],
        "ideal_evidence": ["15-30 candidates with basic metrics", "Search-result screenshots", "Market and audience note"],
        "ready_checklist": ["Candidate set is from one market", "At least basic performance signals exist", "Useful-for tags can be assigned"],
    },
    "02": {
        "minimum_evidence": ["One category", "One market", "Initial keyword set"],
        "ideal_evidence": ["3-10 patrol keywords", "Prior daily notes", "Preferred alert conditions"],
        "ready_checklist": ["Cadence is defined", "Tracked fields are agreed", "Manual vs automated patrol mode is explicit"],
    },
    "03": {
        "minimum_evidence": ["One keyword or topic", "A candidate pool to rank"],
        "ideal_evidence": ["10+ candidate videos", "Links plus screenshots or transcript notes", "Target product or niche"],
        "ready_checklist": ["Shortlist criteria are clear", "Top 3-5 videos have enough evidence for teardown", "Market is not mixed"],
    },
    "04": {
        "minimum_evidence": ["One video link or storyboard summary"],
        "ideal_evidence": ["Transcript", "Screenshots by beat", "Basic performance context"],
        "ready_checklist": ["Hook, proof, and close can be reconstructed", "At least one adaptation target is known"],
    },
    "05": {
        "minimum_evidence": ["One video or visual summary"],
        "ideal_evidence": ["Transcript", "Frame-by-frame notes", "User product for adaptation"],
        "ready_checklist": ["Visual evidence is sufficient to infer shot language", "Low-confidence gaps are explicit if evidence is thin"],
    },
    "06": {
        "minimum_evidence": ["3+ competitor products or listings"],
        "ideal_evidence": ["Price, rating, and offer snapshots", "Past tracking notes", "Desired review cadence"],
        "ready_checklist": ["Each product has a stable identifier", "Fields to track are defined", "Change interpretation rules are explicit"],
    },
    "07": {
        "minimum_evidence": ["One category or product theme", "Some visible market examples"],
        "ideal_evidence": ["Top content examples", "Competitor product set", "Keyword map by market"],
        "ready_checklist": ["Demand evidence exists", "Saturation read is backed by examples", "Recommendation strength matches evidence depth"],
    },
    "08": {
        "minimum_evidence": ["Comments from at least 2 products"],
        "ideal_evidence": ["20-40 comments per product", "Market context", "Positioning goal"],
        "ready_checklist": ["Comments stay grouped by product", "Repeated phrases can be quoted", "Low-volume caveats are explicit"],
    },
    "09": {
        "minimum_evidence": ["Reference video logic", "User product basics"],
        "ideal_evidence": ["Product images", "Selling points", "Audience and market note"],
        "ready_checklist": ["Invariant logic is identified", "Literal copying risks are listed", "Adapted hook and shot path are writable now"],
    },
    "10": {
        "minimum_evidence": ["Product description or product images"],
        "ideal_evidence": ["Multiple angles", "Selling points", "Target audience", "Desired style"],
        "ready_checklist": ["Video goal is clear", "Visual gaps are labeled", "Hook and proof beats can be designed from available assets"],
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
        "ideal_evidence": ["Source script or concept", "Local audience notes", "Visual asset set"],
        "ready_checklist": ["Invariant is separated from localizable layers", "Each market has a clear hook direction", "Avoid-list exists per market if needed"],
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
        "minimum_evidence": ["One creator account or several videos from one creator"],
        "ideal_evidence": ["Top videos", "Transcripts", "Performance notes"],
        "ready_checklist": ["Repeated patterns appear across multiple videos", "Creator-specific advantages are separated", "Adaptation path for user product is possible"],
    },
    "18": {
        "minimum_evidence": ["2+ competitor accounts", "One weekly batch of posts"],
        "ideal_evidence": ["Prior week notes", "Per-post performance context", "Target market"],
        "ready_checklist": ["Posts are grouped by account and week", "Shift vs prior week can be stated", "Weekly response actions can be prioritized"],
    },
    "19": {
        "minimum_evidence": ["Recent post list", "Some performance signal per post"],
        "ideal_evidence": ["Views, likes, comments, saves, shares", "Hook / title notes", "Content-type labels"],
        "ready_checklist": ["Posts can be clustered by pattern", "Winners and losers are distinguishable", "Next-cycle test rules can be written"],
    },
}


SCENE_OPERATOR_GUIDE = {
    "01": {
        "operator_checklist": [
            "Normalize all candidates into one market before ranking.",
            "Tag each selected video by best reuse purpose: hook, proof, structure, or style.",
            "Keep the rejected pool so later ranking logic can be improved.",
        ],
        "common_failure_modes": [
            "Ranking on views only and ignoring reuse value.",
            "Mixing multiple markets or product intents in one shortlist.",
            "Collecting links without enough hook or proof notes for later teardown.",
        ],
    },
    "02": {
        "operator_checklist": [
            "Lock the patrol cadence before defining the table.",
            "Separate routine fields from alert-trigger fields.",
            "Write the daily summary template before claiming the patrol is reusable.",
        ],
        "common_failure_modes": [
            "Trying to automate before the manual SOP is stable.",
            "Tracking too many fields to sustain daily use.",
            "No clear threshold for what counts as a meaningful change.",
        ],
    },
    "03": {
        "operator_checklist": [
            "Shortlist first, then deep-teardown only the top set.",
            "Use the same lens across all chosen videos so patterns are comparable.",
            "End with creation rules, not only observations.",
        ],
        "common_failure_modes": [
            "Deep-analyzing weak candidates that should have been filtered out earlier.",
            "Using different teardown criteria across videos.",
            "Summarizing patterns without enough per-video evidence.",
        ],
    },
    "04": {
        "operator_checklist": [
            "Reconstruct the video in order: hook, setup, proof, close.",
            "Separate core mechanism from creator-specific surface style.",
            "Write at least one adaptation path before closing the report.",
        ],
        "common_failure_modes": [
            "Confusing visual polish with the true conversion mechanism.",
            "Skipping the close or CTA logic because it looks simple.",
            "Giving abstract praise without reusable takeaways.",
        ],
    },
    "05": {
        "operator_checklist": [
            "State the likely creative intent before writing the inferred prompt.",
            "Translate observed output into prompt blocks, not style buzzwords.",
            "Mark low-confidence guesses when evidence is thin.",
        ],
        "common_failure_modes": [
            "Inventing prompt details not justified by the video.",
            "Only describing visual style without pacing, shot, and VO logic.",
            "Forgetting to rewrite the inferred brief for the user's product.",
        ],
    },
    "06": {
        "operator_checklist": [
            "Fix the product identifiers before tracking changes over time.",
            "Define what counts as a commercial signal, not only a data change.",
            "Keep the dashboard schema minimal enough to maintain weekly.",
        ],
        "common_failure_modes": [
            "Tracking products with inconsistent naming and duplicate rows.",
            "Collecting raw data without interpretation rules.",
            "Watching too many fields and never using the board in practice.",
        ],
    },
    "07": {
        "operator_checklist": [
            "Use both content evidence and product evidence before judging the category.",
            "Separate hot angles from overcrowded angles.",
            "Match recommendation strength to evidence depth.",
        ],
        "common_failure_modes": [
            "Calling a category attractive based on a few flashy videos.",
            "Treating attention heat as proof of durable commercial demand.",
            "Missing whitespace because angle saturation was not mapped explicitly.",
        ],
    },
    "08": {
        "operator_checklist": [
            "Keep comments grouped by product before merging category signals.",
            "Quote repeated user language, not only analyst paraphrases.",
            "Translate pains and desires into product and script implications.",
        ],
        "common_failure_modes": [
            "Mixing one-off complaints with true repeated pains.",
            "Summarizing sentiment without concrete user phrases.",
            "Ignoring the difference between desire, complaint, and trust signal.",
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
            "Use multiple creator samples before declaring a repeatable formula.",
            "Map repeated hook, pacing, proof, and CTA patterns separately.",
            "Explicitly separate transferable pattern from creator advantage.",
        ],
        "common_failure_modes": [
            "Overfitting one breakout video into a full creator formula.",
            "Ignoring trust or identity advantages unique to the creator.",
            "Ending with admiration instead of adaptation rules.",
        ],
    },
    "18": {
        "operator_checklist": [
            "Group posts by account and week before comparing anything.",
            "Highlight weekly shifts, not just weekly totals.",
            "Finish with actions the user should take this week.",
        ],
        "common_failure_modes": [
            "Listing activity without interpreting pattern changes.",
            "Calling something a trend with only one baseline week.",
            "No horizontal comparison across accounts.",
        ],
    },
    "19": {
        "operator_checklist": [
            "Cluster posts by pattern, not just by publish date.",
            "Write explicit do-more, do-less, and stop rules.",
            "Turn the retro into one next-cycle testing plan.",
        ],
        "common_failure_modes": [
            "Reading metrics row by row with no pattern grouping.",
            "Blaming outcomes on vague quality judgments.",
            "Ending the retro without a concrete next test cycle.",
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
