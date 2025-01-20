
const profileUpdateForm = document.querySelector('#profile-update-form');
const profileUpdateButton = profileUpdateForm.querySelector('.submit-btn');


addOnPostAndOnResponseFuncAttr(profileUpdateButton, 'Saving changes...');


profileUpdateForm.onsubmit = (e) => {
    e.stopImmediatePropagation();
    e.preventDefault();

    const formData = new FormData(profileUpdateForm);
    const data = {};
    for (const [key, value] of formData.entries()) {
        data[key] = value;
    }

    profileUpdateButton.onPost();

    const options = {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken'),
        },
        mode: 'same-origin',
        body: JSON.stringify(data),
    }

    fetch(profileUpdateForm.action, options).then((response) => {
        if (!response.ok) {
            profileUpdateButton.onResponse();
            response.json().then((data) => {
                const errors = data.errors ?? null;
                const redirectURL = data.redirect_url ?? null;

                if (errors) {
                    if (!typeof errors === Object) throw new TypeError("Invalid response type for 'errors'")

                    for (const [fieldName, msg] of Object.entries(errors)) {
                        let field = profileUpdateForm.querySelector(`input[name=${fieldName}]`);
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
                pushNotification("success", data.message ?? data.detail ?? 'Profile updated!');

                const responseData = data.data ?? null;
                if (!responseData) return;

                const redirectURL = responseData.redirect_url ?? null
                if (!redirectURL) return;

                setTimeout(() => {
                    window.location.href = redirectURL;
                }, 2000);
            });
        }
    }).catch((error) => {
        profileUpdateButton.onResponse();
        pushNotification("error", error.message ?? 'An error occurred!');
    });
};
