import React, { useState, useEffect } from 'react';
import { 
  Card, 
  Row, 
  Col, 
  Statistic, 
  Table, 
  Tag, 
  Button, 
  Switch, 
  Space,
  Typography,
  Alert,
  Spin
} from 'antd';
import { 
  DollarOutlined, 
  RiseOutlined, 
  FallOutlined,
  PlayCircleOutlined,
  StopOutlined,
  ReloadOutlined
} from '@ant-design/icons';

const { Title, Text } = Typography;

interface MarketRegime {
  regime: string;
  btc_price: number;
  change_24h: number;
  timestamp: string;
}

interface UniverseItem {
  symbol: string;
  direction: string;
  change_pct: number;
  quote_volume: number;
  last_price: number;
}

interface LiveStatus {
  is_active: boolean;
  strategy_id: string | null;
  risk_per_trade: number;
  total_pnl: number;
  daily_pnl: number;
  last_updated: string;
}

interface Position {
  symbol: string;
  direction: string;
  entry_price: number;
  size: number;
  pnl: number;
  last_trade: string;
}

const Dashboard: React.FC = () => {
  const [marketRegime, setMarketRegime] = useState<MarketRegime | null>(null);
  const [universe, setUniverse] = useState<UniverseItem[]>([]);
  const [liveStatus, setLiveStatus] = useState<LiveStatus | null>(null);
  const [positions, setPositions] = useState<Position[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboardData();
    const interval = setInterval(fetchDashboardData, 30000); // 30초마다 업데이트
    return () => clearInterval(interval);
  }, []);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      // 실제 API 호출로 대체
      // const [regimeRes, universeRes, statusRes, positionsRes] = await Promise.all([
      //   fetch('/api/regime'),
      //   fetch('/api/universe'),
      //   fetch('/api/live/status'),
      //   fetch('/api/live/positions')
      // ]);

      // 임시 데이터
      setMarketRegime({
        regime: 'UPTREND',
        btc_price: 45000,
        change_24h: 2.5,
        timestamp: new Date().toISOString()
      });

      setUniverse([
        {
          symbol: 'BTC/USDT',
          direction: 'long',
          change_pct: 3.2,
          quote_volume: 1500000000,
          last_price: 45000
        },
        {
          symbol: 'ETH/USDT',
          direction: 'long',
          change_pct: 2.8,
          quote_volume: 800000000,
          last_price: 3200
        }
      ]);

      setLiveStatus({
        is_active: false,
        strategy_id: null,
        risk_per_trade: 0.05,
        total_pnl: 0,
        daily_pnl: 0,
        last_updated: new Date().toISOString()
      });

      setPositions([]);
    } catch (error) {
      console.error('대시보드 데이터 로딩 실패:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleStartTrading = async () => {
    try {
      // 실제 API 호출로 대체
      // await fetch('/api/live/start', {
      //   method: 'POST',
      //   headers: { 'Content-Type': 'application/json' },
      //   body: JSON.stringify({ strategy_id: 'momentum_v1', risk_per_trade: 0.05 })
      // });
      console.log('매매 시작');
      fetchDashboardData();
    } catch (error) {
      console.error('매매 시작 실패:', error);
    }
  };

  const handleStopTrading = async () => {
    try {
      // 실제 API 호출로 대체
      // await fetch('/api/live/stop', { method: 'POST' });
      console.log('매매 중단');
      fetchDashboardData();
    } catch (error) {
      console.error('매매 중단 실패:', error);
    }
  };

  const getRegimeColor = (regime: string) => {
    switch (regime) {
      case 'UPTREND': return 'green';
      case 'DOWNTREND': return 'red';
      case 'SIDEWAYS': return 'orange';
      default: return 'default';
    }
  };

  const getDirectionColor = (direction: string) => {
    return direction === 'long' ? 'green' : 'red';
  };

  const universeColumns = [
    {
      title: '심볼',
      dataIndex: 'symbol',
      key: 'symbol',
    },
    {
      title: '방향',
      dataIndex: 'direction',
      key: 'direction',
      render: (direction: string) => (
        <Tag color={getDirectionColor(direction)}>
          {direction === 'long' ? '롱' : '숏'}
        </Tag>
      ),
    },
    {
      title: '변화율',
      dataIndex: 'change_pct',
      key: 'change_pct',
      render: (change: number) => (
        <Text className={change >= 0 ? 'profit-positive' : 'profit-negative'}>
          {change >= 0 ? '+' : ''}{change.toFixed(2)}%
        </Text>
      ),
    },
    {
      title: '거래대금',
      dataIndex: 'quote_volume',
      key: 'quote_volume',
      render: (volume: number) => `$${(volume / 1000000).toFixed(1)}M`,
    },
    {
      title: '현재가',
      dataIndex: 'last_price',
      key: 'last_price',
      render: (price: number) => `$${price.toLocaleString()}`,
    },
  ];

  const positionsColumns = [
    {
      title: '심볼',
      dataIndex: 'symbol',
      key: 'symbol',
    },
    {
      title: '방향',
      dataIndex: 'direction',
      key: 'direction',
      render: (direction: string) => (
        <Tag color={getDirectionColor(direction)}>
          {direction === 'long' ? '롱' : '숏'}
        </Tag>
      ),
    },
    {
      title: '진입가',
      dataIndex: 'entry_price',
      key: 'entry_price',
      render: (price: number) => `$${price.toLocaleString()}`,
    },
    {
      title: '수량',
      dataIndex: 'size',
      key: 'size',
    },
    {
      title: '손익',
      dataIndex: 'pnl',
      key: 'pnl',
      render: (pnl: number) => (
        <Text className={pnl >= 0 ? 'profit-positive' : 'profit-negative'}>
          ${pnl.toFixed(2)}
        </Text>
      ),
    },
  ];

  if (loading) {
    return (
      <div className="loading-container">
        <Spin size="large" />
      </div>
    );
  }

  return (
    <div className="fade-in">
      <Title level={2}>대시보드</Title>
      
      {/* 시장 국면 알림 */}
      {marketRegime && (
        <Alert
          message={`현재 시장 국면: ${marketRegime.regime}`}
          description={`비트코인: $${marketRegime.btc_price.toLocaleString()} (${marketRegime.change_24h >= 0 ? '+' : ''}${marketRegime.change_24h}%)`}
          type={marketRegime.regime === 'UPTREND' ? 'success' : marketRegime.regime === 'DOWNTREND' ? 'error' : 'warning'}
          showIcon
          style={{ marginBottom: 24 }}
        />
      )}

      {/* 통계 카드 */}
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col span={6}>
          <Card>
            <Statistic
              title="총 자산"
              value={100000}
              prefix={<DollarOutlined />}
              suffix="USD"
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="총 손익"
              value={liveStatus?.total_pnl || 0}
              prefix={<DollarOutlined />}
              suffix="USD"
              valueStyle={{ color: (liveStatus?.total_pnl || 0) >= 0 ? '#3f8600' : '#cf1322' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="일일 손익"
              value={liveStatus?.daily_pnl || 0}
              prefix={<DollarOutlined />}
              suffix="USD"
              valueStyle={{ color: (liveStatus?.daily_pnl || 0) >= 0 ? '#3f8600' : '#cf1322' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="활성 포지션"
              value={positions.length}
              prefix={<RiseOutlined />}
            />
          </Card>
        </Col>
      </Row>

      {/* 실시간 매매 상태 */}
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col span={12}>
          <Card title="실시간 매매 상태">
            <Space direction="vertical" style={{ width: '100%' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <Text>매매 상태</Text>
                <Switch 
                  checked={liveStatus?.is_active || false}
                  checkedChildren="활성"
                  unCheckedChildren="비활성"
                  disabled
                />
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <Text>현재 전략</Text>
                <Text strong>{liveStatus?.strategy_id || '없음'}</Text>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <Text>위험 비율</Text>
                <Text>{(liveStatus?.risk_per_trade || 0) * 100}%</Text>
              </div>
              <Space>
                <Button 
                  type="primary" 
                  icon={<PlayCircleOutlined />}
                  onClick={handleStartTrading}
                  disabled={liveStatus?.is_active}
                >
                  매매 시작
                </Button>
                <Button 
                  danger 
                  icon={<StopOutlined />}
                  onClick={handleStopTrading}
                  disabled={!liveStatus?.is_active}
                >
                  매매 중단
                </Button>
                <Button 
                  icon={<ReloadOutlined />}
                  onClick={fetchDashboardData}
                >
                  새로고침
                </Button>
              </Space>
            </Space>
          </Card>
        </Col>
        <Col span={12}>
          <Card title="시장 국면">
            <Space direction="vertical" style={{ width: '100%' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <Text>현재 국면</Text>
                <Tag color={getRegimeColor(marketRegime?.regime || '')}>
                  {marketRegime?.regime || 'UNKNOWN'}
                </Tag>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <Text>비트코인 가격</Text>
                <Text strong>${marketRegime?.btc_price.toLocaleString()}</Text>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <Text>24시간 변화</Text>
                <Text className={marketRegime?.change_24h && marketRegime.change_24h >= 0 ? 'profit-positive' : 'profit-negative'}>
                  {marketRegime?.change_24h && marketRegime.change_24h >= 0 ? '+' : ''}{marketRegime?.change_24h}%
                </Text>
              </div>
            </Space>
          </Card>
        </Col>
      </Row>

      {/* 유니버스 및 포지션 */}
      <Row gutter={16}>
        <Col span={12}>
          <Card title="현재 유니버스" extra={<Text type="secondary">{universe.length}개</Text>}>
            <Table
              dataSource={universe}
              columns={universeColumns}
              pagination={false}
              size="small"
              rowKey="symbol"
            />
          </Card>
        </Col>
        <Col span={12}>
          <Card title="현재 포지션" extra={<Text type="secondary">{positions.length}개</Text>}>
            {positions.length > 0 ? (
              <Table
                dataSource={positions}
                columns={positionsColumns}
                pagination={false}
                size="small"
                rowKey="symbol"
              />
            ) : (
              <div style={{ textAlign: 'center', padding: '20px', color: '#999' }}>
                보유 중인 포지션이 없습니다.
              </div>
            )}
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default Dashboard; 