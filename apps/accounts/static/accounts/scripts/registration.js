const emailVerificationForm = document.querySelector('#email-verification-form');
const emailVerificationButton = emailVerificationForm.querySelector('.submit-btn');
const emailField = emailVerificationForm.querySelector('#email');

const OTPVerificationForm = document.querySelector("#otp-verification-form");
const OTPVerificationButton = OTPVerificationForm.querySelector(".submit-btn");

const registrationCompletionForm = document.querySelector("#registration-completion-form");
const imageField = registrationCompletionForm.querySelector('#image');
const passwordField1 = registrationCompletionForm.querySelector('#password');
const passwordField2 = registrationCompletionForm.querySelector('#confirm_password');
const registrationCompletionButton = registrationCompletionForm.querySelector(".submit-btn");


addOnPostAndOnResponseFuncAttr(emailVerificationButton, 'Please wait...');
addOnPostAndOnResponseFuncAttr(OTPVerificationButton, 'Verifying OTP...');
addOnPostAndOnResponseFuncAttr(registrationCompletionButton, 'Please wait...');

const REGISTRATION_EVENT = "registration";

const MAX_FILE_SIZE = 200 * 1024;


function showRegistrationCompletionForm(completionData) {
    registrationCompletionForm.onsubmit = (e) => {
        e.stopImmediatePropagation();
        e.preventDefault();

        if (!validateFileSize(imageField, MAX_FILE_SIZE)) return;
        if (!validatePassword(passwordField1, passwordField2)) return;

        const formData = new FormData(registrationCompletionForm);
        formData.append("timezone", getClientTimezone());
        formData.append('email_token', completionData["token"]);
        formData.append('token_event', REGISTRATION_EVENT);

        registrationCompletionButton.onPost();

        const options = {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
            },
            mode: 'same-origin',
            body: formData,
        }

        fetch(registrationCompletionForm.action, options).then((response) => {
            registrationCompletionButton.onResponse();

            if (!response.ok) {
                response.json().then((data) => {
                    const errors = data.errors ?? null;
                    if (errors) {
                        if (!typeof errors === Object) throw new TypeError("Invalid response type for 'errors'")

                        for (const [fieldName, msg] of Object.entries(errors)) {
                            let field = registrationCompletionForm.querySelector(`input[name=${fieldName}]`);
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
                    pushNotification("success", data.message ?? data.detail ?? 'Registration completed successful!');
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
            registrationCompletionButton.onResponse();
            pushNotification("error", error ?? 'An error occurred!');
        });
    };

    showFormCardOnly(registrationCompletionForm.parentElement);
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

                    showRegistrationCompletionForm(responseData)
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
    payload["event"] = REGISTRATION_EVENT;

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
                pushNotification("success", data.message ?? data.detail ?? 'An OTP has been sent to your email. Enter the OTP to continue.');
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


