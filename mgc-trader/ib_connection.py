"""
MGC Day Trader — IB Connection Manager
Fully synchronous using ib_insync's built-in sync API.
"""

import logging
from datetime import datetime
from ib_insync import IB, Future, MarketOrder, LimitOrder, StopOrder
import config

logger = logging.getLogger("mgc-trader.ib")


class IBConnection:
    """Manages IB API connection, contract, and data subscriptions."""

    def __init__(self):
        self.ib = IB()
        self.contract = None
        self.connected = False

    def connect(self):
        """Connect to TWS/IB Gateway (synchronous)."""
        try:
            self.ib.connect(
                host=config.IB_HOST,
                port=config.IB_PORT,
                clientId=config.IB_CLIENT_ID,
                timeout=20,
            )
            self.connected = True
            logger.info(f"Connected to IB at {config.IB_HOST}:{config.IB_PORT}")

            # Request delayed data if real-time isn't subscribed
            self.ib.reqMarketDataType(3)
            logger.info("Requesting delayed market data (fallback if no real-time sub)")

            # Resolve front-month MGC contract
            self.contract = self._resolve_contract()
            logger.info(f"Trading contract: {self.contract.localSymbol}")

            return True
        except Exception as e:
            logger.error(f"Failed to connect to IB: {e}")
            self.connected = False
            return False

    def _resolve_contract(self):
        """Resolve the front-month MGC futures contract."""
        contract = Future(
            symbol=config.SYMBOL,
            exchange=config.EXCHANGE,
            currency=config.CURRENCY,
        )
        details = self.ib.reqContractDetails(contract)
        if not details:
            raise RuntimeError(f"No contract details found for {config.SYMBOL}")

        details.sort(key=lambda d: d.contract.lastTradeDateOrContractMonth)
        today_str = datetime.now().strftime("%Y%m%d")
        front = None
        for d in details:
            expiry = d.contract.lastTradeDateOrContractMonth
            if expiry > today_str and (datetime.strptime(expiry, "%Y%m%d") - datetime.now()).days >= 7:
                front = d.contract
                break
        if front is None:
            front = details[-1].contract
        self.ib.qualifyContracts(front)
        return front

    def get_account_summary(self):
        """Get account balance and P&L info."""
        summary = {}
        acct = self.ib.accountSummary()
        for item in acct:
            if item.tag in ("NetLiquidation", "TotalCashValue", "UnrealizedPnL",
                            "RealizedPnL", "BuyingPower"):
                try:
                    summary[item.tag] = float(item.value)
                except (ValueError, TypeError):
                    pass
        return summary

    def get_positions(self):
        """Get current positions for our contract."""
        positions = []
        for pos in self.ib.positions():
            if pos.contract.symbol == config.SYMBOL:
                positions.append({
                    "symbol": pos.contract.localSymbol,
                    "size": pos.position,
                    "avg_cost": pos.avgCost,
                    "unrealized_pnl": getattr(pos, "unrealizedPnL", 0),
                })
        return positions

    def get_open_orders(self):
        """Get all open orders for our contract."""
        orders = []
        for trade in self.ib.openTrades():
            if trade.contract.symbol == config.SYMBOL:
                orders.append({
                    "order_id": trade.order.orderId,
                    "action": trade.order.action,
                    "type": trade.order.orderType,
                    "quantity": trade.order.totalQuantity,
                    "limit_price": getattr(trade.order, "lmtPrice", None),
                    "stop_price": getattr(trade.order, "auxPrice", None),
                    "status": trade.orderStatus.status,
                })
        return orders

    @staticmethod
    def _round_to_tick(price, tick_size=0.10):
        """Round price to nearest valid tick increment."""
        return round(round(price / tick_size) * tick_size, 2)

    def place_bracket_order(self, action, quantity, entry_price, stop_price, tp_price):
        """Place market entry, then OCA stop+TP for protection."""
        import time as _time
        from ib_insync import Order

        stop_price = self._round_to_tick(stop_price)
        tp_price = self._round_to_tick(tp_price)
        exit_action = "SELL" if action == "BUY" else "BUY"

        # Step 1: Market entry
        entry_order = Order(action=action, totalQuantity=quantity,
                            orderType='MKT', tif='GTC')
        entry_trade = self.ib.placeOrder(self.contract, entry_order)
        logger.info(f"Placed MKT {action} {quantity}")

        # Wait for fill
        self.ib.sleep(3)
        if entry_trade.orderStatus.status == 'Filled':
            fill_price = entry_trade.orderStatus.avgFillPrice
            logger.info(f"✅ Entry FILLED @ {fill_price}")
        else:
            logger.warning(f"⚠️ Entry status: {entry_trade.orderStatus.status}")
            # Wait a bit more
            self.ib.sleep(5)
            if entry_trade.orderStatus.status != 'Filled':
                logger.error(f"Entry NOT filled after 8s — status: {entry_trade.orderStatus.status}")
                return [entry_trade]

        # Step 2: OCA stop + TP (cancel each other when one fills)
        oca_group = f"MGC_{int(_time.time())}"

        stop_order = Order(action=exit_action, totalQuantity=quantity,
                           orderType='STP', auxPrice=stop_price, tif='GTC',
                           ocaGroup=oca_group, ocaType=1)
        stop_trade = self.ib.placeOrder(self.contract, stop_order)
        logger.info(f"Placed STP {exit_action} {quantity} @ stop {stop_price} (OCA: {oca_group})")

        tp_order = Order(action=exit_action, totalQuantity=quantity,
                         orderType='LMT', lmtPrice=tp_price, tif='GTC',
                         ocaGroup=oca_group, ocaType=1)
        tp_trade = self.ib.placeOrder(self.contract, tp_order)
        logger.info(f"Placed LMT {exit_action} {quantity} @ limit {tp_price} (OCA: {oca_group})")

        self.ib.sleep(2)

        # Verify protective orders are live — retry if IB preset cancelled them
        result_trades = [entry_trade]
        for label, trade, order_template in [
            ("STOP", stop_trade, lambda: Order(action=exit_action, totalQuantity=quantity,
                orderType='STP', auxPrice=stop_price, tif='GTC',
                ocaGroup=oca_group, ocaType=1)),
            ("TP", tp_trade, lambda: Order(action=exit_action, totalQuantity=quantity,
                orderType='LMT', lmtPrice=tp_price, tif='GTC',
                ocaGroup=oca_group, ocaType=1)),
        ]:
            s = trade.orderStatus.status
            if s in ('Submitted', 'Filled'):
                result_trades.append(trade)
            elif s in ('PreSubmitted', 'Cancelled'):
                if s == 'PreSubmitted':
                    # PreSubmitted can be transient — wait up to 10s for it to go Submitted
                    logger.warning(f"⚠️ {label} order stuck in PreSubmitted — waiting for activation...")
                    for _wait in range(5):
                        self.ib.sleep(2)
                        s = trade.orderStatus.status
                        if s == 'Submitted':
                            logger.info(f"✅ {label} order activated: Submitted")
                            break
                        elif s == 'Cancelled':
                            break
                    else:
                        logger.warning(f"⚠️ {label} still {s} after 10s")

                # If still not Submitted, cancel and retry without OCA
                if trade.orderStatus.status not in ('Submitted', 'Filled'):
                    logger.warning(f"⚠️ {label} order failed ({trade.orderStatus.status}) — "
                                   f"cancelling and retrying as standalone order")
                    try:
                        self.ib.cancelOrder(trade.order)
                        self.ib.sleep(1)
                    except Exception:
                        pass
                    # Retry WITHOUT OCA group — standalone protection is better than none
                    retry_order = Order(action=exit_action, totalQuantity=quantity,
                        orderType='STP' if label == 'STOP' else 'LMT',
                        tif='GTC')
                    if label == 'STOP':
                        retry_order.auxPrice = stop_price
                    else:
                        retry_order.lmtPrice = tp_price
                    retry_trade = self.ib.placeOrder(self.contract, retry_order)
                    self.ib.sleep(3)
                    rs = retry_trade.orderStatus.status
                    if rs in ('Submitted', 'PreSubmitted', 'Filled'):
                        logger.info(f"✅ {label} standalone retry successful: {rs}")
                        result_trades.append(retry_trade)
                    else:
                        logger.error(f"❌ {label} standalone retry ALSO failed: {rs} — POSITION UNPROTECTED")
                        result_trades.append(retry_trade)
                else:
                    result_trades.append(trade)
            else:
                logger.warning(f"⚠️ {label} order status: {s} (order {trade.order.orderId})")
                result_trades.append(trade)

        # Final verification: ensure STOP specifically is active
        stop_ok = False
        for t in result_trades[1:]:  # skip entry trade
            if t.order.orderType == 'STP' and t.orderStatus.status in ('Submitted', 'PreSubmitted', 'Filled'):
                stop_ok = True
                break
        if not stop_ok:
            logger.error("❌ CRITICAL: No active stop order after all retries — emergency flatten!")
            self.cancel_all_orders()
            self.ib.sleep(1)
            self.flatten_position()
            logger.error("❌ Emergency flatten executed — no stop protection available")

        return result_trades

    def place_market_order(self, action, quantity):
        """Place a market order."""
        order = MarketOrder(action=action, totalQuantity=quantity)
        trade = self.ib.placeOrder(self.contract, order)
        logger.info(f"Market {action} {quantity} contracts")
        return trade

    def place_stop_order(self, action, quantity, stop_price):
        """Place a standalone stop order."""
        stop_price = self._round_to_tick(stop_price)
        from ib_insync import Order
        order = Order(action=action, totalQuantity=quantity, orderType='STP',
                      auxPrice=stop_price, tif='GTC')
        trade = self.ib.placeOrder(self.contract, order)
        logger.info(f"Stop order: {action} {quantity} @ stop {stop_price}, id={order.orderId}")
        return trade

    def place_limit_order(self, action, quantity, limit_price):
        """Place a standalone limit order."""
        limit_price = self._round_to_tick(limit_price)
        from ib_insync import Order
        order = Order(action=action, totalQuantity=quantity, orderType='LMT',
                      lmtPrice=limit_price, tif='GTC')
        trade = self.ib.placeOrder(self.contract, order)
        logger.info(f"Limit order: {action} {quantity} @ limit {limit_price}, id={order.orderId}")
        return trade

    def cancel_all_orders(self):
        """Cancel all open orders for our contract."""
        for trade in self.ib.openTrades():
            if trade.contract.symbol == config.SYMBOL:
                self.ib.cancelOrder(trade.order)
                logger.info(f"Cancelled order {trade.order.orderId}")

    def flatten_position(self):
        """Close all open positions with market orders."""
        for pos in self.ib.positions():
            if pos.contract.symbol == config.SYMBOL and pos.position != 0:
                action = "SELL" if pos.position > 0 else "BUY"
                qty = abs(pos.position)
                self.place_market_order(action, qty)
                logger.info(f"Flattened {qty} contracts ({action})")

    def subscribe_bars(self, handler=None):
        """Subscribe to real-time 5-second bars."""
        bars = self.ib.reqRealTimeBars(
            self.contract, barSize=5, whatToShow="TRADES", useRTH=False
        )
        if handler:
            bars.updateEvent += handler
        return bars

    def get_historical_bars(self, duration="2 D", bar_size="5 mins"):
        """Fetch historical bars for indicator warmup."""
        bars = self.ib.reqHistoricalData(
            self.contract,
            endDateTime="",
            durationStr=duration,
            barSizeSetting=bar_size,
            whatToShow="TRADES",
            useRTH=False,
            formatDate=1,
        )
        return bars

    def reconnect(self, max_retries=10, base_delay=5):
        """Reconnect to IB with exponential backoff. Returns True on success."""
        import time
        self.connected = False
        try:
            self.ib.disconnect()
        except Exception:
            pass

        for attempt in range(1, max_retries + 1):
            delay = min(base_delay * (2 ** (attempt - 1)), 120)
            logger.info(f"Reconnect attempt {attempt}/{max_retries} in {delay}s...")
            time.sleep(delay)
            try:
                self.ib.connect(
                    host=config.IB_HOST,
                    port=config.IB_PORT,
                    clientId=config.IB_CLIENT_ID,
                    timeout=20,
                )
                self.connected = True
                self.ib.reqMarketDataType(3)
                # Re-resolve contract
                self.contract = self._resolve_contract()
                logger.info(f"Reconnected successfully on attempt {attempt}")
                return True
            except Exception as e:
                logger.warning(f"Reconnect attempt {attempt} failed: {e}")
                try:
                    self.ib.disconnect()
                except Exception:
                    pass

        logger.error(f"Failed to reconnect after {max_retries} attempts")
        return False

    def disconnect(self):
        """Disconnect from IB."""
        if self.connected:
            self.ib.disconnect()
            self.connected = False
            logger.info("Disconnected from IB")
