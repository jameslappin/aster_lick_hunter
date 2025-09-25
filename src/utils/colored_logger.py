"""
Colored logging system for enhanced console output.
Provides color-coded log levels and special event formatting.
"""

import logging
import sys
import os
from datetime import datetime

try:
    from colorama import init, Fore, Back, Style

    # Force color support on Windows
    if sys.platform == "win32":
        os.system("")  # Enables ANSI escape sequences on Windows

    # Initialize colorama - always convert on Windows for compatibility
    init(autoreset=True, convert=(sys.platform == "win32"))
    COLORS_AVAILABLE = True
except ImportError:
    COLORS_AVAILABLE = False
    # Define dummy classes for fallback
    class Fore:
        BLACK = RED = GREEN = YELLOW = BLUE = MAGENTA = CYAN = WHITE = RESET = ''
    class Back:
        BLACK = RED = GREEN = YELLOW = BLUE = MAGENTA = CYAN = WHITE = RESET = ''
    class Style:
        DIM = NORMAL = BRIGHT = RESET_ALL = ''

# Color scheme for different log levels and events - Enhanced for readability
COLOR_SCHEME = {
    'DEBUG': Fore.CYAN + Style.DIM + Style.BRIGHT,
    'INFO': Fore.WHITE + Style.BRIGHT,
    'SUCCESS': Fore.GREEN + Style.BRIGHT,
    'WARNING': Fore.YELLOW + Style.BRIGHT,
    'ERROR': Fore.RED + Style.BRIGHT,
    'CRITICAL': Fore.RED + Style.BRIGHT + Back.YELLOW,

    # Trading events
    'TRADE_PLACED': Fore.GREEN + Style.BRIGHT,
    'TRADE_FILLED': Fore.GREEN + Style.BRIGHT + Back.BLACK,
    'TRADE_CANCELLED': Fore.YELLOW + Style.BRIGHT,
    'TRADE_FAILED': Fore.RED + Style.BRIGHT + Back.WHITE,
    'TRADE_PROFIT': Fore.GREEN + Style.BRIGHT + Back.BLACK,
    'TRADE_LOSS': Fore.RED + Style.BRIGHT,

    # Liquidation events
    'LIQUIDATION': Fore.YELLOW + Style.BRIGHT,
    'LIQUIDATION_BIG': Fore.RED + Style.BRIGHT + Back.YELLOW,
    'THRESHOLD_MET': Fore.GREEN + Style.BRIGHT + Back.BLACK,

    # Tranche events
    'TRANCHE_NEW': Fore.MAGENTA + Style.BRIGHT,
    'TRANCHE_ADD': Fore.MAGENTA + Style.BRIGHT,
    'TRANCHE_MERGE': Fore.CYAN + Style.BRIGHT + Back.BLACK,
    'TRANCHE_CLOSE': Fore.BLUE + Style.BRIGHT,

    # Position events
    'POSITION_OPEN': Fore.GREEN + Style.BRIGHT,
    'POSITION_CLOSE': Fore.BLUE + Style.BRIGHT + Back.BLACK,
    'POSITION_PROFIT': Fore.GREEN + Style.BRIGHT + Back.BLACK,
    'POSITION_LOSS': Fore.RED + Style.BRIGHT,

    # System events
    'STARTUP': Fore.CYAN + Style.BRIGHT + Back.BLUE,
    'SHUTDOWN': Fore.YELLOW + Style.BRIGHT + Back.RED,
    'CONNECTION': Fore.BLUE + Style.BRIGHT,
    'DISCONNECTION': Fore.YELLOW + Style.BRIGHT,
}

# Enhanced symbols for better visual distinction (ASCII-safe)
SYMBOLS = {
    'SUCCESS': '[✓]',
    'ERROR': '[✗]',
    'WARNING': '[⚠]',
    'INFO': '[ℹ]',
    'TRADE': '[$]',
    'LOSS': '[↓]',
    'PROFIT': '[↑]',
    'LIQUIDATION': '[💥]',
    'TRANCHE': '[📦]',
    'ARROW_UP': '↑',
    'ARROW_DOWN': '↓',
    'ARROW_RIGHT': '→',
    'DOT': '•',
}


class ColoredFormatter(logging.Formatter):
    """Custom formatter that adds colors to log output."""

    def __init__(self, *args, use_colors=True, **kwargs):
        super().__init__(*args, **kwargs)
        self.use_colors = use_colors and COLORS_AVAILABLE

        # Custom format strings for different log levels
        self.formats = {
            'DEBUG': f"{COLOR_SCHEME['DEBUG']}%(asctime)s - DEBUG - %(message)s{Style.RESET_ALL}",
            'INFO': f"%(asctime)s - {COLOR_SCHEME['INFO']}INFO{Style.RESET_ALL} - %(message)s",
            'WARNING': f"%(asctime)s - {COLOR_SCHEME['WARNING']}WARNING{Style.RESET_ALL} - {COLOR_SCHEME['WARNING']}%(message)s{Style.RESET_ALL}",
            'ERROR': f"%(asctime)s - {COLOR_SCHEME['ERROR']}ERROR{Style.RESET_ALL} - {COLOR_SCHEME['ERROR']}%(message)s{Style.RESET_ALL}",
            'CRITICAL': f"{COLOR_SCHEME['CRITICAL']}%(asctime)s - CRITICAL - %(message)s{Style.RESET_ALL}",
        }

    def format(self, record):
        if self.use_colors:
            # Get the format for this log level
            log_fmt = self.formats.get(record.levelname, self._fmt)

            # Temporarily set the format
            original_fmt = self._fmt
            self._fmt = log_fmt
            self._style._fmt = log_fmt

            try:
                # Format the record
                result = super().format(record)
            except UnicodeEncodeError:
                # Fall back to ASCII-safe formatting if Unicode fails
                ascii_formats = {
                    'DEBUG': '%(asctime)s - DEBUG - %(message)s',
                    'INFO': '%(asctime)s - INFO - %(message)s',
                    'WARNING': '%(asctime)s - [WARNING] - %(message)s',
                    'ERROR': '%(asctime)s - [ERROR] - %(message)s',
                    'CRITICAL': '%(asctime)s - [CRITICAL] - %(message)s',
                }
                ascii_fmt = ascii_formats.get(record.levelname, self._fmt)
                self._fmt = ascii_fmt
                self._style._fmt = ascii_fmt
                result = super().format(record)

            # Restore original format
            self._fmt = original_fmt
            self._style._fmt = original_fmt

            return result
        else:
            return super().format(record)


class ColoredLogger:
    """Enhanced logger with color-coded output and special trading methods."""

    def __init__(self, name=None, level=logging.INFO):
        # Set up base logger
        self.logger = logging.getLogger(name or __name__)
        self.logger.setLevel(level)
        self.logger.handlers.clear()

        # Console handler with colors
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(
            ColoredFormatter(
                '%(asctime)s - %(levelname)s - %(message)s',
                datefmt='%H:%M:%S',
                use_colors=True
            )
        )
        self.logger.addHandler(console_handler)

        # File handler without colors
        data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'data')
        os.makedirs(data_dir, exist_ok=True)
        log_file_path = os.path.join(data_dir, 'bot.log')

        file_handler = logging.FileHandler(log_file_path)
        file_handler.setFormatter(
            logging.Formatter(
                '%(asctime)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
        )
        self.logger.addHandler(file_handler)

    # Standard logging methods
    def debug(self, message):
        self.logger.debug(message)

    def info(self, message):
        # Clean up Unicode characters that can't be encoded in Windows console
        if sys.platform == "win32":
            message = message.replace('Ⓢ', 'S').replace('\u24c8', 'S')
        self.logger.info(message)

    def warning(self, message):
        # Clean up Unicode characters that can't be encoded in Windows console
        if sys.platform == "win32":
            message = message.replace('Ⓢ', 'S').replace('\u24c8', 'S')
        self.logger.warning(message)

    def error(self, message):
        # Clean up Unicode characters that can't be encoded in Windows console
        if sys.platform == "win32":
            # Replace problematic Unicode characters
            message = message.replace('Ⓢ', 'S').replace('\u24c8', 'S')
        self.logger.error(message)

    def critical(self, message):
        self.logger.critical(message)

    # Special trading event methods
    def success(self, message):
        """Log a success message in green."""
        # Use ASCII-safe symbols on Windows to avoid Unicode encode errors
        if sys.platform == "win32":
            self.logger.info(f"[SUCCESS] {message}")
        elif COLORS_AVAILABLE:
            self.logger.info(f"{COLOR_SCHEME['SUCCESS']}{SYMBOLS['SUCCESS']} {message}{Style.RESET_ALL}")
        else:
            self.logger.info(f"[SUCCESS] {message}")

    def trade_placed(self, symbol, side, qty, price):
        """Log a trade placement."""
        message = f"Order placed: {symbol} {side} {qty} @ {price}"
        # Use ASCII-safe symbols on Windows to avoid Unicode encode errors
        if sys.platform == "win32":
            self.logger.info(f"[TRADE] {message}")
        elif COLORS_AVAILABLE:
            self.logger.info(
                f"{COLOR_SCHEME['TRADE_PLACED']}{SYMBOLS['TRADE']} {message}{Style.RESET_ALL}"
            )
        else:
            self.logger.info(f"[TRADE] {message}")

    def trade_filled(self, symbol, side, qty, price, pnl=None):
        """Log a trade fill."""
        message = f"Order filled: {symbol} {side} {qty} @ {price}"
        if pnl is not None:
            message += f" | PNL: {pnl:+.2f}"

        # Use ASCII-safe symbols on Windows to avoid Unicode encode errors
        if sys.platform == "win32":
            self.logger.info(f"[FILLED] {message}")
        elif COLORS_AVAILABLE:
            color = COLOR_SCHEME['TRADE_PROFIT'] if pnl and pnl >= 0 else COLOR_SCHEME['TRADE_LOSS'] if pnl and pnl < 0 else COLOR_SCHEME['TRADE_FILLED']
            symbol = SYMBOLS['PROFIT'] if pnl and pnl >= 0 else SYMBOLS['LOSS'] if pnl and pnl < 0 else SYMBOLS['SUCCESS']
            self.logger.info(f"{color}{symbol} {message}{Style.RESET_ALL}")
        else:
            self.logger.info(f"[FILLED] {message}")

    def trade_failed(self, symbol, reason):
        """Log a failed trade."""
        message = f"Trade failed for {symbol}: {reason}"
        # Use ASCII-safe symbols on Windows to avoid Unicode encode errors
        if sys.platform == "win32":
            self.logger.error(f"[FAILED] {message}")
        elif COLORS_AVAILABLE:
            self.logger.error(
                f"{COLOR_SCHEME['TRADE_FAILED']}{SYMBOLS['ERROR']} {message}{Style.RESET_ALL}"
            )
        else:
            self.logger.error(f"[FAILED] {message}")

    def liquidation(self, symbol, side, qty, price, usdt_value, volume_info=""):
        """Log a liquidation event."""
        position_type = "Long" if side == "SELL" else "Short"
        message = f"{position_type} Liquidation: {symbol} {side} {qty} @ ${price:.4f} (${usdt_value:.2f}){volume_info}"

        # Use ASCII-safe symbols on Windows to avoid Unicode encode errors
        if sys.platform == "win32":
            log_type = "[BIG LIQUIDATION]" if usdt_value > 50000 else "[LIQUIDATION]"
            self.logger.info(f"{log_type} {message}")
        # Big liquidation if > $50k
        elif usdt_value > 50000:
            if COLORS_AVAILABLE:
                self.logger.info(
                    f"{COLOR_SCHEME['LIQUIDATION_BIG']}{SYMBOLS['LIQUIDATION']} BIG {message}{Style.RESET_ALL}"
                )
            else:
                self.logger.info(f"[BIG LIQUIDATION] {message}")
        else:
            if COLORS_AVAILABLE:
                self.logger.info(
                    f"{COLOR_SCHEME['LIQUIDATION']}{message}{Style.RESET_ALL}"
                )
            else:
                self.logger.info(f"[LIQUIDATION] {message}")

    def threshold_met(self, symbol, volume, threshold):
        """Log when volume threshold is met."""
        message = f"Volume threshold met for {symbol}: ${volume:.2f} > ${threshold:.2f}"
        # Use ASCII-safe symbols on Windows to avoid Unicode encode errors
        if sys.platform == "win32":
            self.logger.info(f"[THRESHOLD MET] {message}")
        elif COLORS_AVAILABLE:
            self.logger.info(
                f"{COLOR_SCHEME['THRESHOLD_MET']}{SYMBOLS['SUCCESS']} {message}{Style.RESET_ALL}"
            )
        else:
            self.logger.info(f"[THRESHOLD MET] {message}")

    def tranche_event(self, event_type, symbol, tranche_id, details=""):
        """Log tranche-related events."""
        event_types = {
            'new': ('TRANCHE_NEW', f"New tranche #{tranche_id} created"),
            'add': ('TRANCHE_ADD', f"Adding to tranche #{tranche_id}"),
            'merge': ('TRANCHE_MERGE', f"Merging tranches"),
            'close': ('TRANCHE_CLOSE', f"Closing tranche #{tranche_id}")
        }

        color_key, base_msg = event_types.get(event_type, ('INFO', f"Tranche event"))
        message = f"{symbol}: {base_msg}"
        if details:
            message += f" - {details}"

        # Use ASCII-safe symbols on Windows to avoid Unicode encode errors
        if sys.platform == "win32":
            self.logger.info(f"[TRANCHE] {message}")
        elif COLORS_AVAILABLE:
            self.logger.info(
                f"{COLOR_SCHEME[color_key]}{SYMBOLS['TRANCHE']} {message}{Style.RESET_ALL}"
            )
        else:
            self.logger.info(f"[TRANCHE] {message}")

    def position_update(self, symbol, side, qty, entry_price, current_pnl):
        """Log position updates with PNL coloring."""
        # Use ASCII-safe symbols on Windows to avoid Unicode encode errors
        if sys.platform == "win32":
            status = "[PROFIT]" if current_pnl > 0 else "[LOSS]" if current_pnl < 0 else "[FLAT]"
            message = f"{symbol} {side}: {qty} @ {entry_price:.4f} | PNL: {current_pnl:+.2f}%"
            self.logger.info(f"{status} {message}")
        else:
            arrow = SYMBOLS['ARROW_UP'] if current_pnl > 0 else SYMBOLS['ARROW_DOWN'] if current_pnl < 0 else SYMBOLS['ARROW_RIGHT']
            color = COLOR_SCHEME['POSITION_PROFIT'] if current_pnl > 0 else COLOR_SCHEME['POSITION_LOSS'] if current_pnl < 0 else Fore.YELLOW
            message = f"{symbol} {side}: {qty} @ {entry_price:.4f} | PNL: {current_pnl:+.2f}%"

            if COLORS_AVAILABLE:
                self.logger.info(f"{color}{arrow} {message}{Style.RESET_ALL}")
            else:
                status = "PROFIT" if current_pnl > 0 else "LOSS" if current_pnl < 0 else "FLAT"
                self.logger.info(f"[{status}] {message}")

    def startup(self, message):
        """Log startup messages."""
        # Use ASCII-safe symbols on Windows to avoid Unicode encode errors
        if sys.platform == "win32":
            self.logger.info(f"\n{'='*50}\n{message}\n{'='*50}")
        elif COLORS_AVAILABLE:
            self.logger.info(
                f"{COLOR_SCHEME['STARTUP']}{'='*50}{Style.RESET_ALL}\n"
                f"{COLOR_SCHEME['STARTUP']}{SYMBOLS['INFO']} {message}{Style.RESET_ALL}\n"
                f"{COLOR_SCHEME['STARTUP']}{'='*50}{Style.RESET_ALL}"
            )
        else:
            self.logger.info(f"\n{'='*50}\n{message}\n{'='*50}")

    def shutdown(self, message):
        """Log shutdown messages."""
        # Use ASCII-safe symbols on Windows to avoid Unicode encode errors
        if sys.platform == "win32":
            self.logger.info(f"[WARNING] {message}")
        elif COLORS_AVAILABLE:
            self.logger.info(
                f"{COLOR_SCHEME['SHUTDOWN']}{SYMBOLS['WARNING']} {message}{Style.RESET_ALL}"
            )
        else:
            self.logger.info(f"[SHUTDOWN] {message}")


# Create global colored logger instance
colored_log = ColoredLogger("AsterBot")

# For backward compatibility
log = colored_log
