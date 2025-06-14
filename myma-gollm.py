import MetaTrader5 as mt5
import pyperclip
import time
import tkinter as tk
from tkinter import messagebox
import threading

# --- MT5 Login Details ---
MT5_LOGIN = 99534041
MT5_PASSWORD = "PASS"
MT5_SERVER = "XMGlobal-MT5 5"

btc_symbol = None  # Will be detected on login

# --- GUI Setup ---
root = tk.Tk()
root.geometry("400x200")
root.title("Clipboard BTC BUY Agent")

click_button = tk.Button(root, text="Connect to MT5", width=25)
click_button.pack(pady=40)

# --- Find BTC Symbol Automatically ---
def find_btc_symbol():
    global btc_symbol
    for symbol in mt5.symbols_get():
        if "BTCUSD" in symbol.name.upper():
            btc_symbol = symbol.name
            print("✅ BTC symbol detected:", btc_symbol)
            return True
    print("❌ BTC symbol not found.")
    return False

# --- MT5 Trade Logic ---
def place_buy_btc():
    global btc_symbol
    if not mt5.symbol_select(btc_symbol, True):
        print(f"❌ Failed to select symbol {btc_symbol}.")
        return

    tick = mt5.symbol_info_tick(btc_symbol)
    if tick is None:
        print("❌ No tick data for", btc_symbol)
        return

    price = tick.ask
    volume = 0.01

    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": btc_symbol,
        "volume": volume,
        "type": mt5.ORDER_TYPE_BUY,
        "price": price,
        "deviation": 10,
        "magic": 20240613,
        "comment": "Clipboard-BTC-BUY",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }

    result = mt5.order_send(request)
    if result.retcode == mt5.TRADE_RETCODE_DONE:
        print("✅ BTC BUY order sent!")
    else:
        print("❌ Trade failed:", result)

# --- Clipboard Monitor ---
def start_automation():
    def automation_loop():
        last_text = ""
        while True:
            try:
                current = pyperclip.paste().strip().lower()
                if current != last_text:
                    last_text = current
                    print("[Clipboard]:", current)
                    if current == "$&&buy":
                        place_buy_btc()
            except Exception as e:
                print("Clipboard error:", e)
            time.sleep(0.5)

    threading.Thread(target=automation_loop, daemon=True).start()

# --- MT5 Connection Logic ---
def connect_to_mt5(login, password, server):
    if not mt5.initialize():
        messagebox.showerror("Error", "initialize() failed")
        mt5.shutdown()
        return

    authorized = mt5.login(login=int(login), password=password, server=server)
    if authorized:
        print("✅ Connected to MetaTrader 5")

        if find_btc_symbol():
            start_automation()
        else:
            messagebox.showerror("Error", "BTCUSD symbol not found.")
    else:
        messagebox.showerror("Error", "Failed to connect to MetaTrader 5")

# --- GUI Button Logic ---
def on_button_click():
    connect_to_mt5(MT5_LOGIN, MT5_PASSWORD, MT5_SERVER)
    click_button.config(state="disabled", text="Connected")

click_button.config(command=on_button_click)

# --- Auto Connect After 10s ---
def check_and_auto_click():
    time.sleep(10)
    if click_button["state"] == "normal":
        root.after(0, on_button_click)

threading.Thread(target=check_and_auto_click, daemon=True).start()

# --- Start GUI ---
root.mainloop()
