const docNames = [
  ['Customer Queue Routing Playbook', 'PDF', 'Operations', 'v3.2', 'Indexed'],
  ['Enterprise SLA Matrix', 'XLSX', 'Success', 'v2.8', 'Indexed'],
  ['Priority Escalation Policy', 'DOCX', 'Operations', 'v4.1', 'Indexed'],
  ['Ticket Deduplication Rules', 'MD', 'Product', 'v1.9', 'Indexed'],
  ['Inbox Assignment API Notes', 'HTML', 'Engineering', 'v2.4', 'Needs re-index'],
  ['Northstar Onboarding Guide', 'PDF', 'Implementation', 'v5.0', 'Indexed'],
  ['Billing Inquiry Triage', 'DOCX', 'Finance Ops', 'v2.1', 'Indexed'],
  ['Incident Communication Templates', 'MD', 'Support', 'v3.6', 'Indexed'],
  ['Conversation Tagging Taxonomy', 'CSV', 'Data Ops', 'v1.7', 'Indexing'],
  ['Regional Working Hours Rules', 'XLSX', 'Operations', 'v2.2', 'Indexed'],
  ['SupportFlow Admin Permissions', 'PDF', 'Security', 'v3.4', 'Indexed'],
  ['GDPR Data Deletion Workflow', 'DOCX', 'Compliance', 'v2.9', 'Indexed'],
  ['Customer Sentiment Signals', 'CSV', 'Analytics', 'v1.5', 'Indexed'],
  ['Omnichannel Inbox Setup', 'HTML', 'Implementation', 'v3.0', 'Indexed'],
  ['Webhook Retry Behavior', 'MD', 'Engineering', 'v2.7', 'Needs re-index'],
  ['Knowledge Base Deflection Plan', 'PDF', 'Success', 'v1.8', 'Indexed'],
  ['Agent Productivity Benchmarks', 'XLSX', 'Analytics', 'v4.0', 'Indexed'],
  ['Trial Account Support Scope', 'DOCX', 'Sales Ops', 'v2.3', 'Indexed'],
  ['VIP Account Handling Rules', 'PDF', 'Support', 'v3.8', 'Indexed'],
  ['Attachment Security Review', 'MD', 'Security', 'v1.6', 'Indexed'],
  ['Case Merge Audit Checklist', 'PDF', 'Compliance', 'v2.5', 'Indexed'],
  ['Live Chat Handoff Patterns', 'HTML', 'Product', 'v3.1', 'Indexed'],
  ['CSAT Follow-up Automation', 'DOCX', 'Success', 'v1.4', 'Indexed'],
  ['Queue Health Dashboard Spec', 'MD', 'Analytics', 'v2.6', 'Indexed'],
  ['Auto Reply Governance', 'PDF', 'Compliance', 'v2.0', 'Indexed'],
  ['Partner Support Workflow', 'DOCX', 'Partner Ops', 'v3.7', 'Needs re-index'],
  ['Agent Skill Group Mapping', 'CSV', 'Operations', 'v4.2', 'Indexed'],
  ['Migration Import Error Catalog', 'XLSX', 'Implementation', 'v1.9', 'Indexed'],
  ['Mobile Push Notification Rules', 'MD', 'Product', 'v2.8', 'Indexed'],
  ['SupportFlow Public API Limits', 'HTML', 'Engineering', 'v3.3', 'Indexed'],
  ['Refund Exception Playbook', 'PDF', 'Finance Ops', 'v2.7', 'Indexed'],
  ['Macro Library Maintenance', 'DOCX', 'Support', 'v3.9', 'Indexed'],
  ['Escalation Ownership RACI', 'XLSX', 'Operations', 'v2.4', 'Indexed'],
  ['Churn Risk Inquiry Signals', 'CSV', 'Analytics', 'v1.8', 'Indexing'],
  ['SSO Login Troubleshooting', 'PDF', 'Security', 'v4.5', 'Indexed'],
  ['Customer Portal Release Notes', 'MD', 'Product', 'v5.1', 'Indexed'],
  ['SLA Breach Retrospective Form', 'DOCX', 'Success', 'v2.2', 'Indexed'],
  ['AI Draft Reply Review Guide', 'PDF', 'Support', 'v1.3', 'Indexed'],
  ['Inbound Email Parser Rules', 'HTML', 'Engineering', 'v3.5', 'Needs re-index'],
  ['Renewal Support Motion', 'PDF', 'Customer Ops', 'v2.6', 'Indexed'],
];

export const documents = docNames.map(([name, type, owner, version, status], index) => ({
  id: `doc-${index + 1}`,
  name,
  type,
  owner,
  version,
  status,
  chunks: 28 + ((index * 13) % 96),
  updatedAt: `2026-05-${String(3 + (index % 25)).padStart(2, '0')}`,
  metadata: {
    region: ['Global', 'NA', 'EMEA', 'APAC'][index % 4],
    tier: ['Enterprise', 'Business', 'Scale'][index % 3],
  },
}));

export const providerStatus = [
  {
    id: 'openrouter',
    label: 'OpenRouter',
    detail: 'Selected model from backend configuration',
    health: 'Online',
    latency: '820 ms',
    role: 'Remote answer generation',
  },
  {
    id: 'ollama',
    label: 'Ollama',
    detail: 'Local model from runtime configuration',
    health: 'Available',
    latency: '310 ms',
    role: 'Local fallback and evaluation checks',
  },
];

export const recentQuestions = [
  'How should a VIP SLA breach be escalated?',
  'Which rules govern ticket deduplication?',
  'What metadata is required before re-indexing partner docs?',
  'When should billing inquiries move to Finance Ops?',
  'How are AI draft replies reviewed before sending?',
];

export const evaluation = {
  metrics: [
    { label: 'Recall@3', value: '86.4%', trend: '+3.1%' },
    { label: 'Recall@5', value: '92.1%', trend: '+2.4%' },
    { label: 'MRR', value: '0.78', trend: '+0.05' },
    { label: 'Abstention accuracy', value: '94.0%', trend: '+1.8%' },
    { label: 'Citation rate', value: '89.5%', trend: '-0.7%' },
    { label: 'Expected keyword match', value: '81.2%', trend: '+4.6%' },
  ],
  failedQuestions: [
    {
      question: 'What is the exception path for merged cases with missing audit IDs?',
      issue: 'Retriever ranked general audit checklist above merge-specific chunks.',
      severity: 'Medium',
    },
    {
      question: 'Can APAC trial accounts receive live chat during regional holidays?',
      issue: 'Holiday coverage metadata is sparse across trial support docs.',
      severity: 'High',
    },
    {
      question: 'Which webhook failures should be retried manually?',
      issue: 'Stale API notes need re-indexing before the answer is reliable.',
      severity: 'Medium',
    },
  ],
  suggestions: [
    'Boost documents with matching account tier and region metadata before semantic reranking.',
    'Add negative evaluation cases for questions that should trigger abstention.',
    'Re-index stale engineering notes and compare Recall@5 against the current baseline.',
    'Split long policy PDFs into section-aware chunks to improve citation precision.',
  ],
};

export const logs = [
  ['2026-06-04 15:42', 'OpenRouter', 'hybrid + rerank', '1.42s', 'Complete', 4, 'None'],
  ['2026-06-04 15:36', 'Ollama', 'semantic only', '0.74s', 'Complete', 2, 'Low citation confidence'],
  ['2026-06-04 15:29', 'OpenRouter', 'hybrid + rerank', '1.67s', 'Complete', 5, 'None'],
  ['2026-06-04 15:18', 'OpenRouter', 'keyword fallback', '1.11s', 'Abstained', 0, 'No matching policy source'],
  ['2026-06-04 15:07', 'Ollama', 'semantic only', '0.68s', 'Complete', 3, 'Stale document surfaced'],
  ['2026-06-04 14:55', 'OpenRouter', 'hybrid + rerank', '1.38s', 'Complete', 4, 'None'],
  ['2026-06-04 14:43', 'OpenRouter', 'hybrid + rerank', '1.49s', 'Complete', 3, 'None'],
  ['2026-06-04 14:31', 'Ollama', 'keyword fallback', '0.59s', 'Complete', 1, 'Keyword-only result'],
].map(([time, provider, method, responseTime, status, citations, warning], index) => ({
  id: `log-${index + 1}`,
  time,
  provider,
  method,
  responseTime,
  status,
  citations,
  warning,
}));

export const mockDashboard = {
  documents,
  providerStatus,
  recentQuestions,
  evaluation,
  logs,
};

export function mockAskResponse(question) {
  const normalized = question?.trim() || 'How should an unresolved SupportFlow inquiry be handled?';

  return {
    question: normalized,
    answer:
      'SupportFlow should route the inquiry by customer tier, queue ownership, and SLA risk. If the request is tied to a VIP account or a potential SLA breach, the agent should escalate through the priority owner, attach the source conversation, and verify that the next response includes a policy-backed citation before closing the case.',
    citations: [
      {
        title: 'Priority Escalation Policy',
        snippet: 'VIP inquiries with active SLA risk move to the priority owner with source conversation context.',
        confidence: '0.91',
      },
      {
        title: 'Customer Queue Routing Playbook',
        snippet: 'Queue assignment uses tier, region, inquiry category, and active ownership metadata.',
        confidence: '0.88',
      },
      {
        title: 'AI Draft Reply Review Guide',
        snippet: 'Policy-backed answers must retain citations before agent approval.',
        confidence: '0.82',
      },
    ],
    scores: [
      { label: 'Answer confidence', value: 'High' },
      { label: 'Retrieval score', value: '0.87' },
      { label: 'Citation coverage', value: '3 sources' },
      { label: 'Abstention', value: 'Not needed' },
    ],
  };
}
