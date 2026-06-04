const docNames = [
  ['顧客キュールーティング手順', 'PDF', '運用', 'v3.2', 'Indexed'],
  ['エンタープライズSLA一覧', 'XLSX', 'カスタマーサクセス', 'v2.8', 'Indexed'],
  ['優先エスカレーション規程', 'DOCX', '運用', 'v4.1', 'Indexed'],
  ['チケット重複排除ルール', 'MD', 'プロダクト', 'v1.9', 'Indexed'],
  ['受信箱割り当てAPIメモ', 'HTML', 'エンジニアリング', 'v2.4', 'Needs re-index'],
  ['Northstar導入ガイド', 'PDF', '導入支援', 'v5.0', 'Indexed'],
  ['請求問い合わせ一次対応', 'DOCX', '請求運用', 'v2.1', 'Indexed'],
  ['インシデント連絡テンプレート', 'MD', 'サポート', 'v3.6', 'Indexed'],
  ['会話タグ分類表', 'CSV', 'データ運用', 'v1.7', 'Indexing'],
  ['地域別稼働時間ルール', 'XLSX', '運用', 'v2.2', 'Indexed'],
  ['SupportFlow管理者権限', 'PDF', 'セキュリティ', 'v3.4', 'Indexed'],
  ['GDPRデータ削除ワークフロー', 'DOCX', 'コンプライアンス', 'v2.9', 'Indexed'],
  ['顧客感情シグナル', 'CSV', '分析', 'v1.5', 'Indexed'],
  ['オムニチャネル受信箱設定', 'HTML', '導入支援', 'v3.0', 'Indexed'],
  ['Webhookリトライ挙動', 'MD', 'エンジニアリング', 'v2.7', 'Needs re-index'],
  ['ナレッジベース自己解決計画', 'PDF', 'カスタマーサクセス', 'v1.8', 'Indexed'],
  ['エージェント生産性ベンチマーク', 'XLSX', '分析', 'v4.0', 'Indexed'],
  ['トライアルアカウント支援範囲', 'DOCX', '営業運用', 'v2.3', 'Indexed'],
  ['VIPアカウント対応ルール', 'PDF', 'サポート', 'v3.8', 'Indexed'],
  ['添付ファイル安全確認', 'MD', 'セキュリティ', 'v1.6', 'Indexed'],
  ['ケース統合監査チェックリスト', 'PDF', 'コンプライアンス', 'v2.5', 'Indexed'],
  ['ライブチャット引き継ぎパターン', 'HTML', 'プロダクト', 'v3.1', 'Indexed'],
  ['CSATフォローアップ自動化', 'DOCX', 'カスタマーサクセス', 'v1.4', 'Indexed'],
  ['キュー健全性ダッシュボード仕様', 'MD', '分析', 'v2.6', 'Indexed'],
  ['自動返信ガバナンス', 'PDF', 'コンプライアンス', 'v2.0', 'Indexed'],
  ['パートナー支援ワークフロー', 'DOCX', 'パートナー運用', 'v3.7', 'Needs re-index'],
  ['エージェントスキルグループ対応表', 'CSV', '運用', 'v4.2', 'Indexed'],
  ['移行インポートエラー一覧', 'XLSX', '導入支援', 'v1.9', 'Indexed'],
  ['モバイルプッシュ通知ルール', 'MD', 'プロダクト', 'v2.8', 'Indexed'],
  ['SupportFlow公開API制限', 'HTML', 'エンジニアリング', 'v3.3', 'Indexed'],
  ['返金例外対応プレイブック', 'PDF', '請求運用', 'v2.7', 'Indexed'],
  ['マクロライブラリ保守', 'DOCX', 'サポート', 'v3.9', 'Indexed'],
  ['エスカレーション責任分担RACI', 'XLSX', '運用', 'v2.4', 'Indexed'],
  ['解約リスク問い合わせシグナル', 'CSV', '分析', 'v1.8', 'Indexing'],
  ['SSOログイントラブル対応', 'PDF', 'セキュリティ', 'v4.5', 'Indexed'],
  ['顧客ポータルリリースノート', 'MD', 'プロダクト', 'v5.1', 'Indexed'],
  ['SLA違反振り返りフォーム', 'DOCX', 'カスタマーサクセス', 'v2.2', 'Indexed'],
  ['AI下書き返信レビューガイド', 'PDF', 'サポート', 'v1.3', 'Indexed'],
  ['受信メール解析ルール', 'HTML', 'エンジニアリング', 'v3.5', 'Needs re-index'],
  ['更新契約支援モーション', 'PDF', '顧客運用', 'v2.6', 'Indexed'],
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
    region: ['全社', '北米', '欧州', 'アジア太平洋'][index % 4],
    tier: ['Enterprise', 'Business', 'Scale'][index % 3],
  },
}));

export const providerStatus = [
  {
    id: 'openrouter',
    label: 'OpenRouter',
    detail: 'バックエンド設定から選択したモデル',
    health: 'Online',
    latency: '820 ms',
    role: 'リモート回答生成',
  },
  {
    id: 'ollama',
    label: 'Ollama',
    detail: '実行環境で指定したローカルモデル',
    health: 'Available',
    latency: '310 ms',
    role: 'ローカル代替・評価確認',
  },
];

export const recentQuestions = [
  'VIP SLA違反はどのようにエスカレーションすべきですか？',
  'チケット重複排除にはどのルールが適用されますか？',
  'パートナー文書の再インデックス前に必要なメタデータは何ですか？',
  '請求問い合わせはいつ請求運用チームへ回すべきですか？',
  'AI下書き返信は送信前にどうレビューすべきですか？',
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
      question: '監査IDが欠落した統合ケースの例外対応は？',
      issue: '検索器がケース統合専用チャンクより一般的な監査チェックリストを上位に出しました。',
      severity: 'Medium',
    },
    {
      question: 'APACのトライアルアカウントは地域休日にライブチャットを利用できますか？',
      issue: '休日カバレッジのメタデータがトライアル支援文書に不足しています。',
      severity: 'High',
    },
    {
      question: 'どのWebhook失敗を手動リトライすべきですか？',
      issue: '古いAPIメモを再インデックスしないと回答信頼性が不足します。',
      severity: 'Medium',
    },
  ],
  suggestions: [
    'アカウント階層と地域メタデータが一致する文書を、再ランク前に優先する。',
    '回答保留すべき質問をネガティブ評価ケースとして追加する。',
    '古い技術メモを再インデックスし、Recall@5を現行ベースラインと比較する。',
    '長い規程PDFを章単位で分割し、引用精度を改善する。',
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
  const normalized = question?.trim() || '未解決のSupportFlow問い合わせはどう扱うべきですか？';

  return {
    question: normalized,
    answer:
      'SupportFlowでは、顧客階層、キュー責任者、SLAリスクに基づいて問い合わせを振り分けます。VIPアカウントやSLA違反リスクに関係する場合は、優先担当へエスカレーションし、会話ソースを添付し、ケース終了前に根拠文書付きの返信になっているか確認します。',
    citations: [
      {
        title: '優先エスカレーション規程',
        snippet: 'SLAリスクがあるVIP問い合わせは、会話コンテキストを添えて優先担当へ移管します。',
        confidence: '0.91',
      },
      {
        title: '顧客キュールーティング手順',
        snippet: 'キュー割り当てでは、顧客階層、地域、問い合わせカテゴリ、現在の担当情報を使います。',
        confidence: '0.88',
      },
      {
        title: 'AI下書き返信レビューガイド',
        snippet: '文書根拠にもとづく回答は、エージェント承認前に引用を維持している必要があります。',
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
