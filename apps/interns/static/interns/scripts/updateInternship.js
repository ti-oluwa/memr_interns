
const internshipUpdateForm = document.querySelector('#internship-update-form');
const internshipUpdateButton = internshipUpdateForm.querySelector('.submit-btn');


addOnPostAndOnResponseFuncAttr(internshipUpdateButton, 'Saving changes...');


internshipUpdateForm.onsubmit = (e) => {
    e.stopImmediatePropagation();
    e.preventDefault();

    const formData = new FormData(internshipUpdateForm);
    const data = {};
    for (const [key, value] of formData.entries()) {
        data[key] = value;
    }
    let duration = data.duration ?? null;
    if (duration){
        data['duration'] = data['duration'] + ' ' + 'days';
    }

    internshipUpdateButton.onPost();

    const options = {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken'),
        },
        mode: 'same-origin',
        body: JSON.stringify(data),
    }

    fetch(internshipUpdateForm.action, options).then((response) => {
        if (!response.ok) {
            internshipUpdateButton.onResponse();
            response.json().then((data) => {
                const errors = data.errors ?? null;
                const redirectURL = data.redirect_url ?? null;

                if (errors) {
                    if (!typeof errors === Object) throw new TypeError("Invalid response type for 'errors'")

                    for (const [fieldName, msg] of Object.entries(errors)) {
                        let field = internshipUpdateForm.querySelector(`input[name=${fieldName}]`);
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
                pushNotification("success", data.message ?? data.detail ?? 'Internship details updated!');

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
        internshipUpdateButton.onResponse();
        pushNotification("error", error.message ?? 'An error occurred!');
    });
};
