# Panasonic Viera TV Integration for Unfolded Circle Remote 2/3

Control your Panasonic Viera Smart TVs directly from your Unfolded Circle Remote 2 or Remote 3 with comprehensive media player control, **advanced remote control**, **PIN-based pairing for encrypted TVs**, and **media playback support**.

![Panasonic Viera](https://img.shields.io/badge/Panasonic-Viera%20TV-blue)
[![GitHub Release](https://img.shields.io/github/v/release/mase1981/uc-intg-panasonicviera?style=flat-square)](https://github.com/mase1981/uc-intg-panasonicviera/releases)
![License](https://img.shields.io/badge/license-MPL--2.0-blue?style=flat-square)
[![GitHub issues](https://img.shields.io/github/issues/mase1981/uc-intg-panasonicviera?style=flat-square)](https://github.com/mase1981/uc-intg-panasonicviera/issues)
[![Community Forum](https://img.shields.io/badge/community-forum-blue?style=flat-square)](https://unfolded.community/)
[![Discord](https://badgen.net/discord/online-members/zGVYf58)](https://discord.gg/zGVYf58)
![GitHub Downloads (all assets, all releases)](https://img.shields.io/github/downloads/mase1981/uc-intg-panasonicviera/total?style=flat-square)
[![Buy Me A Coffee](https://img.shields.io/badge/buy%20me%20a%20coffee-donate-yellow.svg?style=flat-square)](https://buymeacoffee.com/meirmiyara)
[![PayPal](https://img.shields.io/badge/PayPal-donate-blue.svg?style=flat-square)](https://paypal.me/mmiyara)
[![Github Sponsors](https://img.shields.io/badge/GitHub%20Sponsors-30363D?&logo=GitHub-Sponsors&logoColor=EA4AAA&style=flat-square)](https://github.com/sponsors/mase1981)


## Features

This integration provides comprehensive control of Panasonic Viera Smart TVs through the Panasonic SOAP/HTTP protocol, delivering seamless integration with your Unfolded Circle Remote for complete TV control.

---
## ❤️ Support Development ❤️

If you find this integration useful, consider supporting development:

[![GitHub Sponsors](https://img.shields.io/badge/Sponsor-GitHub-pink?style=for-the-badge&logo=github)](https://github.com/sponsors/mase1981)
[![Buy Me A Coffee](https://img.shields.io/badge/Buy%20Me%20A%20Coffee-FFDD00?style=for-the-badge&logo=buy-me-a-coffee&logoColor=black)](https://www.buymeacoffee.com/meirmiyara)
[![PayPal](https://img.shields.io/badge/PayPal-00457C?style=for-the-badge&logo=paypal&logoColor=white)](https://paypal.me/mmiyara)

Your support helps maintain this integration. Thank you! ❤️
---

### 📺 **Media Player Control**

#### **Power Management**
- **Power On/Off** - Complete power control
- **State Feedback** - Real-time power state monitoring
- **Network Wake** - Wake TV from network standby

#### **Volume Control**
- **Volume Up/Down** - Precise volume adjustment
- **Set Volume** - Direct volume control (0-100)
- **Volume Slider** - Visual volume control
- **Mute Toggle** - Quick mute/unmute
- **Unmute** - Explicit unmute control

#### **Playback Control**
- **Play/Pause** - Playback control
- **Stop** - Stop playback
- **Fast Forward** - Skip forward in content
- **Rewind** - Skip backward in content
- **Next/Previous** - Chapter navigation

#### **Media Playback**
- **URL Playback** - Play media URLs in TV browser
- **Web Content** - Open web pages on TV
- **Streaming Support** - Play HTTP/HTTPS streams

### 🎮 **Advanced Remote Control**

#### **Navigation Page** (3x4 Grid)
Control your TV with intuitive navigation:
- **Home Button** - Quick access to TV home screen
- **D-Pad** - Up, Down, Left, Right navigation
- **OK Button** - Select/Enter
- **Back/Exit** - Navigation controls
- **Menu** - Access TV settings
- **Info/Guide** - Program information
- **Apps** - Quick access to apps

#### **Playback Page** (3x3 Grid)
Complete playback control:
- **Play/Pause/Stop** - Playback control
- **Skip Back/Forward** - Chapter navigation
- **Rewind/Fast Forward** - Seek controls
- **Record** - Recording control (if supported)

#### **Channels Page** (3x4 Grid)
Channel and number control:
- **Number Pad** - Direct channel entry (0-9)
- **Channel Up/Down** - Channel navigation
- **Previous Channel** - Quick channel switching

#### **Color & Input Page** (2x4 Grid)
Advanced TV features:
- **Color Buttons** - Red, Green, Yellow, Blue for interactive features
- **Input Selection** - Switch between inputs
- **TV/AV** - Input mode switching
- **Netflix** - Quick access to Netflix app

### 🔐 **Encrypted TV Support**

#### **Automatic PIN Pairing**
- **Encryption Detection** - Automatically detects if TV requires pairing
- **PIN Request** - Sends PIN request to TV
- **On-Screen Display** - PIN appears on TV screen
- **Secure Pairing** - Stores credentials for future connections
- **One-Time Setup** - Pairing credentials saved permanently

### 🔌 **Multi-Device Support**

- **Multiple TVs** - Control unlimited Panasonic Viera TVs
- **Individual Configuration** - Each TV with independent settings
- **Manual Configuration** - Direct IP address entry
- **Model Detection** - Automatic TV model identification
- **Mixed Support** - Control both encrypted and unencrypted TVs

### **Supported Models**

#### **Viera Smart TVs** (2011-Present)
- **2011-2014 Models** - Viera Cast platform
- **2015-2018 Models** - Firefox OS platform
- **2019+ Models** - My Home Screen platform
- **4K Models** - All 4K Viera TVs with network control
- **HD Models** - HD Viera TVs with network capability

#### **Encryption Support**
- **Unencrypted TVs** - Direct connection without pairing
- **Encrypted TVs** - Automatic PIN-based pairing
- **Mixed Networks** - Support for both types simultaneously

### **Protocol Requirements**

- **Protocol**: SOAP over HTTP/HTTPS
- **Control Port**: 55000 (default)
- **Network Access**: TV must be on same local network
- **Connection Type**: Local network polling (no cloud)
- **Poll Interval**: 30 seconds (configurable)

### **Network Requirements**

- **Local Network Access** - Integration requires same network as TV
- **HTTP Protocol** - Firewall must allow HTTP traffic on port 55000
- **Static IP Recommended** - TV should have static IP or DHCP reservation
- **Network Control Enabled** - TV must allow network control (usually enabled by default)

## Installation

### Option 1: Remote Web Interface (Recommended)
1. Navigate to the [**Releases**](https://github.com/mase1981/uc-intg-panasonicviera/releases) page
2. Download the latest `uc-intg-panasonicviera-<version>-aarch64.tar.gz` file
3. Open your remote's web interface (`http://your-remote-ip`)
4. Go to **Settings** → **Integrations** → **Add Integration**
5. Click **Upload** and select the downloaded `.tar.gz` file

### Option 2: Docker (Advanced Users)

The integration is available as a pre-built Docker image from GitHub Container Registry:

**Image**: `ghcr.io/mase1981/uc-intg-panasonicviera:latest`

**Docker Compose:**
```yaml
services:
  uc-intg-panasonicviera:
    image: ghcr.io/mase1981/uc-intg-panasonicviera:latest
    container_name: uc-intg-panasonicviera
    network_mode: host
    volumes:
      - </local/path>:/data
    environment:
      - UC_CONFIG_HOME=/data
      - UC_INTEGRATION_HTTP_PORT=9090
      - UC_INTEGRATION_INTERFACE=0.0.0.0
      - PYTHONPATH=/app
    restart: unless-stopped
```

**Docker Run:**
```bash
docker run -d --name uc-panasonicviera --restart unless-stopped --network host -v panasonicviera-config:/app/config -e UC_CONFIG_HOME=/app/config -e UC_INTEGRATION_INTERFACE=0.0.0.0 -e UC_INTEGRATION_HTTP_PORT=9090 -e PYTHONPATH=/app ghcr.io/mase1981/uc-intg-panasonicviera:latest
```

## Configuration

### Step 1: Prepare Your Panasonic Viera TV

**IMPORTANT**: TV must be powered on and connected to your network before adding the integration.

#### Verify Network Connection:
1. Check that TV is connected to network (WiFi or Ethernet)
2. Note the IP address from TV's network settings menu
3. Ensure network control is enabled (Settings → Network → Network Link Settings)
4. Verify TV firmware is up to date

#### Network Setup:
- **Wired Connection**: Recommended for stability
- **Static IP**: Recommended via DHCP reservation
- **Firewall**: Allow HTTP traffic on port 55000
- **Network Isolation**: Must be on same subnet as Remote

### Step 2: Setup Integration

1. After installation, go to **Settings** → **Integrations**
2. The Panasonic Viera TV integration should appear in **Available Integrations**
3. Click **"Configure"** and enter TV details:

#### **Configuration Fields:**

   - **TV Name**: Friendly name (e.g., "Living Room TV")
   - **IP Address**: Enter TV IP (e.g., 192.168.1.100)
   - **Port**: Default 55000 (change only if customized)
   - Click **Complete Setup**

   **Connection Test:**
   - Integration verifies TV connectivity
   - Checks if TV requires encryption

   **For Encrypted TVs:**
   - PIN request automatically sent to TV
   - PIN displays on TV screen (4 digits)
   - Enter PIN in setup form
   - Integration pairs and saves credentials
   - Setup completes automatically

4. Integration will create **two entities**:
   - **Media Player**: `media_player.viera_[tv_name]`
   - **Remote Control**: `remote.viera_[tv_name]`

## Using the Integration

### Media Player Entity

Each Panasonic Viera TV's media player entity provides complete control:

- **Power Control**: On/Off with state feedback
- **Volume Control**: Volume slider (0-100)
- **Volume Buttons**: Up/Down with real-time feedback
- **Mute Control**: Toggle, Mute, Unmute
- **Playback Control**: Play, Pause, Stop, Skip, Fast Forward, Rewind
- **Media URLs**: Play web content in TV browser
- **State Display**: Current power, volume, and mute status

### Remote Control Entity

Complete TV remote control organized into 4 pages:

#### **Page 1: Navigation**
| Button | Function |
|--------|----------|
| Home | TV Home screen |
| Up/Down/Left/Right | D-Pad navigation |
| OK | Select/Enter |
| Back | Back button |
| Exit | Exit menu |
| Menu | TV settings menu |
| Info | Program info |
| Guide | TV guide |
| Apps | Apps menu |

#### **Page 2: Playback**
| Button | Function |
|--------|----------|
| Play | Play content |
| Pause | Pause playback |
| Stop | Stop playback |
| Skip Back | Previous chapter |
| Skip Forward | Next chapter |
| Rewind | Seek backward |
| Fast Forward | Seek forward |
| Record | Record (if supported) |

#### **Page 3: Channels**
| Button | Function |
|--------|----------|
| 0-9 | Number pad for direct channel entry |
| CH Up | Next channel |
| CH Down | Previous channel |

#### **Page 4: Color & Input**
| Button | Function |
|--------|----------|
| Red/Green/Yellow/Blue | Interactive features |
| Input | Input selection |
| TV | Switch to TV mode |
| AV | Switch to AV mode |
| Netflix | Launch Netflix app |

## Credits

- **Developer**: Meir Miyara
- **Panasonic**: Viera Smart TV platform
- **Unfolded Circle**: Remote 2/3 integration framework (ucapi)
- **panasonic-viera**: Python library for Panasonic TV control
- **Protocol**: SOAP over HTTP/HTTPS
- **Community**: Testing and feedback from UC community

## License

This project is licensed under the Mozilla Public License 2.0 (MPL-2.0) - see LICENSE file for details.

## Support & Community

- **GitHub Issues**: [Report bugs and request features](https://github.com/mase1981/uc-intg-panasonicviera/issues)
- **UC Community Forum**: [General discussion and support](https://unfolded.community/)
- **Developer**: [Meir Miyara](https://www.linkedin.com/in/meirmiyara)
- **Panasonic Support**: [Official Panasonic Support](https://www.panasonic.com/global/support.html)

---

**Made with ❤️ for the Unfolded Circle and Panasonic Viera Communities**

**Thank You**: Meir Miyara
