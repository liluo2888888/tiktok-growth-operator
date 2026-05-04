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
                    ["Field", "Answer"],
                    [
                        ["Target audience", ""],
                        ["Conversion goal", ""],
                        ["Reference asset", ""],
                        ["User product", ""],
                    ],
                ),
            ),
            section(
                "Audience",
                "Describe the audience and what they need to believe.",
            ),
            section(
                "Message",
                "Rewrite the hook and proof logic for the user's product.",
                table=blank_table(
                    ["Layer", "Reference Logic", "Adapted Version"],
                    [
                        ["Hook", "", ""],
                        ["Problem framing", "", ""],
                        ["Proof device", "", ""],
                        ["Close / CTA", "", ""],
                    ],
                ),
            ),
            section(
                "Structure",
                "Give an execution-ready shot order.",
                table=blank_table(
                    ["Shot / Beat", "What Happens", "Purpose"],
                    [["1", "", ""], ["2", "", ""], ["3", "", ""], ["4", "", ""]],
                    "Replication Shot Order",
                ),
            ),
            section(
                "Creative Constraints",
                "List what cannot be copied literally and what must change for the user product.",
            ),
            section(
                "Next Action",
                "State whether this brief is ready for scripting, filming, or prompting.",
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
                    ["Field", "Answer"],
                    [
                        ["Audience", ""],
                        ["Market", ""],
                        ["Conversion goal", ""],
                        ["Video type", ""],
                    ],
                ),
            ),
            section(
                "Audience",
                "Describe what the audience must feel or understand quickly.",
            ),
            section(
                "Message",
                "Define the core promise and proof path.",
            ),
            section(
                "Structure",
                "Map the shot flow from opening to close.",
                table=blank_table(
                    ["Beat", "Visual Use", "Voiceover / Overlay", "Purpose"],
                    [["Hook", "", "", ""], ["Proof 1", "", "", ""], ["Proof 2", "", "", ""], ["Close", "", "", ""]],
                ),
            ),
            section(
                "Creative Constraints",
                "Specify style keywords, rendering guardrails, and what to avoid.",
                table=blank_table(
                    ["Constraint Type", "Detail"],
                    [["Visual style", ""], ["Tone", ""], ["Must show", ""], ["Must avoid", ""]],
                    "Render Guardrails",
                ),
            ),
            section(
                "Next Action",
                "List the next two test variables to try.",
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
                bullets=[
                    "What makes a video worth entering the pipeline?",
                    "What is the minimum reuse threshold?",
                ],
            ),
            section(
                "Variable Matrix",
                "Map the pipeline from discovery to production.",
                table=blank_table(
                    ["Stage", "Input", "Decision Rule", "Output"],
                    [
                        ["Discovery", "", "", ""],
                        ["Shortlist", "", "", ""],
                        ["Teardown", "", "", ""],
                        ["Replication brief", "", "", ""],
                        ["Production queue", "", "", ""],
                    ],
                    "Pipeline Stages",
                ),
            ),
            section(
                "Expected Effect",
                "Explain what this pipeline should improve operationally.",
            ),
            section(
                "What To Learn",
                "State what each cycle should teach the operator.",
                table=blank_table(
                    ["Cycle Question", "Why It Matters", "How To Measure"],
                    [["", "", ""], ["", "", ""], ["", "", ""]],
                ),
            ),
            section(
                "Next Action",
                "Give the first weekly implementation sequence.",
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
                    ["Invariant Type", "Locked Element"],
                    [["Core message", ""], ["Product truth", ""], ["Target outcome", ""]],
                ),
            ),
            section(
                "Variable Matrix",
                "Build the full testing matrix.",
                table=blank_table(
                    ["Style", "Audience Lens", "Hook", "Proof Device", "Visual Style", "CTA", "Why Test It"],
                    [
                        ["Style 1", "", "", "", "", "", ""],
                        ["Style 2", "", "", "", "", "", ""],
                        ["Style 3", "", "", "", "", "", ""],
                        ["Style 4", "", "", "", "", "", ""],
                    ],
                    "Multi-Style Testing Matrix",
                ),
            ),
            section(
                "Expected Effect",
                "Explain what each style variation is expected to change.",
            ),
            section(
                "What To Learn",
                "Define the learning agenda from the matrix.",
                table=blank_table(
                    ["Variant", "Main Hypothesis", "Success Signal"],
                    [["Style 1", "", ""], ["Style 2", "", ""], ["Style 3", "", ""], ["Style 4", "", ""]],
                ),
            ),
            section(
                "Next Action",
                "Rank the order of testing and explain why.",
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
                    ["Layer", "Invariant", "Needs Localization?"],
                    [
                        ["Core product promise", "", "No"],
                        ["Hook wording", "", "Yes"],
                        ["Talent / scene cue", "", "Yes"],
                        ["CTA tone", "", "Yes"],
                    ],
                ),
            ),
            section(
                "Audience",
                "Describe how audience expectation changes across markets.",
            ),
            section(
                "Message",
                "Adapt the hook and message by market.",
                table=blank_table(
                    ["Market", "Audience Cue", "Hook Direction", "Language / Tone", "Avoid"],
                    [["", "", "", "", ""], ["", "", "", "", ""], ["", "", "", "", ""]],
                    "Per-Market Localization Grid",
                ),
            ),
            section(
                "Structure",
                "Describe any structural changes by market if needed.",
            ),
            section(
                "Creative Constraints",
                "List cultural, visual, or language cautions per market.",
            ),
            section(
                "Next Action",
                "State what is ready for localized scripting versus what still needs research.",
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
            ),
            section(
                "Variable Matrix",
                "Map each asset to its job.",
                table=blank_table(
                    ["Asset", "Purpose", "Primary Message", "Format / Ratio", "Priority"],
                    [
                        ["Main image", "", "", "", ""],
                        ["Scene image", "", "", "", ""],
                        ["Benefit image", "", "", "", ""],
                        ["Detail image", "", "", "", ""],
                        ["Short video", "", "", "", ""],
                    ],
                    "Launch Asset Family",
                ),
            ),
            section(
                "Expected Effect",
                "Explain how the asset set works together.",
            ),
            section(
                "What To Learn",
                "State what should be learned from launch testing.",
            ),
            section(
                "Next Action",
                "Give the production order and handoff notes.",
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
            ),
            section(
                "Audience",
                "Describe what the target viewer needs from the copy.",
            ),
            section(
                "Message",
                "Translate each block with hierarchy preserved.",
                table=blank_table(
                    ["Source Block", "Function", "Localized Copy", "Notes"],
                    [["", "", "", ""], ["", "", "", ""], ["", "", "", ""]],
                    "Localized Copy Grid",
                ),
            ),
            section(
                "Structure",
                "Describe text hierarchy and placement logic.",
                table=blank_table(
                    ["Text Layer", "Priority", "Placement Note"],
                    [["Headline", "", ""], ["Support line", "", ""], ["CTA", "", ""]],
                ),
            ),
            section(
                "Creative Constraints",
                "List localization cautions, banned phrasing, and readability notes.",
            ),
            section(
                "Next Action",
                "State whether the asset is ready for rendering or needs copy review.",
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
                    ["Field", "Answer"],
                    [["Platform", ""], ["Category", ""], ["User asset", ""], ["Competitor count", ""]],
                ),
            ),
            section(
                "Audience",
                "Describe the click context and viewer expectation.",
            ),
            section(
                "Message",
                "Compare the competitor approaches.",
                table=blank_table(
                    ["Image / Brand", "Dominant Visual Code", "Likely Click Driver", "Weakness", "Keep / Avoid"],
                    [["", "", "", "", ""], ["", "", "", "", ""], ["", "", "", "", ""]],
                    "Competitor Comparison",
                ),
            ),
            section(
                "Structure",
                "Convert the benchmark into a revised main-image direction.",
            ),
            section(
                "Creative Constraints",
                "State what the new main image must avoid and what it must emphasize.",
            ),
            section(
                "Next Action",
                "Leave an execution-ready brief for design or generation.",
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
    return preset
