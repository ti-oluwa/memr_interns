
const signInForm = document.querySelector('#signin-form');
const signInButton = signInForm.querySelector('.submit-btn');
const emailField = signInForm.querySelector('#email');
const passwordField = signInForm.querySelector('#password');


addOnPostAndOnResponseFuncAttr(signInButton, 'Signing in...');

signInForm.onsubmit = (e) => {
    e.stopImmediatePropagation();
    e.preventDefault();

    if (!isValidEmail(emailField.value)) {
        formFieldHasError(emailField.parentElement, 'Invalid email address!');
        return;
    }
    
    const formData = new FormData(signInForm);
    const data = {};
    for (const [key, value] of formData.entries()) {
        data[key] = value;
    }
    data['timezone'] = getClientTimezone();
    
    signInButton.onPost();

    const options = {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken'),
        },
        mode: 'same-origin',
        body: JSON.stringify(data),
    }

    fetch(signInForm.action, options).then((response) => {
        if (!response.ok) {
            signInButton.onResponse();
            response.json().then((data) => {
                const errors = data.errors ?? null;
                const redirectURL = data.redirect_url ?? null;

                if (errors) {
                    if (!typeof errors === Object) throw new TypeError("Invalid response type for 'errors'")

                    for (const [fieldName, msg] of Object.entries(errors)) {
                        let field = signInForm.querySelector(`input[name=${fieldName}]`);
                        if (!field) {
                            pushNotification("error", msg);
                            continue;
                        }
                        formFieldHasError(field.parentElement, msg);
                    };

                } else {
                    pushNotification("error", data.message ?? data.detail ?? 'An error occurred!');
                }
                passwordField.value = "";

                if (!redirectURL) return;
                setTimeout(() => {
                    window.location.href = redirectURL;
                }, 2000);

            });
            
        }else{
            response.json().then((data) => {
                pushNotification("success", data.message ?? data.detail ?? 'Sign in successful!');

                const responseData = data.data ?? null;
                if (!responseData) return;

                const redirectURL  = responseData.redirect_url ?? null
                if(!redirectURL) return;

                setTimeout(() => {
                    window.location.href = redirectURL;
                }, 2000);
            });
        }
    }).catch((error) => {
        signInButton.onResponse();
        pushNotification("error", error.message ?? 'An error occurred!');
    });
};
