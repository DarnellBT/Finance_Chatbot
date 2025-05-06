$(document).ready(() => {
    $('#chat-form').on('submit', event => {
        let userQuery = $('#text-box').val();
        $.ajax({
            data: {
                userQuery: userQuery
            },
            type: 'POST',
            url: '/process'
        }).done(data => {
            if (data.error) {
                alert(data.error);
            } else if (data.answer) {
                $('#chat-window').prepend(`
                    <div class="d-flex flex-row justify-content-start mb-4">
                      <img src="/static/bot_icon.webp" alt="bot avatar" />
                      <div class="bot-chat-bubble p-3 ms-3">
                        <p class="small mb-0">
                            ${data.answer}
                        </p>
                      </div>
                    </div>    
                    <div class="d-flex flex-row justify-content-end mb-4">
                      <div class="user-chat-bubble p-3 me-3 border bg-body-tertiary">
                        <p class="small mb-0">
                            ${userQuery}
                        </p>
                      </div>
                      <img src="/static/user_icon.webp" alt="user avatar" />
                    </div>
                `);
            } else {
                alert('No valid response.');
            }
        });
        event.target.reset();
        event.preventDefault();
    });

    $('#login-form').on('submit', event => {
        let username = $('#login-username').val();
        let password = $('#login-password').val();
        $.ajax({
            data: {
                username: username,
                password: password
            },
            type: 'POST',
            url: '/login'
        }).done(data => {
            if (data.error) {
                alert(data.error);
            } else if (data.success) {
                let login_div = $('#login-div');
                login_div.hide();
                if (data.history) {
                    data.history.forEach(queryAndAnswer => {
                        if (queryAndAnswer.answer && queryAndAnswer.userQuery)
                            $('#chat-window').prepend(`
                            <div class="d-flex flex-row justify-content-start mb-4">
                              <img src="/static/bot_icon.webp" alt="bot avatar" />
                              <div class="bot-chat-bubble p-3 ms-3">
                                <p class="small mb-0">
                                    ${queryAndAnswer.answer}
                                </p>
                              </div>
                            </div>    
                            <div class="d-flex flex-row justify-content-end mb-4">
                              <div class="user-chat-bubble p-3 me-3 border bg-body-tertiary">
                                <p class="small mb-0">
                                    ${queryAndAnswer.userQuery}
                                </p>
                              </div>
                              <img src="/static/user_icon.webp" alt="user avatar" />
                            </div>
                        `);
                    });
                }
                login_div.prev().removeClass('disabled');
            } else {
                alert('No valid response.');
            }
        });
        event.target.reset();
        event.preventDefault();
    });
});
