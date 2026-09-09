// Cắt tin nhắn dài (Discord giới hạn 2000 ký tự)
module.exports = function chunkMessage(text, maxLength = 2000) {
  if (text.length <= maxLength) return [text];
  const chunks = [];
  while (text.length > 0) {
    chunks.push(text.substring(0, maxLength));
    text = text.substring(maxLength);
  }
  return chunks;
};
