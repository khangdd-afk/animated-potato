// Đọc biến môi trường (token, webhook URL...)
require('dotenv').config();

module.exports = {
  BOT_TOKEN: process.env.BOT_TOKEN,
  N8N_WEBHOOK_URL: process.env.N8N_WEBHOOK_URL,
  ALLOWED_CHANNEL_ID: process.env.ALLOWED_CHANNEL_ID,
};
