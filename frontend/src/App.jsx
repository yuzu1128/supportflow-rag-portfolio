import { useEffect, useMemo, useState } from 'react';
import {
  Activity,
  AlertTriangle,
  CheckCircle2,
  ClipboardList,
  Database,
  FileText,
  History,
  RefreshCcw,
  Search,
  Send,
  Server,
  UploadCloud,
} from 'lucide-react';
import { askQuestion, loadDashboard } from './api/client.js';
import { Badge } from './components/Badge.jsx';
import { MetricCard } from './components/MetricCard.jsx';

const tabs = [
  { id: 'ask', label: 'Ask', icon: Search },
  { id: 'documents', label: 'Documents', icon: FileText },
  { id: 'evaluation', label: 'Evaluation', icon: ClipboardList },
  { id: 'logs', label: 'Logs', icon: History },
];

const typeTone = {
  PDF: 'red',
  DOCX: 'blue',
  XLSX: 'green',
  CSV: 'green',
  MD: 'slate',
  HTML: 'amber',
};

function statusTone(status) {
  if (status === 'Indexed' || status === 'Complete' || status === 'Online' || status === 'Available') {
    return 'green';
  }
  if (status === 'Indexing') {
    return 'blue';
  }
  if (status === 'Abstained') {
    return 'amber';
  }
  return 'red';
}

function Shell({ activeTab, onTabChange, mode, children }) {
  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand-block">
          <div className="brand-mark">SF</div>
          <div>
            <h1>SupportFlow RAG</h1>
            <p>Northstar Systems</p>
          </div>
        </div>

        <nav className="tab-list" aria-label="Main sections">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            return (
              <button
                className={activeTab === tab.id ? 'active' : ''}
                key={tab.id}
                onClick={() => onTabChange(tab.id)}
                type="button"
              >
                <Icon size={18} />
                <span>{tab.label}</span>
              </button>
            );
          })}
        </nav>

        <div className="environment-card">
          <span>Environment</span>
          <strong>Local Demo</strong>
          <p>Development</p>
          <Badge tone={mode === 'backend' ? 'green' : 'amber'}>
            {mode === 'backend' ? 'Backend connected' : 'Mock data active'}
          </Badge>
        </div>
      </aside>

      <main className="main-panel">
        <header className="topbar">
          <div>
            <p className="eyebrow">Inquiry-management SaaS portfolio</p>
            <h2>RAG operations console</h2>
          </div>
          <div className="topbar-meta">
            <Badge tone="blue">Local Demo</Badge>
            <Badge tone="slate">Development</Badge>
          </div>
        </header>
        {children}
      </main>
    </div>
  );
}

function AskTab({ data, answer, question, setQuestion, onAsk, asking }) {
  return (
    <section className="tab-content ask-grid">
      <div className="panel ask-panel">
        <div className="section-heading">
          <div>
            <p className="eyebrow">Ask SupportFlow</p>
            <h3>Policy-backed answer generation</h3>
          </div>
          <Badge tone="green">Citations required</Badge>
        </div>

        <label className="question-box">
          <span>Question</span>
          <textarea
            value={question}
            onChange={(event) => setQuestion(event.target.value)}
            placeholder="Ask about routing, escalations, SLAs, billing triage, or inquiry workflows..."
          />
        </label>

        <button className="primary-action" onClick={onAsk} disabled={asking} type="button">
          {asking ? <RefreshCcw className="spin" size={17} /> : <Send size={17} />}
          <span>{asking ? 'Checking sources' : 'Ask knowledge base'}</span>
        </button>

        <div className="answer-area">
          <div className="answer-header">
            <h4>Answer</h4>
            <div className="score-row">
              {answer.scores.map((score) => (
                <Badge key={score.label} tone="blue">
                  {score.label}: {score.value}
                </Badge>
              ))}
            </div>
          </div>
          <p>{answer.answer}</p>
        </div>
      </div>

      <aside className="stack">
        <div className="panel">
          <div className="section-heading compact">
            <h3>Provider status</h3>
            <Server size={18} />
          </div>
          <div className="provider-list">
            {data.providerStatus.map((provider) => (
              <article className="provider-item" key={provider.id}>
                <div>
                  <strong>{provider.label}</strong>
                  <p>{provider.detail}</p>
                </div>
                <Badge tone={statusTone(provider.health)}>{provider.health}</Badge>
                <span>{provider.role}</span>
                <em>{provider.latency}</em>
              </article>
            ))}
          </div>
        </div>

        <div className="panel">
          <div className="section-heading compact">
            <h3>Citations and sources</h3>
            <Database size={18} />
          </div>
          <div className="citation-list">
            {answer.citations.map((citation) => (
              <article key={citation.title}>
                <div>
                  <strong>{citation.title}</strong>
                  <Badge tone="green">Confidence {citation.confidence}</Badge>
                </div>
                <p>{citation.snippet}</p>
              </article>
            ))}
          </div>
        </div>

        <div className="panel">
          <div className="section-heading compact">
            <h3>Recent questions</h3>
            <History size={18} />
          </div>
          <div className="recent-list">
            {data.recentQuestions.map((item) => (
              <button key={item} onClick={() => setQuestion(item)} type="button">
                {item}
              </button>
            ))}
          </div>
        </div>
      </aside>
    </section>
  );
}

function DocumentsTab({ documents }) {
  const indexed = documents.filter((document) => document.status === 'Indexed').length;

  return (
    <section className="tab-content">
      <div className="document-summary">
        <div className="upload-zone">
          <UploadCloud size={30} />
          <div>
            <h3>Upload SupportFlow documents</h3>
            <p>Drop policies, runbooks, API notes, spreadsheets, and operating procedures for local indexing.</p>
          </div>
          <button type="button">Select files</button>
        </div>
        <MetricCard label="Documents" value={documents.length} trend="+6 this week" />
        <MetricCard label="Indexed" value={`${indexed}/${documents.length}`} trend="+4 ready" />
      </div>

      <div className="panel table-panel">
        <div className="section-heading">
          <div>
            <p className="eyebrow">Knowledge corpus</p>
            <h3>SupportFlow document inventory</h3>
          </div>
          <Badge tone="slate">30-50 document demo set</Badge>
        </div>
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Document</th>
                <th>Type</th>
                <th>Owner</th>
                <th>Metadata</th>
                <th>Chunks</th>
                <th>Updated</th>
                <th>Status</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              {documents.map((document) => (
                <tr key={document.id}>
                  <td>
                    <strong>{document.name}</strong>
                    <span>{document.version}</span>
                  </td>
                  <td>
                    <Badge tone={typeTone[document.type] ?? 'neutral'}>{document.type}</Badge>
                  </td>
                  <td>{document.owner}</td>
                  <td>
                    {document.metadata.region} / {document.metadata.tier}
                  </td>
                  <td>{document.chunks}</td>
                  <td>{document.updatedAt}</td>
                  <td>
                    <Badge tone={statusTone(document.status)}>{document.status}</Badge>
                  </td>
                  <td>
                    <button className="icon-action" type="button" title="Re-index document">
                      <RefreshCcw size={15} />
                      <span>Re-index</span>
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </section>
  );
}

function EvaluationTab({ evaluation }) {
  return (
    <section className="tab-content evaluation-grid">
      <div className="metrics-grid">
        {evaluation.metrics.map((metric) => (
          <MetricCard key={metric.label} {...metric} />
        ))}
      </div>

      <div className="panel">
        <div className="section-heading">
          <div>
            <p className="eyebrow">Regression suite</p>
            <h3>Failed questions</h3>
          </div>
          <AlertTriangle size={19} />
        </div>
        <div className="issue-list">
          {evaluation.failedQuestions.map((item) => (
            <article key={item.question}>
              <Badge tone={item.severity === 'High' ? 'red' : 'amber'}>{item.severity}</Badge>
              <div>
                <strong>{item.question}</strong>
                <p>{item.issue}</p>
              </div>
            </article>
          ))}
        </div>
      </div>

      <div className="panel">
        <div className="section-heading">
          <div>
            <p className="eyebrow">Next improvements</p>
            <h3>Suggested tuning</h3>
          </div>
          <CheckCircle2 size={19} />
        </div>
        <ul className="suggestion-list">
          {evaluation.suggestions.map((item) => (
            <li key={item}>{item}</li>
          ))}
        </ul>
      </div>
    </section>
  );
}

function LogsTab({ logs }) {
  return (
    <section className="tab-content">
      <div className="panel table-panel">
        <div className="section-heading">
          <div>
            <p className="eyebrow">Runtime trace</p>
            <h3>Query history and warnings</h3>
          </div>
          <Activity size={19} />
        </div>
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Time</th>
                <th>Provider</th>
                <th>Retrieval method</th>
                <th>Response time</th>
                <th>Status</th>
                <th>Citations</th>
                <th>Warnings</th>
              </tr>
            </thead>
            <tbody>
              {logs.map((log) => (
                <tr key={log.id}>
                  <td>{log.time}</td>
                  <td>{log.provider}</td>
                  <td>{log.method}</td>
                  <td>{log.responseTime}</td>
                  <td>
                    <Badge tone={statusTone(log.status)}>{log.status}</Badge>
                  </td>
                  <td>{log.citations}</td>
                  <td className={log.warning === 'None' ? 'muted' : 'warning-text'}>{log.warning}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </section>
  );
}

export default function App() {
  const [activeTab, setActiveTab] = useState('ask');
  const [data, setData] = useState(null);
  const [question, setQuestion] = useState('How should SupportFlow handle a VIP SLA breach?');
  const [answer, setAnswer] = useState(null);
  const [asking, setAsking] = useState(false);

  useEffect(() => {
    loadDashboard().then((payload) => {
      setData(payload);
      setAnswer({
        ...payload,
        ...{
          answer:
            'Ask a SupportFlow operations question to generate a policy-backed response. The demo starts with mock retrieval results when no backend is configured.',
          citations: [],
          scores: [
            { label: 'Answer confidence', value: 'Pending' },
            { label: 'Retrieval score', value: 'Pending' },
            { label: 'Citation coverage', value: 'Pending' },
          ],
        },
      });
    });
  }, []);

  const visibleAnswer = useMemo(
    () =>
      answer?.citations?.length
        ? answer
        : {
            answer:
              'Ask a SupportFlow operations question to generate a policy-backed response. The demo starts with mock retrieval results when no backend is configured.',
            citations: [
              {
                title: 'No source selected yet',
                snippet: 'Submit a question to view citations from the SupportFlow corpus.',
                confidence: '-',
              },
            ],
            scores: answer?.scores ?? [],
          },
    [answer],
  );

  async function handleAsk() {
    setAsking(true);
    const response = await askQuestion(question);
    setAnswer(response);
    setAsking(false);
  }

  if (!data) {
    return (
      <div className="loading-screen">
        <RefreshCcw className="spin" size={24} />
        <span>Loading SupportFlow RAG</span>
      </div>
    );
  }

  return (
    <Shell activeTab={activeTab} onTabChange={setActiveTab} mode={data.mode}>
      {data.backendWarning && (
        <div className="banner">
          <AlertTriangle size={17} />
          <span>Backend unavailable or not configured. Running with graceful mock data.</span>
        </div>
      )}
      {activeTab === 'ask' && (
        <AskTab
          data={data}
          answer={visibleAnswer}
          question={question}
          setQuestion={setQuestion}
          onAsk={handleAsk}
          asking={asking}
        />
      )}
      {activeTab === 'documents' && <DocumentsTab documents={data.documents} />}
      {activeTab === 'evaluation' && <EvaluationTab evaluation={data.evaluation} />}
      {activeTab === 'logs' && <LogsTab logs={data.logs} />}
    </Shell>
  );
}
