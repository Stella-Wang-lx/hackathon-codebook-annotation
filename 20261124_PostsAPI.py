import pandas as pd
from openai import OpenAI
import os
import time
# ================= Configuration =================
# 1. Your DeepSeek API Key
API_KEY = "XXXX"

# 2. DeepSeek Base URL
BASE_URL = "https://api.deepseek.com"

# 3. Excel File Path
FILE_PATH = r"/data_analysis.xlsx"

# System prompt is codebook_v3.1_en.md, verbatim.
SYSTEM_PROMPT = r"""
## 1\. Research Basis

**Main research question**

Against the backdrop of widespread generative AI adoption, how do hackathon participants construct expectations for creative collaboration through self-presentation and expectations of others on social media?

- **RQ1:** How do hackathon participants communicate their potential value to creative teamwork by presenting their skills, experience, and resources?  
- **RQ2:** What skills and personal qualities do participants expect from prospective teammates, and how do these expectations relate to their self-presentation?  
- **RQ3:** How do participants incorporate generative AI into their presentations of skills, teammate requirements, and expectations for collaboration?

This edition contains 15 binary codes across three themes. It codes explicit expressions of self-presentation, expectations of others, and collaborative expectations in social media texts. Version 6.3 retains the number and structure of codes in v6.2 while clarifying the coding boundaries for technical and non-technical skills, technical inexperience, and disciplinary background.

Morgan et al. (2010) compare narratives about the self and ideal partners in online relationship seeking, using non-exclusive binary codes to examine their relationship. Their approach provides a methodological precedent for distinguishing self-presentation from expectations of others and examining their associations. The collaborative expectations theme and individual codes were developed for this study's questions and hackathon setting.

Morgan, E. M., Richards, T. C., & VanNess, E. M. (2010). Comparing narratives of personal and preferred partner characteristics in online dating advertisements. *Computers in Human Behavior, 26*(5), 883–888. [https\://doi.org/10.1016/j.chb.2010.02.002](https://doi.org/10.1016/j.chb.2010.02.002)

| Theme | Focus | Research question |
| :---- | :---- | :---- |
| A. Self-presentation and positioning (5 codes) | How participants describe what they can offer as collaborators | RQ1. Combined with B for RQ2. A5 addresses RQ3. |
| B. Expectations of others (5 codes) | Who participants want on their team or what kind of team they want to join | RQ2. B3 addresses RQ3. |
| C. Collaborative expectations (5 codes) | What kind of collaboration participants envision and how they expect to create together | Main research question. C5 addresses RQ3. |

## 2\. Code Summary

| ID | Code | Assign 1 when the author |
| :---- | :---- | :---- |
| **A** | **Self-presentation and positioning** |  |
| A1 | Technical skill presentation | Claims skills in programming, development, algorithms, vibe coding for software implementation, UI design, or interaction design |
| A2 | Non-technical skill presentation | Claims skills in product planning, visual design, scriptwriting or content creation, operations, or presentation. Code UI and interaction design as A1. |
| A3 | Presentation of prior achievements and experience | Mentions past projects, hackathon participation, awards, or work produced |
| A4 | Declared technical inexperience | Explicitly describes an inability to code, a weak technical foundation, or no prior technical experience. Self-deprecating phrases such as “clueless humanities newbie” or “humanities rookie” also qualify in the hackathon context when they convey limited ability. |
| A5 | Presentation of AI use competence | Reports AI use skills or experience, AI product development, or model training |
| **B** | **Expectations of others** |  |
| B1 | Technical skill requirements | Seeks teammates skilled in programming, development, vibe coding for software implementation, UI design, or interaction design |
| B2 | Non-technical skill requirements | Seeks teammates skilled in product planning, visual design, scriptwriting or content creation, or operations. Code UI and interaction design as B1. |
| B3 | Generative AI use requirements | Wants teammates who can use generative AI to assist with tasks |
| B4 | Collaborative attitude requirements | Seeks teammates who are responsible, follow through, communicate, or are punctual |
| B5 | Novice inclusion | Explicitly welcomes inexperienced teammates or seeks a beginner-friendly team |
| **C** | **Collaborative expectations** |  |
| C1 | Outcome orientation | Expresses a collaborative goal such as winning an award, completing a project, or delivering a working product |
| C2 | Learning orientation | Expects to gain knowledge or skills or to grow together through collaboration |
| C3 | Creative exploration | Expects to discuss or generate ideas together or jointly explore project directions |
| C4 | Skill complementarity | Explicitly proposes completing a project by combining members' skills or dividing responsibilities |
| C5 | AI-assisted creation | Explicitly expects generative AI to support creative teamwork, improve its efficiency, or address skill gaps |

## 3\. General Coding Rules

### 3.1 Unit and Scope

1. Each target post or comment is one coding unit, uniquely identified by `sample_id`. Apply all 15 codes to each unit.  
2. Code only what the target author explicitly states or endorses. Use parent posts or comments to resolve references, omissions, and brief replies. Attribute skills, experience, and expectations only to the person expressing or endorsing them.  
3. Code statements made during team formation, when considering prospective collaboration, or when recalling team formation expectations. Include actual task allocation, post-event evaluations, or general claims about collaboration only if they explicitly convey relevant self-presentation or collaborative expectations.

### 3.2 Binary Coding Rules (0/1)

| Value | Rule |
| :---- | :---- |
| `1` | At least one explicit statement in the target text meets the inclusion criteria and aligns with the meaning of the code. Retain a verbatim quotation as evidence. |
| `0` | No explicit statement meets the inclusion criteria. This includes silence, mentions that fall short of the criteria, and statements of an opposing position. |

- A unit can receive multiple codes. Count each code at most once per unit.  
- A value of 0 indicates that a qualifying statement was absent. For example, A1=0 leaves programming ability unknown, A5=0 leaves past AI use unknown, and B5=0 leaves willingness to include novices unknown.  
- **Base coding on explicit claims about skills, practice, or limitations.** A major, degree, department, or job title alone is insufficient. A humanities background alone does not trigger A1, A2, or A4, and a computer science major alone does not trigger A1. Apply the same rule to teammate requirements.  
- **Classify the activity described.** Code UI/UX interface and interaction design as technical (A1/B1). Code visual or graphic design, product planning, and scriptwriting as non-technical (A2/B2), provided the text explicitly presents the author's skill or requests it from a teammate. A generic claim such as “I can do design” is insufficient to distinguish A1 from A2.  
- **Interpret vibe coding in context.** An explicit claim of being able to build software, websites, applications, or features through vibe coding qualifies for A1. An explicit request for a teammate with that ability qualifies for B1. Where the text also explicitly indicates competence with generative AI tools, apply A5 or B3 as appropriate. A passing mention, interest, or an intention to learn is insufficient.  
- Interpret grammatical negation in context. “I can't code” qualifies for A4. “I don't want teammates who flake” qualifies for B4. “We don't plan to use AI for development” does not qualify for C5.  
- Code clear conditional expectations. “Experience preferred, but complete beginners are welcome” qualifies for B5. Treat stated preferences as preferences unless the text makes them mandatory.  
- Flag relevant statements for review when the actor, timing, or meaning is unclear. Assign 0 if the evidence remains insufficient after review and record the ambiguity.  
- Code current expectations and explicitly recalled earlier expectations under the same definitions. Keep general statements for contextual rereading unless the author explicitly applies them to their own team formation or collaboration.

### 3.3 Minimum Output and Evidence

The formal wide-format coding table contains one row per text unit. Link to the source data for original texts and parent post or comment relationships.

```
sample_id,source_type,A1,A2,A3,A4,A5,B1,B2,B3,B4,B5,C1,C2,C3,C4,C5
```

Use `post` or `comment` for `source_type`. The 15 code fields must contain only integer 0s or 1s. Maintain a separate evidence table.

| Evidence field | Requirement |
| :---- | :---- |
| `sample_id` | Text ID in the formal coding table |
| `code` | Assigned code (A1–A5, B1–B5, or C1–C5) |
| `quote` | Verbatim evidence that can be matched exactly in the target text |
| `context_quote` | Optional parent post or comment excerpt used to interpret the target text |

Each 1 requires at least one valid quotation. Multiple quotations may support the same code. Track ambiguities in a review list outside the 15 code fields. Retain details such as skill domains, tool names, and experience levels in the original text.

### 3.4 Example Sources

Examples with S-IDs come from the uploaded `posts_coded.csv` and `comments_coded.csv`. The quotations below are English translations. Use the complete context for formal coding and retain verbatim source-language excerpts in the evidence table. Examples labeled “Illustrative” were constructed to explain the rules and must not be cited as empirical data.

## 4\. Theme A. Self-Presentation and Positioning

How participants describe what kind of collaborator they can be.

### A1 \| Technical Skill Presentation

- **Include.** Explicit claims of skills in programming, front-end or back-end development, algorithms, engineering implementation, data processing, UI/UX interface design, and interaction design. Include claims of using vibe coding to implement software, such as building a webpage, app, or feature. Include explicit statements of potential contributions based on these skills.  
- **Exclude.** Academic, educational, or occupational background alone, including computer science or software engineering. Also exclude wanting to learn programming, volunteering for development without claiming relevant skills, proposing an AI project, scriptwriting or general content creation alone, and statements about someone else's technical skills. Mentioning AI tools or general AI use is insufficient without evidence of software implementation.  
- **Positive.** S-C0001 “For front end, I know React. For back end, I know Express.js and FastAPI, and I know a little Java.” The same commenter says, “For UI, I can also use Figma,” which explicitly identifies a UI skill.  
- **Illustrative positive.** “I can vibe code and use AI tools to build a webpage.”  
- **Negative.** S-C0875 “Signing up for development.” The author volunteers for a task without claiming an existing technical skill.  
- **Illustrative negative.** “I can write scripts and stories.” This describes a non-technical contribution under this codebook.  
- **Boundary.** Code UI and interaction design as A1. Apply A2 as well only when the text also explicitly presents a separate skill such as product planning or visual or graphic design. Vibe coding for software implementation can qualify for both A1 and A5 when the text meets both definitions.

### A2 \| Non-Technical Skill Presentation

- **Include.** Explicit claims of skills relevant to creative teamwork, including product planning, visual or graphic design, operations, business analysis, pitching, presentation, scriptwriting, or content creation. Code scriptwriting when authors explicitly offer it as a skill they can contribute. Occupational or disciplinary background alone is insufficient.  
- **Exclude.** UI/UX interface and interaction design (A1). Also exclude background labels such as humanities or a major outside computer science, personal interests or traits, identity alone, and wanting a product, design, or writing role without claiming the relevant skill. “Non-technical” is an operational category for the division of labor in hackathon software development. These activities may require specialized expertise.  
- **Positive.** S-C0048 “I can pitch and do product work.” The wording conveys an ability to make those contributions.  
- **Illustrative positive.** “I can write scripts and handle the story and copy for the project.”  
- **Illustrative negative.** “I'd like to learn some product design” conveys a desire to learn. “I'm a humanities student” conveys a disciplinary background.  
- **Boundary.** “For UI, I can also use Figma” qualifies for A1 as interface design. The generic phrase “I can do design” gives insufficient evidence of the design type.

### A3 \| Presentation of Prior Achievements and Experience

- **Include.** Past projects, work produced, hackathon participation, awards, or accomplishments from relevant practice that the author presents in relation to prospective collaboration.  
- **Exclude.** Lists of skills, schools, or job titles alone, future participation or award goals, work by someone else, and a first-time participation statement with no information about prior practice.  
- **Positive.** S-C0012 “Longtime hackathon participant. I've won awards.”  
- **Illustrative negative.** “I hope to win a prize this time.” This expresses a future goal.

### A4 \| Declared Technical Inexperience

- **Include.** Explicit statements that the author cannot code, lacks a technical foundation, has limited relevant development experience, or faces a specific technical limitation. Code limitations in one skill even when the author has another technical skill. In hackathon technical collaboration, explicitly self-deprecating descriptions such as “clueless humanities newbie” also qualify when they communicate limited ability, even without the words “I can't code.”  
- **Exclude.** A humanities or non-computer-science background alone, first-time hackathon participation, omission of skills, student status, and generic terms such as “newbie” or “beginner” with no technical context.  
- **Positive.** S-C0005 “On the back end, I'm limited to CRUD and that sort of thing.” This explicitly delimits the author's back-end skills.  
- **Illustrative positive.** “I'm a clueless humanities newbie looking for hackathon teammates” conveys limited ability through self-deprecation in context. “I'm a humanities student and I can't code at all” explicitly states a technical limitation.  
- **Negative.** S-P0136 “I'm currently doing a master's in computer science.” This supplies academic background only.  
- **Illustrative negative.** “I'm a humanities student and I'd like to join a hackathon.” This conveys background and an intention to participate.  
- **Boundary.** A1 and A4 can co-occur. “I can do front-end work, but I can't do back-end work” conveys both a skill and a limitation. In “clueless humanities newbie,” the explicit self-deprecation supports the code.

### A5 \| Presentation of Generative AI Use Competence

- **Include.** Explicit reports of past or current generative AI tool use to perform or assist with concrete tasks, including coding, design, copywriting, and prototyping. Success and independent completion are optional. Following the broad v6.1 definition, include claims such as “I know how to use AI” or “I have experience with prompts,” and explicit reports of having undertaken AI product development or model training.  
- **Exclude.** Tool names, interest in AI, an AI project direction, learning AI, or an intention to use AI in the future, when these appear alone.  
- **Illustrative positive.** “I've used Cursor to build a webpage.”  
- **Negative.** S-C0409 “I'm leaning toward developing an AI application.” This states a project direction.  
- **Boundary.** Assign A1, A2, or A3 only if the text separately supports the relevant skill or prior accomplishment. An explicit claim of using vibe coding for software implementation can qualify for A1 and A5. An intention to learn vibe coding is insufficient. Given the broad A5 definition, reread original texts when interpreting results to distinguish AI product development or model training from generative AI use in other creative tasks.

## 5\. Theme B. Expectations of Others

Who participants want on their team or what kind of team they want to join.

### B1 \| Technical Skill Requirements

- **Include.** Explicit requests for teammates skilled in programming, development, algorithms, engineering implementation, UI/UX interface design, interaction design, or vibe coding for software implementation. Include recruiting explicitly for such responsibilities, such as front-end development or UI and interaction design.  
- **Exclude.** The author's own skills, requests for a computing-related background alone, unspecified experience, project development needs without a corresponding teammate requirement, and generic AI tool competence without a software implementation requirement.  
- **Positive.** S-C0006 “Jumping in here to look for a teammate who can do front-end development.”  
- **Illustrative positive.** “I'm looking for a teammate who can do UI interaction design.”  
- **Negative.** S-C0001 “For front end, I know React.” This presents the author's own skill.  
- **Boundary.** Code UI and interaction design requirements as B1. If the author explicitly asks for someone who can build an app through vibe coding, assess B1 and B3 independently against the source wording.

### B2 \| Non-Technical Skill Requirements

- **Include.** Explicit requests for teammates who can contribute product planning, visual or graphic design, operations, business analysis, pitching, scriptwriting, or other work outside software implementation. Include recruitment for these specific responsibilities.  
- **Exclude.** UI/UX interface or interaction design (B1), the author's own non-technical skills, disciplinary background alone, general working qualities such as punctuality and responsiveness, and recruitment without a specific contribution.  
- **Illustrative positive.** “I'm looking for a teammate who can do product planning and pitch the business idea.” / “Looking for someone who can write scripts and copy.”  
- **Negative.** S-C0431 “Looking for reliable teammates.” This expresses a collaborative attitude requirement.  
- **Boundary.** Code professional presentation and pitching as B2. Code willingness to communicate and timely responsiveness in everyday teamwork as B4. Apply both when both are explicit. An explicit request for both UI design and product planning can receive B1 and B2. “Design” alone is insufficient to classify the skill.

### B3 \| Generative AI Use Requirements

- **Include.** Explicit requirements or preferences for teammates who can use generative AI tools to assist with practical tasks such as development, design, or writing. Code explicit use competence as a selection criterion regardless of whether teammates are expected to have completed prior work with the tools.  
- **Exclude.** A desire to build an AI product together, the author's own AI tool experience, and proposals to use AI as a team that do not specify teammate competence.  
- **Illustrative positive.** “I hope my teammates know how to use Cursor to assist with development.”  
- **Illustrative negative.** “Looking for an algorithms teammate who can train large models.” This identifies a technical specialty and provides insufficient evidence of a generative AI use requirement.

### B4 \| Collaborative Attitude Requirements

- **Include.** Explicit preferences for teammates who are reliable, keep commitments, take responsibility or initiative, communicate, respond promptly, follow through, or commit enough time.  
- **Exclude.** Descriptions of the author's own traits or attitude, event dates or locations, general invitations to get in touch, and technical or design skill requirements.  
- **Positive.** S-C0431 “Looking for reliable teammates.”  
- **Negative.** S-C0022 “I'm an ENFJ and easy to communicate with.” This describes the author.

### B5 \| Novice Inclusion

- **Include.** Explicitly welcoming teammates with little or no experience, or seeking a team that allows or welcomes novice participation. Conditional openness qualifies.  
- **Exclude.** Calling oneself a novice, a generic request to join a team, a general “everyone is welcome,” openness to people from other schools or companies, and asking to join without specifying novice inclusion.  
- **Illustrative positive.** “Experience preferred, but complete beginners are welcome.” / “I can't code and hope to find a team willing to help beginners get started.”  
- **Negative.** S-C0423 “People from other schools or companies are welcome too.” This expresses openness across institutions.  
- **Boundary.** Use this code for both recruiters' expressions of openness and novices' requests for beginner-friendly teams. These statements capture expressed expectations. Actual inclusion requires separate evidence.

## 6\. Theme C. Collaborative Expectations

What kind of collaboration participants envision and how they expect to create together.

### C1 \| Outcome Orientation

- **Include.** Explicit goals for proposed teamwork, such as completing an artifact, building a usable product, delivering a project, winning an award, or achieving a competitive result. A completion goal alone qualifies.  
- **Exclude.** Existing work or past awards, personal motives without a connection to team collaboration, official event requirements, and generic statements such as “looking for a team” or “let's do a project together” without an explicit outcome goal.  
- **Illustrative positive.** “I hope we can build a usable product before the competition ends and ideally win a prize.”  
- **Negative.** S-C0012 “Longtime hackathon participant. I've won awards.” This reports a past achievement.

### C2 \| Learning Orientation

- **Include.** Explicit expectations of gaining knowledge, improving skills, exchanging experiences, learning from teammates, or developing together through collaboration. This can be an individual learning benefit of teamwork or a shared learning goal.  
- **Exclude.** Studying independently, planning to teach oneself a skill, entering the event to strengthen one's profile, and seeking experienced teammates without expressing a learning expectation.  
- **Illustrative positive.** “I'd like to find teammates to learn AI development together and exchange experiences.”  
- **Negative.** S-P0001 “I want to improve my skills and build my profile through a hackathon.” This excerpt alone leaves the connection to teamwork unclear.

### C3 \| Creative Exploration

- **Include.** Explicit expectations of brainstorming together, discussing ideas, posing questions, exploring project directions, or jointly developing and revising a product concept. Include explicit invitations for teammates to help shape ideas.  
- **Exclude.** Personal product ideas alone, recruiting people solely to execute a settled plan, generic mentions of communication or doing a project together, and implementation or trial and error without a link to joint ideation or exploration.  
- **Positive.** S-P0166 “Happy to brainstorm together.”  
- **Negative.** S-C0262 “I want to build a supply chain product.” This states an individual idea.

### C4 \| Skill Complementarity

- **Include.** Explicit proposals to combine or complement members' different skills or resources, or to complete a shared project by dividing responsibilities. Planned divisions of labor qualify.  
- **Exclude.** Recruitment for a single role, lists of individual skills, mentions of multiple people's skills without a complementary or task-sharing relationship, general hopes of teamwork, and mutual help without a link between distinct contributions.  
- **Positive.** S-C0165 “For now I'll focus on learning the front-end part, and I hope to find a teammate with complementary skills.”  
- **Illustrative.** “I'll handle product and pitching, and I'm looking for a teammate to take charge of development so we can build the prototype.”  
- **Negative.** S-C0006 “Jumping in here to look for a teammate who can do front-end development.” This specifies a skill requirement without explaining how contributions would fit together.  
- **Boundary.** B1 and B2 identify the skills sought. C4 identifies how different contributions are expected to fit together. Apply each code whose criteria are met. C4 captures proposed arrangements. Actual knowledge integration and collaboration effectiveness require separate evidence.

### C5 \| AI-Assisted Creation

- **Include.** Explicit expectations of using generative AI for idea generation, product design, code development, prototyping, or other stages of team creation. Include plans to improve efficiency, fill individual or team skill gaps, take on otherwise difficult creative tasks, or enable members with limited skills to contribute. One member's planned AI use for a team task qualifies. Explicitly linking AI's ability to compensate for skill gaps to proposed teamwork qualifies even without naming a particular stage.  
- **Exclude.** Personal past AI use, a preference for AI-capable teammates without a proposed creative practice, AI as a product feature or research subject, generic claims that AI is useful, wanting to build AI products, and claims of efficiency or skill-gap compensation unrelated to the proposed teamwork.  
- **Illustrative positive.** “We want to use generative AI to design the product and build the prototype together.” / “We plan to use AI to speed up coding.” / “We could use AI-assisted coding so teammates who can't code can help build the prototype.”  
- **Negative.** S-C0409 “I'm leaning toward developing an AI application.” This states what the author wants to build and leaves the use of AI as a creative tool unspecified.  
- **Boundary.** Use the same code for expected efficiency gains and compensation for skill gaps. When A4 and C5 co-occur, check the original text for an explicit link between AI use and the stated limitation. Assign A4 only when the author explicitly presents their own technical inexperience. C5 records expectations. Actual efficiency gains or reduced skill gaps require separate evidence.

---

**Coding checks.** Confirm that the table has all 15 code columns, that each valid text unit has 15 binary values, and that each 1 has verifiable source evidence. Keep additional analytical labels out of the table. Spot-check A1/A2 for UI and interaction design versus scriptwriting, A1/A5 co-occurrence for vibe coding, and A4 for the distinction between “humanities student” and self-deprecating phrases such as “clueless humanities newbie” or “humanities rookie.” Check that A and B codes are not inferred from disciplinary background alone. Also check the boundaries between A1/A2 and A3, B1 and B3, A4 and B5, B1/B2 and C4, and A5/B3/C5. Recode according to v3.1 before using the labels for analysis.

**Interpreting results.** For RQ1, examine A codes and their combinations. For RQ2, examine B codes and A × B co-occurrence within the same unit, comparing same-type and cross-type skill presentation and requests, as well as A4 × B5. Use associations among A, B, and C to examine how self-positioning and teammate expectations relate to collaborative goals and methods, such as A3 × C1, A4 × C2, B5 × C2, and B1/B2 × C4. For RQ3, compare the occurrence of A5, B3, and C5 and how they co-occur across themes. Reread A4 × C5 and B5 × C5 cases to examine whether authors expect AI to compensate for skill gaps. Same-type A and B co-occurrence alone is insufficient to establish a preference for similarity, and cross-type co-occurrence alone is insufficient to establish an intention to seek complementarity. Use C4 and the original wording to assess both. Reread B5 texts to distinguish recruiters welcoming novices from novices seeking friendly teams. Analyze posts and comments separately. Co-occurrence shows associations between textual expressions. Actual team formation, collaboration outcomes, and causal effects of AI require other evidence."""
# ===========================================

# Codebook v3.1 binary codes, in the order given in section 3.3.
CODE_IDS = [
    "A1", "A2", "A3", "A4", "A5",
    "B1", "B2", "B3", "B4", "B5",
    "C1", "C2", "C3", "C4", "C5",
]


def parse_codes(text):
    """Take the 15 binary codes from one model response."""
    for raw_line in text.splitlines():
        line = raw_line.strip().strip("`")
        if not line or line.lower().startswith("sample_id"):
            continue
        parts = [part.strip() for part in line.split(",")]
        if len(parts) == 15 and all(part in {"0", "1"} for part in parts):
            return parts
        # Codebook wide-format row: sample_id, source_type, then the 15 codes.
        if len(parts) == 17 and all(part in {"0", "1"} for part in parts[-15:]):
            return parts[-15:]
    return ["Error_Missing"] * len(CODE_IDS)


def get_annotation(client, target_text, context_text=None):
    """
    按 codebook v3.1 标注，返回 A1–C5 共 15 个 0/1。
    """
    if pd.isna(target_text) or str(target_text).strip() == "":
        return ["0"] * len(CODE_IDS)

    clean_target = str(target_text).replace("\n", " ")[:1000]
    instruction = (
        "Code the target text with all 15 codes. "
        "Return one line only, 15 comma-separated integers (0 or 1), in this order: "
        + ",".join(CODE_IDS)
        + ". No other text."
    )

    if context_text:
        clean_context = str(context_text).replace("\n", " ")[:1000]
        user_content = f"{instruction}\n\nContext:\n{clean_context}\n\nTarget text:\n{clean_target}"
    else:
        user_content = f"{instruction}\n\nTarget text:\n{clean_target}"

    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_content},
            ],
            temperature=0,
            stream=False,
        )
        res = response.choices[0].message.content.strip()
        parsed = parse_codes(res)
        if parsed[0] == "Error_Missing":
            print(f"❌ Parse Error: {res}")
        return parsed

    except Exception as e:
        print(f"❌ API Error: {e}")
        return ["Error"] * len(CODE_IDS)


def _code_cell(value):
    if value in {"0", "1"}:
        return int(value)
    return value


def auto_label_data():
    print("=" * 40)
    print("Starting annotation...")
    print("=" * 40)

    client = OpenAI(api_key=API_KEY, base_url=BASE_URL)

    try:
        print(f"Reading file: {FILE_PATH}")
        df = pd.read_excel(FILE_PATH, sheet_name="Sheet1")
        if "sample_text" not in df.columns:
            raise ValueError("Input sheet must contain a sample_text column.")

        total_count = len(df)
        print(f"Processing {total_count} texts...\n")

        records = []
        for index, row in df.iterrows():
            current_num = index + 1
            sample_text = row.get("sample_text", "")
            if pd.isna(sample_text):
                sample_text = ""
            source_type = row.get("source_type", "")
            if pd.isna(source_type):
                source_type = ""

            print(f"[{current_num}/{total_count}] Coding one text...")
            codes = get_annotation(client, sample_text, context_text=None)
            record = {
                "sample_text": sample_text,
                "source_type": source_type,
            }
            for code, value in zip(CODE_IDS, codes):
                record[code] = _code_cell(value)
            records.append(record)
            print(f"   {dict(zip(CODE_IDS, codes))}")
            time.sleep(0.1)

        out = pd.DataFrame(records, columns=["sample_text", "source_type", *CODE_IDS])
        output_path = os.path.join(os.path.dirname(FILE_PATH), "Annotated_Hackathon_v3.1.xlsx")
        out.to_excel(output_path, index=False)

        print("=" * 40)
        print(f"Saved {len(out)} rows, {len(out.columns)} columns.")
        print(f"Saved to: {output_path}")
        print("=" * 40)

    except Exception as e:
        print(f"\nProgram Error: {e}")


if __name__ == "__main__":
    # Clear proxies
    os.environ.pop("http_proxy", None)
    os.environ.pop("https_proxy", None)

    auto_label_data()