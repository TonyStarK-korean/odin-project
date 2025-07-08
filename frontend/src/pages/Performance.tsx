import React, { useState, useEffect } from 'react';
import { 
  Card, 
  Row, 
  Col, 
  Table, 
  Tag, 
  Space,
  Typography,
  Spin,
  Checkbox,
  Button,
  Statistic,
  Select
} from 'antd';
import { 
  LineChart, 
  Line, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  Legend, 
  ResponsiveContainer,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell
} from 'recharts';
import { 
  ReloadOutlined,
  DownloadOutlined
} from '@ant-design/icons';

const { Title, Text } = Typography;
const { Option } = Select;

interface BacktestResult {
  job_id: string;
  strategy_id: string;
  strategy_name: string;
  start_date: string;
  end_date: string;
  total_return: number;
  total_trades: number;
  winning_trades: number;
  losing_trades: number;
  win_rate: number;
  max_drawdown: number;
  sharpe_ratio: number;
  profit_factor: number;
  avg_win: number;
  avg_loss: number;
  equity_curve: Array<{
    date: string;
    equity: number;
  }>;
}

const Performance: React.FC = () => {
  const [results, setResults] = useState<BacktestResult[]>([]);
  const [selectedResults, setSelectedResults] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const [timeframe, setTimeframe] = useState('1d');

  useEffect(() => {
    fetchResults();
  }, []);

  const fetchResults = async () => {
    try {
      setLoading(true);
      // 실제 API 호출로 대체
      // const response = await fetch('/api/backtest/history');
      // const data = await response.json();
      
      // 임시 데이터
      setResults([
        {
          job_id: '1',
          strategy_id: 'momentum_v1',
          strategy_name: '모멘텀 전략 v1',
          start_date: '2024-01-01',
          end_date: '2024-01-15',
          total_return: 15.5,
          total_trades: 45,
          winning_trades: 28,
          losing_trades: 17,
          win_rate: 62.2,
          max_drawdown: 8.3,
          sharpe_ratio: 1.8,
          profit_factor: 2.1,
          avg_win: 150,
          avg_loss: -80,
          equity_curve: [
            { date: '2024-01-01', equity: 10000 },
            { date: '2024-01-05', equity: 10500 },
            { date: '2024-01-10', equity: 11200 },
            { date: '2024-01-15', equity: 11550 }
          ]
        },
        {
          job_id: '2',
          strategy_id: 'mean_reversion_v1',
          strategy_name: '평균회귀 전략 v1',
          start_date: '2024-01-01',
          end_date: '2024-01-15',
          total_return: 8.2,
          total_trades: 32,
          winning_trades: 20,
          losing_trades: 12,
          win_rate: 62.5,
          max_drawdown: 5.1,
          sharpe_ratio: 1.2,
          profit_factor: 1.8,
          avg_win: 120,
          avg_loss: -70,
          equity_curve: [
            { date: '2024-01-01', equity: 10000 },
            { date: '2024-01-05', equity: 10200 },
            { date: '2024-01-10', equity: 10800 },
            { date: '2024-01-15', equity: 10820 }
          ]
        }
      ]);
    } catch (error) {
      console.error('성과 데이터 로딩 실패:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleResultSelection = (jobId: string, checked: boolean) => {
    if (checked) {
      setSelectedResults([...selectedResults, jobId]);
    } else {
      setSelectedResults(selectedResults.filter(id => id !== jobId));
    }
  };

  const getReturnColor = (returnValue: number) => {
    return returnValue >= 0 ? '#52c41a' : '#ff4d4f';
  };

  const getWinRateColor = (winRate: number) => {
    if (winRate >= 70) return '#52c41a';
    if (winRate >= 50) return '#faad14';
    return '#ff4d4f';
  };

  const columns = [
    {
      title: '선택',
      key: 'select',
      render: (record: BacktestResult) => (
        <Checkbox
          checked={selectedResults.includes(record.job_id)}
          onChange={(e) => handleResultSelection(record.job_id, e.target.checked)}
        />
      ),
      width: 60,
    },
    {
      title: '전략',
      dataIndex: 'strategy_name',
      key: 'strategy_name',
    },
    {
      title: '기간',
      key: 'period',
      render: (record: BacktestResult) => (
        <Text>{record.start_date} ~ {record.end_date}</Text>
      ),
    },
    {
      title: '총 수익률',
      dataIndex: 'total_return',
      key: 'total_return',
      render: (returnValue: number) => (
        <Text style={{ color: getReturnColor(returnValue), fontWeight: 'bold' }}>
          {returnValue >= 0 ? '+' : ''}{returnValue.toFixed(2)}%
        </Text>
      ),
      sorter: (a: BacktestResult, b: BacktestResult) => a.total_return - b.total_return,
    },
    {
      title: '총 거래수',
      dataIndex: 'total_trades',
      key: 'total_trades',
      sorter: (a: BacktestResult, b: BacktestResult) => a.total_trades - b.total_trades,
    },
    {
      title: '승률',
      dataIndex: 'win_rate',
      key: 'win_rate',
      render: (winRate: number) => (
        <Tag color={getWinRateColor(winRate)}>
          {winRate.toFixed(1)}%
        </Tag>
      ),
      sorter: (a: BacktestResult, b: BacktestResult) => a.win_rate - b.win_rate,
    },
    {
      title: '최대 낙폭',
      dataIndex: 'max_drawdown',
      key: 'max_drawdown',
      render: (drawdown: number) => (
        <Text style={{ color: '#ff4d4f' }}>
          -{drawdown.toFixed(2)}%
        </Text>
      ),
      sorter: (a: BacktestResult, b: BacktestResult) => a.max_drawdown - b.max_drawdown,
    },
    {
      title: '샤프 비율',
      dataIndex: 'sharpe_ratio',
      key: 'sharpe_ratio',
      render: (sharpe: number) => (
        <Text style={{ color: sharpe >= 1 ? '#52c41a' : '#faad14' }}>
          {sharpe.toFixed(2)}
        </Text>
      ),
      sorter: (a: BacktestResult, b: BacktestResult) => a.sharpe_ratio - b.sharpe_ratio,
    },
    {
      title: '수익 팩터',
      dataIndex: 'profit_factor',
      key: 'profit_factor',
      render: (factor: number) => (
        <Text style={{ color: factor >= 2 ? '#52c41a' : factor >= 1 ? '#faad14' : '#ff4d4f' }}>
          {factor.toFixed(2)}
        </Text>
      ),
      sorter: (a: BacktestResult, b: BacktestResult) => a.profit_factor - b.profit_factor,
    },
  ];

  const selectedResultsData = results.filter(result => selectedResults.includes(result.job_id));

  const comparisonData = selectedResultsData.map(result => ({
    name: result.strategy_name,
    total_return: result.total_return,
    win_rate: result.win_rate,
    max_drawdown: result.max_drawdown,
    sharpe_ratio: result.sharpe_ratio,
    profit_factor: result.profit_factor,
  }));

  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8'];

  if (loading) {
    return (
      <div className="loading-container">
        <Spin size="large" />
      </div>
    );
  }

  return (
    <div className="fade-in">
      <Title level={2}>성과 분석</Title>
      
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col span={24}>
          <Card 
            title="백테스트 결과 목록" 
            extra={
              <Space>
                <Select
                  value={timeframe}
                  onChange={setTimeframe}
                  style={{ width: 120 }}
                >
                  <Option value="1d">일별</Option>
                  <Option value="1w">주별</Option>
                  <Option value="1m">월별</Option>
                </Select>
                <Button 
                  icon={<ReloadOutlined />} 
                  onClick={fetchResults}
                >
                  새로고침
                </Button>
                <Button 
                  icon={<DownloadOutlined />}
                  disabled={selectedResults.length === 0}
                >
                  내보내기
                </Button>
              </Space>
            }
          >
            <Table
              dataSource={results}
              columns={columns}
              rowKey="job_id"
              pagination={{
                pageSize: 10,
                showSizeChanger: true,
                showQuickJumper: true,
                showTotal: (total, range) => `${range[0]}-${range[1]} / 총 ${total}개`
              }}
            />
          </Card>
        </Col>
      </Row>

      {selectedResults.length > 0 && (
        <>
          {/* 종합 성과 비교 */}
          <Row gutter={16} style={{ marginBottom: 24 }}>
            <Col span={24}>
              <Card title="종합 성과 비교">
                <Row gutter={16}>
                  {selectedResultsData.map((result, index) => (
                    <Col span={6} key={result.job_id}>
                      <Card size="small">
                        <Statistic
                          title={result.strategy_name}
                          value={result.total_return}
                          suffix="%"
                          valueStyle={{ color: getReturnColor(result.total_return) }}
                        />
                        <div style={{ marginTop: 8 }}>
                          <Text type="secondary">
                            승률: {result.win_rate.toFixed(1)}% | 
                            MDD: -{result.max_drawdown.toFixed(1)}%
                          </Text>
                        </div>
                      </Card>
                    </Col>
                  ))}
                </Row>
              </Card>
            </Col>
          </Row>

          {/* 차트 비교 */}
          <Row gutter={16}>
            <Col span={12}>
              <Card title="수익률 비교">
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={comparisonData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="name" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Bar dataKey="total_return" fill="#8884d8" name="총 수익률 (%)" />
                  </BarChart>
                </ResponsiveContainer>
              </Card>
            </Col>
            <Col span={12}>
              <Card title="승률 비교">
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={comparisonData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="name" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Bar dataKey="win_rate" fill="#82ca9d" name="승률 (%)" />
                  </BarChart>
                </ResponsiveContainer>
              </Card>
            </Col>
          </Row>

          <Row gutter={16} style={{ marginTop: 16 }}>
            <Col span={12}>
              <Card title="샤프 비율 비교">
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={comparisonData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="name" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Bar dataKey="sharpe_ratio" fill="#ffc658" name="샤프 비율" />
                  </BarChart>
                </ResponsiveContainer>
              </Card>
            </Col>
            <Col span={12}>
              <Card title="수익 팩터 비교">
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={comparisonData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="name" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Bar dataKey="profit_factor" fill="#ff7300" name="수익 팩터" />
                  </BarChart>
                </ResponsiveContainer>
              </Card>
            </Col>
          </Row>

          {/* 자산 곡선 비교 */}
          <Row gutter={16} style={{ marginTop: 16 }}>
            <Col span={24}>
              <Card title="자산 곡선 비교">
                <ResponsiveContainer width="100%" height={400}>
                  <LineChart>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="date" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    {selectedResultsData.map((result, index) => (
                      <Line
                        key={result.job_id}
                        type="monotone"
                        dataKey="equity"
                        data={result.equity_curve}
                        name={result.strategy_name}
                        stroke={COLORS[index % COLORS.length]}
                        strokeWidth={2}
                      />
                    ))}
                  </LineChart>
                </ResponsiveContainer>
              </Card>
            </Col>
          </Row>
        </>
      )}
    </div>
  );
};

export default Performance; 