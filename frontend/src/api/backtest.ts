import { webClient } from './client'

export interface BacktestStrategy {
  id: string
  name: string
  description: string
  params: Record<string, {
    type: string
    default: number
    min: number
    max: number
    label: string
  }>
}

export interface BacktestTrade {
  entry_date: string
  entry_time: string
  exit_date: string
  exit_time: string
  side: string
  strike: number
  entry_spot: number
  exit_spot: number
  entry_premium: number
  exit_premium: number
  quantity: number
  gross_pnl: number
  costs: Record<string, number>
  net_pnl: number
  exit_reason: string
  holding_minutes: number
}

export interface EquityPoint {
  datetime: string
  equity: number
  capital: number
  mtm: number
  spot: number
  date: string
}

export interface BacktestMetrics {
  summary: {
    total_trades: number
    winning_trades: number
    losing_trades: number
    breakeven_trades: number
    win_rate: number
    net_pnl: number
    gross_pnl: number
    total_costs: number
    initial_capital: number
    final_capital: number
    total_return_pct: number
  }
  pnl: {
    total_profit: number
    total_loss: number
    avg_win: number
    avg_loss: number
    avg_trade: number
    profit_factor: number | string
    expectancy: number
    reward_risk: number | string
  }
  risk: {
    max_drawdown: number
    max_drawdown_pct: number
    sharpe_ratio: number
    sortino_ratio: number
    max_consec_wins: number
    max_consec_losses: number
  }
  sides: {
    ce_trades: number
    ce_wins: number
    ce_win_rate: number
    pe_trades: number
    pe_wins: number
    pe_win_rate: number
  }
  exit_reasons: Record<string, { count: number; total_pnl: number; pct: number }>
  timing: {
    avg_holding_minutes: number
    trading_days: number
    trades_per_day: number
  }
}

export interface BacktestResult {
  trades: BacktestTrade[]
  equity_curve: EquityPoint[]
  metrics: BacktestMetrics
}

export interface BacktestConfig {
  initial_capital?: number
  lots?: number
  lot_size?: number
  stop_loss_points?: number
  target_points?: number
  trailing_stop_points?: number
  max_trades_per_day?: number
  max_daily_loss_pct?: number
  iv?: number
  risk_free_rate?: number
  last_entry_time?: string
  eod_exit_time?: string
  strike_rounding?: number
}

export interface OptionQuote {
  strike: number
  flag: string
  spot: number
  premium: number
  delta: number
  iv: number
  time_to_expiry_days: number
}

export const backtestApi = {
  getStrategies: async () => {
    const response = await webClient.get<{ status: string; strategies: BacktestStrategy[] }>(
      '/backtest/api/strategies',
    )
    return response.data
  },

  checkData: async (symbol: string, exchange: string) => {
    const response = await webClient.post<{ status: string; data: Record<string, unknown> }>(
      '/backtest/api/data',
      { symbol, exchange },
    )
    return response.data
  },

  runBacktest: async (params: {
    strategy: string
    strategy_params?: Record<string, unknown>
    symbol: string
    exchange: string
    interval?: string
    start_date?: string
    end_date?: string
    config?: BacktestConfig
  }) => {
    const response = await webClient.post<{ status: string; result?: BacktestResult; message?: string }>(
      '/backtest/api/run',
      params,
    )
    return response.data
  },

  getQuote: async (params: {
    spot: number
    flag?: string
    iv?: number
    risk_free_rate?: number
    strike_rounding?: number
    minutes_elapsed?: number
  }) => {
    const response = await webClient.post<{ status: string; quote?: OptionQuote }>(
      '/backtest/api/pricer/quote',
      params,
    )
    return response.data
  },
}
