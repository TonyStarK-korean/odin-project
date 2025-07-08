import React, { useState, useEffect } from 'react';
import { 
  Card, 
  Form, 
  Select, 
  DatePicker, 
  InputNumber, 
  Button, 
  Table, 
  Tag, 
  Space,
  Typography,
  Spin,
  message,
  Modal,
  Progress,
  Row,
  Col,
  Statistic
} from 'antd';
import { 
  PlayCircleOutlined,
  EyeOutlined,
  DeleteOutlined,
  ReloadOutlined
} from '@ant-design/icons';
import dayjs from 'dayjs';

const { Title, Text } = Typography;
const { RangePicker } = DatePicker;

interface BacktestJob {
  job_id: string;
  created_at: string;
  strategy_id: string;
  start_date: string;
  end_date: string;
  initial_capital: number;
  timeframe: string;
  status: string;
  results_summary?: {
    total_return: number;
    total_trades: number;
    win_rate: number;
    max_drawdown: number;
  };
}

interface Strategy {
  strategy_id: string;
  name: string;
  description: string;
}

const Backtesting: React.FC = () => {
  const [form] = Form.useForm();
  const [jobs, setJobs] = useState<BacktestJob[]>([]);
  const [strategies, setStrategies] = useState<Strategy[]>([]);
  const [loading, setLoading] = useState(false);
  const [jobsLoading, setJobsLoading] = useState(false);
  const [selectedJob, setSelectedJob] = useState<BacktestJob | null>(null);
  const [resultModalVisible, setResultModalVisible] = useState(false);

  useEffect(() => {
    fetchStrategies();
    fetchJobs();
  }, []);

  const fetchStrategies = async () => {
    try {
      // 실제 API 호출로 대체
      // const response = await fetch('/api/backtest/strategies');
      // const data = await response.json();
      
      // 임시 데이터
      setStrategies([
        {
          strategy_id: 'momentum_v1',
          name: '모멘텀 전략 v1',
          description: 'RSI와 이동평균을 활용한 모멘텀 전략'
        },
        {
          strategy_id: 'mean_reversion_v1',
          name: '평균회귀 전략 v1',
          description: '볼린저 밴드를 활용한 평균회귀 전략'
        },
        {
          strategy_id: 'bollinger_breakout_v1',
          name: '볼린저 밴드 돌파 매수전략 v1',
          description: '1시간봉 기준 볼린저 밴드 돌파 매수전략 - 시가가 20BB 아래에서 시작하고 고점이 20BB+80BB 상단선 동시 돌파하면서 양봉 마감'
        }
      ]);
    } catch (error) {
      console.error('전략 목록 로딩 실패:', error);
    }
  };

  const fetchJobs = async () => {
    try {
      setJobsLoading(true);
      // 실제 API 호출로 대체
      // const response = await fetch('/api/backtest/history');
      // const data = await response.json();
      
      // 임시 데이터
      setJobs([
        {
          job_id: '1',
          created_at: '2024-01-15T10:30:00Z',
          strategy_id: 'momentum_v1',
          start_date: '2024-01-01',
          end_date: '2024-01-15',
          initial_capital: 10000,
          timeframe: '1h',
          status: 'COMPLETED',
          results_summary: {
            total_return: 15.5,
            total_trades: 45,
            win_rate: 62.2,
            max_drawdown: 8.3
          }
        },
        {
          job_id: '2',
          created_at: '2024-01-14T15:20:00Z',
          strategy_id: 'mean_reversion_v1',
          start_date: '2024-01-01',
          end_date: '2024-01-14',
          initial_capital: 10000,
          timeframe: '1h',
          status: 'RUNNING'
        }
      ]);
    } catch (error) {
      console.error('백테스트 작업 목록 로딩 실패:', error);
    } finally {
      setJobsLoading(false);
    }
  };

  const handleSubmit = async (values: any) => {
    try {
      setLoading(true);
      
      const [startDate, endDate] = values.dateRange;
      const requestData = {
        strategy_id: values.strategy_id,
        start_date: startDate.format('YYYY-MM-DD'),
        end_date: endDate.format('YYYY-MM-DD'),
        initial_capital: values.initial_capital,
        timeframe: values.timeframe
      };

      // 실제 API 호출로 대체
      // const response = await fetch('/api/backtest/backtest', {
      //   method: 'POST',
      //   headers: { 'Content-Type': 'application/json' },
      //   body: JSON.stringify(requestData)
      // });
      
      console.log('백테스트 요청:', requestData);
      message.success('백테스트가 시작되었습니다.');
      form.resetFields();
      fetchJobs();
    } catch (error) {
      console.error('백테스트 시작 실패:', error);
      message.error('백테스트 시작에 실패했습니다.');
    } finally {
      setLoading(false);
    }
  };

  const handleViewResult = async (job: BacktestJob) => {
    try {
      // 실제 API 호출로 대체
      // const response = await fetch(`/api/backtest/result/${job.job_id}`);
      // const data = await response.json();
      
      setSelectedJob(job);
      setResultModalVisible(true);
    } catch (error) {
      console.error('결과 조회 실패:', error);
      message.error('결과 조회에 실패했습니다.');
    }
  };

  const handleDeleteJob = async (jobId: string) => {
    try {
      // 실제 API 호출로 대체
      // await fetch(`/api/backtest/job/${jobId}`, { method: 'DELETE' });
      
      console.log('작업 삭제:', jobId);
      message.success('작업이 삭제되었습니다.');
      fetchJobs();
    } catch (error) {
      console.error('작업 삭제 실패:', error);
      message.error('작업 삭제에 실패했습니다.');
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'COMPLETED': return 'green';
      case 'RUNNING': return 'blue';
      case 'PENDING': return 'orange';
      case 'FAILED': return 'red';
      default: return 'default';
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'COMPLETED': return '완료';
      case 'RUNNING': return '실행중';
      case 'PENDING': return '대기중';
      case 'FAILED': return '실패';
      default: return status;
    }
  };

  const columns = [
    {
      title: '작업 ID',
      dataIndex: 'job_id',
      key: 'job_id',
      width: 100,
    },
    {
      title: '생성일',
      dataIndex: 'created_at',
      key: 'created_at',
      render: (date: string) => dayjs(date).format('YYYY-MM-DD HH:mm'),
      width: 150,
    },
    {
      title: '전략',
      dataIndex: 'strategy_id',
      key: 'strategy_id',
      render: (strategyId: string) => {
        const strategy = strategies.find(s => s.strategy_id === strategyId);
        return strategy?.name || strategyId;
      },
    },
    {
      title: '기간',
      key: 'period',
      render: (record: BacktestJob) => (
        <Text>{record.start_date} ~ {record.end_date}</Text>
      ),
      width: 200,
    },
    {
      title: '초기 자본',
      dataIndex: 'initial_capital',
      key: 'initial_capital',
      render: (capital: number) => `$${capital.toLocaleString()}`,
      width: 120,
    },
    {
      title: '상태',
      dataIndex: 'status',
      key: 'status',
      render: (status: string) => (
        <Tag color={getStatusColor(status)}>
          {getStatusText(status)}
        </Tag>
      ),
      width: 100,
    },
    {
      title: '결과',
      key: 'results',
      render: (record: BacktestJob) => {
        if (record.status === 'COMPLETED' && record.results_summary) {
          return (
            <Space direction="vertical" size="small">
              <Text>수익률: {record.results_summary.total_return}%</Text>
              <Text>거래수: {record.results_summary.total_trades}</Text>
              <Text>승률: {record.results_summary.win_rate}%</Text>
            </Space>
          );
        }
        return <Text type="secondary">-</Text>;
      },
    },
    {
      title: '작업',
      key: 'actions',
      render: (record: BacktestJob) => (
        <Space>
          {record.status === 'COMPLETED' && (
            <Button
              type="link"
              icon={<EyeOutlined />}
              onClick={() => handleViewResult(record)}
            >
              결과 보기
            </Button>
          )}
          <Button
            type="link"
            danger
            icon={<DeleteOutlined />}
            onClick={() => handleDeleteJob(record.job_id)}
          >
            삭제
          </Button>
        </Space>
      ),
      width: 150,
    },
  ];

  return (
    <div className="fade-in">
      <Title level={2}>백테스팅</Title>
      
      <Row gutter={24}>
        <Col span={8}>
          <Card title="백테스트 설정">
            <Form
              form={form}
              layout="vertical"
              onFinish={handleSubmit}
              initialValues={{
                timeframe: '1h',
                initial_capital: 10000
              }}
            >
              <Form.Item
                name="strategy_id"
                label="전략 선택"
                rules={[{ required: true, message: '전략을 선택해주세요' }]}
              >
                <Select placeholder="전략을 선택하세요">
                  {strategies.map(strategy => (
                    <Select.Option key={strategy.strategy_id} value={strategy.strategy_id}>
                      {strategy.name}
                    </Select.Option>
                  ))}
                </Select>
              </Form.Item>

              <Form.Item
                name="dateRange"
                label="백테스트 기간"
                rules={[{ required: true, message: '기간을 선택해주세요' }]}
              >
                <RangePicker 
                  style={{ width: '100%' }}
                  format="YYYY-MM-DD"
                />
              </Form.Item>

              <Form.Item
                name="timeframe"
                label="시간프레임"
                rules={[{ required: true, message: '시간프레임을 선택해주세요' }]}
              >
                <Select>
                  <Select.Option value="1m">1분</Select.Option>
                  <Select.Option value="5m">5분</Select.Option>
                  <Select.Option value="15m">15분</Select.Option>
                  <Select.Option value="1h">1시간</Select.Option>
                  <Select.Option value="4h">4시간</Select.Option>
                  <Select.Option value="1d">1일</Select.Option>
                </Select>
              </Form.Item>

              <Form.Item
                name="initial_capital"
                label="초기 자본금"
                rules={[{ required: true, message: '초기 자본금을 입력해주세요' }]}
              >
                <InputNumber
                  style={{ width: '100%' }}
                  formatter={value => `$ ${value}`.replace(/\B(?=(\d{3})+(?!\d))/g, ',')}
                  parser={value => value!.replace(/\$\s?|(,*)/g, '')}
                  min={1000}
                  step={1000}
                />
              </Form.Item>

              <Form.Item>
                <Button
                  type="primary"
                  htmlType="submit"
                  loading={loading}
                  icon={<PlayCircleOutlined />}
                  block
                >
                  백테스트 실행
                </Button>
              </Form.Item>
            </Form>
          </Card>
        </Col>

        <Col span={16}>
          <Card 
            title="백테스트 내역" 
            extra={
              <Button 
                icon={<ReloadOutlined />} 
                onClick={fetchJobs}
                loading={jobsLoading}
              >
                새로고침
              </Button>
            }
          >
            <Table
              dataSource={jobs}
              columns={columns}
              rowKey="job_id"
              loading={jobsLoading}
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

      {/* 결과 모달 */}
      <Modal
        title="백테스트 결과"
        open={resultModalVisible}
        onCancel={() => setResultModalVisible(false)}
        footer={null}
        width={800}
      >
        {selectedJob && selectedJob.results_summary && (
          <div>
            <Row gutter={16} style={{ marginBottom: 24 }}>
              <Col span={6}>
                <Card>
                  <Statistic
                    title="총 수익률"
                    value={selectedJob.results_summary.total_return}
                    suffix="%"
                    valueStyle={{ color: selectedJob.results_summary.total_return >= 0 ? '#3f8600' : '#cf1322' }}
                  />
                </Card>
              </Col>
              <Col span={6}>
                <Card>
                  <Statistic
                    title="총 거래수"
                    value={selectedJob.results_summary.total_trades}
                  />
                </Card>
              </Col>
              <Col span={6}>
                <Card>
                  <Statistic
                    title="승률"
                    value={selectedJob.results_summary.win_rate}
                    suffix="%"
                  />
                </Card>
              </Col>
              <Col span={6}>
                <Card>
                  <Statistic
                    title="최대 낙폭"
                    value={selectedJob.results_summary.max_drawdown}
                    suffix="%"
                    valueStyle={{ color: '#cf1322' }}
                  />
                </Card>
              </Col>
            </Row>
            
            <Card title="자산 곡선">
              <div style={{ height: 300, display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#999' }}>
                차트가 여기에 표시됩니다
              </div>
            </Card>
          </div>
        )}
      </Modal>
    </div>
  );
};

export default Backtesting; 