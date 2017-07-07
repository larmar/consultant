/*odoo.define('website_consultant', function(require) {

'use strict';
var base = require('web_editor.base');
require('website.website');

$('.oe_website_consultant #confirm_submit').click(function (event) {
        var $form = $(this).closest('form');
        
        event.preventDefault();
        ajax.jsonRpc("/my/consultants/terms", 'call', {
                'kwargs': {
                   'context': _.extend(base.get_context())
                },
            }).then(function (modal) {
                var $modal = $(modal);

                $modal.appendTo($form)
                    .modal()
                    .on('hidden.bs.modal', function () {
                        $(this).remove();
                    });

                $modal.on('click', '#confirm_submit', function () {
                    var $a = $(this);
                    $form.ajaxSubmit({
                        url:  '/my/consultants/terms/update',
                        data: {lang: base.get_context().lang},
                        success: function () {
                        }
                    });
                    $modal.modal('hide');
                });
                    
            });
        return false;
    });



});
*/


function confirmTerms() {
    var isCurrentPortalChecked = $('input[name="web_approved_status"]').attr("checked") ? 1 : 0;

    /*if (isCurrentPortalChecked) {
        location.reload();
    } else {
        $('.confirm-popup').show();
    }*/

    $('.confirm-popup').show();

}
