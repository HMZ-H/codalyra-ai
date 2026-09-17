import {themes as prismThemes} from 'prism-react-renderer';

/** @type {import('@docusaurus/types').Config} */
const config = {
  title: 'Codalyra-AI',
  tagline: 'Multi-Agent AI Code Review Pipeline',
  favicon: 'img/favicon.ico',

  future: {
    v4: true,
  },

  url: 'https://hmz-h.github.io',
  baseUrl: '/codalyra-ai/',

  organizationName: 'HMZ-H',
  projectName: 'codalyra-ai',

  onBrokenLinks: 'throw',

  markdown: {
    format: 'detect',
  },

  i18n: {
    defaultLocale: 'en',
    locales: ['en'],
  },

  presets: [
    [
      'classic',
      /** @type {import('@docusaurus/preset-classic').Options} */
      ({
        docs: {
          sidebarPath: './sidebars.js',
          editUrl: 'https://github.com/HMZ-H/codalyra-ai/tree/main/docs/',
          remarkPlugins: [],
        },
        blog: {
          showReadingTime: true,
          feedOptions: {
            type: ['rss', 'atom'],
            xslt: true,
          },
          editUrl: 'https://github.com/HMZ-H/codalyra-ai/tree/main/docs/',
          onInlineTags: 'warn',
          onInlineAuthors: 'warn',
          onUntruncatedBlogPosts: 'warn',
          remarkPlugins: [],
        },
        theme: {
          customCss: './src/css/custom.css',
        },
      }),
    ],
  ],

  themeConfig:
    /** @type {import('@docusaurus/preset-classic').ThemeConfig} */
    ({
      image: 'img/codalyra-social-card.png',
      colorMode: {
        defaultMode: 'dark',
        respectPrefersColorScheme: true,
      },
      navbar: {
        title: 'Codalyra-AI',
        logo: {
          alt: 'Codalyra Logo',
          src: 'img/logo.svg',
        },
        items: [
          {
            type: 'docSidebar',
            sidebarId: 'userGuideSidebar',
            position: 'left',
            label: 'User Guide',
          },
          {
            type: 'docSidebar',
            sidebarId: 'developerGuideSidebar',
            position: 'left',
            label: 'Developer Guide',
          },
          {
            type: 'docSidebar',
            sidebarId: 'apiReferenceSidebar',
            position: 'left',
            label: 'API Reference',
          },
          {to: '/blog', label: 'Blog', position: 'left'},
          {
            href: 'https://github.com/HMZ-H/codalyra-ai',
            label: 'GitHub',
            position: 'right',
          },
        ],
      },
      footer: {
        style: 'dark',
        links: [
          {
            title: 'Documentation',
            items: [
              { label: 'User Guide', to: '/docs/user-guide/getting-started' },
              { label: 'Developer Guide', to: '/docs/developer-guide/architecture' },
              { label: 'API Reference', to: '/docs/api-reference/overview' },
            ],
          },
          {
            title: 'Deployment',
            items: [
              { label: 'Docker Compose', to: '/docs/deployment/docker' },
              { label: 'Environment Variables', to: '/docs/deployment/environment-variables' },
            ],
          },
          {
            title: 'More',
            items: [
              { label: 'Blog', to: '/blog' },
              { label: 'GitHub', href: 'https://github.com/HMZ-H/codalyra-ai' },
            ],
          },
        ],
        copyright: `Copyright © ${new Date().getFullYear()} Codalyra-AI. Built by Hamza Haji.`,
      },
      prism: {
        theme: prismThemes.github,
        darkTheme: prismThemes.dracula,
        additionalLanguages: ['bash', 'python', 'json', 'toml', 'yaml', 'docker'],
      },
    }),
};

export default config;
