// Khởi tạo client, đăng nhập bot, đăng ký intents
const { Client, GatewayIntentBits } = require('discord.js');
const config = require('./config');

const client = new Client({
  intents: [
    GatewayIntentBits.Guilds,
    GatewayIntentBits.GuildMessages,
    GatewayIntentBits.MessageContent,
    GatewayIntentBits.GuildMembers, // Quan trọng: Yêu cầu bật Server Members Intent trên Discord Developer Portal
  ],
});

const guildMemberAddHandler = require('./handlers/guildMemberAdd');

client.once('ready', () => {
  console.log(`Bot đã sẵn sàng! Đăng nhập dưới tên ${client.user.tag}`);
});

client.on('guildMemberAdd', guildMemberAddHandler);

client.login(config.BOT_TOKEN);
