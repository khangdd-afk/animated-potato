const { sendToN8n } = require('../services/n8nClient');

module.exports = async (member) => {
  console.log(`Thành viên mới tham gia: ${member.user.tag} (ID: ${member.user.id})`);
  
  try {
    // Gửi thông tin thành viên mới sang n8n Webhook Onboarding
    await sendToN8n({
      userId: member.user.id,
      username: member.user.username,
      tag: member.user.tag,
      guildId: member.guild.id
    });
    console.log(`Đã gửi sự kiện join của ${member.user.tag} sang n8n thành công.`);
  } catch (error) {
    console.error('Lỗi khi gửi sự kiện join sang n8n:', error.message);
  }
};
