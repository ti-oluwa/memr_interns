
const profileUpdateForm = document.querySelector('#profile-update-form');
const imageField = profileUpdateForm.querySelector('#image');
const profileUpdateButton = profileUpdateForm.querySelector('.submit-btn');


addOnPostAndOnResponseFuncAttr(profileUpdateButton, 'Saving changes...');

const MAX_FILE_SIZE = 200 * 1024;

profileUpdateForm.onsubmit = (e) => {
    e.stopImmediatePropagation();
    e.preventDefault();

    if (!validateFileSize(imageField, MAX_FILE_SIZE)) return;

    const formData = new FormData(profileUpdateForm);
    profileUpdateButton.onPost();
    
    const options = {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
        },
        mode: 'same-origin',
        body: formData,
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
