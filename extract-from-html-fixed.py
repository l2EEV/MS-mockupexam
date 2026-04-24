#!/usr/bin/env python3
"""
Extract IC exam questions from ic_quiz_mock6.html and convert to embedded-questions.js format
"""

import re
import json
import os

def extract_questions_from_html():
    """Extract questions from ic_quiz_mock6.html"""

    html_file = "/sessions/happy-gracious-shannon/mnt/Claude KN/outputs/Mock exam/ic_quiz_mock6.html"
    output_file = "embedded-questions.js"

    try:
        with open(html_file, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"ERROR: Cannot find {html_file}")
        return False

    # Find the const questions = [...]; array
    # Look for pattern: const questions = [{...}, {...}, ...];
    pattern = r'const\s+questions\s*=\s*(\[[\s\S]*?\]);'
    match = re.search(pattern, content)

    if not match:
        print("ERROR: Could not find 'const questions = [...]' in HTML file")
        return False

    questions_str = match.group(1)

    # Extract individual question objects
    # Pattern: {q: "...", choices: [...], answer: N, exp: "..."}
    question_pattern = r'\{\s*q:\s*"([^"]*?)"\s*,\s*choices:\s*\[(.*?)\]\s*,\s*answer:\s*(\d+)\s*,\s*exp:\s*"([^"]*)"\s*\}'

    questions = []
    for match in re.finditer(question_pattern, questions_str, re.DOTALL):
        q_text = match.group(1)
        choices_str = match.group(2)
        answer_idx = int(match.group(3))
        explanation = match.group(4)

        # Extract individual choices from the choices array
        # Pattern: "choice1", "choice2", "choice3", "choice4"
        choices = re.findall(r'"([^"]*?)"', choices_str)

        # Clean up newlines in question text (replace \n with space)
        q_text = q_text.replace('\\n', ' ').strip()
        explanation = explanation.replace('\\n', ' ').strip()

        if len(choices) >= 4:  # Ensure we have at least 4 choices
            question = {
                'q': q_text,
                'c': choices[:4],  # Take only first 4 choices
                'a': answer_idx,
                'exp': explanation,
                'tag': 'IC Exam'
            }
            questions.append(question)

    if not questions:
        print("ERROR: No questions extracted from HTML")
        return False

    print(f"Successfully extracted {len(questions)} questions")

    # Generate JavaScript file
    js_content = "const EMBEDDED_QUESTIONS = [\n"
    for i, q in enumerate(questions):
        # Escape quotes and backslashes for JavaScript
        q_text = q['q'].replace('\\', '\\\\').replace('"', '\\"')
        exp_text = q['exp'].replace('\\', '\\\\').replace('"', '\\"')

        js_content += "  {\n"
        js_content += f"    q: \"{q_text}\",\n"
        js_content += f"    c: {json.dumps(q['c'], ensure_ascii=False)},\n"
        js_content += f"    a: {q['a']},\n"
        js_content += f"    exp: \"{exp_text}\",\n"
        js_content += f"    tag: \"{q['tag']}\"\n"
        js_content += "  }"

        if i < len(questions) - 1:
            js_content += ",\n"
        else:
            js_content += "\n"

    js_content += "];\n"

    # Write to file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(js_content)

    print(f"Saved {len(questions)} questions to {output_file}")
    return True

if __name__ == "__main__":
    success = extract_questions_from_html()
    exit(0 if success else 1)
