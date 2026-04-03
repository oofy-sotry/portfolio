// data-* 속성에서 값 읽기
const postDetail = document.getElementById('post-detail');
const postId = postDetail ? postDetail.dataset.postId : null;
const relatedApiUrl = postDetail ? postDetail.dataset.relatedUrl : null;

// 좋아요 토글
function toggleLike(id) {
    fetch(`/board/${id}/like`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            alert(data.error);
        } else {
            document.getElementById('like-count').textContent = data.like_count;
        }
    })
    .catch(error => console.error('Error:', error));
}

// 댓글 작성
const commentForm = document.getElementById('comment-form');
if (commentForm && postId) {
    commentForm.addEventListener('submit', function(e) {
        e.preventDefault();

        const formData = new FormData(this);
        const content = formData.get('content');

        if (!content.trim()) {
            alert('댓글 내용을 입력해주세요.');
            return;
        }

        fetch(`/board/${postId}/comment`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ content: content })
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                alert(data.error);
            } else {
                location.reload();
            }
        })
        .catch(error => console.error('Error:', error));
    });
}

// 게시글 삭제
function deletePost(id) {
    if (confirm('정말로 이 게시글을 삭제하시겠습니까?')) {
        fetch(`/board/${id}/delete`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                alert(data.error);
            } else {
                window.location.href = '/board/';
            }
        })
        .catch(error => console.error('Error:', error));
    }
}

// 댓글 삭제
function deleteComment(commentId) {
    if (confirm('정말로 이 댓글을 삭제하시겠습니까?')) {
        alert('댓글 삭제 기능은 구현 중입니다.');
    }
}

// 관련 글 로드
if (relatedApiUrl && postId) {
    fetch(`${relatedApiUrl}?id=post-${postId}`)
        .then(r => r.json())
        .then(docs => {
            const container = document.getElementById('relatedDocs');
            if (!container) return;
            if (docs.length === 0) {
                container.innerHTML = '<p class="text-muted mb-0">관련 글이 없습니다.</p>';
                return;
            }
            container.innerHTML = docs.map(doc => {
                const src = doc._source || {};
                const pid = src.post_id;
                const title = src.title || '제목 없음';
                const link = pid ? `/board/${pid}` : '#';
                return `<a href="${link}" class="d-block text-decoration-none mb-2">${title}</a>`;
            }).join('');
        })
        .catch(() => {
            const container = document.getElementById('relatedDocs');
            if (container) {
                container.innerHTML = '<p class="text-muted mb-0">관련 글을 불러올 수 없습니다.</p>';
            }
        });
}
