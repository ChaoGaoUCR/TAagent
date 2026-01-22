# TA Agent (Canvas + LLM)

这是一个用于 Canvas 作业自动评分的本地脚本工具：
- 自动拉取一门课中某个作业的学生提交（支持 `.zip`）
- 解析文档文本（txt/md/docx/pdf）
- 根据你提供的 rubric（JSON）调用 OpenAI/Anthropic 打分
- 生成 Markdown 评分报告 + 成绩汇总 CSV

> 适用：文档类作业（论文、报告、作业说明等）

---

## 目录
- [安装](#安装)
- [配置](#配置)
- [Rubric 格式](#rubric-格式)
- [运行](#运行)
- [输出结果](#输出结果)
- [常见问题](#常见问题)
- [安全与隐私建议](#安全与隐私建议)

---

## 安装

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

---

## 配置

复制示例配置：

```bash
cp config.example.json config.json
```

编辑 `config.json`，关键字段说明如下：

```json
{
  "canvas": {
    "base_url": "https://canvas.yourschool.edu",
    "course_id": 12345,
    "assignment_id": 67890,
    "api_token": "CANVAS_API_TOKEN"
  },
  "rubric_path": "rubric.json",
  "output_dir": "outputs",
  "llm": {
    "provider": "openai",
    "model": "gpt-4o",
    "api_key": "OPENAI_API_KEY"
  },
  "limits": {
    "max_submissions": 50
  }
}
```

说明：
- `base_url`: 你的 Canvas 域名，如 `https://canvas.yourschool.edu`
- `course_id`: Canvas 课程 ID
- `assignment_id`: 作业 ID
- `api_token`: Canvas 访问令牌（在 Canvas 个人设置里生成）
- `rubric_path`: Rubric JSON 文件路径
- `output_dir`: 输出目录
- `provider`: `openai` 或 `anthropic`
- `model`: 模型名称，如 `gpt-4o` / `gpt-4o-mini`
- `api_key`: 对应模型服务的 API Key
- `max_submissions`: 可选，限制最多处理的提交数量

---

## Rubric 格式

Rubric 使用 JSON 格式，至少包含 `criteria`，每项需要 `id` 和 `max_points`：

```json
{
  "title": "Essay Rubric",
  "criteria": [
    {
      "id": "thesis",
      "name": "Thesis & Argument",
      "description": "Clear thesis, well-supported argument.",
      "max_points": 10
    },
    {
      "id": "organization",
      "name": "Organization",
      "description": "Logical flow, coherent structure.",
      "max_points": 10
    }
  ]
}
```

说明：
- `id` 是该维度的唯一标识，LLM 必须返回相同的 id 才能对齐评分
- `max_points` 用于限制该维度最高分
- `name` / `description` 用于给模型参考（建议写清楚）

---

## 运行

```bash
python -m src.main --config config.json
```

流程：
1. 拉取 Canvas 提交
2. 下载附件（如 `.zip` 会自动解压）
3. 读取第一份可解析文档
4. 调用 LLM 评分
5. 生成 Markdown 评分报告与 `grades.csv`

---

## 输出结果

运行后会生成：

- `outputs/submission_<id>/report.md`
- `outputs/grades.csv`

`report.md` 示例结构：

```
# 学生名 — 作业名

- Submission ID: ...
- User ID: ...
- File: ...
- Score: ... / ...

## Summary
总体评价...

## Rubric Breakdown
| Criterion | Score | Max | Comment |
|---|---:|---:|---|
| Thesis & Argument | 8 | 10 | ... |
```

`grades.csv` 示例列：

```
submission_id,user_id,student_name,score,max_score,report_path
```

---

## 常见问题

**1. 如何限制提交数量？**  
在 `config.json` 里设置：

```json
"limits": { "max_submissions": 10 }
```

**2. 支持哪些文件格式？**  
支持 `.txt` / `.md` / `.docx` / `.pdf`。如果是 `.zip` 会先解压。

**3. 如果一个提交里有多个文件？**  
当前逻辑是“找到第一个可读文档就打分”。如需合并评分或指定规则可以扩展。

**4. 模型输出不稳定怎么办？**  
可以降低 `temperature`，或增加 prompt 约束（在 `src/llm.py`）。

---

## 安全与隐私建议

- 建议在本地安全地保存 `config.json`（包含 API Key）
- 可用环境变量替代 API Key（需要扩展代码）
- 处理学生作业时注意校内政策

---

如需功能扩展（比如写回 Canvas 成绩、支持多文件合并评分、HTML 报告等），直接告诉我。
