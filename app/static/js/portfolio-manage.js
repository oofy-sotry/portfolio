// 초기 경력 인덱스
const expCountEl = document.getElementById('experience_count');
let experienceIndex = expCountEl ? parseInt(expCountEl.value, 10) : 0;

// 경력 추가
function addExperience() {
    const container = document.getElementById('experiences');
    const div = document.createElement('div');
    div.className = 'experience-item border p-3 mb-3 rounded';
    div.innerHTML = `
        <div class="d-flex justify-content-between align-items-center mb-3">
            <h6 class="mb-0">경력 ${experienceIndex + 1}</h6>
            <button type="button" class="btn btn-sm btn-outline-danger" onclick="removeExperience(this)">
                <i class="fas fa-trash"></i>
            </button>
        </div>
        <div class="row">
            <div class="col-md-6 mb-3">
                <label class="form-label">제목</label>
                <input type="text" class="form-control" name="exp_title_${experienceIndex}" required>
            </div>
            <div class="col-md-6 mb-3">
                <label class="form-label">기간</label>
                <input type="text" class="form-control" name="exp_period_${experienceIndex}" required>
            </div>
        </div>
        <div class="mb-3">
            <label class="form-label">설명</label>
            <textarea class="form-control" name="exp_description_${experienceIndex}" rows="3" required></textarea>
        </div>
        <div class="mb-3">
            <label class="form-label">사용 기술</label>
            <div class="technologies-input">
                <div class="input-group mb-2">
                    <input type="text" class="form-control" name="exp_technologies_${experienceIndex}">
                    <button type="button" class="btn btn-outline-danger" onclick="removeTech(this)">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
            </div>
            <button type="button" class="btn btn-sm btn-outline-secondary" onclick="addTech(this)">
                <i class="fas fa-plus"></i> 기술 추가
            </button>
        </div>
    `;
    container.appendChild(div);
    experienceIndex++;
    updateExperienceCount();
}

// 경력 제거
function removeExperience(button) {
    button.closest('.experience-item').remove();
    updateExperienceCount();
}

// 경력 수 업데이트
function updateExperienceCount() {
    const count = document.querySelectorAll('.experience-item').length;
    if (expCountEl) expCountEl.value = count;
}

// 기술 추가 (경력 내)
function addTech(button) {
    const container = button.previousElementSibling;
    const div = document.createElement('div');
    div.className = 'input-group mb-2';
    const nameAttr = container.querySelector('input').getAttribute('name');
    div.innerHTML = `
        <input type="text" class="form-control" name="${nameAttr}">
        <button type="button" class="btn btn-outline-danger" onclick="removeTech(this)">
            <i class="fas fa-times"></i>
        </button>
    `;
    container.appendChild(div);
}

// 기술 제거 (경력 내)
function removeTech(button) {
    button.parentElement.remove();
}
