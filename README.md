# Discord Captcha Bot
<div align="center">
  
![Bot Logo](https://cdn.discordapp.com/attachments/1351096159510204456/1353292755966889984/Verify_Bot.png?ex=67e11f97&is=67dfce17&hm=be5e77f3cff1f4acccaa93d71be99bcec8eb23a60cf5d1828f30e79ec649846c&)

**A powerful, customizable solution to protect your Discord server from bots and raids**

[![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)](https://github.com/codingjonas009/discord-captcha-bot)
[![License](https://img.shields.io/badge/license-MIT-orange.svg)](LICENCE)
[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
[![Discord.py](https://img.shields.io/badge/discord.py-2.0%2B-blue)](https://discordpy.readthedocs.io/en/stable/)
</div>

## 🛡️ Features
- **Visual CAPTCHA Verification**: Sophisticated image-based CAPTCHAs with distortion effects
- **Role Integration**: Automatically assigns customizable roles upon successful verification
- **Timeout Protection**: Implements configurable timeout periods for failed verification attempts
- **Customizable Settings**: Adjust CAPTCHA complexity, appearance, and verification parameters
- **Persistent Verification**: Database-driven system that maintains verification status across user sessions
- **Interactive UI**: Clean, modern interface with custom embeds and interactive buttons
- **Server-specific Verification**: Manages verification on a per-server basis
- **Admin Controls**: Comprehensive commands for server administrators

## 📋 Requirements
- Python 3.8 or higher
- discord.py 2.0 or higher
- Pillow (PIL) for image generation
- SQLite3 for database management

## ⚙️ Installation
1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/discord-captcha-bot.git
   cd discord-captcha-bot
   ```

2. **Install dependencies**
   ```bash
   pip install discord.py pillow
   ```

3. **Configure the bot**
   - Create a new application in the [Discord Developer Portal](https://discord.com/developers/applications)
   - Enable necessary intents (Server Members, Message Content)
   - Create a bot user and copy your token
   - Add the token to your bot configuration

4. **Start the bot**
   ```bash
   python bot.py
   ```

## 🔧 Configuration
The bot configuration is stored in `verify_config.json`:

```json
{
  "verified_role_id": 1342506397526655046,
  "captcha_settings": {
    "length": 6,
    "width": 280,
    "height": 90,
    "font_size": 40,
    "font_path": "arial.ttf"
  },
  "verification_settings": {
    "max_attempts": 5,
    "timeout_minutes": 10,
    "db_filename": "captcha_verification.db"
  },
  "messages": {
    "welcome": "Welcome to the server. Please complete the captcha verification process to gain access.",
    "already_verified": "Your account has already been verified on this server.",
    "verification_success": "Verification completed successfully. You now have full access to the server.",
    "verification_failed": "The captcha entry was incorrect. Please attempt verification again.",
    "verification_timeout": "Maximum verification attempts exceeded. Please try again after the timeout period."
  }
}
```

## 📚 Commands
| Command | Description |
|---------|-------------|
| `!setup_verification` | Creates a verification system in the current channel |

## 🖼️ Preview
<div align="center">
  <img src="https://via.placeholder.com/800x400" alt="Bot Preview" width="80%">
</div>

## 📊 Verification System Flow
1. User clicks the "Verify" button on the verification message
2. Bot sends a CAPTCHA image in an ephemeral (private) message
3. User enters the CAPTCHA text in the modal dialog
4. If correct, user receives the verified role and gains access
5. If incorrect, user can retry (up to configured maximum)
6. After too many failures, a timeout period is enforced

## 🔒 Security Features
- **Progressive Difficulty**: CAPTCHA difficulty increases with failed attempts
- **Timeout Mechanism**: Prevents brute-force attacks
- **Image Distortion**: Multiple distortion techniques make automation difficult
- **Ephemeral Messages**: Private verification that only the user can see
- **Database Tracking**: Monitors verification attempts and suspicious patterns

## 🔗 Links
- [Documentation Wiki](https://github.com/codingjonas009/discord-captcha-bot/wiki)
- Contact: Discord username `jonas.redstone` (DMs open)
- [Report Bugs](https://github.com/codingjonas009/discord-captcha-bot/issues)

## 🛠️ Advanced Customization
### Custom CAPTCHA Generation
The bot includes a sophisticated CAPTCHA generation system:
- Character rotation for increased difficulty
- Random noise and line generation
- Gaussian blur effects
- Custom fonts support

### Custom Fonts
To use a custom font:
1. Place your TTF font file in the bot's directory
2. Update the `font_path` in the configuration file

## 🤝 Contributing
Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## ⭐ Star History
[![Star History Chart](https://via.placeholder.com/800x300)](https://star-history.com/codingjonas009/discord-captcha-bot)

---
<div align="center">
  
Made with ❤️ by Jonas
</div>
