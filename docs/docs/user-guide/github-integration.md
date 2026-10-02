---
sidebar_position: 4
title: GitHub Integration
---

# GitHub Integration

Codalyra connects to GitHub for OAuth login, repository browsing, PR review, and automated webhooks.

## Connecting GitHub

### Option 1: Sign In with GitHub

Click **Continue with GitHub** on the login page. This:

1. Redirects you to GitHub to authorize the app
2. Grants access to your profile, email, and repositories
3. Creates or links your Codalyra account
4. Stores your GitHub access token (encrypted) for API calls

### Option 2: Link to Existing Account

If you already have a Codalyra account:

1. Go to **Settings** → **GitHub**
2. Click **Connect GitHub**
3. Authorize on GitHub
4. Your accounts are now linked

## Browsing Repositories

Once connected:

1. Go to any project → **GitHub** tab
2. Click **Browse Repos** to see your accessible repositories
3. Connect a repository to the project
4. Browse open pull requests
5. Click a PR to view its diff and trigger a review

## Reviewing Pull Requests

1. Select a repository and PR
2. Click **Review This PR**
3. Codalyra fetches the diff via the GitHub API
4. The review runs through the full multi-agent pipeline
5. Results appear in the report view

### Posting Comments

After a review completes, you can post findings back to the PR:

1. Open the review report
2. Click **Post to GitHub**
3. A formatted comment with findings and score is added to the PR

## Webhooks (Auto-Review)

### Setup

1. In your GitHub repository: **Settings** → **Webhooks** → **Add webhook**
2. **Payload URL**: `https://your-domain.com/api/v1/github/webhook`
3. **Content type**: `application/json`
4. **Secret**: Match your `GITHUB_WEBHOOK_SECRET` environment variable
5. **Events**: Select **Pull requests**

### How It Works

When a PR is opened or updated:

1. GitHub sends a webhook to Codalyra
2. The webhook handler verifies the HMAC-SHA256 signature
3. It finds the user by GitHub ID and locates the connected repository
4. A review is automatically created and dispatched
5. Notifications fire to Slack/Discord when complete

### Supported Events

| Event | Action | Behavior |
|-------|--------|----------|
| `pull_request` | `opened` | Triggers a new review |
| `pull_request` | `synchronize` | Triggers a review on new push |

## Required Scopes

The GitHub OAuth app requests:

- `read:user` — Profile information
- `user:email` — Email address
- `repo` — Repository access (read diffs, post comments)

## Setting Up a GitHub OAuth App

1. Go to **GitHub** → **Settings** → **Developer settings** → **OAuth Apps**
2. Click **New OAuth App**
3. Set the callback URL to `https://your-domain.com/auth/github/callback`
4. Copy the **Client ID** and **Client Secret**
5. Set them as `GITHUB_CLIENT_ID` and `GITHUB_CLIENT_SECRET` in your backend `.env`
