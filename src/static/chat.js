// Main Chat

// Basic Chat Functionality
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

        let conversationId = null;
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
                conversation_id: conversationId,
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
            var botHtml = '<div class="d-flex justify-content-start mb-4"><div class="img_cont_msg"><img src="/static/robot-assistant.png" class="rounded-circle user_img_msg"></div><div class="msg_cotainer">' + data + '<span class="msg_time"></span></div></div>';
            $("#chatMessageForm").append($.parseHTML(botHtml));
            // scroll down
            jQuery(document).find("#chatMessageForm").scrollTop(function () { return this.scrollHeight });
        });
        event.preventDefault();
    });
});
