// ------------------------------------------------------------------------------------------------------------------------
// Chat.js
// ------------------------------------------------------------------------------------------------------------------------

// -----------------------------------------------------------
// Initial Screen Load - Get First Chat Selected
// -----------------------------------------------------------
$(document).ready(function () {
    // Initial Chat Load
    let claimIdFrst = $("#claimsDropdown option:first").val();
    let convoIdFrst = $("#convoDropdown option:first").val();

    if (convoIdFrst === "") // if the first conversation is blank, no need to load anything
        return;

    let getConvoUrl = `/claims/${claimIdFrst}/conversations/${convoIdFrst}`;

    $.ajax({
        type: "GET",
        url: getConvoUrl,
        headers: {
            "Content-Type": "application/json"
        },
        dataType: "json",
        data: JSON.stringify({
            claim_id: claimIdFrst,
            conversation_id: convoIdFrst,
        })
    }).done(function (return_data) {

        // add the new messages for the first convo
        $.each(return_data.messages, function (index, value) {
            console.log("value: " + value)
            // add response
            if (value.role === 'user') {
                var chatHtml = '<div class="d-flex justify-content-end mb-4"><div class="msg_cotainer_send">' + value.content + '<span class="msg_time_send"></span></div><div class="img_cont_msg"><img src="/static/user.png" class="rounded-circle user_img_msg"></div></div>';
            } else {
                var chatHtml = '<div class="d-flex justify-content-start mb-4"><div class="img_cont_msg"><img src="/static/robot-assistant.png" class="rounded-circle user_img_msg"></div><div class="msg_cotainer">' + value.content + '<span class="msg_time"></span></div></div>';
            }
            $("#chatMessageForm").append($.parseHTML(chatHtml));
        });
        // scroll down
        jQuery(document).find("#chatMessageForm").scrollTop(function () { return this.scrollHeight });
    }).fail((jqXHR, textStatus, errorThrown) => {
        let requestId = appInsights.context.telemetryTrace.traceID;
        alert(`An error occurred while retrieving the conversations.
                RequestId: ${requestId}
                Status: ${textStatus}
                Error: ${errorThrown}`);
    });
});

$(document).ready(function () {
    function resetChat() {
        $("#send").prop("disabled", true);
        $("#chatMessageForm").empty();
        $("#text").empty();
    }

    function createMessageHtml(message) {
        return message.role === 'user'
            ? '<div class="d-flex justify-content-end mb-4"><div class="msg_cotainer_send">' + message.content + '<span class="msg_time_send"></span></div><div class="img_cont_msg"><img src="/static/user.png" class="rounded-circle user_img_msg"></div></div>'
            : '<div class="d-flex justify-content-start mb-4"><div class="img_cont_msg"><img src="/static/robot-assistant.png" class="rounded-circle user_img_msg"></div><div class="msg_cotainer">' + message.content + '<span class="msg_time"></span></div></div>';
    }

    function loadConversation(conversation) {
        $("#chatMessageForm").empty();
        conversation.messages.forEach(message => {
            $("#chatMessageForm").append(createMessageHtml(message));
        });
        jQuery(document).find("#chatMessageForm").scrollTop(function () { return this.scrollHeight });
    }

    // need to handle on change for the claims dropdown
    function onClaimSelect(event, callback) {
        // get the selected claim id
        let claimId = $("#claimsDropdown option:selected").val();

        // reset chat
        $("#send").prop("disabled", true);
        resetChat();


        // get the latest conversations for the selected claim
        // $.get(`/claims/${claimId}/conversations`)

        $.ajax({
            type: "GET",
            url: `/claims/${claimId}/conversations`,
            dataType: "json"
        })
            .done((conversations) => {
                // clear out the conversation dropdown
                $("#convoDropdown").empty();
                // add create new option
                $("#convoDropdown").append($.parseHTML('<option value=""> ** new conversation ** </option>'));
                // load api results into the conversation dropdown
                $.each(conversations, function (index, value) {
                    var optHtml = '<option value=' + value.id + '> ' + value.id + ' </option>'
                    $("#convoDropdown").append($.parseHTML(optHtml));
                });
            }).fail((jqXHR, textStatus, errorThrown) => {
                let requestId = appInsights.context.telemetryTrace.traceID;
                alert(`An error occurred while retrieving the conversations.
                        RequestId: ${requestId}
                        Status: ${textStatus}
                        Error: ${errorThrown}`);
            }).always(() => {
                // enable submission button
                $("#send").prop("disabled", false);
                if (callback)
                    callback();
            });

        if (event)
            event.preventDefault();
    }

    // need to handle on change for the conversation dropdown
    function onConversationSelect(event) {
        // get the selected claim id
        let claimId = $("#claimsDropdown option:selected").val();
        // get the selected conversation id
        let convoId = $("#convoDropdown option:selected").val();

        // if the conversation id is blank, do nothing - it means we've selected to create a new conversation
        if (convoId === "") {
            $("#send").prop("disabled", true);
            sessionStorage.removeItem("conversation");
            resetChat();
            return;
        }

        // get the conversation details
        // $.get(`/claims/${claimId}/conversations/${convoId}`)
        $.ajax({
            type: "GET",
            url: `/claims/${claimId}/conversations/${convoId}`,
            dataType: "json"
        })
            .done((conversation) => {
                // load the conversation into the chat
                sessionStorage.setItem("conversation", JSON.stringify(conversation));
                loadConversation(conversation);
            }).fail((jqXHR, textStatus, errorThrown) => {
                let requestId = appInsights.context.telemetryTrace.traceID;
                alert(`An error occurred while retrieving the conversations.
                        RequestId: ${requestId}
                        Status: ${textStatus}
                        Error: ${errorThrown}`);
            }).always(() => {
                // enable submission button
                $("#send").prop("disabled", false);
            });

        if (event)
            event.preventDefault();
    }

    // need to handle on submit for the chatMessageArea
    function submitChat(event) {
        // display current message and spinner while waiting for api response
        var latestMessage = { content: $("#text").val(), role: 'user', date: new Date().toISOString() };
        var userHtml = createMessageHtml(latestMessage);
        $("#text").val("");
        $("#chatMessageForm").append(userHtml);
        var thinking = '<div id="fullSpinner"><div class="spinner-border text-light" role="status"><span class="visually-hidden">Thinking...</span></div><span style="color:white;padding:20px;">Thinking...</span></div>'
        $("#chatMessageForm").append(thinking);
        jQuery(document).find("#chatMessageForm").scrollTop(function () { return this.scrollHeight });
        $("#send").prop("disabled", true);

        let conversation = sessionStorage.getItem("conversation");
        if (conversation) {
            conversation = JSON.parse(conversation);
            conversation.messages.push(latestMessage);
        } else {
            conversation = {
                claim_id: $("#claimsDropdown option:selected").val(),
                messages: [
                    latestMessage
                ]
            };
        }

        let claimId = $("#claimsDropdown option:selected").val();
        let conversationId = $("#convoDropdown option:selected").val();
        let converseUrl = conversationId === "" ? `/claims/${claimId}/conversations` : `/claims/${claimId}/conversations/${conversationId}`;

        if (conversationId !== "") {
            conversation.id = conversationId;
        }

        delete conversation.user_id;
        delete conversation.user_group_id;

        $.ajax({
            type: "POST",
            url: converseUrl,
            headers: {
                "Content-Type": "application/json"
            },
            dataType: "json",
            data: JSON.stringify(conversation)
        }).done(function (data) {
            if (conversationId === "") {
                onClaimSelect(null, () => {
                    $("#convoDropdown").val(data.id).change();
                });
            }
            conversation = data;
            delete conversation.user_id;
            delete conversation.user_group_id;
            sessionStorage.setItem("conversation", JSON.stringify(conversation));
            loadConversation(data);
        }).fail((jqXHR, textStatus, errorThrown) => {
            let requestId = appInsights.context.telemetryTrace.traceID;
            alert(`An error occurred while retrieving the conversations.
                    RequestId: ${requestId}
                    Status: ${textStatus}
                    Error: ${errorThrown}`);
        }).always(() => {
            $("#fullSpinner").remove();
            $("#send").prop("disabled", false);
        });

        if (event)
            event.preventDefault();
    }

    $("#chatMessageArea").on("submit", submitChat);
    $("#claimsDropdown").on("change", onClaimSelect);
    $("#convoDropdown").on("change", onConversationSelect);
});
