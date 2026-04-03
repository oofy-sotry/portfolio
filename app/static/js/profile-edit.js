// 기술 스택 추가
function addSkill(category) {
    const container = document.getElementById(category + '-skills');
    const div = document.createElement('div');
    div.className = 'input-group mb-2';
    div.innerHTML = `
        <input type="text" class="form-control" name="${category}_skills" placeholder="기술명 입력">
        <button type="button" class="btn btn-outline-danger" onclick="removeSkill(this)">
            <i class="fas fa-times"></i>
        </button>
    `;
    container.appendChild(div);
}

// 기술 스택 제거
function removeSkill(button) {
    button.parentElement.remove();
}

// 이미지 미리보기
function previewImage(input) {
    if (input.files && input.files[0]) {
        const reader = new FileReader();
        reader.onload = function(e) {
            document.getElementById('previewImg').src = e.target.result;
            document.getElementById('imagePreview').style.display = 'block';
        };
        reader.readAsDataURL(input.files[0]);
    }
}

// 현재 이미지 삭제
function deleteCurrentImage() {
    if (confirm('현재 프로필 이미지를 삭제하시겠습니까?')) {
        fetch('/profile/delete-image', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('이미지가 삭제되었습니다.');
                location.reload();
            } else {
                alert('이미지 삭제 중 오류가 발생했습니다: ' + data.message);
            }
        })
        .catch(() => alert('이미지 삭제 중 오류가 발생했습니다.'));
    }
}

// URL 형식 검증
function isValidUrl(string) {
    if (!string || string.trim() === '') return true;
    try {
        const url = new URL(string);
        return url.protocol === 'http:' || url.protocol === 'https:';
    } catch (_) {
        return false;
    }
}

// 폼 제출 시 검증
const profileForm = document.getElementById('profileForm');
if (profileForm) {
    profileForm.addEventListener('submit', function(e) {
        const profileImageUrl = document.getElementById('profile_image_url').value.trim();
        const website = document.getElementById('website').value.trim();

        if (profileImageUrl && !isValidUrl(profileImageUrl)) {
            e.preventDefault();
            alert('프로필 이미지 URL이 올바른 형식이 아닙니다. (http:// 또는 https://로 시작해야 합니다)');
            document.getElementById('profile_image_url').focus();
            return false;
        }

        if (website && !isValidUrl(website)) {
            e.preventDefault();
            alert('웹사이트 URL이 올바른 형식이 아닙니다. (http:// 또는 https://로 시작해야 합니다)');
            document.getElementById('website').focus();
            return false;
        }
    });
}
