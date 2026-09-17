import clsx from 'clsx';
import Heading from '@theme/Heading';
import styles from './styles.module.css';

const FeatureList = [
  {
    title: 'Multi-Agent Review',
    description: '4 specialist AI agents analyze code from different angles — logic, security, performance, and quality — then synthesis merges their findings.',
  },
  {
    title: 'Static + AI Hybrid',
    description: 'Deterministic regex pre-scan feeds findings into the LLM, boosting recall to 95% while reducing false positives and cost per finding.',
  },
  {
    title: 'Deploy in Minutes',
    description: 'Docker Compose with 5 services, health checks, and auto-migration. Connect GitHub, submit a diff, and get a scored report.',
  },
];

function Feature({title, description}) {
  return (
    <div className={clsx('col col--4')}>
      <div className="text--center padding-horiz--md">
        <Heading as="h3">{title}</Heading>
        <p>{description}</p>
      </div>
    </div>
  );
}

export default function HomepageFeatures() {
  return (
    <section className={styles.features}>
      <div className="container">
        <div className="row">
          {FeatureList.map((props, idx) => (
            <Feature key={idx} {...props} />
          ))}
        </div>
      </div>
    </section>
  );
}
