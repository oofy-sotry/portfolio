// 게시글 작성/수정 공통 폼 처리
const boardForm = document.getElementById('board-form');
if (boardForm) {
    const actionUrl = boardForm.dataset.actionUrl;

    boardForm.addEventListener('submit', function(e) {
        e.preventDefault();

        const formData = new FormData(this);
        const data = {
            title: formData.get('title'),
            content: formData.get('content'),
            category_id: parseInt(formData.get('category_id')),
            tags: formData.get('tags')
        };

        if (!data.title.trim()) {
            alert('제목을 입력해주세요.');
            return;
        }
        if (!data.content.trim()) {
            alert('내용을 입력해주세요.');
            return;
        }
        if (!data.category_id) {
            alert('카테고리를 선택해주세요.');
            return;
        }

        fetch(actionUrl, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                alert(data.error);
            } else {
                alert(data.message);
                window.location.href = data.redirect;
            }
        })
        .catch(() => alert('게시글 처리 중 오류가 발생했습니다.'));
    });
}
