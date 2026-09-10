# Security Console

A tool that runs **on your own computer** and checks devices on a network **you own** (or have written permission to test).

It is not a website and not for scanning the public internet.

**Contact:** [catflap55.GIT@proton.me](mailto:catflap55.GIT@proton.me)

| Check | What you get |
| --- | --- |
| Nmap quick | Common open ports |
| Nmap safe breadth | More ports, slower |
| TLS certificate | HTTPS certificate and protocol |
| HTTP security headers | Missing browser-security headers |
| Lab host discovery | Which hosts answer a ping (`LAB_MODE` on) |

Only scan what you are allowed to scan. Misuse can be illegal.

You do **not** need to know how to use a terminal. Install the programs for your computer, download the zip, open **only the folder named after this computer**, then open **Start** inside it.

Pick your computer and follow **only that section**, in order.

- [Choose the correct folder](#choose-the-correct-folder)
- [Windows](#windows)
- [Mac](#mac)
- [Linux](#linux)
- [Which web address to open](#which-web-address-to-open)
- [After it is running](#after-it-is-running)

---

## Choose the correct folder

After you unzip, you will see three folders: **`Mac`**, **`Windows`**, and **`Linux`**. Open **one** of them — the one that matches this computer. Ignore the other two. Inside, you should only see the files you need (plus a short `How-to-open.txt`).

| This computer | Open this folder | Then open |
| --- | --- | --- |
| **Apple Mac** | **`Mac`** | Double-click **`Read-me-first.html`**, then right-click **`Start.command`** → **Open** (see [Mac](#mac)) |
| **Windows PC** | **`Windows`** | Double-click **`Start.cmd`** |
| **Linux** | **`Linux`** | **`Start.sh`** (see [Linux](#linux)) |

A Mac must not open anything inside **`Windows`**. Those files end in `.cmd`. A Mac will say *There is no application set to open the document*. Close that, go back, and open the **`Mac`** folder instead.

If you are unsure, open **`00-START-HERE.txt`** in the unzipped folder (next to `Mac`, `Windows`, and `Linux`).

---

## Windows

**Open the `Windows` folder only.** See [Choose the correct folder](#choose-the-correct-folder). Do not open the `Mac` folder.

You will use a web browser and **File Explorer** (the yellow folder icon). You should not need to type commands.

### 1. Install three programs

Download each file and run it. Click Next / Install on each.

1. [Python](https://www.python.org/downloads/) — on the **first** screen tick **Add python.exe to PATH**. If you skip that box, uninstall Python and install it again with the box ticked.
2. [Node.js](https://nodejs.org/) — keep the defaults. This program is required.
3. [Nmap](https://nmap.org/download.html) — if you see **Add to PATH**, leave it ticked.

### 2. Download this app

1. Open [https://github.com/catflap55/network-security-tool](https://github.com/catflap55/network-security-tool)
2. Click the green **Code** button, then **Download ZIP**
3. Open your **Downloads** folder
4. Right-click the zip file → **Extract All** → **Extract**
5. Open the **new folder** that appears (not the zip). You must see folders named `Mac`, `Windows`, and `Linux`, plus `00-START-HERE.txt`. If you only see one folder, open that inner folder.
6. Open the **`Windows`** folder. You should see `Start.cmd` and `How-to-open.txt`.

### 3. Start

Inside the **`Windows`** folder, double-click **`Start.cmd`**.

If Windows says it protected your PC: **More info** → **Run anyway**.

A second window will open. That is normal. **Leave it open.** The first start can take a few minutes. Your browser should open the app. If the page fails, see [Which web address to open](#which-web-address-to-open) (try **http://localhost:5173** if **http://127.0.0.1:5173** does not load, or the other way round).

If a **Microsoft Store** window opens instead of starting: Settings → Apps → Advanced app settings → App execution aliases → turn **off** `python.exe` and `python3.exe`. Reinstall Python with **Add python.exe to PATH** ticked. Then double-click `Start.cmd` again.

If a window appears and closes, or you see a message about `python` or `npm`, go back to step 1. Then double-click start again. The real error is in the **second** window — read that text.

### 4. Stop

Still inside the **`Windows`** folder, double-click **`Stop.cmd`**.

---

## Mac

**Open the `Mac` folder only.** See [Choose the correct folder](#choose-the-correct-folder). Do not open the `Windows` folder. If you already saw *There is no application set to open the document … .cmd*, you were in the Windows folder — close that and open **`Mac`** instead.

You will use **Safari** and **Finder**. You should not need to type commands. Ignore Homebrew (`brew`).

### 1. Install Node.js and Nmap

Many Macs already have Python. They usually do **not** have Node.js or Nmap.

1. [Node.js](https://nodejs.org/) — choose the macOS installer, open the downloaded file, click through.
2. [Nmap](https://nmap.org/download.html) — open the macOS `.dmg` and finish the install.
3. Optional: [Python](https://www.python.org/downloads/) if the start file later says Python is missing.

### 2. Download this app

1. In Safari open [https://github.com/catflap55/network-security-tool](https://github.com/catflap55/network-security-tool)
2. Click the green **Code** button, then **Download ZIP**
3. In **Downloads**, double-click the zip so a **folder** appears
4. Open that folder. You must see folders named `Mac`, `Windows`, and `Linux`, plus `00-START-HERE.txt`. If you only see one folder inside, open that inner folder.
5. Open the **`Mac`** folder. You should see `Read-me-first.html`, `Start.command`, `Stop.command`, and `How-to-open.txt`. Stay in this folder. Do not open `Windows`.
6. Double-click **`Read-me-first.html`**. Safari can open that file. It explains the malware warning you will see next.

### 3. Start (the malware warning is expected)

Apple will show:

> “Start.command” Not Opened  
> Apple could not verify “Start.command” is free of malware…

That is **normal**. Apple shows it for a start file downloaded from the internet. It is **not** saying this project is a virus. Do not delete the file.

1. Click **Done** on that warning.
2. Apple menu (top-left) → **System Settings** → **Privacy & Security**.
3. Scroll to **Security**. Click **Open Anyway** next to `Start.command`.
4. Click **Open Anyway** again if asked, and enter the Mac password.
5. Back in the **`Mac`** folder, **right-click** **`Start.command`** → **Open**. Do not double-click.

A text window will appear on its own. **Do not type in it. Do not close it.** Wait until that window says **Ready**. Then the browser opens the app. The first start can take a few minutes.

If the browser says it cannot connect, see [Which web address to open](#which-web-address-to-open). On many Macs **http://localhost:5173** works when **http://127.0.0.1:5173** does not. They are the same app. Keep the Start text window open.

If the window says Node.js or Python is not installed, finish step 1, fully quit that text window, then start again.

If you never see **Open Anyway**, open `Start.command` once so the warning appears (you already did that), then check Privacy & Security again.

### 4. Stop

Still inside the **`Mac`** folder, right-click **`Stop.command`** → **Open**. Or click the text window and press the Control key and the C key together.

---

## Linux

**Open the `Linux` folder only.** See [Choose the correct folder](#choose-the-correct-folder). Do not open the `Windows` folder.

Linux needs a **Terminal** once, to install packages. Terminal is a program on your computer. You paste one line, press Enter, wait, then paste the next.

**Ubuntu / Linux Mint:** click the grid of dots (or Activities), type `Terminal`, press Enter.

**Fedora:** Activities → type `Terminal` → Enter.

Click the terminal window so it is active. To paste: **Ctrl+Shift+V** (not Ctrl+V). Then press **Enter**. Wait until it finishes before the next line.

### 1. Install the programs

Ubuntu / Debian / Linux Mint — paste these two lines, one at a time:

```bash
sudo apt update
sudo apt install -y python3 python3-pip python3-venv nodejs npm nmap unzip
```

It may ask for your login password. Type it (nothing will show as you type) and press Enter.

Fedora:

```bash
sudo dnf install -y python3 python3-pip nodejs npm nmap unzip
```

### 2. Download this app

You can use the browser: open [https://github.com/catflap55/network-security-tool](https://github.com/catflap55/network-security-tool) → green **Code** → **Download ZIP** → extract it in Files. Open the unzipped folder until you see `Mac`, `Windows`, and `Linux`. Open the **`Linux`** folder.

### 3. Start

In Files, inside **`Linux`**, right-click **`Start.sh`** and choose **Run as a program** or **Run in Terminal** if you see that.

If nothing happens, click the terminal window, type `cd ` (cd and a space), drag the **`Linux`** folder onto the terminal, press Enter, then paste:

```bash
bash Start.sh
```

Leave that window open. When the app is ready, open it in the browser. See [Which web address to open](#which-web-address-to-open) if one address fails.

### 4. Stop

Click the terminal window and press **Ctrl+C**.

---

## Which web address to open

This applies to **Windows, Mac, and Linux**.

The app runs on **this computer** at port **5173**. These two addresses are the **same app**:

- http://localhost:5173
- http://127.0.0.1:5173

If one does not load, try the other. Do not mix them up with a public website.

On some Macs, **http://localhost:5173** works when **http://127.0.0.1:5173** shows “Can’t Connect to the Server”. That is normal. Use whichever one opens the Unlock page.

The Start window must still be open. If both addresses fail, the app is not running yet.

## After it is running

The **Unlock** page is asking for a password-like code from **this computer**. You did not choose it. The app created it.

1. Click the **text window** that Start opened (leave it running).
2. Scroll until you see `CONSOLE_TOKEN` and a long line of letters. Copy that line (not the words `CONSOLE_TOKEN=` if they are on a separate label — copy the long value).
3. Or, in Finder / File Explorer, open the unzipped folder and double-click **`CONSOLE-TOKEN.txt`**. Copy the value after `CONSOLE_TOKEN=`.
4. Paste it into the web page → **Continue**.
5. Tick the permission box.
6. Type a target you are allowed to test, such as `127.0.0.1`.

If the Unlock page never appears, see [Which web address to open](#which-web-address-to-open).

Do not put this console on the public internet.

Unlock screen (token field left empty on purpose):

![Unlock Security Console](docs/images/unlock-console.png)

Main screen:

![Main console with a Home lab project](docs/images/main-console.png)

A finished check:

![Scan job log and findings](docs/images/scan-results.png)

---

## If something fails

| You see | Meaning |
| --- | --- |
| “There is no application set to open the document … **.cmd**” | You opened a file from the **`Windows`** folder on a **Mac**. Close that. Open the **`Mac`** folder and right-click **`Start.command`** → **Open**. |
| **“Not Opened”** / **“Apple could not verify … is free of malware”** | Normal Mac block on a downloaded start file. Click **Done**. Then **Apple menu → System Settings → Privacy & Security**. Under **Security**, click **Open Anyway**. Then right-click **`Mac/Start.command`** → **Open**. Do not delete the file. |
| Browser cannot connect to `127.0.0.1:5173` or `localhost:5173` | They are the same app. Try the **other** address. On some Macs only **localhost** works. If both fail, the Start window is not running — start again. |
| Windows blocked the app | **More info** → **Run anyway** |
| Mac: “cannot be opened because it is from an unidentified developer” | Right-click **`Mac/Start.command`** → **Open** → **Open**. If that fails, use Privacy & Security → **Open Anyway** as above. |
| A **Microsoft Store** window opens for Python | The Store python stub is on PATH, not real Python. Turn off App execution aliases for python.exe, reinstall Python with PATH ticked, then `Start.cmd` again. |
| `python` / `npm` / Node.js is not installed | Install that program from the link in your computer’s section, then start again |
| You cannot find the start file | You are looking inside the zip. Extract it, then open the **`Mac`**, **`Windows`**, or **`Linux`** folder. Or open `00-START-HERE.txt`. |
| `brew: command not found` | Ignore Homebrew. Use the Mac section above |

---

## Disclaimer

This tool is for information only. It is not legal, credit, tax, or financial advice. You must do your own independent checks at the official source before you act. The authors are not liable for decisions you make from these results.

The MIT licence still applies to the code. This note is about how you use the console.

---

## Extra (optional)

A file `backend/.env` is created on your machine. Do not upload it. Leave the console on this computer only.

Security reports: [SECURITY.md](SECURITY.md) — email **catflap55.GIT@proton.me**.
