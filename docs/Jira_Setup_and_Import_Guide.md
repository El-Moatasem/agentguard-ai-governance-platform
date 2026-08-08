# Jira Setup and Import Guide

## Should AgentGuard use Jira?

Yes. Jira is an appropriate agile task board for the Capstone and provides strong evidence of sprint planning, user stories, subtasks, status changes, and completion history. For a solo project, GitHub Projects is simpler and integrates more directly with commits and pull requests; however, Jira is a good choice when you want to demonstrate an industry-standard Scrum workflow.

**Recommendation:** Use Jira if you are comfortable maintaining it consistently. Do not use both Jira and GitHub Projects as competing sources of truth. Keep Jira as the official board and link every story to the relevant GitHub issue, branch, commit, or pull request.

## Suggested Jira Project

- **Project name:** AgentGuard MSSE Capstone
- **Project key:** AG
- **Template:** Scrum
- **Board:** One Scrum board
- **Sprints:** Sprint 1, Sprint 2, Sprint 3, Sprint 4

## Suggested Workflow

`Backlog → Selected for Development → In Progress → Code Review → Testing → Done`

Use `Blocked` as a flag or an additional status when required.

## Recommended Issue Types

- Epic
- Story
- Task
- Sub-task
- Bug

## Recommended Labels

- `capstone`
- `sprint-1` / `sprint-2`
- `backend`
- `frontend`
- `database`
- `policy-engine`
- `audit`
- `security`
- `testing`
- `documentation`
- `devops`

## CSV Files

- `sprints/sprint_1/jira_import_sprint_1.csv`
- `sprints/sprint_2/jira_import_sprint_2.csv`
- `docs/jira_import_all_sprints_1_2.csv`

The CSV files include `Issue ID` and `Parent ID` columns so that stories can be associated with their epic and tasks can be associated with their parent story. Jira CSV field names and import permissions may vary by Jira configuration. During import, map the supplied columns to the closest available Jira fields.

## After Import

1. Create Sprint 1 and Sprint 2 on the backlog.
2. Assign the imported stories to the appropriate sprint.
3. Review estimates and priorities instead of accepting them blindly.
4. Set Sprint 1 items to Done only when you have evidence.
5. Set Sprint 2 items to In Review until you personally run and verify the generated release.
6. Attach test output, screenshots, demo recordings, and pull-request links.
7. Record any scope changes or deferred work in the relevant story.
8. Export or screenshot the final board for the Capstone documentation.

## Academic Evidence Guidance

The board should reflect your actual process. Generated stories are planning material, not evidence that the work was personally completed. Use your own commits, decisions, testing, demos, and retrospective notes to demonstrate authorship and learning.
