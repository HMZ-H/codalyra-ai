---
sidebar_position: 6
title: Teams
---

# Teams & Collaboration

Codalyra supports teams with role-based access for collaborative code review.

## Creating a Team

1. Navigate to **Teams** from the sidebar
2. Click **Create Team**
3. Enter a team name and optional description
4. You're automatically added as **Admin**

## Roles

| Role | View Reviews | Create Reviews | Manage Members | Delete Team |
|------|-------------|----------------|----------------|-------------|
| **Admin** | ✅ | ✅ | ✅ | ✅ |
| **Reviewer** | ✅ | ✅ | ❌ | ❌ |
| **Viewer** | ✅ | ❌ | ❌ | ❌ |

## Managing Members

As an admin:

1. Open your team page
2. Click **Add Member**
3. Search by email or username
4. Assign a role (admin, reviewer, or viewer)
5. Click **Add**

To change a member's role or remove them, use the member list actions.

The team owner (creator) cannot be removed.

## Linking Projects to Teams

Projects can optionally be linked to a team, making them visible to all team members based on their roles.

## Notifications

Teams benefit from shared notification settings. When a review completes on a team project, Slack/Discord notifications include the team context.

### Setting Up Slack Notifications

1. Create a Slack Incoming Webhook in your workspace
2. Add the webhook URL to **Settings** → **Notifications** or set `SLACK_WEBHOOK_URL` in your environment
3. Review completions post formatted messages with score, finding count, and severity breakdown

### Setting Up Discord Notifications

1. Create a Discord webhook in your channel settings
2. Add the webhook URL to **Settings** → **Notifications** or set `DISCORD_WEBHOOK_URL`
3. Reviews post as rich embeds with color-coded scores (green ≥80, yellow ≥60, red <60)
