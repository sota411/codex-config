"""Public-artifact tests for the repo-eli5 v2 learning page contract."""

from __future__ import annotations

import subprocess
import tempfile
import unittest
from pathlib import Path

from validate_learning_html import browser_smoke_file, find_browser, validate_source

TEST_REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
TEST_SOURCE_FILE = (
    TEST_REPOSITORY_ROOT
    / "user-skills"
    / "repo-eli5"
    / "scripts"
    / "validate_learning_html.py"
)
TEST_SOURCE_URI = TEST_SOURCE_FILE.as_uri()
TEST_REVISION = subprocess.check_output(
    ["git", "-C", str(TEST_REPOSITORY_ROOT), "rev-parse", "HEAD"],
    text=True,
).strip()
TEST_TREE_REVISION = subprocess.check_output(
    ["git", "-C", str(TEST_REPOSITORY_ROOT), "rev-parse", f"{TEST_REVISION}^{{tree}}"],
    text=True,
).strip()


def source_reference(number: int) -> str:
    return f"{TEST_SOURCE_FILE}:{11 + number}"


def teaching_unit(number: int) -> str:
    return f"""    <article data-teaching-unit="concept-{number}">
      <h2>概念{number}は入力を結果へ変える</h2>
      <p data-concept-intro>まず、入力を受け取って結果へ変える仕組みがあります。</p>
      <figure data-visual-kind="diagram">
        <svg role="img" aria-labelledby="concept-{number}-title concept-{number}-desc" viewBox="0 0 640 320">
          <title id="concept-{number}-title">概念{number}の流れ</title>
          <desc id="concept-{number}-desc">入力が処理され、結果になるまでを示す。</desc>
          <rect width="640" height="320"></rect>
        </svg>
        <figcaption>この図は代表的な流れだけを示します。</figcaption>
      </figure>
      <p data-diagram-reading>左から読むと、入力が処理を通って結果になります。</p>
      <details data-evidence-group>
        <summary>コード上の根拠を見る</summary>
        <p data-evidence-kind="fact"><span data-evidence-description>概念{number}の処理を実装しています。</span><a href="{TEST_SOURCE_URI}"><code data-source-ref>{source_reference(number)}</code></a></p>
      </details>
    </article>"""


def quiz_question(number: int, *, hidden: bool) -> str:
    hidden_attribute = " hidden" if hidden else ""
    return f"""        <fieldset data-quiz-question data-question-kind="choice" data-correct="q{number}-a" tabindex="-1"{hidden_attribute}>
          <legend>概念{number}の説明として正しいものはどれですか。</legend>
          <div>
            <label><input type="radio" name="q{number}" value="q{number}-a">入力を処理して結果へ変える</label>
            <label><input type="radio" name="q{number}" value="q{number}-b">入力を保存せず捨てる</label>
            <label><input type="radio" name="q{number}" value="q{number}-c">結果を入力へ戻す</label>
            <label><input type="radio" name="q{number}" value="q{number}-d">何も処理しない</label>
          </div>
          <button type="button" data-quiz-action="check">答えを見る</button>
          <button type="button" data-quiz-action="next" hidden>次の問題へ</button>
          <p data-quiz-feedback role="status" aria-live="polite" aria-atomic="true"></p>
          <div data-answer-panel hidden>正解は「入力を処理して結果へ変える」です。</div>
        </fieldset>"""


DIAGRAM_UNITS = "\n".join(teaching_unit(number) for number in range(1, 4))
QUIZ_QUESTIONS = "\n".join(
    quiz_question(number, hidden=number > 1) for number in range(1, 4)
)

VALID_PAGE = f"""<!doctype html>
<html lang="ja">
<head>
  <meta charset="utf-8"><title>Sample repository</title>
  <style>
    * {{ box-sizing: border-box; }}
    body {{ margin: 0; }}
    figure {{ margin: 0; overflow-x: auto; }}
    figure svg {{ display: block; min-width: 640px; }}
    @media (prefers-reduced-motion: reduce) {{ * {{ scroll-behavior: auto; }} }}
    @media print {{ button {{ display: none; }} }}
  </style>
</head>
<body data-repo-eli5-page="v2" data-repo-eli5-mode="repository">
  <main>
    <header data-learning-section="introduction">
      <h1>入力を一つの結果へ変えるrepositoryです</h1>
      <p data-repo-summary>入力を受け取り、三つの仕事を通して結果へ変えます。</p>
      <dl data-repo-meta>
        <dt>対象</dt><dd data-repo-root>{TEST_REPOSITORY_ROOT}</dd>
        <dt>Branch</dt><dd data-repo-branch>main</dd>
        <dt>Commit</dt><dd data-repo-revision>{TEST_REVISION}</dd>
      </dl>
    </header>
    <section data-learning-section="explanation">
{DIAGRAM_UNITS}
      <aside data-evidence-kind="unverified">実際の外部サービスには接続していません。</aside>
    </section>
    <section data-learning-section="quiz" data-repo-eli5-quiz>
      <h2>三つの仕組みを4択で確かめる</h2>
      <p data-quiz-progress role="status" aria-live="polite" aria-atomic="true">問題 1 / 3</p>
      <form>
{QUIZ_QUESTIONS}
      </form>
      <div data-quiz-complete tabindex="-1" hidden>
        <p>確認は完了です。</p>
        <button type="button" data-quiz-action="reset">最初から解き直す</button>
      </div>
      <noscript><style>[data-quiz-question][hidden], [data-answer-panel][hidden] {{ display: block !important; }}</style>クイズの回答確認にはJavaScriptが必要です。問題と解説はすべて表示されています。</noscript>
    </section>
  </main>
  <script data-repo-eli5-controller>
    document.addEventListener("DOMContentLoaded", () => {{
      const quiz = document.querySelector("[data-repo-eli5-quiz]");
      const questions = Array.from(quiz.querySelectorAll("[data-quiz-question]"));
      const progress = quiz.querySelector("[data-quiz-progress]");
      const complete = quiz.querySelector("[data-quiz-complete]");
      const reset = quiz.querySelector('[data-quiz-action="reset"]');
      let current = 0;

      const showQuestion = (index) => {{
        current = index;
        questions.forEach((question, questionIndex) => {{
          question.hidden = questionIndex !== current;
        }});
        complete.hidden = true;
        progress.textContent = `問題 ${{current + 1}} / ${{questions.length}}`;
        questions[current].focus();
      }};

      const resetQuestion = (question) => {{
        question.removeAttribute("data-state");
        question.querySelector("[data-quiz-feedback]").textContent = "";
        question.querySelector("[data-answer-panel]").hidden = true;
        question.querySelector('[data-quiz-action="next"]').hidden = true;
        question.querySelector('[data-quiz-action="check"]').disabled = false;
        question.querySelectorAll('input[type="radio"]').forEach((input) => {{
          input.checked = false;
          input.disabled = false;
        }});
      }};

      questions.forEach((question, index) => {{
        const check = question.querySelector('[data-quiz-action="check"]');
        const next = question.querySelector('[data-quiz-action="next"]');
        const feedback = question.querySelector("[data-quiz-feedback]");
        const answerPanel = question.querySelector("[data-answer-panel]");

        check.addEventListener("click", () => {{
          const selected = question.querySelector('input[type="radio"]:checked');
          if (!selected) {{
            feedback.textContent = "選択肢を一つ選んでください。";
            return;
          }}
          const correct = selected.value === question.dataset.correct;
          question.dataset.state = correct ? "correct" : "incorrect";
          feedback.textContent = correct ? "正解です。理由を確認してください。" : "不正解です。正解と理由を確認してください。";
          question.querySelectorAll('input[type="radio"]').forEach((input) => {{
            input.disabled = true;
          }});
          answerPanel.hidden = false;
          next.hidden = false;
          check.disabled = true;
          next.focus();
        }});

        next.addEventListener("click", () => {{
          if (index + 1 < questions.length) {{
            showQuestion(index + 1);
            return;
          }}
          questions[index].hidden = true;
          complete.hidden = false;
          progress.textContent = "確認完了";
          complete.focus();
        }});
      }});

      reset.addEventListener("click", () => {{
        questions.forEach(resetQuestion);
        showQuestion(0);
      }});

      questions.forEach((question, index) => {{
        question.hidden = index !== 0;
      }});
    }});
  </script>
</body>
</html>
"""


class LearningPageContractTests(unittest.TestCase):
    def test_complete_v2_repository_page_passes(self) -> None:
        self.assertEqual(validate_source(VALID_PAGE), [])

    def test_v1_page_identifier_fails(self) -> None:
        errors = validate_source(
            VALID_PAGE.replace('data-repo-eli5-page="v2"', 'data-repo-eli5-page="v1"')
        )

        self.assertTrue(any("v2" in error for error in errors), errors)

    def test_repository_mode_requires_three_teaching_units(self) -> None:
        two_units = VALID_PAGE.replace(teaching_unit(3), "", 1)

        errors = validate_source(two_units)

        self.assertTrue(any("3章" in error for error in errors), errors)

    def test_each_unit_requires_intro_visual_reading_order(self) -> None:
        out_of_order = VALID_PAGE.replace(
            "      <p data-concept-intro>まず、入力を受け取って結果へ変える仕組みがあります。</p>",
            "      <p data-diagram-reading>先に結論だけを置きます。</p>",
            1,
        ).replace(
            "      <p data-diagram-reading>左から読むと、入力が処理を通って結果になります。</p>",
            "      <p data-concept-intro>後から仕組みを説明します。</p>",
            1,
        )

        errors = validate_source(out_of_order)

        self.assertTrue(any("説明、図、読み方" in error for error in errors), errors)

    def test_each_unit_requires_non_empty_intro_and_reading(self) -> None:
        empty_copy = VALID_PAGE.replace(
            "<p data-concept-intro>まず、入力を受け取って結果へ変える仕組みがあります。</p>",
            "<p data-concept-intro></p>",
            1,
        ).replace(
            "<p data-diagram-reading>左から読むと、入力が処理を通って結果になります。</p>",
            "<p data-diagram-reading></p>",
            1,
        )

        errors = validate_source(empty_copy)

        self.assertTrue(
            any("章 1" in error and "説明本文" in error for error in errors), errors
        )
        self.assertTrue(
            any("章 1" in error and "読み方" in error for error in errors), errors
        )

    def test_each_unit_requires_a_fact_and_source_reference(self) -> None:
        missing_evidence = VALID_PAGE.replace(
            f'<p data-evidence-kind="fact"><span data-evidence-description>概念2の処理を実装しています。</span><a href="{TEST_SOURCE_URI}"><code data-source-ref>{source_reference(2)}</code></a></p>',
            "<p>根拠なし</p>",
            1,
        )

        errors = validate_source(missing_evidence)

        self.assertTrue(
            any("章 2" in error and "根拠" in error for error in errors), errors
        )

    def test_each_fact_requires_its_own_source_reference(self) -> None:
        source_less_fact = VALID_PAGE.replace(
            "      </details>",
            """        <p data-evidence-kind="fact"><span data-evidence-description>別の確認済み事実です。</span></p>
      </details>""",
            1,
        )

        errors = validate_source(source_less_fact)

        self.assertTrue(
            any(
                "章 1" in error and "各fact" in error and "source" in error
                for error in errors
            ),
            errors,
        )

    def test_evidence_must_follow_reading_and_contain_facts(self) -> None:
        intro = "      <p data-concept-intro>まず、入力を受け取って結果へ変える仕組みがあります。</p>"
        evidence = f"""      <details data-evidence-group>
        <summary>コード上の根拠を見る</summary>
        <p data-evidence-kind="fact"><span data-evidence-description>概念1の処理を実装しています。</span><a href="{TEST_SOURCE_URI}"><code data-source-ref>{source_reference(1)}</code></a></p>
      </details>"""
        fact = f'<p data-evidence-kind="fact"><span data-evidence-description>概念1の処理を実装しています。</span><a href="{TEST_SOURCE_URI}"><code data-source-ref>{source_reference(1)}</code></a></p>'
        unit = teaching_unit(1)
        evidence_first_unit = unit.replace(evidence, "", 1).replace(
            intro, f"{evidence}\n{intro}", 1
        )
        fact_outside_unit = unit.replace(f"        {fact}\n", "", 1).replace(
            "      </details>", f"      </details>\n      {fact}", 1
        )

        order_errors = validate_source(VALID_PAGE.replace(unit, evidence_first_unit, 1))
        containment_errors = validate_source(
            VALID_PAGE.replace(unit, fact_outside_unit, 1)
        )

        self.assertTrue(
            any("説明、図、読み方、根拠" in error for error in order_errors),
            order_errors,
        )
        self.assertTrue(
            any("章 1" in error and "根拠欄" in error for error in containment_errors),
            containment_errors,
        )

    def test_source_reference_requires_real_file_line_and_matching_link(self) -> None:
        valid_reference = (
            f'<a href="{TEST_SOURCE_URI}"><code data-source-ref>'
            f"{source_reference(1)}</code></a>"
        )
        invalid_reference = VALID_PAGE.replace(
            valid_reference,
            '<a href="file:///not-a-file"><code data-source-ref>not-a-file</code></a>',
            1,
        )
        missing_link = VALID_PAGE.replace(
            valid_reference,
            f"<code data-source-ref>{source_reference(1)}</code>",
            1,
        )

        invalid_errors = validate_source(invalid_reference)
        missing_link_errors = validate_source(missing_link)

        self.assertTrue(
            any("source reference" in error for error in invalid_errors), invalid_errors
        )
        self.assertTrue(
            any("file://" in error for error in missing_link_errors),
            missing_link_errors,
        )

    def test_repository_metadata_requires_non_empty_summary_and_branch(self) -> None:
        empty_summary = VALID_PAGE.replace(
            "<p data-repo-summary>入力を受け取り、三つの仕事を通して結果へ変えます。</p>",
            "<p data-repo-summary></p>",
            1,
        )
        empty_branch = VALID_PAGE.replace(
            "<dd data-repo-branch>main</dd>",
            "<dd data-repo-branch></dd>",
            1,
        )

        summary_errors = validate_source(empty_summary)
        branch_errors = validate_source(empty_branch)

        self.assertTrue(
            any("summary" in error for error in summary_errors), summary_errors
        )
        self.assertTrue(
            any("branch" in error for error in branch_errors), branch_errors
        )

    def test_revision_must_identify_a_commit_object(self) -> None:
        tree_revision = VALID_PAGE.replace(TEST_REVISION, TEST_TREE_REVISION, 1)

        errors = validate_source(tree_revision)

        self.assertTrue(any("commit" in error for error in errors), errors)

    def test_each_unit_requires_non_empty_fact_description_and_caption(self) -> None:
        empty_fact = VALID_PAGE.replace(
            "<span data-evidence-description>概念1の処理を実装しています。</span>",
            "<span data-evidence-description></span>",
            1,
        )
        empty_caption = VALID_PAGE.replace(
            "<figcaption>この図は代表的な流れだけを示します。</figcaption>",
            "<figcaption></figcaption>",
            1,
        )

        fact_errors = validate_source(empty_fact)
        caption_errors = validate_source(empty_caption)

        self.assertTrue(
            any("章 1" in error and "根拠の説明" in error for error in fact_errors),
            fact_errors,
        )
        self.assertTrue(
            any("章 1" in error and "caption" in error for error in caption_errors),
            caption_errors,
        )

    def test_each_unit_requires_one_folded_evidence_group(self) -> None:
        unfolded = VALID_PAGE.replace("<details data-evidence-group>", "<details>", 1)

        errors = validate_source(unfolded)

        self.assertTrue(
            any("章 1" in error and "折りたたみ" in error for error in errors), errors
        )

    def test_repository_mode_requires_three_accessible_diagrams(self) -> None:
        missing_diagram = VALID_PAGE.replace(' data-visual-kind="diagram"', "", 1)

        errors = validate_source(missing_diagram)

        self.assertTrue(any("図が1つ" in error for error in errors), errors)

    def test_simple_diff_can_use_one_accessible_table(self) -> None:
        table_unit = f"""    <article data-teaching-unit="change">
      <h2>出力形式が新しくなる</h2>
      <p data-concept-intro>変更前と変更後を比べると、利用者に見える差が分かります。</p>
      <table data-visual-kind="table">
        <caption>変更前後の比較</caption>
        <thead><tr><th scope="col">観点</th><th scope="col">変更前</th><th scope="col">変更後</th></tr></thead>
        <tbody><tr><th scope="row">出力</th><td>旧形式</td><td>新形式</td></tr></tbody>
      </table>
      <p data-diagram-reading>右の列が変更後の動きです。</p>
      <details data-evidence-group><summary>コード上の根拠を見る</summary>
        <p data-evidence-kind="fact"><span data-evidence-description>変更後の処理を実装しています。</span><a href="{TEST_SOURCE_URI}"><code data-source-ref>{source_reference(1)}</code></a></p>
      </details>
    </article>"""
        source = VALID_PAGE.replace(
            'data-repo-eli5-mode="repository"', 'data-repo-eli5-mode="diff"'
        ).replace(DIAGRAM_UNITS, table_unit)

        self.assertEqual(validate_source(source), [])

    def test_repository_quiz_requires_three_choice_questions(self) -> None:
        two_questions = VALID_PAGE.replace(quiz_question(3, hidden=True), "", 1)
        reflection = VALID_PAGE.replace(
            'data-question-kind="choice"', 'data-question-kind="reflection"', 1
        )

        count_errors = validate_source(two_questions)
        kind_errors = validate_source(reflection)

        self.assertTrue(any("3問" in error for error in count_errors), count_errors)
        self.assertTrue(any("choice" in error for error in kind_errors), kind_errors)

    def test_every_quiz_question_requires_exactly_four_choices(self) -> None:
        three_choices = VALID_PAGE.replace(
            '            <label><input type="radio" name="q1" value="q1-d">何も処理しない</label>\n',
            "",
            1,
        )

        errors = validate_source(three_choices)

        self.assertTrue(any("4つ" in error for error in errors), errors)

    def test_every_quiz_question_requires_a_non_empty_reason(self) -> None:
        empty_reason = VALID_PAGE.replace(
            "<div data-answer-panel hidden>正解は「入力を処理して結果へ変える」です。</div>",
            "<div data-answer-panel hidden></div>",
            1,
        )

        errors = validate_source(empty_reason)

        self.assertTrue(
            any("問題 1" in error and "理由" in error for error in errors), errors
        )

    def test_quiz_requires_one_question_at_a_time_and_accessible_feedback(self) -> None:
        simultaneous = VALID_PAGE.replace(
            'data-correct="q2-a" tabindex="-1" hidden',
            'data-correct="q2-a" tabindex="-1"',
            1,
        )
        inaccessible = VALID_PAGE.replace(
            ' aria-live="polite" aria-atomic="true"></p>', "></p>", 1
        )

        simultaneous_errors = validate_source(simultaneous)
        inaccessible_errors = validate_source(inaccessible)

        self.assertTrue(any("最初の1問だけ" in error for error in simultaneous_errors))
        self.assertTrue(any("aria-live" in error for error in inaccessible_errors))

    def test_quiz_requires_hidden_completion_and_reset_control(self) -> None:
        source = VALID_PAGE.replace(
            ' data-quiz-complete tabindex="-1" hidden', "", 1
        ).replace(
            '<button type="button" data-quiz-action="reset">最初から解き直す</button>',
            "<span>最初から解き直す</span>",
            1,
        )

        errors = validate_source(source)

        self.assertTrue(any("完了領域" in error for error in errors))
        self.assertTrue(any("reset" in error for error in errors))

    def test_remote_script_and_executable_attribute_fail(self) -> None:
        source = VALID_PAGE.replace(
            "<main>",
            '<main onclick="alert(1)"><script src="https://example.com/app.js"></script>',
            1,
        )

        errors = validate_source(source)

        self.assertTrue(any("onclick" in error for error in errors))
        self.assertTrue(any("外部script" in error for error in errors))

    def test_external_svg_and_srcset_cannot_load_resources(self) -> None:
        external_use = VALID_PAGE.replace(
            "</svg>", '<use href="https://example.com/icons.svg#flow"></use></svg>', 1
        )
        mixed_srcset = VALID_PAGE.replace(
            "</svg>",
            '<image srcset="data:image/png;base64,AA== 1x, https://example.com/image.png 2x"></image></svg>',
            1,
        )

        self.assertTrue(
            any("外部resource" in error for error in validate_source(external_use))
        )
        self.assertTrue(
            any("srcset" in error for error in validate_source(mixed_srcset))
        )

    def test_inline_style_track_and_meta_refresh_cannot_load_resources(self) -> None:
        cases = {
            "inline style": VALID_PAGE.replace(
                "<main>",
                '<main style="background-image:url(https://example.com/x.png)">',
                1,
            ),
            "track": VALID_PAGE.replace(
                "</main>",
                '<video><track src="https://example.com/subtitles.vtt"></video></main>',
                1,
            ),
            "meta refresh": VALID_PAGE.replace(
                '<meta charset="utf-8">',
                '<meta charset="utf-8"><meta http-equiv="refresh" content="0;url=https://example.com">',
                1,
            ),
            "image-set": VALID_PAGE.replace(
                "<main>",
                '<main style="background-image:image-set(https://example.com/x.png 1x)">',
                1,
            ),
            "escaped url": VALID_PAGE.replace(
                "<main>",
                r'<main style="background-image:u\72l(https://example.com/x.png)">',
                1,
            ),
            "fully escaped url": VALID_PAGE.replace(
                "<main>",
                r'<main style="background-image:u\000072l(http\00003a\00002f\00002f127.0.0.1:9/x.png)">',
                1,
            ),
            "fully escaped image-set": VALID_PAGE.replace(
                "<main>",
                r'<main style="background-image:image\00002dset(http\00003a\00002f\00002f127.0.0.1:9/x.png 1x)">',
                1,
            ),
        }

        for label, source in cases.items():
            with self.subTest(label=label):
                errors = validate_source(source)
                self.assertTrue(
                    any("外部resource" in error for error in errors), errors
                )

    def test_document_root_cannot_force_a_minimum_width(self) -> None:
        source = VALID_PAGE.replace(
            "body { margin: 0; }",
            "body { min-width: 320px; margin: 0; }",
            1,
        )

        errors = validate_source(source)

        self.assertTrue(any("本文全体" in error for error in errors), errors)

    def test_evidence_summary_question_and_choices_must_have_text(self) -> None:
        cases = {
            "summary": (
                VALID_PAGE.replace(
                    "<summary>コード上の根拠を見る</summary>",
                    "<summary></summary>",
                    1,
                ),
                "根拠欄",
            ),
            "legend": (
                VALID_PAGE.replace(
                    "<legend>概念1の説明として正しいものはどれですか。</legend>",
                    "<legend></legend>",
                    1,
                ),
                "問題文",
            ),
            "choice": (
                VALID_PAGE.replace(
                    '<label><input type="radio" name="q1" value="q1-a">入力を処理して結果へ変える</label>',
                    '<label><input type="radio" name="q1" value="q1-a"></label>',
                    1,
                ),
                "選択肢",
            ),
        }

        for label, (source, expected) in cases.items():
            with self.subTest(label=label):
                errors = validate_source(source)
                self.assertTrue(any(expected in error for error in errors), errors)

    def test_persistence_and_form_submission_fail(self) -> None:
        source = VALID_PAGE.replace(
            "<form>", '<form action="https://example.com/answers">', 1
        ).replace(
            'document.addEventListener("DOMContentLoaded", () => {',
            'localStorage.setItem("answer", "saved");\n    document.addEventListener("DOMContentLoaded", () => {',
            1,
        )

        errors = validate_source(source)
        input_errors = validate_source(
            VALID_PAGE.replace(
                "</form>",
                '<input type="submit" formaction="https://example.com/answers"></form>',
                1,
            )
        )

        self.assertTrue(any("外部へ送信" in error for error in errors))
        self.assertTrue(any("localStorage" in error for error in errors))
        self.assertTrue(any("外部へ送信" in error for error in input_errors))

    def test_cookie_indexed_db_cache_and_beacon_fail(self) -> None:
        forbidden_calls = {
            "document.cookie": 'document.cookie = "answer=saved";',
            "indexedDB": 'indexedDB.open("repo-eli5");',
            "Cache Storage": 'caches.open("repo-eli5");',
            "sendBeacon": 'navigator.sendBeacon("https://example.com", "answer");',
        }

        for label, statement in forbidden_calls.items():
            with self.subTest(label=label):
                source = VALID_PAGE.replace(
                    '    document.addEventListener("DOMContentLoaded", () => {',
                    f'    {statement}\n    document.addEventListener("DOMContentLoaded", () => {{',
                    1,
                )

                errors = validate_source(source)

                self.assertTrue(any(label in error for error in errors), errors)

    def test_unresolved_placeholder_fails_for_an_artifact(self) -> None:
        source = VALID_PAGE.replace("Sample repository", "{{REPO_NAME}}", 1)

        errors = validate_source(source)

        self.assertTrue(any("placeholder" in error for error in errors), errors)

    @unittest.skipUnless(find_browser(), "system Chromium is not installed")
    def test_browser_smoke_accepts_wrong_answers_then_advances(self) -> None:
        broken_page = VALID_PAGE.replace(
            "          next.hidden = false;",
            "          next.hidden = correct ? false : true;",
            1,
        )
        self.assertNotEqual(broken_page, VALID_PAGE)
        leaking_page = VALID_PAGE.replace(
            '        check.addEventListener("click", () => {',
            """        check.addEventListener("click", () => {
          const leak = new Image();
          leak.src = "http://127.0.0.1:9/repo-eli5-answer.png";""",
            1,
        )
        empty_intro_page = VALID_PAGE.replace(
            "<p data-concept-intro>まず、入力を受け取って結果へ変える仕組みがあります。</p>",
            "<p data-concept-intro></p>",
            1,
        )
        empty_reason_page = VALID_PAGE.replace(
            "<div data-answer-panel hidden>正解は「入力を処理して結果へ変える」です。</div>",
            "<div data-answer-panel hidden></div>",
            1,
        )
        empty_summary_page = VALID_PAGE.replace(
            "<summary>コード上の根拠を見る</summary>",
            "<summary></summary>",
            1,
        )
        empty_legend_page = VALID_PAGE.replace(
            "<legend>概念1の説明として正しいものはどれですか。</legend>",
            "<legend></legend>",
            1,
        )
        empty_choice_page = VALID_PAGE.replace(
            '<label><input type="radio" name="q1" value="q1-a">入力を処理して結果へ変える</label>',
            '<label><input type="radio" name="q1" value="q1-a"></label>',
            1,
        )

        with tempfile.TemporaryDirectory() as directory:
            valid_path = Path(directory) / "valid.html"
            broken_path = Path(directory) / "broken.html"
            leaking_path = Path(directory) / "leaking.html"
            empty_intro_path = Path(directory) / "empty-intro.html"
            empty_reason_path = Path(directory) / "empty-reason.html"
            empty_summary_path = Path(directory) / "empty-summary.html"
            empty_legend_path = Path(directory) / "empty-legend.html"
            empty_choice_path = Path(directory) / "empty-choice.html"
            valid_path.write_text(VALID_PAGE, encoding="utf-8")
            broken_path.write_text(broken_page, encoding="utf-8")
            leaking_path.write_text(leaking_page, encoding="utf-8")
            empty_intro_path.write_text(empty_intro_page, encoding="utf-8")
            empty_reason_path.write_text(empty_reason_page, encoding="utf-8")
            empty_summary_path.write_text(empty_summary_page, encoding="utf-8")
            empty_legend_path.write_text(empty_legend_page, encoding="utf-8")
            empty_choice_path.write_text(empty_choice_page, encoding="utf-8")

            valid_errors = browser_smoke_file(valid_path)
            broken_errors = browser_smoke_file(broken_path)
            leaking_errors = browser_smoke_file(leaking_path)
            empty_intro_errors = browser_smoke_file(empty_intro_path)
            empty_reason_errors = browser_smoke_file(empty_reason_path)
            empty_summary_errors = browser_smoke_file(empty_summary_path)
            empty_legend_errors = browser_smoke_file(empty_legend_path)
            empty_choice_errors = browser_smoke_file(empty_choice_path)

        self.assertEqual(valid_errors, [])
        self.assertTrue(
            any("choice_wrong" in error for error in broken_errors), broken_errors
        )
        self.assertTrue(
            any("external_resources_after_quiz" in error for error in leaking_errors),
            leaking_errors,
        )
        self.assertTrue(
            any("unit_intro_1" in error for error in empty_intro_errors),
            empty_intro_errors,
        )
        self.assertTrue(
            any("question_1_reason" in error for error in empty_reason_errors),
            empty_reason_errors,
        )
        self.assertTrue(
            any("unit_evidence_summary_1" in error for error in empty_summary_errors),
            empty_summary_errors,
        )
        self.assertTrue(
            any("question_1_legend" in error for error in empty_legend_errors),
            empty_legend_errors,
        )
        self.assertTrue(
            any("question_1_labels" in error for error in empty_choice_errors),
            empty_choice_errors,
        )

    def test_cli_style_file_input_reports_all_errors(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            page = Path(directory) / "legacy.html"
            page.write_text(
                '<html lang="ja"><body><h1>図だけ</h1></body></html>', encoding="utf-8"
            )

            errors = validate_source(page.read_text(encoding="utf-8"))

        self.assertGreaterEqual(len(errors), 4)


if __name__ == "__main__":
    unittest.main()
