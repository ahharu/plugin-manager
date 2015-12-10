$(document).ready(function () {

    $(".item").find(".form-group").addClass('col-lg-5');
    $(".item").find(".controls").addClass('col-lg-10');
    $(".item").find(".control-label").addClass('col-lg-2');
    $("input[id='id_password']").attr('type','password');

    // Code adapted from http://djangosnippets.org/snippets/1389/
    function updateElementIndex(el, prefix, ndx) {
        var id_regex = new RegExp('(' + prefix + '-\\d+-)');
        var replacement = prefix + '-' + ndx + '-';
        if ($(el).attr("for")) $(el).attr("for", $(el).attr("for").replace(id_regex,
        replacement));
        if (el.id) el.id = el.id.replace(id_regex, replacement);
        if (el.name) el.name = el.name.replace(id_regex, replacement);
    }

    function deleteForm(btn, prefix) {
        var formCount = parseInt($('#id_' + prefix + '-TOTAL_FORMS').val());
        if (formCount > 1) {
            // Delete the item/form
            $(btn).parents('.item').remove();
            var forms = $('.item'); // Get all the forms
            // Update the total number of forms (1 less than before)
            $('#id_' + prefix + '-TOTAL_FORMS').val(forms.length);
            var i = 0;
            // Go through the forms and set their indices, names and IDs
            for (formCount = forms.length; i < formCount; i++) {
                $(forms.get(i)).children().children().children().children().each(function () {
                    updateElementIndex(this, prefix, i);
                });
            }
        } // End if
        else {
            alert("At least one log path must be set");
        }
        return false;
    }

    function addForm(btn, prefix) {
        var formCount = parseInt($('#id_' + prefix + '-TOTAL_FORMS').val());
        // You can only submit a maximum of 10 todo items
        if (formCount < 999) {
            // Clone a form (without event handlers) from the first form
            var row = $(".item:first").clone(false).get(0);
            // Insert it after the last form
            $(row).removeAttr('id').hide().insertAfter(".item:last").slideDown(300);

            // Remove the bits we don't want in the new row/form
            // e.g. error messages
            $(".errorlist", row).remove();
            $(row).children().children().removeClass("error");
            $(row).children().children().removeClass("has-error");



            // Relabel or rename all the relevant bits
            $(row).children().children().each(function () {
                updateElementIndex(this, prefix, formCount);
                $(this).val("");
            });

            $(row).children().children().children().find('input').each(function () {
                updateElementIndex(this, prefix, formCount);
                $(this).val("");
            });

            $(row).children().children().children().each(function () {
                updateElementIndex(this, prefix, formCount);
            });

            $(row).children().children().children().children().each(function () {
                updateElementIndex(this, prefix, formCount);
            });

            // Add an event handler for the delete item/form link
            $(row).find(".delete").click(function () {
                return deleteForm(this, prefix);
            });
            // Update the total form count
            $("#id_" + prefix + "-TOTAL_FORMS").val(formCount + 1);
        } // End if
        else {
            alert("Sorry, you can only enter a maximum of ten items.");
        }
        return false;
    }
    // Register the click event handlers
    $("#add").click(function () {
        return addForm(this, "form");
    });

    $(".delete").click(function () {
        return deleteForm(this, "form");
    });
});
