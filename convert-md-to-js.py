#!/usr/bin/env python3
"""
Convert markdown formatted questions to embedded JavaScript data
"""

import re
import json

def extract_questions_from_md(md_file):
    """Parse markdown file and extract questions"""

    print(f"Reading: {md_file}\n")
    with open(md_file, 'r', encoding='utf-8') as f:
        content = f.read()

    questions = []

    # Split by question blocks (### ข้อ N:)
    # Pattern: ### ข้อ 21: question text
    pattern = r'### ข้อ (\d+):([^\n]+)\n'

    question_blocks = re.split(r'(?=### ข้อ \d+:)', content)

    for block in question_blocks:
        if not block.strip():
            continue

        lines = block.split('\n')

        # Extract question number and text
        q_match = re.match(r'### ข้อ (\d+):(.+)', lines[0])
        if not q_match:
            continue

        q_num = int(q_match.group(1))
        q_text = q_match.group(2).strip()

        # Find the Question section
        q_start = None
        for i, line in enumerate(lines):
            if line.strip() == '### Question':
                q_start = i + 1
                break

        if q_start is None:
            print(f"⚠️  ข้อ {q_num}: Could not find Question section")
            continue

        # Extract question text and options
        question_full = []
        options = []
        opt_idx = 0

        for i in range(q_start, len(lines)):
            line = lines[i]

            # Stop at next section
            if line.startswith('**ตัวเลือก:**') or line.startswith('### Answer'):
                break

            # Match options: "1) text" or "1) text"
            opt_match = re.match(r'^\s*(\d+)\)\s+(.+)$', line)
            if opt_match:
                opt_num = int(opt_match.group(1))
                opt_text = opt_match.group(2).strip()
                if opt_num <= 4:
                    options.append(opt_text)
            elif line.strip() and not line.startswith('**') and opt_idx == 0:
                # Collect question text before options
                question_full.append(line.strip())

        # Extract answer and explanation
        answer_idx = None
        explanation = []
        exp_start = False

        for i, line in enumerate(lines):
            # Find answer: **เฉลย: N)**
            if '**เฉลย:**' in line or 'เฉลย:' in line:
                ans_match = re.search(r'(\d+)\)', line)
                if ans_match:
                    answer_idx = int(ans_match.group(1)) - 1

            # Find explanation start
            if '**คำอธิบายแนวคิด:**' in line or 'คำอธิบายแนวคิด:' in line:
                exp_start = True
                continue

            # Collect explanation until next question
            if exp_start:
                if line.startswith('###') or line.startswith('---'):
                    break
                if line.strip():
                    explanation.append(line.strip())

        # Validate
        if len(options) != 4:
            print(f"⚠️  ข้อ {q_num}: Only {len(options)} options found, skipping")
            continue

        if answer_idx is None:
            print(f"⚠️  ข้อ {q_num}: Could not find answer, skipping")
            continue

        # Get full question text
        q_full_text = q_text + ' ' + ' '.join(question_full)
        q_full_text = q_full_text.strip()

        # Get explanation
        exp_text = ' '.join(explanation)
        exp_text = re.sub(r'\s+', ' ', exp_text).strip()

        # Create question object
        q_obj = {
            'q': q_full_text,
            'c': options,
            'a': answer_idx,
            'exp': exp_text[:500] if len(exp_text) > 500 else exp_text,  # Limit explanation length
            'tag': 'IC Exam'
        }

        questions.append(q_obj)
        print(f"✅ ข้อ {q_num}: {q_full_text[:60]}...")

    return questions

def questions_to_javascript(questions):
    """Convert questions to JavaScript code"""

    code = 'const EMBEDDED_QUESTIONS = [\n'

    for q in questions:
        # Escape single quotes and backslashes
        q_text = q['q'].replace("\\", "\\\\").replace("'", "\\'")
        exp_text = q['exp'].replace("\\", "\\\\").replace("'", "\\'")

        # Escape choices
        choices = [opt.replace("\\", "\\\\").replace("'", "\\'") for opt in q['c']]

        code += f"  {{q:'{q_text}',c:['{choices[0]}','{choices[1]}','{choices[2]}','{choices[3]}'],a:{q['a']},exp:'{exp_text}',tag:'{q['tag']}'}},\n"

    code = code.rstrip(',\n') + '\n'
    code += '];\n'

    return code

def main():
    md_file = '/sessions/happy-gracious-shannon/mnt/uploads/MS one mockup i.md'
    output_file = '/sessions/happy-gracious-shannon/mnt/Claude KN/outputs/Magniselect html/embedded-questions.js'

    try:
        # Extract questions
        questions = extract_questions_from_md(md_file)

        print(f'\n✅ Successfully extracted {len(questions)} questions\n')

        if len(questions) == 0:
            print("❌ No questions found!")
            return False

        # Generate JavaScript code
        js_code = questions_to_javascript(questions)

        # Save to file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(js_code)

        print(f'✅ Generated {output_file}')
        print(f'File size: {len(js_code):,} bytes')
        print(f'Number of questions: {len(questions)}')
        print(f'\nFirst question preview:\n{js_code[30:300]}...\n')

        return True

    except Exception as e:
        print(f'❌ Error: {e}')
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)
