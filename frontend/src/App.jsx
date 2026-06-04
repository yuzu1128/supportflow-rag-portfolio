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
  { id: 'ask', label: '質問', icon: Search },
  { id: 'documents', label: '文書', icon: FileText },
  { id: 'evaluation', label: '評価', icon: ClipboardList },
  { id: 'logs', label: 'ログ', icon: History },
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

const statusLabels = {
  Indexed: 'インデックス済み',
  Complete: '完了',
  Online: 'オンライン',
  Available: '利用可能',
  Indexing: 'インデックス中',
  Abstained: '回答保留',
  'Not configured': '未設定',
  'Needs re-index': '再インデックス必要',
};

const textLabels = {
  Environment: '環境',
  'Local Demo': 'ローカルデモ',
  Development: '開発環境',
  'Backend connected': 'バックエンド接続済み',
  'Mock data active': 'モックデータで表示中',
  'configured by runtime': '実行時設定で有効',
  'selected later': 'モデル未選定',
  'local model selected later': 'ローカルモデル未選定',
  runtime: '実行時',
  'Remote answer generation': 'リモート回答生成',
  'Local fallback': 'ローカル代替',
  'Test fallback': 'テスト用フォールバック',
  'Local fallback and evaluation checks': 'ローカル代替・評価確認',
  'Answer confidence': '回答信頼度',
  'Retrieval score': '検索スコア',
  'Citation coverage': '引用カバー率',
  Abstention: '回答保留',
  Pending: '未実行',
  Grounded: '根拠あり',
  Triggered: '発動',
  'Not needed': '不要',
  '3 sources': '3件の引用',
  'local run': 'ローカル実行',
  'logged locally': '記録済み',
  None: 'なし',
  'Low confidence': '信頼度不足',
  'No matching policy source': '該当する規程文書なし',
  'Low citation confidence': '引用信頼度が低い',
  'Stale document surfaced': '古い文書が上位表示',
  'Keyword-only result': 'キーワード検索のみ',
  'hybrid search': 'ハイブリッド検索',
  'hybrid + rerank': 'ハイブリッド + 再ランク',
  'semantic only': 'セマンティック検索のみ',
  'keyword fallback': 'キーワード検索',
  High: '高',
  Medium: '中',
  Low: '低',
};

const metricLabels = {
  Documents: '文書数',
  Indexed: 'インデックス済み',
  'Recall@3': 'Recall@3',
  'Recall@5': 'Recall@5',
  MRR: 'MRR',
  'Abstention accuracy': '回答保留精度',
  'Citation rate': '引用率',
  'Expected keyword match': '期待キーワード一致率',
};

const categoryLabels = {
  '01_user_manual': 'ユーザーマニュアル',
  '02_faq': 'FAQ',
  '03_incident_response': 'インシデント対応',
  '04_api_specs': 'API仕様',
  '05_release_notes': 'リリースノート',
  '06_test_specs': 'テスト仕様',
  '07_support_templates': 'サポートテンプレート',
  '08_operations_rules': '運用ルール',
  supportflow: 'SupportFlow',
  md: 'Markdown',
  txt: 'テキスト',
  json: 'JSON',
  csv: 'CSV',
  pdf: 'PDF',
  docx: 'DOCX',
  'local-demo': 'ローカルデモ',
};

const documentNameLabels = {
  'Queue Sla Rules': 'キューSLAルール',
  'Knowledge Review Rules': 'ナレッジレビュー規程',
  'Escalation Matrix': 'エスカレーションマトリクス',
  'Data Retention Policy': 'データ保持ポリシー',
  'Access Review Checklist.Pdf': 'アクセスレビュー・チェックリスト（PDFテキスト）',
  'Access Review Checklist': 'アクセスレビュー・チェックリスト',
  'Response Templates': '返信テンプレート',
  'Outage Notice Template': '障害通知テンプレート',
  'Escalation Summary Template.Docx': 'エスカレーション要約テンプレート（DOCXテキスト）',
  'Escalation Summary Template': 'エスカレーション要約テンプレート',
  'Customer Update Snippets': '顧客向け更新文スニペット',
  'Api Error Response Macros': 'APIエラー返信マクロ',
  'Search Relevance Test Cases': '検索関連性テストケース',
  'Routing Regression Test': 'ルーティング回帰テスト',
  'Permissions Qa Checklist': '権限QAチェックリスト',
  'Bulk Import Test Plan': '一括インポートテスト計画',
  'Api Contract Tests': 'API契約テスト',
  'Release Changelog': 'リリース変更履歴',
  'Migration Notes V2': '移行メモ v2',
  '2026-04-Release': '2026年4月リリース',
  '2026-03-Release': '2026年3月リリース',
  '2026-02-Release': '2026年2月リリース',
  'Webhooks Api': 'Webhook API',
  'Rate Limits': 'レート制限',
  'Errors Reference': 'エラーリファレンス',
  'Conversations Api': '会話API',
  'Api Quickstart.Pdf': 'APIクイックスタート（PDFテキスト）',
  'Api Quickstart': 'APIクイックスタート',
  'Webhook Delivery Incident Runbook': 'Webhook配信インシデント・ランブック',
  'Sev Policy': 'SEVポリシー',
  'Search Index Lag Runbook': '検索インデックス遅延ランブック',
  'Postmortem Template.Docx': 'ポストモーテムテンプレート（DOCXテキスト）',
  'Postmortem Template': 'ポストモーテムテンプレート',
  'Incident Contacts': 'インシデント連絡先',
  'Import Export Faq': 'インポート/エクスポートFAQ',
  'Faq Catalog': 'FAQカタログ',
  'Customer Admin Faq': '顧客管理者FAQ',
  'Channel Setup Faq': 'チャネル設定FAQ',
  'Agent Faq': 'エージェントFAQ',
  'Roles Permissions': 'ロールと権限',
  'Queue Configuration': 'キュー設定',
  'Macros And Templates': 'マクロとテンプレート',
  'Knowledge Base Authoring': 'ナレッジベース作成',
  'Agent Workspace Guide': 'エージェントワークスペースガイド',
};

const questionLabels = {
  'How should SupportFlow handle a VIP SLA breach?': 'VIP SLA違反リスクはどう扱うべきですか？',
  'How should a VIP SLA breach be escalated?': 'VIP SLA違反はどのようにエスカレーションすべきですか？',
  'Which API errors should be retried?': 'どのAPIエラーをリトライ対象にすべきですか？',
  'When should webhook delivery incidents be escalated?':
    'Webhook配信インシデントはいつエスカレーションすべきですか？',
  'How should AUTH_401 token expired errors be handled?':
    'AUTH_401のトークン期限切れエラーはどう対応すべきですか？',
  'Evaluation run required': '評価実行が必要です',
};

const issueLabels = {
  'Run /api/evaluation/run after indexing documents to populate failed cases.':
    '文書をインデックスした後に /api/evaluation/run を実行すると、失敗ケースが表示されます。',
};

const suggestionLabels = {
  'Tune keyword/vector weighting after reviewing Recall@5.':
    'Recall@5を確認したうえで、キーワード検索とベクトル検索の重みを調整する。',
  'Add missing SupportFlow runbooks when failed questions lack sources.':
    '失敗した質問に根拠文書が不足している場合は、SupportFlowのランブックを追加する。',
  'Adjust abstention threshold for low-confidence answers.':
    '信頼度が低い回答では回答保留しやすいよう、しきい値を調整する。',
  'Boost documents with matching account tier and region metadata before semantic reranking.':
    'アカウント階層と地域メタデータが一致する文書を、再ランク前に優先する。',
  'Add negative evaluation cases for questions that should trigger abstention.':
    '回答保留すべき質問をネガティブ評価ケースとして追加する。',
  'Re-index stale engineering notes and compare Recall@5 against the current baseline.':
    '古い技術メモを再インデックスし、Recall@5を現行ベースラインと比較する。',
  'Split long policy PDFs into section-aware chunks to improve citation precision.':
    '長い規程PDFを章単位で分割し、引用精度を改善する。',
};

function labelText(value) {
  return textLabels[value] ?? value;
}

function labelStatus(value) {
  return statusLabels[value] ?? labelText(value);
}

function labelMetric(value) {
  return metricLabels[value] ?? labelText(value);
}

function labelQuestion(value) {
  return questionLabels[value] ?? value;
}

function labelIssue(value) {
  return issueLabels[value] ?? value;
}

function labelSuggestion(value) {
  return suggestionLabels[value] ?? value;
}

function labelMeta(value) {
  return categoryLabels[value] ?? value;
}

function labelDocumentName(value) {
  return documentNameLabels[value] ?? value;
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

        <nav className="tab-list" aria-label="主要セクション">
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
          <span>環境</span>
          <strong>ローカルデモ</strong>
          <p>開発環境</p>
          <Badge tone={mode === 'backend' ? 'green' : 'amber'}>
            {mode === 'backend' ? 'バックエンド接続済み' : 'モックデータで表示中'}
          </Badge>
        </div>
      </aside>

      <main className="main-panel">
        <header className="topbar">
          <div>
            <p className="eyebrow">問い合わせ管理SaaS ポートフォリオ</p>
            <h2>RAG運用コンソール</h2>
          </div>
          <div className="topbar-meta">
            <Badge tone="blue">ローカルデモ</Badge>
            <Badge tone="slate">開発環境</Badge>
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
            <p className="eyebrow">SupportFlowに質問</p>
            <h3>文書根拠にもとづく回答生成</h3>
          </div>
          <Badge tone="green">引用必須</Badge>
        </div>

        <label className="question-box">
          <span>質問</span>
          <textarea
            value={question}
            onChange={(event) => setQuestion(event.target.value)}
            placeholder="ルーティング、エスカレーション、SLA、請求一次対応、問い合わせ運用について質問..."
          />
        </label>

        <button className="primary-action" onClick={onAsk} disabled={asking} type="button">
          {asking ? <RefreshCcw className="spin" size={17} /> : <Send size={17} />}
          <span>{asking ? '根拠文書を確認中' : 'ナレッジベースに質問'}</span>
        </button>

        <div className="answer-area">
          <div className="answer-header">
            <h4>回答</h4>
            <div className="score-row">
              {answer.scores.map((score) => (
                <Badge key={score.label} tone="blue">
                  {labelMetric(score.label)}: {labelText(score.value)}
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
            <h3>モデル接続状態</h3>
            <Server size={18} />
          </div>
          <div className="provider-list">
            {data.providerStatus.map((provider) => (
              <article className="provider-item" key={provider.id}>
                <div>
                  <strong>{provider.label}</strong>
                  <p>{labelText(provider.detail)}</p>
                </div>
                <Badge tone={statusTone(provider.health)}>{labelStatus(provider.health)}</Badge>
                <span>{labelText(provider.role)}</span>
                <em>{labelText(provider.latency)}</em>
              </article>
            ))}
          </div>
        </div>

        <div className="panel">
          <div className="section-heading compact">
            <h3>引用と参照元</h3>
            <Database size={18} />
          </div>
          <div className="citation-list">
            {answer.citations.map((citation) => (
              <article key={citation.title}>
                <div>
                  <strong>{labelDocumentName(citation.title)}</strong>
                  <Badge tone="green">信頼度 {citation.confidence}</Badge>
                </div>
                <p>{citation.snippet}</p>
              </article>
            ))}
          </div>
        </div>

        <div className="panel">
          <div className="section-heading compact">
            <h3>最近の質問</h3>
            <History size={18} />
          </div>
          <div className="recent-list">
            {data.recentQuestions.map((item) => (
              <button key={item} onClick={() => setQuestion(labelQuestion(item))} type="button">
                {labelQuestion(item)}
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
            <h3>SupportFlow文書を登録</h3>
            <p>規程、ランブック、APIメモ、表データ、運用手順をローカルでインデックスします。</p>
          </div>
          <button type="button">ファイル選択</button>
        </div>
        <MetricCard label="文書数" value={documents.length} trend="30-50件のデモ文書" />
        <MetricCard label="インデックス済み" value={`${indexed}/${documents.length}`} trend="検索対象" />
      </div>

      <div className="panel table-panel">
        <div className="section-heading">
          <div>
            <p className="eyebrow">ナレッジコーパス</p>
            <h3>SupportFlow文書一覧</h3>
          </div>
          <Badge tone="slate">30-50件のデモ文書</Badge>
        </div>
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>文書</th>
                <th>種類</th>
                <th>管理者</th>
                <th>メタデータ</th>
                <th>チャンク</th>
                <th>更新日</th>
                <th>状態</th>
                <th>操作</th>
              </tr>
            </thead>
            <tbody>
              {documents.map((document) => (
                <tr key={document.id}>
                  <td>
                    <strong>{labelDocumentName(document.name)}</strong>
                    <span>{labelMeta(document.version)}</span>
                  </td>
                  <td>
                    <Badge tone={typeTone[document.type] ?? 'neutral'}>{document.type}</Badge>
                  </td>
                  <td>{document.owner}</td>
                  <td>
                    {labelMeta(document.metadata.region)} / {labelMeta(document.metadata.tier)}
                  </td>
                  <td>{document.chunks}</td>
                  <td>{document.updatedAt}</td>
                  <td>
                    <Badge tone={statusTone(document.status)}>{labelStatus(document.status)}</Badge>
                  </td>
                  <td>
                    <button className="icon-action" type="button" title="文書を再インデックス">
                      <RefreshCcw size={15} />
                      <span>再実行</span>
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
            <p className="eyebrow">評価セット</p>
            <h3>改善対象の質問</h3>
          </div>
          <AlertTriangle size={19} />
        </div>
        <div className="issue-list">
          {evaluation.failedQuestions.map((item) => (
            <article key={item.question}>
              <Badge tone={item.severity === 'High' ? 'red' : 'amber'}>{labelText(item.severity)}</Badge>
              <div>
                <strong>{labelQuestion(item.question)}</strong>
                <p>{labelIssue(item.issue)}</p>
              </div>
            </article>
          ))}
        </div>
      </div>

      <div className="panel">
        <div className="section-heading">
          <div>
            <p className="eyebrow">次の改善</p>
            <h3>チューニング案</h3>
          </div>
          <CheckCircle2 size={19} />
        </div>
        <ul className="suggestion-list">
          {evaluation.suggestions.map((item) => (
            <li key={item}>{labelSuggestion(item)}</li>
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
            <p className="eyebrow">実行履歴</p>
            <h3>質問ログと警告</h3>
          </div>
          <Activity size={19} />
        </div>
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>時刻</th>
                <th>プロバイダー</th>
                <th>検索方式</th>
                <th>応答時間</th>
                <th>状態</th>
                <th>引用数</th>
                <th>警告</th>
              </tr>
            </thead>
            <tbody>
              {logs.map((log) => (
                <tr key={log.id}>
                  <td>{log.time}</td>
                  <td>{log.provider}</td>
                  <td>{labelText(log.method)}</td>
                  <td>{labelText(log.responseTime)}</td>
                  <td>
                    <Badge tone={statusTone(log.status)}>{labelStatus(log.status)}</Badge>
                  </td>
                  <td>{log.citations}</td>
                  <td className={log.warning === 'None' ? 'muted' : 'warning-text'}>{labelText(log.warning)}</td>
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
  const [question, setQuestion] = useState('VIP SLA違反リスクはどう扱うべきですか？');
  const [answer, setAnswer] = useState(null);
  const [asking, setAsking] = useState(false);

  useEffect(() => {
    loadDashboard().then((payload) => {
      setData(payload);
      setAnswer({
        ...payload,
        ...{
          answer:
            'SupportFlowの運用に関する質問を入力すると、根拠文書にもとづく回答と引用元を表示します。',
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
              'SupportFlowの運用に関する質問を入力すると、根拠文書にもとづく回答と引用元を表示します。',
            citations: [
              {
                title: '参照元はまだ選択されていません',
                snippet: '質問を送信すると、SupportFlowコーパスから引用元が表示されます。',
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
        <span>SupportFlow RAGを読み込み中</span>
      </div>
    );
  }

  return (
    <Shell activeTab={activeTab} onTabChange={setActiveTab} mode={data.mode}>
      {data.backendWarning && (
        <div className="banner">
          <AlertTriangle size={17} />
          <span>バックエンドに接続できないため、モックデータで表示しています。</span>
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
