// 연락처 폼
const contactForm = document.getElementById('contactForm');
if (contactForm) {
    contactForm.addEventListener('submit', function(e) {
        e.preventDefault();
        alert('메시지가 전송되었습니다! (실제 구현에서는 서버로 전송됩니다)');
        this.reset();
    });
}
