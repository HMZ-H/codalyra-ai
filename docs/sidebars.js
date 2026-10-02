/** @type {import('@docusaurus/plugin-content-docs').SidebarsConfig} */
const sidebars = {
  userGuideSidebar: [
    {
      type: 'category',
      label: 'User Guide',
      collapsed: false,
      items: [
        'user-guide/getting-started',
        'user-guide/submitting-reviews',
        'user-guide/understanding-reports',
        'user-guide/github-integration',
        'user-guide/custom-rules',
        'user-guide/teams',
        'user-guide/settings',
      ],
    },
  ],
  developerGuideSidebar: [
    {
      type: 'category',
      label: 'Developer Guide',
      collapsed: false,
      items: [
        'developer-guide/architecture',
        'developer-guide/review-pipeline',
        'developer-guide/multi-agent-system',
        'developer-guide/llm-providers',
        'developer-guide/static-analysis',
        'developer-guide/database-schema',
        'developer-guide/authentication',
        'developer-guide/testing',
      ],
    },
    {
      type: 'category',
      label: 'Deployment',
      collapsed: false,
      items: [
        'deployment/docker',
        'deployment/environment-variables',
        'deployment/ci-cd',
        'deployment/production-checklist',
      ],
    },
  ],
  apiReferenceSidebar: [
    {
      type: 'category',
      label: 'API Reference',
      collapsed: false,
      items: [
        'api-reference/overview',
        'api-reference/auth',
        'api-reference/reviews',
        'api-reference/projects',
        'api-reference/github',
        'api-reference/analytics',
      ],
    },
  ],
};

export default sidebars;
