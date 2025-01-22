const emailVerificationForm = document.querySelector('#email-verification-form');
const emailVerificationButton = emailVerificationForm.querySelector('.submit-btn');
const emailField = emailVerificationForm.querySelector('#email');

const OTPVerificationForm = document.querySelector("#otp-verification-form");
const OTPVerificationButton = OTPVerificationForm.querySelector(".submit-btn");

const passwordResetCompletionForm = document.querySelector("#password-reset-completion-form");
const passwordField1 = passwordResetCompletionForm.querySelector('#password');
const passwordField2 = passwordResetCompletionForm.querySelector('#confirm_password');
const passwordResetCompletionButton = passwordResetCompletionForm.querySelector(".submit-btn");


addOnPostAndOnResponseFuncAttr(emailVerificationButton, 'Verifying...');
addOnPostAndOnResponseFuncAttr(OTPVerificationButton, 'Verifying OTP...');
addOnPostAndOnResponseFuncAttr(passwordResetCompletionButton, 'Please wait...');

const PASSWORD_RESET_EVENT = "password_reset";


function showPasswordResetCompletionForm(completionData) {
    passwordResetCompletionForm.onsubmit = (e) => {
        e.stopImmediatePropagation();
        e.preventDefault();

        if (!validatePassword(passwordField1, passwordField2)) return;

        const formData = new FormData(passwordResetCompletionForm);
        const payload = {};
        for (const [key, value] of formData.entries()) {
            payload[key] = value;
        }

        passwordResetCompletionButton.onPost();

        const options = {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken'),
            },
            mode: 'same-origin',
            body: JSON.stringify({ ...payload, email_token: completionData['token'], token_event: PASSWORD_RESET_EVENT }),
        }

        fetch(passwordResetCompletionForm.action, options).then((response) => {
            passwordResetCompletionButton.onResponse();

            if (!response.ok) {
                response.json().then((data) => {
                    const errors = data.errors ?? null;
                    if (errors) {
                        if (!typeof errors === Object) throw new TypeError("Invalid response type for 'errors'")

                        for (const [fieldName, msg] of Object.entries(errors)) {
                            let field = passwordResetCompletionForm.querySelector(`input[name=${fieldName}]`);
                            if (!field) {
                                pushNotification("error", msg);
                                continue;
                            }
                            formFieldHasError(field.parentElement, msg);
                        };

                    } else {
                        pushNotification("error", data.message ?? data.detail ?? 'An error occurred!');
                    }
                });

            } else {
                response.json().then((data) => {
                    pushNotification("success", data.message ?? data.detail ?? 'Password reset successful!');

                    const responseData = data.data ?? null;
                    if (!responseData) return;

                    const redirectURL = responseData.redirect_url ?? null;
                    if (!redirectURL) return;

                    setTimeout(() => {
                        window.location.href = redirectURL;
                    }, 2000);
                });
            }
        }).catch((error) => {
            passwordResetCompletionButton.onResponse();
            pushNotification("error", error ?? 'An error occurred!');
        });
    };

    showFormCardOnly(passwordResetCompletionForm.parentElement);
}


function showOTPVerificationForm(verificationData) {
    OTPVerificationForm.onsubmit = (e) => {
        e.stopImmediatePropagation();
        e.preventDefault();

        const formData = new FormData(OTPVerificationForm);
        const payload = {};
        for (const [key, value] of formData.entries()) {
            payload[key] = value;
        }

        OTPVerificationButton.onPost();

        const options = {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken'),
            },
            mode: 'same-origin',
            body: JSON.stringify({ ...payload, ...verificationData }),
        }

        fetch(OTPVerificationForm.action, options).then((response) => {
            OTPVerificationButton.onResponse();

            if (!response.ok) {
                response.json().then((data) => {
                    const errors = data.errors ?? null;
                    if (errors) {
                        if (!typeof errors === Object) throw new TypeError("Invalid response type for 'errors'")

                        for (const [fieldName, msg] of Object.entries(errors)) {
                            let field = OTPVerificationForm.querySelector(`input[name=${fieldName}]`);
                            if (!field) {
                                pushNotification("error", msg);
                                continue;
                            }
                            formFieldHasError(field.parentElement, msg);
                        };

                    } else {
                        pushNotification("error", data.message ?? data.detail ?? 'An error occurred!');
                    }
                });

            } else {
                response.json().then((data) => {
                    pushNotification("success", data.message ?? data.detail ?? 'OTP verified successfully!');
                    OTPVerificationForm.reset();

                    const responseData = data.data ?? null;
                    if (!responseData) return;

                    showPasswordResetCompletionForm(responseData)
                });
            }
        }).catch((error) => {
            OTPVerificationButton.onResponse();
            pushNotification("error", error ?? 'An error occurred!');
        });
    };

    showFormCardOnly(OTPVerificationForm.parentElement);
}


emailVerificationForm.onsubmit = (e) => {
    e.stopImmediatePropagation();
    e.preventDefault();

    if (!isValidEmail(emailField.value)) {
        formFieldHasError(emailField.parentElement, 'Invalid email address!');
        return;
    }

    const formData = new FormData(emailVerificationForm);
    const payload = {};
    for (const [key, value] of formData.entries()) {
        payload[key] = value;
    }
    payload["event"] = PASSWORD_RESET_EVENT;

    emailVerificationButton.onPost();

    const options = {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken'),
        },
        mode: 'same-origin',
        body: JSON.stringify(payload),
    }

    fetch(emailVerificationForm.action, options).then((response) => {
        emailVerificationButton.onResponse();

        if (!response.ok) {
            response.json().then((data) => {
                const errors = data.errors ?? null;
                const redirectURL = data.redirect_url ?? null;

                if (errors) {
                    if (!typeof errors === Object) throw new TypeError("Invalid response type for 'errors'")

                    for (const [fieldName, msg] of Object.entries(errors)) {
                        let field = emailVerificationForm.querySelector(`input[name=${fieldName}]`);
                        if (!field) {
                            pushNotification("error", msg);
                            continue;
                        }
                        formFieldHasError(field.parentElement, msg);
                    };

                } else {
                    pushNotification("error", data.message ?? data.detail ?? 'An error occurred!');
                }

                if (!redirectURL) return;
                setTimeout(() => {
                    window.location.href = redirectURL;
                }, 2000);
            });

        } else {
            response.json().then((data) => {
                pushNotification("success", data.message ?? data.detail ?? 'Verification successful!');
                emailVerificationForm.reset();

                const responseData = data.data ?? null;
                if (!responseData) return;

                showOTPVerificationForm(responseData);
            });
        }
    }).catch((error) => {
        emailVerificationButton.onResponse();
        pushNotification("error", error ?? 'An error occurred!');
    });
};

