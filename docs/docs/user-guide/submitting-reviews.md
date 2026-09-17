---
sidebar_position: 2
title: Submitting Reviews
---

# Submitting Code Reviews

There are three ways to submit code for review in Codalyra-AI.

## Method 1: Paste a Diff

The simplest approach — paste a unified diff directly:

1. Navigate to your project from the Dashboard
2. Click **New Review**
3. Paste your diff (the output of `git diff`) into the text area
4. Click **Submit Review**

The system detects languages automatically from file extensions in the diff.

## Method 2: GitHub Pull Request

If you've connected a GitHub repository:

1. Go to your project → **GitHub** tab
2. Browse your repositories and select a PR
3. Click **Review This PR**
4. Codalyra fetches the diff automatically

You can also post the review results back as a PR comment.

## Method 3: Automatic via Webhooks

Set up a GitHub webhook to auto-trigger reviews on every PR:

1. Go to **Settings** → **GitHub Integration**
2. Copy the webhook URL
3. Add it to your GitHub repo's Settings → Webhooks
4. Set the secret to match your `GITHUB_WEBHOOK_SECRET`
5. Select **Pull request** events

Reviews trigger automatically on `opened` and `synchronize` (new push) events.

## Review Options

Before submitting, you can configure:

- **Agents** — Enable/disable specific specialist agents
- **Provider** — Choose Gemini, OpenAI, or Anthropic per agent
- **Custom model** — Override the default model for any agent

## What Happens After Submission

1. A `Review` record is created with status `pending`
2. Celery dispatches 6 tasks: 4 specialists + 1 synthesis + 1 baseline
3. Specialists run **in parallel** (static analysis → LLM call per agent)
4. When all 4 specialists finish, synthesis merges their findings
5. The baseline runs independently as a single-pass control
6. Status updates stream via WebSocket in real-time
7. Notifications fire to Slack/Discord if configured

Typical review time: **10–25 seconds** depending on diff size and LLM provider.

## Diff Size Limits

Large diffs are rejected before any processing begins. The `MAX_DIFF_SIZE` configuration prevents runaway LLM costs. If your diff is too large, consider splitting it into smaller PRs.
