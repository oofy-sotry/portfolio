// 로그인 폼
const loginForm = document.getElementById('login-form');
if (loginForm) {
    loginForm.addEventListener('submit', function(e) {
        e.preventDefault();

        const formData = new FormData(this);
        const data = {
            username: formData.get('username'),
            password: formData.get('password')
        };

        fetch('/auth/login', {
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
        .catch(() => alert('로그인 중 오류가 발생했습니다.'));
    });
}

// 회원가입 폼
const registerForm = document.getElementById('register-form');
if (registerForm) {
    registerForm.addEventListener('submit', function(e) {
        e.preventDefault();

        const formData = new FormData(this);
        const data = {
            username: formData.get('username'),
            email: formData.get('email'),
            password: formData.get('password'),
            confirm_password: formData.get('confirm_password')
        };

        if (data.password !== data.confirm_password) {
            alert('비밀번호가 일치하지 않습니다.');
            return;
        }

        if (data.password.length < 8) {
            alert('비밀번호는 8자 이상이어야 합니다.');
            return;
        }

        if (!data.username.match(/^[a-zA-Z0-9_]{3,20}$/)) {
            alert('사용자명은 3-20자의 영문, 숫자, 언더스코어만 사용 가능합니다.');
            return;
        }

        fetch('/auth/register', {
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
        .catch(() => alert('회원가입 중 오류가 발생했습니다.'));
    });
}
