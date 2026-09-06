"""
FnO transaction costs for Indian derivatives markets.

Covers NFO/BFO options buying: STT on premium, exchange fees, SEBI, stamp duty, GST.
"""

from dataclasses import dataclass

from utils.logging import get_logger

logger = get_logger(__name__)


@dataclass(frozen=True)
class FnOCosts:
    """Transaction cost model for FnO option buying."""

    #: STT on sell-side premium (0.0625% = 0.000625)
    stt_rate: float = 0.000625
    #: Exchange transaction charge (0.053% = 0.00053 per side)
    exchange_txn_rate: float = 0.00053
    #: SEBI turnover fee (Rs 10 per crore = 0.000001)
    sebi_rate: float = 10.0 / 1_00_00_000
    #: GST on brokerage + exchange fees + SEBI (18%)
    gst_rate: float = 0.18
    #: Stamp duty on buy side (0.003% = 0.00003)
    stamp_duty_rate: float = 0.00003
    #: Brokerage per order (flat, most discount brokers charge 0 for equity FnO)
    brokerage_per_order: float = 0.0
    #: Slippage as fraction of premium (e.g. 0.005 = 0.5%)
    slippage: float = 0.005

    def calculate(
        self,
        entry_premium: float,
        exit_premium: float,
        quantity: int,
        entry_spot_value: float | None = None,
    ) -> dict:
        """
        Calculate total transaction costs for a round-trip options trade.

        Args:
            entry_premium: Premium paid per unit at entry
            exit_premium: Premium received per unit at exit
            quantity: Number of units (lots * lot_size)
            entry_spot_value: Notional value for exchange fee calculation (premium * qty)

        Returns:
            Dictionary with cost breakdown and total
        """
        buy_value = entry_premium * quantity
        sell_value = exit_premium * quantity
        turnover = buy_value + sell_value

        # STT only on sell side (premium)
        stt = sell_value * self.stt_rate

        # Exchange transaction charges (both sides)
        exchange_txn = turnover * self.exchange_txn_rate

        # SEBI charges (both sides)
        sebi = turnover * self.sebi_rate

        # GST on (brokerage + exchange + SEBI)
        taxable = self.brokerage_per_order * 2 + exchange_txn + sebi
        gst = taxable * self.gst_rate

        # Stamp duty on buy side
        stamp_duty = buy_value * self.stamp_duty_rate

        # Brokerage (per order, 2 orders total)
        brokerage = self.brokerage_per_order * 2

        # Slippage
        slippage_cost = turnover * self.slippage

        total = stt + exchange_txn + sebi + gst + stamp_duty + brokerage + slippage_cost

        return {
            "stt": round(stt, 2),
            "exchange_txn": round(exchange_txn, 2),
            "sebi": round(sebi, 2),
            "gst": round(gst, 2),
            "stamp_duty": round(stamp_duty, 2),
            "brokerage": round(brokerage, 2),
            "slippage": round(slippage_cost, 2),
            "total": round(total, 2),
        }

    def net_pnl(
        self,
        entry_premium: float,
        exit_premium: float,
        quantity: int,
    ) -> dict:
        """
        Calculate net P&L after costs.

        Returns:
            Dictionary with gross_pnl, costs, and net_pnl
        """
        gross_pnl = (exit_premium - entry_premium) * quantity
        costs = self.calculate(entry_premium, exit_premium, quantity)
        net = gross_pnl - costs["total"]

        return {
            "gross_pnl": round(gross_pnl, 2),
            "costs": costs,
            "net_pnl": round(net, 2),
        }


# Presets
INDIA_FNO_DEFAULT = FnOCosts()

INDIA_FNO_ZERO_BROKERAGE = FnOCosts(
    brokerage_per_order=0.0,
    slippage=0.003,
)
