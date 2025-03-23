# Discord Captcha Bot

<div align="center">
  
![Bot Logo]([https://via.placeholder.com/150](https://cdn.discordapp.com/attachments/1351096159510204456/1353292755966889984/Verify_Bot.png?ex=67e11f97&is=67dfce17&hm=be5e77f3cff1f4acccaa93d71be99bcec8eb23a60cf5d1828f30e79ec649846c&))

**A powerful, customizable solution to protect your Discord server from bots and raids**

[![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)](https://github.com/yourusername/discord-captcha-bot)
[![License](https://img.shields.io/badge/license-Custom-orange.svg)](LICENSE)
[![Discord Server](https://img.shields.io/badge/Discord-Support%20Server-7289da.svg)](https://discord.gg/your-invite-link)

</div>

## 🛡️ Features

- **Advanced CAPTCHA Systems**: Image-based, math problems, and text verification methods
- **Customizable Security Levels**: Adjust strictness based on your server's needs
- **Raid Protection**: Automatic detection of suspicious join patterns
- **Member Verification**: Ensures only real users gain access to your server
- **Role Integration**: Automatically assign roles to verified members
- **Logging System**: Detailed logs of verification attempts and outcomes
- **Multi-language Support**: CAPTCHA challenges in multiple languages
- **User-friendly Setup**: Simple configuration for server administrators

## 📋 Requirements

- Node.js v16.0.0 or higher
- Discord.js v14.0.0 or higher
- A Discord Bot Token
- MongoDB (for storing verification data)

## ⚙️ Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/discord-captcha-bot.git
   cd discord-captcha-bot
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Configure the bot**
   ```bash
   cp config.example.json config.json
   # Edit config.json with your bot token and preferences
   ```

4. **Start the bot**
   ```bash
   npm start
   ```

## 🔧 Configuration

Open `config.json` and customize the following settings:

```json
{
  "token": "YOUR_DISCORD_BOT_TOKEN",
  "prefix": "!",
  "mongoURI": "YOUR_MONGODB_CONNECTION_STRING",
  "captchaSettings": {
    "type": "image", // Options: "image", "math", "text"
    "difficulty": "medium", // Options: "easy", "medium", "hard"
    "timeout": 300 // Time in seconds for users to complete CAPTCHA
  },
  "verifiedRole": "ROLE_ID_TO_ASSIGN",
  "logChannel": "CHANNEL_ID_FOR_LOGS"
}
```

## 📚 Commands

| Command | Description |
|---------|-------------|
| `!captcha setup` | Initial setup wizard for the verification system |
| `!captcha test` | Test the CAPTCHA system |
| `!captcha stats` | View verification statistics |
| `!captcha settings` | Modify CAPTCHA settings |
| `!captcha reset <@user>` | Reset verification for a specific user |
| `!captcha toggle` | Enable or disable the verification system |

## 🖼️ Preview

<div align="center">
  <img src="https://via.placeholder.com/800x400" alt="Bot Preview" width="80%">
</div>

## 📊 Statistics Dashboard

Access your verification statistics through the web dashboard:
- Verification success rate
- Average completion time
- Failed verification attempts
- Raid detection events

## 🔗 Links

- [Documentation](https://github.com/yourusername/discord-captcha-bot/wiki)
- [Support Server](https://discord.gg/your-invite-link)
- [Report Bugs](https://github.com/yourusername/discord-captcha-bot/issues)

## 🔒 Security

This bot implements several security measures:
- Rate limiting to prevent brute force attempts
- IP logging for suspicious activity detection
- Regular security updates

## 📝 License

This project is licensed under a custom license - see the [LICENSE](LICENSE) file for details.

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
