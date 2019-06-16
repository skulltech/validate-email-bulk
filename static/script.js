// custom javascript

$(document).ready(() => {
    console.log('Sanity Check!');
});

//USAGE: $("#form").serializefiles();
(function ($) {
    $.fn.serializefiles = function () {
        var obj = $(this);
        /* ADD FILE TO PARAM AJAX */
        var formData = new FormData();
        $.each($(obj).find("input[type='file']"), function (i, tag) {
            $.each($(tag)[0].files, function (i, file) {
                formData.append(tag.name, file);
            });
        });
        var params = $(obj).serializeArray();
        $.each(params, function (i, val) {
            formData.append(val.name, val.value);
        });
        return formData;
    };
})(jQuery);

$('form').submit(function (event) {
    var formdata = $(this).serializefiles();
    console.log(formdata);
    event.preventDefault();

    var l = Ladda.create(document.querySelector('.ladda-button'));
    l.start();

    $.ajax(
        {
            url: '/process',
            data: formdata,
            method: 'POST',
            contentType: false,
            processData: false
        }
    ).done((res) => {
        getStatus(res.data.submission_id)
    }).fail((err) => {
        console.log(err)
    })
});

function getStatus(submission_id) {
    $.ajax({
        url: `/status/${submission_id}`,
        method: 'GET'
    }).done((res) => {
        let completed = res.data.completed;
        let total = res.data.total_tasks;
        console.log(total, completed);

        var l = Ladda.create(document.querySelector('.ladda-button'));
        let progress = completed / total;
        l.setProgress(progress);

        if (completed === total) {
            window.location.assign(`/download/${submission_id}`);
            l.stop();
            return false;
        }

        setTimeout(function () {
            getStatus(res.data.submission_id);
        }, 1000);
    }).fail((err) => {
        console.log(err)
    })
}