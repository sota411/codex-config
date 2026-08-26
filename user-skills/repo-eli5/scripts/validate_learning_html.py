#!/usr/bin/env python3
"""Validate a generated repo-eli5 HTML learning page.

The validator intentionally checks the public artifact rather than the wording
of the skill. Static checks use only the Python standard library; completed
artifacts additionally run their quiz flow in system Chromium.
"""

from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile
from html.parser import HTMLParser
from pathlib import Path

REQUIRED_SECTIONS = {"visual", "explanation", "evidence", "quiz"}
PLACEHOLDER_PATTERN = re.compile(r"\{\{[^{}\n]+\}\}")
REFERENCE_ATTRIBUTES = {
    "action",
    "formaction",
    "src",
    "href",
    "xlink:href",
    "poster",
    "srcset",
}
RESOURCE_TAGS = {
    "audio",
    "embed",
    "feimage",
    "iframe",
    "image",
    "img",
    "object",
    "script",
    "source",
    "use",
    "video",
}
FORBIDDEN_SCRIPT_PATTERNS = {
    r"\beval\s*\(": "eval",
    r"\bFunction\s*\(": "Function constructor",
    r"document\.write\s*\(": "document.write",
    r"\.innerHTML\s*=": "innerHTML",
    r"\bfetch\s*\(": "fetch",
    r"\bXMLHttpRequest\b": "XMLHttpRequest",
    r"\bWebSocket\b": "WebSocket",
    r"\blocalStorage\b": "localStorage",
    r"\bsessionStorage\b": "sessionStorage",
    r"\bdocument\s*\.\s*cookie\b": "document.cookie",
    r"\bindexedDB\b": "indexedDB",
    r"\b(?:caches\s*\.|CacheStorage\b)": "Cache Storage",
    r"\bsendBeacon\s*\(": "sendBeacon",
    r"\bEventSource\b": "EventSource",
    r"\bRTCPeerConnection\b": "RTCPeerConnection",
    r"\bnavigator\s*\.\s*serviceWorker\b": "Service Worker",
    r"\bshow(?:SaveFile|Directory)Picker\s*\(": "File System Access API",
}

REQUIRED_CONTROLLER_PATTERNS = {
    r"\bDOMContentLoaded\b": "初期化",
    r"querySelector\s*\(\s*['\"]\[data-repo-eli5-quiz\]['\"]\s*\)": "quiz rootの取得",
    r"querySelectorAll\s*\(\s*['\"]\[data-quiz-question\]['\"]\s*\)": "問題一覧の取得",
    r"querySelector\s*\(\s*['\"]\[data-quiz-progress\]['\"]\s*\)": "進捗領域の取得",
    r"querySelector\s*\(\s*['\"]\[data-quiz-complete\]['\"]\s*\)": "完了領域の取得",
    r"\[data-quiz-action=['\"]reset['\"]\]": "reset操作の取得",
    r"question\.hidden\s*=\s*questionIndex\s*!==\s*current": "一問ずつの表示",
    r"question\.hidden\s*=\s*index\s*!==\s*0": "初期問題の表示",
    r"questions\.forEach\s*\(\s*resetQuestion\s*\)": "問題状態のreset",
    r"\.textContent\s*=": "feedbackまたは進捗の更新",
    r"(?:dataset\.state|setAttribute\s*\(\s*['\"]data-state['\"]\s*,)": "回答状態の更新",
    r"\.focus\s*\(": "keyboard focusの移動",
}

BROWSER_SMOKE_SCRIPT = r"""
<output id="repo-eli5-smoke-result" data-status="pending" hidden></output>
<script>
window.addEventListener("load", async () => {
  const result = document.querySelector("#repo-eli5-smoke-result");
  const failures = [];
  const check = (name, condition) => {
    if (!condition) failures.push(name);
  };

  try {
    const quiz = document.querySelector("[data-repo-eli5-quiz]");
    const questions = Array.from(quiz.querySelectorAll("[data-quiz-question]"));
    const progress = quiz.querySelector("[data-quiz-progress]");
    const complete = quiz.querySelector("[data-quiz-complete]");
    const reset = quiz.querySelector('[data-quiz-action="reset"]');
    const visible = (node) => !node.hidden && getComputedStyle(node).display !== "none";
    const externalResources = () => performance
      .getEntriesByType("resource")
      .filter((entry) => /^https?:/i.test(entry.name));

    check("external_resources", externalResources().length === 0);
    check("initial_question_count", questions.length >= 2);
    check("initial_one_question", visible(questions[0]) && questions.slice(1).every((node) => !visible(node)));

    questions.forEach((question, index) => {
      const number = index + 1;
      const questionCheck = question.querySelector('[data-quiz-action="check"]');
      const questionNext = question.querySelector('[data-quiz-action="next"]');
      const answer = question.querySelector("[data-answer-panel]");
      const feedback = question.querySelector("[data-quiz-feedback]");
      check(
        `question_${number}_visible`,
        visible(question) && questions.every((candidate, candidateIndex) => candidateIndex === index || !visible(candidate)),
      );

      if (question.dataset.questionKind === "reflection") {
        const input = question.querySelector("textarea");
        questionCheck.click();
        check(`reflection_${number}_empty`, !question.hasAttribute("data-state") && questionNext.hidden);
        input.value = "入力から結果までの主要な流れを説明する。";
        questionCheck.click();
        check(`reflection_${number}_state`, question.dataset.state === "reviewed");
      } else {
        const options = Array.from(question.querySelectorAll('input[type="radio"]'));
        const correct = options.find((option) => option.value === question.dataset.correct);
        const wrong = options.find((option) => option.value !== question.dataset.correct);
        check(`choice_${number}_options`, Boolean(correct && wrong));
        wrong.checked = true;
        questionCheck.click();
        check(
          `choice_wrong_${number}`,
          question.dataset.state === "incorrect" && questionNext.hidden && !questionCheck.disabled,
        );
        correct.checked = true;
        questionCheck.click();
        check(`choice_correct_${number}`, question.dataset.state === "correct");
      }

      check(`question_${number}_feedback`, feedback.textContent.trim().length > 0);
      check(`question_${number}_answer`, !answer.hidden);
      check(`question_${number}_next`, !questionNext.hidden);
      check(`question_${number}_focus`, document.activeElement === questionNext);
      questionNext.click();
      if (number < questions.length) {
        check(`question_${number}_advance`, visible(questions[index + 1]) && !visible(question) && !visible(complete));
      }
    });

    check("complete_visible", visible(complete) && questions.every((question) => !visible(question)));
    check("complete_progress", progress.textContent.trim() === "確認完了");
    check("complete_focus", document.activeElement === complete);

    reset.click();
    check("reset_visibility", visible(questions[0]) && questions.slice(1).every((node) => !visible(node)) && !visible(complete));
    check("reset_state", questions.every((question) => !question.hasAttribute("data-state")));
    check("reset_textareas", Array.from(quiz.querySelectorAll("textarea")).every((input) => input.value === ""));
    check("reset_radios", Array.from(quiz.querySelectorAll('input[type="radio"]')).every((input) => !input.checked));
    check("reset_panels", questions.every((question) => question.querySelector("[data-answer-panel]").hidden));
    check("reset_next", questions.every((question) => question.querySelector('[data-quiz-action="next"]').hidden));
    await new Promise((resolve) => setTimeout(resolve, 100));
    check("external_resources_after_quiz", externalResources().length === 0);
  } catch (error) {
    failures.push(`exception_${error.name}`);
  }

  result.dataset.status = failures.length === 0 ? "pass" : "fail";
  result.dataset.failures = failures.join(",");
});
</script>
"""


class LearningPageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.has_html_doctype = False
        self.html_attrs: list[dict[str, str]] = []
        self.page_roots = 0
        self.main_count = 0
        self.sections: list[str] = []
        self.visual_kinds: list[tuple[str, str]] = []
        self.table_captions = 0
        self.table_headers = 0
        self.repo_meta = 0
        self.repo_roots = 0
        self.repo_branches = 0
        self.repo_revisions = 0
        self.repo_summaries = 0
        self.flow_steps = 0
        self.evidence_kinds: list[str] = []
        self.source_refs: list[str] = []
        self.quiz_roots = 0
        self.quiz_progress: list[dict[str, str]] = []
        self.quiz_questions: list[dict[str, object]] = []
        self.quiz_actions: list[tuple[str, str]] = []
        self.quiz_complete: list[dict[str, str]] = []
        self.quiz_noscript = 0
        self.scripts: list[dict[str, object]] = []
        self.styles: list[str] = []
        self.svgs: list[dict[str, object]] = []
        self.unsafe: list[str] = []
        self.references: list[tuple[str, str, str, str]] = []

        self._current_question: dict[str, object] | None = None
        self._current_script: dict[str, object] | None = None
        self._current_source_ref: list[str] | None = None
        self._in_style = False
        self._svg_depth = 0
        self._current_svg: dict[str, object] | None = None
        self._svg_capture: str | None = None

    def handle_decl(self, decl: str) -> None:
        if decl.strip().casefold() == "doctype html":
            self.has_html_doctype = True

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag = tag.casefold()
        normalized = [(name.casefold(), value or "") for name, value in attrs]
        data = {name: value for name, value in normalized}

        if tag == "html":
            self.html_attrs.append(data)
        if tag == "body" and data.get("data-repo-eli5-page") == "v1":
            self.page_roots += 1
        if tag == "main":
            self.main_count += 1

        if tag in {"base", "embed", "iframe", "object"}:
            self.unsafe.append(f"<{tag}>は使用できません")
        for name, value in normalized:
            if name.startswith("on"):
                self.unsafe.append(f"<{tag}>の実行属性{name}は使用できません")
            if name == "srcdoc":
                self.unsafe.append(f"<{tag}>のsrcdoc属性は使用できません")
            if name in REFERENCE_ATTRIBUTES:
                self.references.append((tag, data.get("rel", ""), name, value))

        if tag == "section" and "data-learning-section" in data:
            self.sections.append(data["data-learning-section"])
        if "data-visual-kind" in data:
            self.visual_kinds.append((tag, data["data-visual-kind"]))
        if tag == "caption":
            self.table_captions += 1
        if tag == "th":
            self.table_headers += 1
        if "data-repo-meta" in data:
            self.repo_meta += 1
        if "data-repo-root" in data:
            self.repo_roots += 1
        if "data-repo-branch" in data:
            self.repo_branches += 1
        if "data-repo-revision" in data:
            self.repo_revisions += 1
        if "data-repo-summary" in data:
            self.repo_summaries += 1
        if "data-flow-step" in data:
            self.flow_steps += 1
        if "data-evidence-kind" in data:
            self.evidence_kinds.append(data["data-evidence-kind"])
        if "data-source-ref" in data:
            self._current_source_ref = []

        if "data-repo-eli5-quiz" in data:
            self.quiz_roots += 1
        if "data-quiz-progress" in data:
            self.quiz_progress.append(data)
        if tag == "fieldset" and "data-quiz-question" in data:
            question: dict[str, object] = {
                "attrs": data,
                "legends": 0,
                "radios": [],
                "textareas": 0,
                "actions": [],
                "feedback": [],
                "answer_panels": [],
                "answer_points": 0,
            }
            self.quiz_questions.append(question)
            self._current_question = question
        if self._current_question is not None:
            if tag == "legend":
                self._current_question["legends"] = (
                    int(self._current_question["legends"]) + 1
                )
            if tag == "input" and data.get("type", "").casefold() == "radio":
                radios = self._current_question["radios"]
                assert isinstance(radios, list)
                radios.append((data.get("name", ""), data.get("value", "")))
            if tag == "textarea":
                self._current_question["textareas"] = (
                    int(self._current_question["textareas"]) + 1
                )
            if tag == "button" and "data-quiz-action" in data:
                actions = self._current_question["actions"]
                assert isinstance(actions, list)
                actions.append(
                    (data["data-quiz-action"], data.get("type", ""), "hidden" in data)
                )
            if "data-quiz-feedback" in data:
                feedback = self._current_question["feedback"]
                assert isinstance(feedback, list)
                feedback.append(data)
            if "data-answer-panel" in data:
                answer_panels = self._current_question["answer_panels"]
                assert isinstance(answer_panels, list)
                answer_panels.append(data)
            if "data-answer-points" in data:
                self._current_question["answer_points"] = (
                    int(self._current_question["answer_points"]) + 1
                )
        if tag == "noscript":
            self.quiz_noscript += 1
        if tag == "button" and "data-quiz-action" in data:
            self.quiz_actions.append((data["data-quiz-action"], data.get("type", "")))
        if "data-quiz-complete" in data:
            self.quiz_complete.append(data)

        if tag == "script":
            self._current_script = {
                "attrs": data,
                "attr_names": [name for name, _ in normalized],
                "body": [],
            }
            self.scripts.append(self._current_script)
        if tag == "style":
            self._in_style = True

        if tag == "svg" and self._svg_depth == 0:
            self._svg_depth = 1
            self._current_svg = {"attrs": data, "first": None, "title": {}, "desc": {}}
            self.svgs.append(self._current_svg)
        elif self._svg_depth:
            self._svg_depth += 1
            assert self._current_svg is not None
            if self._svg_depth == 2 and self._current_svg["first"] is None:
                self._current_svg["first"] = tag
            if self._svg_depth == 2 and tag in {"title", "desc"}:
                self._current_svg[tag] = {"attrs": data, "text": ""}
                self._svg_capture = tag

    def handle_endtag(self, tag: str) -> None:
        tag = tag.casefold()
        if tag == "fieldset":
            self._current_question = None
        if tag == "script":
            self._current_script = None
        if tag == "style":
            self._in_style = False
        if self._current_source_ref is not None:
            self.source_refs.append("".join(self._current_source_ref).strip())
            self._current_source_ref = None

        if self._svg_depth:
            if tag in {"title", "desc"}:
                self._svg_capture = None
            self._svg_depth -= 1
            if self._svg_depth == 0:
                self._current_svg = None

    def handle_data(self, data: str) -> None:
        if self._current_script is not None:
            body = self._current_script["body"]
            assert isinstance(body, list)
            body.append(data)
        if self._in_style:
            self.styles.append(data)
        if self._current_source_ref is not None:
            self._current_source_ref.append(data)
        if self._svg_capture and self._current_svg:
            node = self._current_svg[self._svg_capture]
            assert isinstance(node, dict)
            node["text"] = str(node.get("text", "")) + data


def _is_embedded_reference(value: str) -> bool:
    stripped = value.strip().casefold()
    return not stripped or stripped.startswith(("#", "data:image/"))


def _check_svg(svg: dict[str, object], number: int) -> list[str]:
    errors: list[str] = []
    attrs = svg["attrs"]
    title = svg["title"]
    desc = svg["desc"]
    assert (
        isinstance(attrs, dict) and isinstance(title, dict) and isinstance(desc, dict)
    )
    title_attrs = title.get("attrs", {})
    desc_attrs = desc.get("attrs", {})
    assert isinstance(title_attrs, dict) and isinstance(desc_attrs, dict)
    if attrs.get("role") != "img":
        errors.append(f"SVG {number}にはrole=imgが必要です")
    if svg.get("first") != "title":
        errors.append(f"SVG {number}の最初の子要素はtitleでなければなりません")
    if not str(title.get("text", "")).strip() or not str(desc.get("text", "")).strip():
        errors.append(f"SVG {number}には空でないtitleとdescが必要です")
    title_id = str(title_attrs.get("id", ""))
    desc_id = str(desc_attrs.get("id", ""))
    if title_id in {"", "title"} or desc_id in {"", "desc"}:
        errors.append(f"SVG {number}のtitle/desc IDには図固有のprefixが必要です")
    if str(attrs.get("aria-labelledby", "")).split() != [title_id, desc_id]:
        errors.append(
            f"SVG {number}のaria-labelledbyはtitle、descの順で参照する必要があります"
        )
    return errors


def _check_question(question: dict[str, object], number: int) -> list[str]:
    errors: list[str] = []
    attrs = question["attrs"]
    assert isinstance(attrs, dict)
    kind = str(attrs.get("data-question-kind", ""))
    if kind not in {"choice", "reflection"}:
        errors.append(
            f"問題 {number}のdata-question-kindはchoiceまたはreflectionでなければなりません"
        )
    if int(question["legends"]) != 1:
        errors.append(f"問題 {number}にはlegendが1つ必要です")
    if attrs.get("tabindex") != "-1":
        errors.append(f"問題 {number}にはkeyboard focus用のtabindex=-1が必要です")

    actions = question["actions"]
    assert isinstance(actions, list)
    action_names = [str(action) for action, _button_type, _hidden in actions]
    if action_names.count("check") != 1 or action_names.count("next") != 1:
        errors.append(f"問題 {number}にはcheckとnextの操作がそれぞれ1つ必要です")
    if any(button_type != "button" for _action, button_type, _hidden in actions):
        errors.append(f"問題 {number}の操作buttonにはtype=buttonが必要です")
    next_actions = [
        hidden for action, _button_type, hidden in actions if action == "next"
    ]
    if next_actions and not all(next_actions):
        errors.append(
            f"問題 {number}のnext操作は回答確認までhiddenでなければなりません"
        )

    feedback_items = question["feedback"]
    assert isinstance(feedback_items, list)
    if len(feedback_items) != 1:
        errors.append(f"問題 {number}にはfeedback領域が1つ必要です")
    else:
        feedback = feedback_items[0]
        assert isinstance(feedback, dict)
        if (
            feedback.get("role") != "status"
            or feedback.get("aria-live") != "polite"
            or feedback.get("aria-atomic") != "true"
        ):
            errors.append(
                f"問題 {number}のfeedbackにはrole=status、aria-live=polite、aria-atomic=trueが必要です"
            )
    answer_panels = question["answer_panels"]
    assert isinstance(answer_panels, list)
    if len(answer_panels) != 1:
        errors.append(f"問題 {number}には回答後に開くanswer panelが1つ必要です")
    elif "hidden" not in answer_panels[0]:
        errors.append(
            f"問題 {number}のanswer panelは回答確認までhiddenでなければなりません"
        )

    if kind == "choice":
        radios = question["radios"]
        assert isinstance(radios, list)
        if len(radios) < 2:
            errors.append(f"問題 {number}のchoiceには2つ以上の選択肢が必要です")
        radio_names = {name for name, _value in radios if name}
        values = {value for _name, value in radios if value}
        if len(radio_names) != 1:
            errors.append(
                f"問題 {number}のradioは同じ空でないnameでまとめる必要があります"
            )
        correct = str(attrs.get("data-correct", ""))
        if not correct or correct not in values:
            errors.append(
                f"問題 {number}のdata-correctは実在する選択肢を参照する必要があります"
            )
    if kind == "reflection":
        if int(question["textareas"]) != 1:
            errors.append(f"問題 {number}のreflectionにはtextareaが1つ必要です")
        if int(question["answer_points"]) != 1:
            errors.append(
                f"問題 {number}のreflectionにはdata-answer-pointsが1つ必要です"
            )
    return errors


def validate_source(source: str, *, allow_placeholders: bool = False) -> list[str]:
    parser = LearningPageParser()
    parser.feed(source)
    parser.close()
    errors: list[str] = list(parser.unsafe)

    if not allow_placeholders and PLACEHOLDER_PATTERN.search(source):
        errors.append("未解決の{{...}} placeholderが残っています")

    if not parser.has_html_doctype:
        errors.append("HTML5 doctypeが必要です")
    if len(parser.html_attrs) != 1 or parser.html_attrs[0].get("lang") != "ja":
        errors.append("html要素にはlang=jaが必要です")
    if parser.page_roots != 1:
        errors.append("bodyにdata-repo-eli5-page=v1という学習ページ識別子が必要です")
    if parser.main_count != 1:
        errors.append("main要素が1つ必要です")

    section_counts = {name: parser.sections.count(name) for name in REQUIRED_SECTIONS}
    for name, count in sorted(section_counts.items()):
        if count != 1:
            errors.append(f"data-learning-section={name}が1つ必要です")
    unknown_sections = sorted(set(parser.sections) - REQUIRED_SECTIONS)
    if unknown_sections:
        errors.append(
            f"未定義のlearning sectionがあります: {', '.join(unknown_sections)}"
        )

    if parser.repo_meta != 1:
        errors.append("調査対象を固定するdata-repo-metaが1つ必要です")
    if (parser.repo_roots, parser.repo_branches, parser.repo_revisions) != (1, 1, 1):
        errors.append(
            "repository root、branch、revisionをそれぞれ1つ表示する必要があります"
        )
    if parser.repo_summaries != 1:
        errors.append(
            "repositoryまたは差分を一文で説明するdata-repo-summaryが1つ必要です"
        )
    if not 3 <= parser.flow_steps <= 5:
        errors.append("主要な流れを示すdata-flow-stepが3〜5個必要です")
    if parser.evidence_kinds.count("fact") < 2 or len(parser.source_refs) < 2:
        errors.append("確認済みの事実とsource referenceがそれぞれ2件以上必要です")

    if len(parser.visual_kinds) != 1:
        errors.append("data-visual-kindが1つ必要です")
        visual_kind = ""
    else:
        visual_kind = parser.visual_kinds[0][1]
        if visual_kind not in {"diagram", "table"}:
            errors.append("data-visual-kindはdiagramまたはtableでなければなりません")

    accessible_svgs = [
        svg
        for svg in parser.svgs
        if isinstance(svg["attrs"], dict)
        and str(svg["attrs"].get("aria-hidden", "")).casefold() != "true"
    ]
    if visual_kind == "diagram":
        if len(accessible_svgs) != 1:
            errors.append("diagramには主要なaccessible SVGが1つ必要です")
        for number, svg in enumerate(accessible_svgs, 1):
            errors.extend(_check_svg(svg, number))
    elif visual_kind == "table":
        visual_tag = parser.visual_kinds[0][0]
        if (
            visual_tag != "table"
            or parser.table_captions < 1
            or parser.table_headers < 1
        ):
            errors.append(
                "tableの可視化にはcaptionと見出しcellを持つtable要素が必要です"
            )

    if parser.quiz_roots != 1:
        errors.append("data-repo-eli5-quizが1つ必要です")
    if len(parser.quiz_progress) != 1:
        errors.append("data-quiz-progressが1つ必要です")
    else:
        progress = parser.quiz_progress[0]
        if (
            progress.get("role") != "status"
            or progress.get("aria-live") != "polite"
            or progress.get("aria-atomic") != "true"
        ):
            errors.append(
                "quiz progressにはrole=status、aria-live=polite、aria-atomic=trueが必要です"
            )
    if len(parser.quiz_questions) < 2:
        errors.append("quizには2問以上が必要です")
    kinds = {
        str(question["attrs"].get("data-question-kind", ""))
        for question in parser.quiz_questions
        if isinstance(question["attrs"], dict)
    }
    if not {"choice", "reflection"}.issubset(kinds):
        errors.append("quizにはchoice問題とreflection問題がそれぞれ必要です")
    if len(parser.quiz_questions) >= 2:
        first_attrs = parser.quiz_questions[0]["attrs"]
        second_attrs = parser.quiz_questions[1]["attrs"]
        assert isinstance(first_attrs, dict) and isinstance(second_attrs, dict)
        if (
            first_attrs.get("data-question-kind") != "reflection"
            or second_attrs.get("data-question-kind") != "choice"
        ):
            errors.append("quizの最初はreflection、次はchoiceでなければなりません")
        if "hidden" in first_attrs or any(
            isinstance(question["attrs"], dict) and "hidden" not in question["attrs"]
            for question in parser.quiz_questions[1:]
        ):
            errors.append(
                "quizは最初の1問だけを表示し、後続問題をhiddenにする必要があります"
            )
    for number, question in enumerate(parser.quiz_questions, 1):
        errors.extend(_check_question(question, number))
    if parser.quiz_noscript != 1:
        errors.append("quizにはJavaScript無効時のnoscript説明が1つ必要です")
    if (
        len(parser.quiz_complete) != 1
        or "hidden" not in parser.quiz_complete[0]
        or parser.quiz_complete[0].get("tabindex") != "-1"
    ):
        errors.append("quizにはhiddenかつtabindex=-1の完了領域が1つ必要です")
    reset_actions = [
        (action, button_type)
        for action, button_type in parser.quiz_actions
        if action == "reset"
    ]
    if reset_actions != [("reset", "button")]:
        errors.append("quizにはtype=buttonのreset操作が1つ必要です")

    if len(parser.scripts) != 1:
        errors.append("inline quiz controller scriptが1つ必要です")
    else:
        script = parser.scripts[0]
        attrs = script["attrs"]
        attr_names = script["attr_names"]
        body = script["body"]
        assert (
            isinstance(attrs, dict)
            and isinstance(attr_names, list)
            and isinstance(body, list)
        )
        if attr_names != ["data-repo-eli5-controller"]:
            errors.append(
                "quiz controller scriptにはdata-repo-eli5-controller属性だけを付けてください"
            )
        script_source = "".join(body)
        click_handlers = re.findall(
            r"addEventListener\s*\(\s*['\"]click['\"]", script_source
        )
        if len(click_handlers) < 3:
            errors.append("quiz controllerにはcheck、next、resetのclick処理が必要です")
        if not re.search(r"\.hidden\s*=\s*true", script_source) or not re.search(
            r"\.hidden\s*=\s*false", script_source
        ):
            errors.append("quiz controllerには問題、回答、完了領域の表示切替が必要です")
        for pattern, behavior in REQUIRED_CONTROLLER_PATTERNS.items():
            if re.search(pattern, script_source) is None:
                errors.append(f"quiz controllerに{behavior}が必要です")
        for pattern, label in FORBIDDEN_SCRIPT_PATTERNS.items():
            if re.search(pattern, script_source):
                errors.append(f"quiz controllerで{label}は使用できません")

    for tag, rel, attribute, value in parser.references:
        lowered = value.strip().casefold()
        if lowered.startswith(("javascript:", "data:text/html")):
            errors.append(f"<{tag}>に実行可能URLは使用できません")
            continue
        if attribute == "srcset" and value.strip():
            errors.append(f"<{tag}>のsrcsetは外部resource混在を防ぐため使用できません")
        elif tag == "script" and value.strip():
            errors.append("外部scriptは使用できません")
        elif tag == "link" and value.strip():
            errors.append("外部link resourceは使用できません")
        elif tag in {"form", "button"} and value.strip():
            errors.append(f"<{tag}>から外部へ送信できません")
        elif tag in RESOURCE_TAGS and not _is_embedded_reference(value):
            errors.append(f"<{tag}>の外部resourceは使用できません")

    style_source = "".join(parser.styles)
    css_urls = re.findall(r"url\s*\(\s*['\"]?([^)'\"\s]+)", style_source, re.IGNORECASE)
    if re.search(r"@import\b", style_source, re.IGNORECASE) or any(
        not value.startswith(("#", "data:image/")) for value in css_urls
    ):
        errors.append("CSSから外部resourceを読み込めません")
    if "prefers-reduced-motion" not in style_source:
        errors.append("prefers-reduced-motionのCSSが必要です")
    if re.search(r"@media\s+print\b", style_source, re.IGNORECASE) is None:
        errors.append("印刷用CSSが必要です")

    return errors


class SmokeResultParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.status = ""
        self.failures = ""

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        data = {name.casefold(): value or "" for name, value in attrs}
        if tag.casefold() == "output" and data.get("id") == "repo-eli5-smoke-result":
            self.status = data.get("data-status", "")
            self.failures = data.get("data-failures", "")


def find_browser() -> Path | None:
    configured = os.environ.get("REPO_ELI5_BROWSER")
    candidates = [configured] if configured else []
    candidates.extend(
        ["chromium", "chromium-browser", "google-chrome", "google-chrome-stable"]
    )
    for candidate in candidates:
        if not candidate:
            continue
        resolved = shutil.which(candidate)
        if resolved:
            return Path(resolved)
        path = Path(candidate).expanduser()
        if path.is_file() and os.access(path, os.X_OK):
            return path.resolve()
    return None


def _inject_browser_smoke(source: str) -> str | None:
    matches = list(re.finditer(r"</body\s*>", source, re.IGNORECASE))
    if len(matches) != 1:
        return None
    match = matches[0]
    return source[: match.start()] + BROWSER_SMOKE_SCRIPT + source[match.start() :]


def browser_smoke_file(path: Path, *, browser: Path | None = None) -> list[str]:
    browser = browser or find_browser()
    if browser is None:
        return [
            "browser smokeを実行できません。ChromiumをinstallするかREPO_ELI5_BROWSERを指定してください"
        ]
    try:
        source = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        return [str(exc)]
    instrumented = _inject_browser_smoke(source)
    if instrumented is None:
        return ["browser smokeにはbody終了tagが1つ必要です"]

    with tempfile.TemporaryDirectory(prefix="repo-eli5-browser-") as directory:
        temp_root = Path(directory)
        page = temp_root / "artifact.html"
        profile = temp_root / "profile"
        page.write_text(instrumented, encoding="utf-8")
        command = [
            str(browser),
            "--headless=new",
            "--disable-background-networking",
            "--disable-component-update",
            "--disable-default-apps",
            "--disable-domain-reliability",
            "--disable-extensions",
            "--disable-gpu",
            "--disable-sync",
            "--metrics-recording-only",
            "--mute-audio",
            "--no-first-run",
            "--no-pings",
            f"--user-data-dir={profile}",
            "--virtual-time-budget=2000",
            "--dump-dom",
            page.as_uri(),
        ]
        if hasattr(os, "geteuid") and os.geteuid() == 0:
            command.insert(1, "--no-sandbox")
        try:
            completed = subprocess.run(
                command,
                check=False,
                capture_output=True,
                text=True,
                timeout=20,
            )
        except (OSError, subprocess.TimeoutExpired) as exc:
            return [f"browser smokeの起動に失敗しました: {exc}"]
    if completed.returncode != 0:
        detail = completed.stderr.strip().splitlines()
        suffix = f": {detail[-1]}" if detail else ""
        return [f"browser smokeが終了code {completed.returncode}で失敗しました{suffix}"]

    result = SmokeResultParser()
    result.feed(completed.stdout)
    result.close()
    if result.status == "pass":
        return []
    failures = result.failures or "result_missing"
    return [f"browser smokeでquizの状態遷移が失敗しました: {failures}"]


def validate_file(path: Path, *, allow_placeholders: bool = False) -> list[str]:
    try:
        return validate_source(
            path.read_text(encoding="utf-8"), allow_placeholders=allow_placeholders
        )
    except (OSError, UnicodeError) as exc:
        return [str(exc)]


def main() -> int:
    argument_parser = argparse.ArgumentParser(description=__doc__)
    argument_parser.add_argument(
        "--template",
        action="store_true",
        help="placeholderを許可し、browser smokeを省略してtemplate構造だけを検査する",
    )
    argument_parser.add_argument("files", nargs="+", type=Path)
    args = argument_parser.parse_args()
    failed = False
    for path in args.files:
        errors = validate_file(path, allow_placeholders=args.template)
        if not errors and not args.template:
            errors.extend(browser_smoke_file(path))
        if errors:
            failed = True
            print(f"FAIL {path}")
            for error in errors:
                print(f"  - {error}")
        else:
            validation_kind = (
                "template static" if args.template else "static + browser smoke"
            )
            print(f"OK {path} ({validation_kind})")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
