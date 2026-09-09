// Hàm gọi HTTP đến n8n webhook, xử lý retry/timeout
const axios = require('axios');
const config = require('../config');

async function sendToN8n(data) {
  try {
    const response = await axios.post(config.N8N_WEBHOOK_URL, data);
    return response.data;
  } catch (error) {
    console.error('Lỗi khi gọi n8n webhook:', error);
    throw error;
  }
}

module.exports = { sendToN8n };
