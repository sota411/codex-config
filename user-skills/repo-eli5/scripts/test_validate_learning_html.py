"""Public-artifact tests for the repo-eli5 learning page contract."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from validate_learning_html import browser_smoke_file, find_browser, validate_source

VALID_PAGE = """<!doctype html>
<html lang="ja">
<head>
  <meta charset="utf-8"><title>Sample repository</title>
  <style>
    @media (prefers-reduced-motion: reduce) { * { scroll-behavior: auto; } }
    @media print { button { display: none; } }
  </style>
</head>
<body data-repo-eli5-page="v1">
  <main>
    <header>
      <h1>Sample repository</h1>
      <dl data-repo-meta>
        <dt>対象</dt><dd data-repo-root>/tmp/sample</dd>
        <dt>Branch</dt><dd data-repo-branch>main</dd>
        <dt>Commit</dt><dd data-repo-revision>abc1234</dd>
      </dl>
    </header>
    <section id="visual" data-learning-section="visual">
      <h2>まず、全体像を見る</h2>
      <svg data-visual-kind="diagram" role="img" aria-labelledby="sample-title sample-desc" viewBox="0 0 1280 720">
        <title id="sample-title">Sample repositoryの主要フロー</title>
        <desc id="sample-desc">入力が処理され、結果になるまでの主要な流れを示す。</desc>
        <rect width="1280" height="720"></rect>
      </svg>
    </section>
    <section id="explanation" data-learning-section="explanation">
      <h2>流れを追う</h2>
      <p data-repo-summary>入力を一つの結果へ変換するrepositoryである。</p>
      <article data-flow-step><h3>入力を受け取る</h3><p>公開境界で入力を受け取る。</p></article>
      <article data-flow-step><h3>入力を変換する</h3><p>中核処理が入力を変換する。</p></article>
      <article data-flow-step><h3>結果を返す</h3><p>変換した結果を返す。</p></article>
    </section>
    <section id="evidence" data-learning-section="evidence">
      <h2>根拠を確認する</h2>
      <ul>
        <li data-evidence-kind="fact"><code data-source-ref>/tmp/sample/src/main.ts:12</code></li>
        <li data-evidence-kind="fact"><code data-source-ref>/tmp/sample/test/main.test.ts:8</code></li>
      </ul>
    </section>
    <section id="quiz" data-learning-section="quiz" data-repo-eli5-quiz>
      <h2>理解を確かめる</h2>
      <p data-quiz-progress role="status" aria-live="polite" aria-atomic="true">問題 1 / 2</p>
      <form>
        <fieldset data-quiz-question data-question-kind="reflection" tabindex="-1">
          <legend>入力から結果までを自分の言葉で説明してください。</legend>
          <label>回答<textarea name="q1"></textarea></label>
          <button type="button" data-quiz-action="check">観点を確認する</button>
          <button type="button" data-quiz-action="next" hidden>次の問題へ</button>
          <p data-quiz-feedback role="status" aria-live="polite" aria-atomic="true"></p>
          <div data-answer-panel hidden><ul data-answer-points><li>入力</li><li>結果</li></ul></div>
        </fieldset>
        <fieldset data-quiz-question data-question-kind="choice" data-correct="flow-a" tabindex="-1" hidden>
          <legend>最初に呼ばれる境界はどれですか。</legend>
          <label><input type="radio" name="q2" value="flow-a">公開entrypoint</label>
          <label><input type="radio" name="q2" value="flow-b">永続化層</label>
          <button type="button" data-quiz-action="check">回答を確認する</button>
          <button type="button" data-quiz-action="next" hidden>完了する</button>
          <p data-quiz-feedback role="status" aria-live="polite" aria-atomic="true"></p>
          <div data-answer-panel hidden>公開entrypointから始まる。</div>
        </fieldset>
      </form>
      <div data-quiz-complete tabindex="-1" hidden>
        <p>確認は完了です。</p>
        <button type="button" data-quiz-action="reset">最初から振り返る</button>
      </div>
      <noscript><style>[data-quiz-question][hidden], [data-answer-panel][hidden] { display: block !important; }</style>クイズの回答確認にはJavaScriptが必要です。問題と解説はすべて表示されています。</noscript>
    </section>
  </main>
  <script data-repo-eli5-controller>
    document.addEventListener("DOMContentLoaded", () => {
      const quiz = document.querySelector("[data-repo-eli5-quiz]");
      const questions = Array.from(quiz.querySelectorAll("[data-quiz-question]"));
      const progress = quiz.querySelector("[data-quiz-progress]");
      const complete = quiz.querySelector("[data-quiz-complete]");
      const reset = quiz.querySelector('[data-quiz-action="reset"]');
      let current = 0;

      const showQuestion = (index) => {
        current = index;
        questions.forEach((question, questionIndex) => {
          question.hidden = questionIndex !== current;
        });
        complete.hidden = true;
        progress.textContent = `問題 ${current + 1} / ${questions.length}`;
        questions[current].focus();
      };

      const resetQuestion = (question) => {
        question.removeAttribute("data-state");
        question.querySelector("[data-quiz-feedback]").textContent = "";
        question.querySelector("[data-answer-panel]").hidden = true;
        question.querySelector('[data-quiz-action="next"]').hidden = true;
        question.querySelector('[data-quiz-action="check"]').disabled = false;
        question.querySelectorAll('input[type="radio"]').forEach((input) => {
          input.checked = false;
        });
        const textarea = question.querySelector("textarea");
        if (textarea) textarea.value = "";
      };

      questions.forEach((question, index) => {
        const check = question.querySelector('[data-quiz-action="check"]');
        const next = question.querySelector('[data-quiz-action="next"]');
        const feedback = question.querySelector("[data-quiz-feedback]");
        const answerPanel = question.querySelector("[data-answer-panel]");

        check.addEventListener("click", () => {
          if (question.dataset.questionKind === "reflection") {
            const response = question.querySelector("textarea").value.trim();
            if (!response) {
              feedback.textContent = "先に説明を書いてください。";
              return;
            }
            question.dataset.state = "reviewed";
            feedback.textContent = "確認観点を表示しました。";
          } else {
            const selected = question.querySelector('input[type="radio"]:checked');
            if (!selected) {
              feedback.textContent = "選択肢を一つ選んでください。";
              return;
            }
            const correct = selected.value === question.dataset.correct;
            question.dataset.state = correct ? "correct" : "incorrect";
            feedback.textContent = correct ? "正解です。" : "選び直してください。";
            if (!correct) {
              answerPanel.hidden = false;
              next.hidden = true;
              return;
            }
          }
          answerPanel.hidden = false;
          next.hidden = false;
          check.disabled = true;
          next.focus();
        });

        next.addEventListener("click", () => {
          if (index + 1 < questions.length) {
            showQuestion(index + 1);
            return;
          }
          questions[index].hidden = true;
          complete.hidden = false;
          progress.textContent = "確認完了";
          complete.focus();
        });
      });

      reset.addEventListener("click", () => {
        questions.forEach(resetQuestion);
        showQuestion(0);
      });

      questions.forEach((question, index) => {
        question.hidden = index !== 0;
      });
    });
  </script>
</body>
</html>
"""


class LearningPageContractTests(unittest.TestCase):
    def test_complete_learning_page_passes(self) -> None:
        self.assertEqual(validate_source(VALID_PAGE), [])

    def test_diagram_only_page_fails(self) -> None:
        source = """<!doctype html><html lang="ja"><body>
        <svg role="img" aria-labelledby="d-title d-desc">
          <title id="d-title">図</title><desc id="d-desc">説明</desc>
        </svg></body></html>"""

        errors = validate_source(source)

        self.assertTrue(any("学習ページ識別子" in error for error in errors))
        self.assertTrue(any("explanation" in error for error in errors))
        self.assertTrue(any("quiz" in error for error in errors))

    def test_quiz_requires_two_questions_and_accessible_feedback(self) -> None:
        source = VALID_PAGE.replace(
            '<fieldset data-quiz-question data-question-kind="reflection" tabindex="-1">',
            '<fieldset data-question-kind="reflection" tabindex="-1">',
        ).replace(' aria-live="polite" aria-atomic="true"></p>', "></p>")

        errors = validate_source(source)

        self.assertTrue(any("2問以上" in error for error in errors))
        self.assertTrue(any("aria-live" in error for error in errors))

    def test_accessible_table_can_replace_a_diagram(self) -> None:
        svg = """<svg data-visual-kind="diagram" role="img" aria-labelledby="sample-title sample-desc" viewBox="0 0 1280 720">
        <title id="sample-title">Sample repositoryの主要フロー</title>
        <desc id="sample-desc">入力が処理され、結果になるまでの主要な流れを示す。</desc>
        <rect width="1280" height="720"></rect>
      </svg>"""
        table = """<table data-visual-kind="table">
        <caption>変更前後の比較</caption>
        <thead><tr><th scope="col">観点</th><th scope="col">変更前</th><th scope="col">変更後</th></tr></thead>
        <tbody><tr><th scope="row">出力</th><td>旧形式</td><td>新形式</td></tr></tbody>
      </table>"""

        self.assertEqual(validate_source(VALID_PAGE.replace(svg, table)), [])

    def test_quiz_requires_reflection_then_choice(self) -> None:
        source = (
            VALID_PAGE.replace(
                'data-question-kind="reflection"',
                'data-question-kind="temporary"',
                1,
            )
            .replace(
                'data-question-kind="choice"',
                'data-question-kind="reflection"',
                1,
            )
            .replace(
                'data-question-kind="temporary"',
                'data-question-kind="choice"',
                1,
            )
        )

        errors = validate_source(source)

        self.assertTrue(any("最初はreflection" in error for error in errors))

    def test_flow_requires_between_three_and_five_steps(self) -> None:
        two_steps = VALID_PAGE.replace(
            "      <article data-flow-step><h3>入力を変換する</h3><p>中核処理が入力を変換する。</p></article>\n",
            "",
            1,
        )
        six_steps = VALID_PAGE.replace(
            "      <article data-flow-step><h3>結果を返す</h3><p>変換した結果を返す。</p></article>",
            """      <article data-flow-step><h3>中間処理A</h3><p>入力を処理する。</p></article>
      <article data-flow-step><h3>中間処理B</h3><p>入力を処理する。</p></article>
      <article data-flow-step><h3>中間処理C</h3><p>入力を処理する。</p></article>
      <article data-flow-step><h3>結果を返す</h3><p>変換した結果を返す。</p></article>""",
            1,
        )

        self.assertTrue(any("3〜5" in error for error in validate_source(two_steps)))
        self.assertTrue(any("3〜5" in error for error in validate_source(six_steps)))

    def test_quiz_requires_one_question_at_a_time_and_working_controls(self) -> None:
        simultaneous_questions = VALID_PAGE.replace(
            'data-question-kind="choice" data-correct="flow-a" tabindex="-1" hidden',
            'data-question-kind="choice" data-correct="flow-a" tabindex="-1"',
            1,
        )
        script_start = VALID_PAGE.index("  <script data-repo-eli5-controller>")
        script_end = VALID_PAGE.index("  </script>", script_start) + len("  </script>")
        inert_controller = (
            VALID_PAGE[:script_start]
            + """  <script data-repo-eli5-controller>
    document.addEventListener("DOMContentLoaded", () => {
      document.querySelectorAll("[data-quiz-action]");
    });
  </script>"""
            + VALID_PAGE[script_end:]
        )

        self.assertTrue(
            any(
                "最初の1問だけ" in error
                for error in validate_source(simultaneous_questions)
            )
        )
        self.assertTrue(
            any(
                "quiz controller" in error
                for error in validate_source(inert_controller)
            )
        )

    def test_quiz_requires_hidden_completion_and_reset_control(self) -> None:
        source = VALID_PAGE.replace(
            ' data-quiz-complete tabindex="-1" hidden', "", 1
        ).replace(
            '<button type="button" data-quiz-action="reset">最初から振り返る</button>',
            "<span>最初から振り返る</span>",
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

    def test_svg_use_and_srcset_cannot_load_external_resources(self) -> None:
        external_use = VALID_PAGE.replace(
            "</svg>",
            '<use href="https://example.com/icons.svg#flow"></use></svg>',
            1,
        )
        external_xlink = VALID_PAGE.replace(
            "</svg>",
            '<use xlink:href="https://example.com/icons.svg#flow"></use></svg>',
            1,
        )
        mixed_srcset = VALID_PAGE.replace(
            "</svg>",
            '<image srcset="data:image/png;base64,AA== 1x, https://example.com/image.png 2x"></image></svg>',
            1,
        )

        use_errors = validate_source(external_use)
        xlink_errors = validate_source(external_xlink)
        srcset_errors = validate_source(mixed_srcset)

        self.assertTrue(
            any("外部resource" in error for error in use_errors), use_errors
        )
        self.assertTrue(
            any("外部resource" in error for error in xlink_errors), xlink_errors
        )
        self.assertTrue(
            any("srcset" in error for error in srcset_errors), srcset_errors
        )

    def test_persistence_and_form_submission_fail(self) -> None:
        source = VALID_PAGE.replace(
            "<form>",
            '<form action="https://example.com/answers">',
            1,
        ).replace(
            'document.addEventListener("DOMContentLoaded", () => {',
            'localStorage.setItem("answer", "saved");\n    document.addEventListener("DOMContentLoaded", () => {',
            1,
        )

        errors = validate_source(source)

        self.assertTrue(any("外部へ送信" in error for error in errors))
        self.assertTrue(any("localStorage" in error for error in errors))

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
    def test_browser_smoke_rejects_wrong_choice_advancing(self) -> None:
        broken_page = VALID_PAGE.replace(
            """            if (!correct) {
              answerPanel.hidden = false;
              next.hidden = true;
              return;
            }""",
            """            if (!correct) {
              answerPanel.hidden = false;
              next.hidden = false;
              return;
            }""",
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
        self.assertNotEqual(leaking_page, VALID_PAGE)
        third_question = """
        <fieldset data-quiz-question data-question-kind="reflection" tabindex="-1" hidden>
          <legend>もう一度、別の条件で流れを説明してください。</legend>
          <label>回答<textarea name="q3"></textarea></label>
          <button type="button" data-quiz-action="check">観点を確認する</button>
          <button type="button" data-quiz-action="next" hidden>完了する</button>
          <p data-quiz-feedback role="status" aria-live="polite" aria-atomic="true"></p>
          <div data-answer-panel hidden><ul data-answer-points><li>入力</li><li>結果</li></ul></div>
        </fieldset>"""
        three_question_page = VALID_PAGE.replace(
            "      </form>", third_question + "\n      </form>", 1
        )

        with tempfile.TemporaryDirectory() as directory:
            valid_path = Path(directory) / "valid.html"
            broken_path = Path(directory) / "broken.html"
            leaking_path = Path(directory) / "leaking.html"
            three_question_path = Path(directory) / "three-questions.html"
            valid_path.write_text(VALID_PAGE, encoding="utf-8")
            broken_path.write_text(broken_page, encoding="utf-8")
            leaking_path.write_text(leaking_page, encoding="utf-8")
            three_question_path.write_text(three_question_page, encoding="utf-8")

            valid_errors = browser_smoke_file(valid_path)
            broken_errors = browser_smoke_file(broken_path)
            leaking_errors = browser_smoke_file(leaking_path)
            three_question_errors = browser_smoke_file(three_question_path)

        self.assertEqual(valid_errors, [])
        self.assertEqual(three_question_errors, [])
        self.assertTrue(
            any("external_resources_after_quiz" in error for error in leaking_errors),
            leaking_errors,
        )
        self.assertTrue(
            any("choice_wrong" in error for error in broken_errors), broken_errors
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
