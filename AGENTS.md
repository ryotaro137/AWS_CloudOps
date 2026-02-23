# Agent Global Instructions

## AWS Questions Policy

Whenever the user asks a question, requests an explanation, or seeks advice related to AWS (Amazon Web Services), you **MUST** follow these rules:

1. **Always Use a Skill**: You must utilize the appropriate skill from the `.agent/skills/` directory.
2. **`cloudops-practical` Skill**: Use this skill when the question is related to learning AWS services, exam preparation (e.g., CloudOps, SysOps, Solutions Architect), practical operational use cases, or freelance/side-job demand and unit prices. (This is the primary skill for learning and operations).
3. **`aws-skills` Skill**: Use this skill when the question is related to infrastructure automation, IaC (Terraform, CloudFormation), or cloud architecture patterns.
4. **Execution**: Before answering, you must read the `SKILL.md` of the chosen skill using the `view_file` tool to ensure you strictly follow its specific formatting and output guidelines. At the beginning of your response, explicitly mention which skill you applied.
