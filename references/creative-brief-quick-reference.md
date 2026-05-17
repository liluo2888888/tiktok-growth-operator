# 创意制作简报速查

Use this file when you want the creative-production half of the skill without scanning all 19 scenes.

It focuses on scenes 09-16:

- reference-video adaptation
- image-to-video 制作简报
- replication pipeline design
- multi-style testing matrix
- multi-market localization
- launch asset family planning
- image-copy localization
- competitor main-image benchmarking

## Fast Pick

当你已经知道自己需要哪类制作简报时，直接把下面任意一句复制进 Codex：

- Scene 09 - Reference-Video Replication Brief: `按场景 09 执行：把一条对标视频改造成适合新产品的复刻制作简报，先锁定不该改的 winning logic，再重写 hook、证明和收口。`
- Scene 10 - Product-Image-To-Video Brief: `按场景 10 执行：仅基于产品图设计一版短视频制作简报，明确视频类型、证明镜头、CTA 和资产缺口，不要假设用户已经有额外素材。`
- Scene 11 - Hot-Video Replication Pipeline: `按场景 11 执行：搭一个可重复跑的热点视频复制 pipeline，把发现、筛选、深拆、入池和生产交接拆成明确阶段和门槛。`
- Scene 12 - One-Product Multi-Style Testing Matrix: `按场景 12 执行：为一个产品做多风格测试矩阵，先锁 invariant message，再设计真正有差异的测试风格，并写出每个变体要学什么。`
- Scene 13 - Multi-Market Localization Pack: `按场景 13 执行：把一个产品概念做成多市场本地化包，拆清共享产品真相和各市场的 hook、语气、禁区，不要只做直译。`
- Scene 14 - Launch Asset Family Pack: `按场景 14 执行：设计一套上新素材家族，先定义最小可上线资产集，再给每个素材分配一个转化职责，并排出制作优先级。`
- Scene 15 - Image Translation Brief: `按场景 15 执行：做图片文案翻译与本地化制作简报，区分信息性文案和转化型文案，保留层级关系，并说明新文案如何适配原布局。`
- Scene 16 - Competitor Main-Image Benchmark: `按场景 16 执行：对标竞品主图并定义更强方向，先说清点击场景，再总结类目共性、差异机会和一版可执行的超车制作简报。`

## How To Choose Quickly

- Choose `09` when you already have one strong reference video and want an adapted replication production brief.
- Choose `10` when you mainly have product images or product facts and need a first video concept from scratch.
- Choose `11` when you need a repeatable hot-video intake and replication system, not one production brief.
- Choose `12` when one product needs several clearly different creative directions to test.
- Choose `13` when one product concept must be translated into several markets without doing naive literal localization.
- Choose `14` when you need a launch asset family with production priority and role assignment.
- Choose `15` when the main task is translating or localizing image copy while preserving layout logic.
- Choose `16` when the main task is benchmarking competitor main images and defining a stronger visual route.

## Missing Evidence That Usually Blocks Good Output

- `09`: no clear reference logic, no product truth, no restriction on what cannot be copied literally
- `10`: no asset inventory, no proof material, no clarity on whether talent or hands-on footage exists
- `11`: no discovery scope, no ranking rule, no cadence owner
- `12`: no invariant message, no audience split, no definition of what each variant is supposed to teach
- `13`: no market nuance evidence, no native review context, no banned claims or compliance notes
- `14`: no asset dependency map, no priority rule, no owner for each production lane
- `15`: no source layout capture, no target-language limits, no reviewer for local tone and fit
- `16`: no click context, no category baseline set, no proof for why the proposed direction is stronger

## Scene 09 - Reference-Video Replication Brief

- Deliverable Type: `creation_brief`
- Use When: Turn a reference video into an adapted replication brief.
- 中文直呼请求: `按场景 09 执行：把一条对标视频改造成适合新产品的复刻制作简报，先锁定不该改的 winning logic，再重写 hook、证明和收口。`

### 只复制这一句

`按场景 09 执行：把一条对标视频改造成适合新产品的复刻制作简报，先锁定不该改的 winning logic，再重写 hook、证明和收口。`

### Main Runner

`python scripts/run_operator_workflow.py --mode scene --scene 09 --project "<project-name>" --output-root ".\tmp\reference-replication-brief"`

### Minimum Inputs

- Reference video logic
- User product basics

### Ideal Inputs

- 产品图片
- 卖点
- 目标人群与市场备注

### Workflow Focus

- Lock the invariant logic from the reference before adapting anything.
- Swap product-specific pieces one layer at a time: hook, proof, close.
- End with a filmable or promptable shot order.

### 制作简报填写区块

- Target: `Field | Answer | Why It Matters`
- Sample Rows: `Target audience |  | ` / `Conversion goal |  | `
- Message: `Layer | Reference Logic | Adapted Version | Required Product Evidence`
- Sample Rows: `Hook |  |  | ` / `Problem framing |  |  | `
- Structure: `Shot / Beat | What Happens | Purpose | Asset / Talent Needed | Line / Overlay | Dependency / Risk`
- Sample Rows: `1 |  |  |  |  | ` / `2 |  |  |  |  | `
- Creative Constraints: `Constraint | Keep / Change | Reason | Owner / Check`
- Sample Rows: `Visual identity |  |  | ` / `Claim language |  |  | `
- Production Handoff: `Handoff Item | Locked Decision | Owner | Blocking Risk`
- Sample Rows: `Hook direction |  |  | ` / `Proof asset |  |  | `

### Output Must Include

- Invariant reference logic is clearly separated from adapted layers.
- The adapted production brief is specific enough to produce from.
- Literal-copy risks are called out explicitly.

### 中文 Prompt Scaffold

- 按场景 09 执行：把一条对标视频改造成适合新产品的复刻制作简报，先锁定不该改的 winning logic，再重写 hook、证明和收口。
- 先把我提供的材料整理成这组输入：Reference video or breakdown, User product details, Selling points, Target audience / market。
- 如果证据不足，先明确缺口再继续。最低开工证据：Reference video logic, User product basics。
- 最终必须产出：Replication brief, Adapted hook, Adapted proof sequence, Shot order, Optional voiceover draft, Production handoff。
- 输出必须可直接给运营、拆解、脚本、测试或交付使用，优先给表格、排序逻辑、复用规则和下一步动作。

## Scene 10 - Product-Image-To-Video Brief

- Deliverable Type: `creation_brief`
- Use When: Design a short-form video brief from product images.
- 中文直呼请求: `按场景 10 执行：仅基于产品图设计一版短视频制作简报，明确视频类型、证明镜头、CTA 和资产缺口，不要假设用户已经有额外素材。`

### 只复制这一句

`按场景 10 执行：仅基于产品图设计一版短视频制作简报，明确视频类型、证明镜头、CTA 和资产缺口，不要假设用户已经有额外素材。`

### Main Runner

`python scripts/run_operator_workflow.py --mode scene --scene 10 --project "<project-name>" --output-root ".\tmp\product-image-to-video-brief"`

### Minimum Inputs

- Product description or product images

### Ideal Inputs

- 多角度素材
- 卖点
- 目标人群
- 期望风格

### Workflow Focus

- Choose the video type before writing scenes.
- Use the available images to design proof beats, not just beauty shots.
- Leave explicit visual-gap notes when the asset set is weak.

### 制作简报填写区块

- Target: `Field | Answer | Why It Matters`
- Sample Rows: `Audience |  | ` / `Market |  | `
- Message: `Layer | Draft | Supported By Which Asset | Missing Proof?`
- Sample Rows: `Core promise |  |  | ` / `Primary proof |  |  | `
- Structure: `Beat | Visual Use | Voiceover / Overlay | Purpose | Asset / Talent Source | Missing Asset?`
- Sample Rows: `Hook |  |  |  |  | ` / `Proof 1 |  |  |  |  | `
- Creative Constraints: `Constraint Type | Detail | Risk If Ignored | Fix Path`
- Sample Rows: `Visual style |  |  | ` / `Tone |  |  | `
- Production Handoff: `Handoff Item | Locked Decision | Open Gap | Owner`
- Sample Rows: `Hook frame |  |  | ` / `Primary proof beat |  |  | `
- Next Action: `Test Variable | Why Test It First | What Asset Change Is Needed`
- Sample Rows: `Hook framing |  | ` / `Proof order |  | `

### Output Must Include

- The production brief is compatible with the available asset set.
- Hook, proof beats, and CTA are all defined.
- Any visual gaps are explicit instead of hidden inside optimistic wording.

### 中文 Prompt Scaffold

- 按场景 10 执行：仅基于产品图设计一版短视频制作简报，明确视频类型、证明镜头、CTA 和资产缺口，不要假设用户已经有额外素材。
- 先把我提供的材料整理成这组输入：Product images or product description, Selling points, Target audience, Market language。
- 如果证据不足，先明确缺口再继续。最低开工证据：Product description or product images。
- 最终必须产出：Video concept, Shot structure, Voiceover structure, Style keywords, Test variables, Production handoff。
- 输出必须可直接给运营、拆解、脚本、测试或交付使用，优先给表格、排序逻辑、复用规则和下一步动作。

## Scene 11 - Hot-Video Replication Pipeline

- Deliverable Type: `testing_matrix`
- Use When: Build a repeated pipeline from hot-video discovery to new creative directions.
- 中文直呼请求: `按场景 11 执行：搭一个可重复跑的热点视频复制 pipeline，把发现、筛选、深拆、入池和生产交接拆成明确阶段和门槛。`

### 只复制这一句

`按场景 11 执行：搭一个可重复跑的热点视频复制 pipeline，把发现、筛选、深拆、入池和生产交接拆成明确阶段和门槛。`

### Main Runner

`python scripts/run_operator_workflow.py --mode scene --scene 11 --project "<project-name>" --output-root ".\tmp\hot-video-replication-pipeline"`

### Minimum Inputs

- One category or product and a testing goal

### Ideal Inputs

- Hot-video shortlist
- Product assets
- Weekly operating cadence

### Workflow Focus

- Define the pipeline stages and decision gates clearly.
- Decide what makes a hot video worth entering the replication queue.
- Tie the workflow to a repeatable daily or weekly cadence.

### 制作简报填写区块

- Core Invariant: `Invariant | Rule | Why It Cannot Drift`
- Sample Rows: `Entry threshold |  | ` / `Teardown lens |  | `
- Variable Matrix: `Stage | Input | Decision Rule | Asset Need | Owner | Output | SLA / Cadence`
- Sample Rows: `Discovery |  |  |  |  |  | ` / `Shortlist |  |  |  |  |  | `
- What To Learn: `Cycle Question | Why It Matters | How To Measure | What Decision It Changes | If Confirmed | If Rejected`
- Sample Rows: ` |  |  |  |  | ` / ` |  |  |  |  | `
- Execution Handoff: `Queue Artifact | Who Owns It | Ready When | Blocking Risk`
- Sample Rows: `Discovery shortlist |  |  | ` / `Teardown packet |  |  | `

### Output Must Include

- Pipeline stages and gates are explicit.
- The replication queue has ranking logic, not only intake logic.
- The workflow is light enough to repeat on a real cadence.

### 中文 Prompt Scaffold

- 按场景 11 执行：搭一个可重复跑的热点视频复制 pipeline，把发现、筛选、深拆、入池和生产交接拆成明确阶段和门槛。
- 先把我提供的材料整理成这组输入：Category or product, Keyword set, Target market, Testing goal。
- 如果证据不足，先明确缺口再继续。最低开工证据：One category or product and a testing goal。
- 最终必须产出：Candidate ladder, Replication brief bank, Production queue, Testing recommendation, Weekly runbook。
- 输出必须可直接给运营、拆解、脚本、测试或交付使用，优先给表格、排序逻辑、复用规则和下一步动作。

## Scene 12 - One-Product Multi-Style Testing Matrix

- Deliverable Type: `testing_matrix`
- Use When: Create a multi-style testing matrix for one product.
- 中文直呼请求: `按场景 12 执行：为一个产品做多风格测试矩阵，先锁 invariant message，再设计真正有差异的测试风格，并写出每个变体要学什么。`

### 只复制这一句

`按场景 12 执行：为一个产品做多风格测试矩阵，先锁 invariant message，再设计真正有差异的测试风格，并写出每个变体要学什么。`

### Main Runner

`python scripts/run_operator_workflow.py --mode scene --scene 12 --project "<project-name>" --output-root ".\tmp\multi-style-testing-matrix"`

### Minimum Inputs

- One product
- One market
- One core message

### Ideal Inputs

- Product images
- Selling points
- Audience segments
- Style constraints

### Workflow Focus

- Lock the invariant message before varying style.
- Ensure each style meaningfully changes hook, proof, or audience lens.
- Define success signals before recommending test order.

### 制作简报填写区块

- Core Invariant: `Invariant Type | Locked Element | Why It Must Stay Fixed`
- Sample Rows: `Core message |  | ` / `Product truth |  | `
- Variable Matrix: `Style | Audience Lens | Hook | Proof Device | Visual Style | CTA | Asset Need | Production Complexity | Primary Hypothesis | Why Test It`
- Sample Rows: `Style 1 |  |  |  |  |  |  |  |  | ` / `Style 2 |  |  |  |  |  |  |  |  | `
- Expected Effect: `Variant | Expected Attention Shift | Expected Conversion Shift | Main Risk`
- Sample Rows: `Style 1 |  |  | ` / `Style 2 |  |  | `
- What To Learn: `Variant | Main Hypothesis | Success Signal | What It Teaches | If Confirmed | If Rejected`
- Sample Rows: `Style 1 |  |  |  |  | ` / `Style 2 |  |  |  |  | `
- Execution Handoff: `Variant | First Asset Need | Owner | Ready For Test When`
- Sample Rows: `Style 1 |  |  | ` / `Style 2 |  |  | `
- Next Action: `Priority | Variant | Why It Goes Now`
- Sample Rows: `1 |  | ` / `2 |  | `

### Output Must Include

- The invariant message stays fixed across rows.
- Variants differ in a meaningful strategic way.
- Each row has a clear learning goal and test priority.

### 中文 Prompt Scaffold

- 按场景 12 执行：为一个产品做多风格测试矩阵，先锁 invariant message，再设计真正有差异的测试风格，并写出每个变体要学什么。
- 先把我提供的材料整理成这组输入：One product, One target market, Product images or selling points。
- 如果证据不足，先明确缺口再继续。最低开工证据：One product, One market, One core message。
- 最终必须产出：Style matrix, Hook variants, Proof variants, Testing order, Variant handoff。
- 输出必须可直接给运营、拆解、脚本、测试或交付使用，优先给表格、排序逻辑、复用规则和下一步动作。

## Scene 13 - Multi-Market Localization Pack

- Deliverable Type: `creation_brief`
- Use When: Localize a product concept across multiple markets.
- 中文直呼请求: `按场景 13 执行：把一个产品概念做成多市场本地化包，拆清共享产品真相和各市场的 hook、语气、禁区，不要只做直译。`

### 只复制这一句

`按场景 13 执行：把一个产品概念做成多市场本地化包，拆清共享产品真相和各市场的 hook、语气、禁区，不要只做直译。`

### Main Runner

`python scripts/run_operator_workflow.py --mode scene --scene 13 --project "<project-name>" --output-root ".\tmp\multi-market-localization-pack"`

### Minimum Inputs

- One product
- At least 2 target markets

### Ideal Inputs

- 源脚本或创意概念
- 本地受众备注
- 视觉素材集

### Workflow Focus

- Separate shared product truth from market-specific adaptation layers.
- Write each market's hook, tone, and avoid-list explicitly.
- Keep localization tied to conversion context, not literal translation.

### 制作简报填写区块

- Target: `Layer | Invariant | Needs Localization? | Why`
- Sample Rows: `Core product promise |  | No | ` / `Hook wording |  | Yes | `
- Audience: `Market | Viewer Expectation | Key Trigger | Key Risk`
- Sample Rows: ` |  |  | ` / ` |  |  | `
- Message: `Market | Audience Cue | Hook Direction | Language / Tone | Proof Angle | Avoid`
- Sample Rows: ` |  |  |  |  | ` / ` |  |  |  |  | `
- Structure: `Market | Opening Beat | Middle Proof | Close / CTA | Visual Cue | Talent / Asset Need | Localization Dependency`
- Sample Rows: ` |  |  |  |  |  | ` / ` |  |  |  |  |  | `
- Creative Constraints: `Market | Do Not Use | Must Adapt | Open Risk | Review Owner`
- Sample Rows: ` |  |  |  | ` / ` |  |  |  | `
- Production Handoff: `Market | What Is Ready To Script | What Still Needs Native Review | Owner`
- Sample Rows: ` |  |  | ` / ` |  |  | `

### Output Must Include

- Shared invariant logic is separated from local layers.
- Each target market has a concrete hook direction.
- Avoid-lists or local-risk notes are visible where relevant.

### 中文 Prompt Scaffold

- 按场景 13 执行：把一个产品概念做成多市场本地化包，拆清共享产品真相和各市场的 hook、语气、禁区，不要只做直译。
- 先把我提供的材料整理成这组输入：One product, 2+ target markets, Source concept or script, Local audience notes。
- 如果证据不足，先明确缺口再继续。最低开工证据：One product, At least 2 target markets。
- 最终必须产出：Shared invariant, Per-market notes, Per-market hook and script direction, Per-market visual cues, Market handoff。
- 输出必须可直接给运营、拆解、脚本、测试或交付使用，优先给表格、排序逻辑、复用规则和下一步动作。

## Scene 14 - Launch Asset Family Pack

- Deliverable Type: `testing_matrix`
- Use When: Design a coordinated launch asset family.
- 中文直呼请求: `按场景 14 执行：设计一套上新素材家族，先定义最小可上线资产集，再给每个素材分配一个转化职责，并排出制作优先级。`

### 只复制这一句

`按场景 14 执行：设计一套上新素材家族，先定义最小可上线资产集，再给每个素材分配一个转化职责，并排出制作优先级。`

### Main Runner

`python scripts/run_operator_workflow.py --mode scene --scene 14 --project "<project-name>" --output-root ".\tmp\launch-asset-family-pack"`

### Minimum Inputs

- Product description

### Ideal Inputs

- Product images
- Selling points
- Platform constraints
- Launch priority

### Workflow Focus

- Define the minimum viable asset family before adding nice-to-have assets.
- Assign one conversion job to each asset.
- Order production by launch leverage, not by creative preference.

### 制作简报填写区块

- Core Invariant: `Invariant | Definition | Why It Must Stay Consistent`
- Sample Rows: `Core promise |  | ` / `Visual code |  | `
- Variable Matrix: `Asset | Purpose | Primary Message | Format / Ratio | Owner / Tool | Dependency / Blocking Risk | Priority`
- Sample Rows: `Main image |  |  |  |  |  | ` / `Scene image |  |  |  |  |  | `
- What To Learn: `Asset | Question | Success Signal | What It Changes Next | If It Wins`
- Sample Rows: `Main image |  |  |  | ` / `Benefit image |  |  |  | `
- Production Handoff: `Asset Family Item | Ready Spec | Missing Input | Owner`
- Sample Rows: `Main image |  |  | ` / `Scene image |  |  | `
- Next Action: `Priority | Asset | Why It Goes First | Dependency | Owner`
- Sample Rows: `1 |  |  |  | ` / `2 |  |  |  | `

### Output Must Include

- Each asset has one explicit job in the launch system.
- Production order is prioritized.
- The family shares one coherent creative direction.

### 中文 Prompt Scaffold

- 按场景 14 执行：设计一套上新素材家族，先定义最小可上线资产集，再给每个素材分配一个转化职责，并排出制作优先级。
- 先把我提供的材料整理成这组输入：Product description, Optional product images, Selling points, Target market。
- 如果证据不足，先明确缺口再继续。最低开工证据：Product description。
- 最终必须产出：Asset list, Purpose of each asset, Creative direction, Production priority, Production handoff。
- 输出必须可直接给运营、拆解、脚本、测试或交付使用，优先给表格、排序逻辑、复用规则和下一步动作。

## Scene 15 - Image Translation Brief

- Deliverable Type: `creation_brief`
- Use When: Translate and localize image copy for conversion.
- 中文直呼请求: `按场景 15 执行：做图片文案翻译与本地化制作简报，区分信息性文案和转化型文案，保留层级关系，并说明新文案如何适配原布局。`

### 只复制这一句

`按场景 15 执行：做图片文案翻译与本地化制作简报，区分信息性文案和转化型文案，保留层级关系，并说明新文案如何适配原布局。`

### Main Runner

`python scripts/run_operator_workflow.py --mode scene --scene 15 --project "<project-name>" --output-root ".\tmp\image-translation-brief"`

### Minimum Inputs

- Source image text or OCR
- Target language

### Ideal Inputs

- Image layout
- Product context
- Market note
- Conversion goal

### Workflow Focus

- Separate literal information from persuasive copy blocks.
- Preserve hierarchy while adapting for local conversion language.
- Add layout notes so the localized copy can actually fit.

### 制作简报填写区块

- Target: `Field | Answer | Why It Matters`
- Sample Rows: `Target market |  | ` / `Target language |  | `
- Message: `Source Block | Function | Localized Copy | Length Risk | Layout Fit | Native Review Needed? | Notes`
- Sample Rows: ` |  |  |  |  |  | ` / ` |  |  |  |  |  | `
- Structure: `Text Layer | Priority | Placement Note | Can Be Shortened? | Design Action`
- Sample Rows: `Headline |  |  |  | ` / `Support line |  |  |  | `
- Creative Constraints: `Constraint | Localized Rule | Reason | Review Owner`
- Sample Rows: `Banned phrasing |  |  | ` / `Tone guardrail |  |  | `
- Production Handoff: `Handoff Item | Localized Decision | Needs Review? | Owner`
- Sample Rows: `Headline block |  |  | ` / `Support copy |  |  | `

### Output Must Include

- Headline, support copy, and literal information are separated.
- Localized copy is compatible with the original layout constraints.
- Conversion tone is adapted for the target market instead of translated blindly.

### 中文 Prompt Scaffold

- 按场景 15 执行：做图片文案翻译与本地化制作简报，区分信息性文案和转化型文案，保留层级关系，并说明新文案如何适配原布局。
- 先把我提供的材料整理成这组输入：Source image text or OCR, Target language, Product context, Target market。
- 如果证据不足，先明确缺口再继续。最低开工证据：Source image text or OCR, Target language。
- 最终必须产出：Translated copy, Layout notes, Text hierarchy, Localization cautions, Render handoff。
- 输出必须可直接给运营、拆解、脚本、测试或交付使用，优先给表格、排序逻辑、复用规则和下一步动作。

## Scene 16 - Competitor Main-Image Benchmark

- Deliverable Type: `creation_brief`
- Use When: Benchmark competitor main images and define a stronger direction.
- 中文直呼请求: `按场景 16 执行：对标竞品主图并定义更强方向，先说清点击场景，再总结类目共性、差异机会和一版可执行的超车制作简报。`

### 只复制这一句

`按场景 16 执行：对标竞品主图并定义更强方向，先说清点击场景，再总结类目共性、差异机会和一版可执行的超车制作简报。`

### Main Runner

`python scripts/run_operator_workflow.py --mode scene --scene 16 --project "<project-name>" --output-root ".\tmp\main-image-benchmark"`

### Minimum Inputs

- 2+ competitor images
- User image or product

### Ideal Inputs

- Platform click context
- Category norms
- Known strengths or weaknesses

### Workflow Focus

- Describe the click context before judging the images.
- Identify both category norms and sharp opportunities to differ.
- End with a more useful brief than generic 'make it cleaner' advice.

### 制作简报填写区块

- Target: `Field | Answer | Why It Matters`
- Sample Rows: `Platform |  | ` / `Category |  | `
- Message: `Image / Brand | Dominant Visual Code | Likely Click Driver | Weakness | What To Keep | What To Avoid | Execution Note`
- Sample Rows: ` |  |  |  |  |  | ` / ` |  |  |  |  |  | `
- Structure: `Layer | New Direction | Purpose | Must Be Visible? | Asset Need`
- Sample Rows: `Hero visual |  |  |  | ` / `Text treatment |  |  |  | `
- Creative Constraints: `Constraint | Emphasize / Avoid | Reason | Owner / Check`
- Sample Rows: `Category cliche |  |  | ` / `Clutter risk |  |  | `
- Production Handoff: `Handoff Item | Decision | Owner | Risk Before Design`
- Sample Rows: `Hero concept |  |  | ` / `Text hierarchy |  |  | `

### Output Must Include

- The benchmark is grounded in comparable category context.
- Likely click drivers are identified explicitly.
- The final production brief is sharper than generic advice such as make it cleaner.

### 中文 Prompt Scaffold

- 按场景 16 执行：对标竞品主图并定义更强方向，先说清点击场景，再总结类目共性、差异机会和一版可执行的超车制作简报。
- 先把我提供的材料整理成这组输入：Competitor main images, User image or product, Platform and category context。
- 如果证据不足，先明确缺口再继续。最低开工证据：2+ competitor images, User image or product。
- 最终必须产出：Competitor comparison, Design weakness map, Outperform strategy, Revised main-image brief, Design handoff。
- 输出必须可直接给运营、拆解、脚本、测试或交付使用，优先给表格、排序逻辑、复用规则和下一步动作。
