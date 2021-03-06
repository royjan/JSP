$('.flexdatalist').flexdatalist({
    minLength: 2,
    searchByWord: true
});

function copyToClipboard(element) {
    let $temp = $("<input>");
    $("body").append($temp);
    $temp.val($(element).text()).select();
    document.execCommand("copy");
    $temp.remove();
}

$(function () {
    $("#reset-button").click(function () {
        $('#part_name').val('').parent().find("ul.flexdatalist-multiple li.value").remove();
    });
});

function init()
{
   MyOption();
   //Any other functions to be called upon page load go here
}

function MyOption() {
    let value = $('#search-box').val();
    switch (value) {
    case 'mkt':
        $('#mktform').show();
        $('#itemsform').hide();
        $('#thbrform').hide();
        break;
    case 'items':
        $('#mktform').hide();
        $('#thbrform').hide();
        $('#itemsform').show();
        break;
    default:
        $('#mktform').hide();
        $('#thbrform').show();
        $('#itemsform').hide();
        break;
    }
}

function safeParse(data) {
    try {
        data = JSON.parse(data);
        return data
    } catch (e) {
        return data
    }
}


jQuery.ajaxSetup({async: false});

function submitMkt() {
    document.getElementById("mktform").submit();
}

function submitThbr() {
    document.getElementById("thbrform").submit();
}

function resetBtn() {
   document.getElementById("mktform").reset();
   document.getElementById("itemsform").reset();
   document.getElementById("thbrform").reset();
   window.history.replaceState(null, null, window.location.pathname);
}

function submitItems() {
    let vin = document.getElementById('vin').value;
    let license_plate = document.getElementById('license_plate').value;
    let parts_name = document.getElementById('part_name').value;
    let parts = document.getElementById('part_name').value.split(",");
    parts = parts.filter(value => value.startsWith("טיפול"));
    for (let index = 0; index < parts.length; index++) {
        let data = $.ajax({
            async: false,
            type: 'GET',
            contentType: 'application/json',
            data: {"name": parts[index]},
            dataType: 'json',
            cache: false,
            url: '/get_parts_by_kit'
        }).responseText;
        data = safeParse(data);
        $('#part_name').val($("#part_name").val().replace(parts[index], data.parts));
    }
    let change;
    if (!license_plate && !vin) {
        alert("עליך להזין מס' רישוי או מס' שלדה");
        return;
    }
    if (!parts_name) {
        alert("עליך להזין פריטים");
        return;
    } else if (license_plate && vin) {
        let all_vins = $.map($('#vins option'), function (e) {
            return e.value;
        });
        let all_license_plates = $.map($('#license_plates option'), function (e) {
            return e.value;
        });
        if (all_vins.includes(vin.toUpperCase()) || all_license_plates.includes(license_plate.toUpperCase())) {
            let data = $.ajax({
                async: false,
                type: 'GET',
                contentType: 'application/json',
                data: {"vin": vin},
                dataType: 'json',
                cache: false,
                url: '/get_license_number'
            }).responseText;
            data = safeParse(data);
            if (data.license_number !== license_plate) {
                change = confirm("להחליף " + data.license_number + " עם " + license_plate + " ?");
                if (change) {
                    $('#license_plate').val(license_plate)
                } else {
                    $('#license_plate').val(data.license_number)
                }
            }
        }
    }
    document.getElementById("itemsform").submit();
}

