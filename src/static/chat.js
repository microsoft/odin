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
        $.each(return_data.messages, function(index, value){
            console.log("value: " + value)
            // add response
            if (value.role==='user') {
                var chatHtml = '<div class="d-flex justify-content-end mb-4"><div class="msg_cotainer_send">' + value.content + '<span class="msg_time_send"></span></div><div class="img_cont_msg"><img src="/static/user.png" class="rounded-circle user_img_msg"></div></div>';
            } else {
                var chatHtml = '<div class="d-flex justify-content-start mb-4"><div class="img_cont_msg"><img src="/static/robot-assistant.png" class="rounded-circle user_img_msg"></div><div class="msg_cotainer">' + value.content + '<span class="msg_time"></span></div></div>';
            }
            $("#chatMessageForm").append($.parseHTML(chatHtml));
        });
        // scroll down
        jQuery(document).find("#chatMessageForm").scrollTop(function () { return this.scrollHeight });
    });
});

// -----------------------------------------------------------
// Basic Chat Functionality
// -----------------------------------------------------------
$(document).ready(function () {
    $("#chatMessageArea").on("submit", function (event) {
        var rawText = $("#text").val();

        // https://getbootstrap.com/docs/4.0/utilities/flex/
        // d-flex creates a flexbox container which can be modified with additional shorthand properties
        // https://getbootstrap.com/docs/4.0/utilities/flex/#justify-content
        // justify-content-end is bootstrap shorthand to change the alignment of the flex item to the right side
        // https://getbootstrap.com/docs/4.1/utilities/spacing/
        // mb-4 is bootstrap shorhand for a margin-bottom of $spacer * 1.5
        var userHtml = '<div class="d-flex justify-content-end mb-4"><div class="msg_cotainer_send">' + rawText + '<span class="msg_time_send"></span></div><div class="img_cont_msg"><img src="/static/user.png" class="rounded-circle user_img_msg"></div></div>';

        $("#text").val("");
        // The append() method inserts specified content at the end of the selected elements.
        // i.e. within the div with ID=chatMessageForm, the userHtml content will be added AS THE LAST element within the div chatMessageForm
        //      so if div chatMessageForm has 4 child divs, then this would add a 5th child div at the end of the 4 child divs  
        //      see https://www.w3schools.com/jquery/html_append.asp for demo of this
        $("#chatMessageForm").append(userHtml);

        // Thinking...
        var thinking = '<div id="fullSpinner"><div class="spinner-border text-light" role="status"><span class="visually-hidden">Thinking...</span></div><span style="color:white;padding:20px;">Thinking...</span></div>'
        $("#chatMessageForm").append(thinking);
        // scroll down
        jQuery(document).find("#chatMessageForm").scrollTop(function () { return this.scrollHeight });

        let conversationId = $("#convoDropdown option:selected").val(); // null;
        let claimId = $("#claimsDropdown option:selected").val();
        let converseUrl = conversationId
            ? `/claims/${claimId}/conversations/${conversationId}`
            : `/claims/${claimId}/conversations`;

        $.ajax({
            type: "POST",
            url: converseUrl,
            headers: {
                "Content-Type": "application/json"
            },
            dataType: "json",
            data: JSON.stringify({
                id: conversationId,
                claim_id: claimId,
                messages: [
                    {
                        content: rawText,
                        date: new Date().toISOString(),
                        role: "user"
                    }
                ]
            })
        }).done(function (data) {
            // removing thinking
            $("#fullSpinner").remove();
            // add response
            var botHtml = '<div class="d-flex justify-content-start mb-4"><div class="img_cont_msg"><img src="/static/robot-assistant.png" class="rounded-circle user_img_msg"></div><div class="msg_cotainer">' + data.messages[data.messages.length - 1].content + '<span class="msg_time"></span></div></div>';
            $("#chatMessageForm").append($.parseHTML(botHtml));
            // scroll down
            jQuery(document).find("#chatMessageForm").scrollTop(function () { return this.scrollHeight });
        });
        
        event.preventDefault();
    });
});

// -----------------------------------------------------------
// Screen Updates - New Claim Selected
// -----------------------------------------------------------
$(document).ready(function () {
    $("#claimsDropdown").on("change", function (event) {

        let claimId = $("#claimsDropdown option:selected").val();
        let getConvosUrl = `/claims/${claimId}/conversations`;

        $.ajax({
            type: "GET",
            url: getConvosUrl,
            headers: {
                "Content-Type": "application/json"
            },
            dataType: "json",
            data: JSON.stringify({
                claim_id: claimId,
            })
        }).done(function (return_data) {
            // console.log("return_data: " + JSON.stringify(return_data))
            // Swap out old convo options for new ones
            $("#convoDropdown").empty();
            $.each(return_data, function(index, value){
                var optHtml = '<option value='+value.id+'> '+value.id+' </option>'
                $("#convoDropdown").append($.parseHTML(optHtml));
            });
            // clear our the chat message area
            $("#chatMessageForm").empty();
            // add the new messages for the first convo
            $.each(return_data[0].messages, function(index, value){
                // add response
                if (value.role==='user') {
                    var chatHtml = '<div class="d-flex justify-content-end mb-4"><div class="msg_cotainer_send">' + value.content + '<span class="msg_time_send"></span></div><div class="img_cont_msg"><img src="/static/user.png" class="rounded-circle user_img_msg"></div></div>';
                } else {
                    var chatHtml = '<div class="d-flex justify-content-start mb-4"><div class="img_cont_msg"><img src="/static/robot-assistant.png" class="rounded-circle user_img_msg"></div><div class="msg_cotainer">' + value.content + '<span class="msg_time"></span></div></div>';
                }
                $("#chatMessageForm").append($.parseHTML(chatHtml));
            });
            // scroll down
            jQuery(document).find("#chatMessageForm").scrollTop(function () { return this.scrollHeight });
        });
        
        event.preventDefault();
    });
});


// -----------------------------------------------------------
// Screen Updates - New Conversation Selected
// -----------------------------------------------------------
$(document).ready(function () {
    $("#convoDropdown").on("change", function (event) {

        let claimId = $("#claimsDropdown option:selected").val();
        let convoId = $("#convoDropdown option:selected").val();
        let getConvoUrl = `/claims/${claimId}/conversations/${convoId}`;

        $.ajax({
            type: "GET",
            url: getConvoUrl,
            headers: {
                "Content-Type": "application/json"
            },
            dataType: "json",
            data: JSON.stringify({
                claim_id: claimId,
                conversation_id: convoId,
            })
        }).done(function (return_data) {
            console.log("return_data: " + JSON.stringify(return_data))
            // clear our the chat message area
            $("#chatMessageForm").empty();
            // add the new messages for the selected
            $.each(return_data.messages, function(index, value){
                // console.log("value: " + value)
                // add response
                if (value.role==='user') {
                    var chatHtml = '<div class="d-flex justify-content-end mb-4"><div class="msg_cotainer_send">' + value.content + '<span class="msg_time_send"></span></div><div class="img_cont_msg"><img src="/static/user.png" class="rounded-circle user_img_msg"></div></div>';
                } else {
                    var chatHtml = '<div class="d-flex justify-content-start mb-4"><div class="img_cont_msg"><img src="/static/robot-assistant.png" class="rounded-circle user_img_msg"></div><div class="msg_cotainer">' + value.content + '<span class="msg_time"></span></div></div>';
                }
                $("#chatMessageForm").append($.parseHTML(chatHtml));
            });
            // scroll down
            jQuery(document).find("#chatMessageForm").scrollTop(function () { return this.scrollHeight });
        });
        
        event.preventDefault();
    });
});