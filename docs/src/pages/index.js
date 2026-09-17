import clsx from 'clsx';
import Link from '@docusaurus/Link';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import Layout from '@theme/Layout';
import Heading from '@theme/Heading';
import styles from './index.module.css';

function HomepageHeader() {
  const {siteConfig} = useDocusaurusContext();
  return (
    <header className={clsx('hero hero--primary', styles.heroBanner)}>
      <div className="container">
        <Heading as="h1" className="hero__title">
          {siteConfig.title}
        </Heading>
        <p className="hero__subtitle">{siteConfig.tagline}</p>
        <p style={{fontSize: '1.1rem', maxWidth: '600px', margin: '0 auto 1.5rem'}}>
          4 specialist AI agents analyze your code from different angles, then a synthesis agent
          combines their findings into a unified, prioritized report.
        </p>
        <div className={styles.buttons}>
          <Link
            className="button button--secondary button--lg"
            to="/docs/user-guide/getting-started">
            Get Started
          </Link>
          <Link
            className="button button--outline button--secondary button--lg"
            to="/docs/developer-guide/architecture"
            style={{marginLeft: '1rem'}}>
            Developer Guide
          </Link>
        </div>
      </div>
    </header>
  );
}

const features = [
  {
    title: 'Multi-Agent Analysis',
    description: 'Logic, Security, Performance, and Quality agents run in parallel via Celery, each with domain-specific prompts and static pre-analysis.',
  },
  {
    title: 'Hybrid Static + AI',
    description: 'Regex catches hardcoded secrets and code smells deterministically. The LLM builds on those findings for deeper semantic analysis.',
  },
  {
    title: 'Pluggable LLM Providers',
    description: 'Gemini, OpenAI, and Anthropic — configurable per-agent per-project. API keys encrypted at rest with Fernet.',
  },
  {
    title: 'GitHub Integration',
    description: 'OAuth login, PR browsing, diff fetching, comment posting, and webhook-triggered auto-reviews with HMAC verification.',
  },
  {
    title: 'Built-in Baseline',
    description: 'Every review includes a single-pass control. Multi-agent catches 176% more findings — measurable, not claimed.',
  },
  {
    title: 'One-Command Deploy',
    description: '5 Docker Compose services with health checks, auto-migration, and nginx reverse proxy. Production-ready.',
  },
];

function Feature({title, description}) {
  return (
    <div className={clsx('col col--4')}>
      <div className="padding-horiz--md" style={{marginBottom: '2rem'}}>
        <Heading as="h3">{title}</Heading>
        <p>{description}</p>
      </div>
    </div>
  );
}

export default function Home() {
  const {siteConfig} = useDocusaurusContext();
  return (
    <Layout
      title="Documentation"
      description="Multi-Agent AI Code Review Pipeline — User Guide, Developer Guide, and API Reference">
      <HomepageHeader />
      <main>
        <section style={{padding: '2rem 0'}}>
          <div className="container">
            <div className="row">
              {features.map((props, idx) => (
                <Feature key={idx} {...props} />
              ))}
            </div>
          </div>
        </section>
      </main>
    </Layout>
  );
}
