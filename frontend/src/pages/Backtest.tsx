import { useCallback, useRef, useState } from 'react'
import { backtestApi, type BacktestResult, type BacktestStrategy } from '@/api/backtest'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { showToast } from '@/utils/toast'

function formatCurrency(value: number): string {
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    maximumFractionDigits: 0,
  }).format(value)
}

function MetricCard({ label, value, color }: { label: string; value: string; color?: string }) {
  return (
    <div className="flex flex-col">
      <span className="text-xs text-muted-foreground">{label}</span>
      <span className={`text-lg font-semibold ${color || ''}`}>{value}</span>
    </div>
  )
}

export default function Backtest() {
  const [strategies, setStrategies] = useState<BacktestStrategy[]>([])
  const [selectedStrategy, setSelectedStrategy] = useState('nifty_orb')
  const [symbol, setSymbol] = useState('NIFTY')
  const [exchange, setExchange] = useState('NSE_INDEX')
  const [interval, setInterval_] = useState('1m')
  const [startDate, setStartDate] = useState('')
  const [endDate, setEndDate] = useState('')
  const [capital, setCapital] = useState('100000')
  const [lots, setLots] = useState('1')
  const [lotSize, setLotSize] = useState('50')
  const [stopLoss, setStopLoss] = useState('50')
  const [trailingStop, setTrailingStop] = useState('20')
  const [iv, setIv] = useState('0.18')
  const [maxTrades, setMaxTrades] = useState('2')
  const [orbBuffer, setOrbBuffer] = useState('3')

  const [result, setResult] = useState<BacktestResult | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const requestIdRef = useRef(0)

  // Load strategies on mount
  const loadStrategies = useCallback(async () => {
    try {
      const resp = await backtestApi.getStrategies()
      if (resp.status === 'success') setStrategies(resp.strategies)
    } catch {
      // ignore
    }
  }, [])

  // Load strategies on first interaction
  const [loaded, setLoaded] = useState(false)
  const onFocus = useCallback(() => {
    if (!loaded) {
      loadStrategies()
      setLoaded(true)
    }
  }, [loaded, loadStrategies])

  const runBacktest = useCallback(async () => {
    const requestId = ++requestIdRef.current
    setIsLoading(true)
    try {
      const resp = await backtestApi.runBacktest({
        strategy: selectedStrategy,
        strategy_params: { orb_buffer: parseFloat(orbBuffer) },
        symbol,
        exchange,
        interval,
        start_date: startDate || undefined,
        end_date: endDate || undefined,
        config: {
          initial_capital: parseFloat(capital),
          lots: parseInt(lots),
          lot_size: parseInt(lotSize),
          stop_loss_points: parseFloat(stopLoss),
          trailing_stop_points: parseFloat(trailingStop),
          iv: parseFloat(iv),
          max_trades_per_day: parseInt(maxTrades),
          strike_rounding: symbol === 'BANKNIFTY' ? 100 : 50,
        },
      })
      if (requestIdRef.current !== requestId) return
      if (resp.status === 'success' && resp.result) {
        setResult(resp.result)
        showToast.success(`Backtest complete: ${resp.result.metrics.summary.total_trades} trades`)
      } else {
        showToast.error(resp.message || 'Backtest failed')
      }
    } catch {
      if (requestIdRef.current !== requestId) return
      showToast.error('Failed to run backtest')
    } finally {
      if (requestIdRef.current === requestId) setIsLoading(false)
    }
  }, [selectedStrategy, symbol, exchange, interval, startDate, endDate, capital, lots, lotSize, stopLoss, trailingStop, iv, maxTrades, orbBuffer])

  const m = result?.metrics

  return (
    <div className="py-6 space-y-4" onFocus={onFocus}>
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold">Options Backtester</h1>
          <p className="text-sm text-muted-foreground">
            Backtest intraday options buying strategies with synthetic Black-76 pricing
          </p>
        </div>
      </div>

      <Tabs defaultValue="config">
        <TabsList>
          <TabsTrigger value="config">Configuration</TabsTrigger>
          <TabsTrigger value="results" disabled={!result}>
            Results {m ? `(${m.summary.total_trades} trades)` : ''}
          </TabsTrigger>
          <TabsTrigger value="trades" disabled={!result?.trades.length}>
            Trade Log
          </TabsTrigger>
        </TabsList>

        <TabsContent value="config" className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Card>
              <CardHeader>
                <CardTitle className="text-base">Data & Strategy</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <Label>Symbol</Label>
                    <Select value={symbol} onValueChange={(v) => { setSymbol(v); setLotSize(v === 'BANKNIFTY' ? '15' : '50') }}>
                      <SelectTrigger><SelectValue /></SelectTrigger>
                      <SelectContent>
                        <SelectItem value="NIFTY">NIFTY</SelectItem>
                        <SelectItem value="BANKNIFTY">BANKNIFTY</SelectItem>
                        <SelectItem value="FINNIFTY">FINNIFTY</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div>
                    <Label>Exchange</Label>
                    <Select value={exchange} onValueChange={setExchange}>
                      <SelectTrigger><SelectValue /></SelectTrigger>
                      <SelectContent>
                        <SelectItem value="NSE_INDEX">NSE_INDEX</SelectItem>
                        <SelectItem value="BSE_INDEX">BSE_INDEX</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <Label>Interval</Label>
                    <Select value={interval} onValueChange={setInterval_}>
                      <SelectTrigger><SelectValue /></SelectTrigger>
                      <SelectContent>
                        <SelectItem value="1m">1 Minute</SelectItem>
                        <SelectItem value="5m">5 Minutes</SelectItem>
                        <SelectItem value="15m">15 Minutes</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div>
                    <Label>Strategy</Label>
                    <Select value={selectedStrategy} onValueChange={setSelectedStrategy}>
                      <SelectTrigger><SelectValue /></SelectTrigger>
                      <SelectContent>
                        <SelectItem value="nifty_orb">Nifty ORB</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <Label>Start Date</Label>
                    <Input type="date" value={startDate} onChange={(e) => setStartDate(e.target.value)} />
                  </div>
                  <div>
                    <Label>End Date</Label>
                    <Input type="date" value={endDate} onChange={(e) => setEndDate(e.target.value)} />
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="text-base">Risk & Sizing</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <Label>Capital</Label>
                    <Input type="number" value={capital} onChange={(e) => setCapital(e.target.value)} />
                  </div>
                  <div>
                    <Label>Lots</Label>
                    <Input type="number" value={lots} onChange={(e) => setLots(e.target.value)} />
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <Label>Lot Size</Label>
                    <Input type="number" value={lotSize} onChange={(e) => setLotSize(e.target.value)} />
                  </div>
                  <div>
                    <Label>Max Trades/Day</Label>
                    <Input type="number" value={maxTrades} onChange={(e) => setMaxTrades(e.target.value)} />
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <Label>Stop Loss (pts)</Label>
                    <Input type="number" value={stopLoss} onChange={(e) => setStopLoss(e.target.value)} />
                  </div>
                  <div>
                    <Label>Trailing Stop (pts)</Label>
                    <Input type="number" value={trailingStop} onChange={(e) => setTrailingStop(e.target.value)} />
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <Label>IV (%)</Label>
                    <Input type="number" step="0.01" value={iv} onChange={(e) => setIv(e.target.value)} />
                  </div>
                  <div>
                    <Label>ORB Buffer</Label>
                    <Input type="number" value={orbBuffer} onChange={(e) => setOrbBuffer(e.target.value)} />
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          <div className="flex justify-center">
            <Button size="lg" onClick={runBacktest} disabled={isLoading}>
              {isLoading ? 'Running...' : 'Run Backtest'}
            </Button>
          </div>
        </TabsContent>

        <TabsContent value="results" className="space-y-4">
          {m && (
            <>
              <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
                <MetricCard label="Net P&L" value={formatCurrency(m.summary.net_pnl)} color={m.summary.net_pnl >= 0 ? 'text-green-600' : 'text-red-600'} />
                <MetricCard label="Win Rate" value={`${m.summary.win_rate}%`} />
                <MetricCard label="Profit Factor" value={String(m.pnl.profit_factor)} />
                <MetricCard label="Max Drawdown" value={`${formatCurrency(m.risk.max_drawdown)} (${m.risk.max_drawdown_pct}%)`} color="text-red-600" />
                <MetricCard label="Sharpe" value={String(m.risk.sharpe_ratio)} />
                <MetricCard label="Sortino" value={String(m.risk.sortino_ratio)} />
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <Card>
                  <CardHeader><CardTitle className="text-base">Trade Summary</CardTitle></CardHeader>
                  <CardContent className="space-y-2 text-sm">
                    <div className="flex justify-between"><span>Total Trades</span><span>{m.summary.total_trades}</span></div>
                    <div className="flex justify-between"><span>Winners</span><span className="text-green-600">{m.summary.winning_trades}</span></div>
                    <div className="flex justify-between"><span>Losers</span><span className="text-red-600">{m.summary.losing_trades}</span></div>
                    <div className="flex justify-between"><span>Avg Win</span><span>{formatCurrency(m.pnl.avg_win)}</span></div>
                    <div className="flex justify-between"><span>Avg Loss</span><span>{formatCurrency(m.pnl.avg_loss)}</span></div>
                    <div className="flex justify-between"><span>Expectancy</span><span>{formatCurrency(m.pnl.expectancy)}</span></div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader><CardTitle className="text-base">By Side</CardTitle></CardHeader>
                  <CardContent className="space-y-2 text-sm">
                    <div className="flex justify-between"><span>CE Trades</span><span>{m.sides.ce_trades}</span></div>
                    <div className="flex justify-between"><span>CE Win Rate</span><span>{m.sides.ce_win_rate}%</span></div>
                    <div className="flex justify-between"><span>PE Trades</span><span>{m.sides.pe_trades}</span></div>
                    <div className="flex justify-between"><span>PE Win Rate</span><span>{m.sides.pe_win_rate}%</span></div>
                    <div className="flex justify-between"><span>Consec Wins</span><span>{m.risk.max_consec_wins}</span></div>
                    <div className="flex justify-between"><span>Consec Losses</span><span>{m.risk.max_consec_losses}</span></div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader><CardTitle className="text-base">Exit Reasons</CardTitle></CardHeader>
                  <CardContent className="space-y-2 text-sm">
                    {Object.entries(m.exit_reasons).map(([reason, data]) => (
                      <div key={reason} className="flex justify-between">
                        <span>{reason}</span>
                        <span>{data.count} ({data.pct}%)</span>
                      </div>
                    ))}
                  </CardContent>
                </Card>
              </div>

              <Card>
                <CardHeader><CardTitle className="text-base">Capital</CardTitle></CardHeader>
                <CardContent className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                  <MetricCard label="Initial" value={formatCurrency(m.summary.initial_capital)} />
                  <MetricCard label="Final" value={formatCurrency(m.summary.final_capital)} color={m.summary.total_return_pct >= 0 ? 'text-green-600' : 'text-red-600'} />
                  <MetricCard label="Return" value={`${m.summary.total_return_pct}%`} color={m.summary.total_return_pct >= 0 ? 'text-green-600' : 'text-red-600'} />
                  <MetricCard label="Total Costs" value={formatCurrency(m.summary.total_costs)} />
                </CardContent>
              </Card>
            </>
          )}
        </TabsContent>

        <TabsContent value="trades">
          {result?.trades && result.trades.length > 0 && (
            <Card>
              <CardContent className="p-0 overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b bg-muted/50">
                      <th className="p-2 text-left">#</th>
                      <th className="p-2 text-left">Entry</th>
                      <th className="p-2 text-left">Exit</th>
                      <th className="p-2 text-left">Side</th>
                      <th className="p-2 text-right">Strike</th>
                      <th className="p-2 text-right">Entry Prem</th>
                      <th className="p-2 text-right">Exit Prem</th>
                      <th className="p-2 text-right">Gross P&L</th>
                      <th className="p-2 text-right">Costs</th>
                      <th className="p-2 text-right">Net P&L</th>
                      <th className="p-2 text-left">Reason</th>
                    </tr>
                  </thead>
                  <tbody>
                    {result.trades.map((t, i) => (
                      <tr key={i} className="border-b hover:bg-muted/30">
                        <td className="p-2">{i + 1}</td>
                        <td className="p-2">{t.entry_date} {t.entry_time}</td>
                        <td className="p-2">{t.exit_date} {t.exit_time}</td>
                        <td className="p-2">
                          <Badge variant={t.side === 'CE' ? 'default' : 'secondary'}>{t.side}</Badge>
                        </td>
                        <td className="p-2 text-right">{t.strike}</td>
                        <td className="p-2 text-right">{t.entry_premium.toFixed(2)}</td>
                        <td className="p-2 text-right">{t.exit_premium.toFixed(2)}</td>
                        <td className={`p-2 text-right ${t.gross_pnl >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                          {formatCurrency(t.gross_pnl)}
                        </td>
                        <td className="p-2 text-right text-muted-foreground">{formatCurrency(t.costs.total)}</td>
                        <td className={`p-2 text-right font-medium ${t.net_pnl >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                          {formatCurrency(t.net_pnl)}
                        </td>
                        <td className="p-2">{t.exit_reason}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </CardContent>
            </Card>
          )}
        </TabsContent>
      </Tabs>
    </div>
  )
}
