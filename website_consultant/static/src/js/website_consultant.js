function confirmTerms() {
    $('.modalDialog').show();
};

odoo.define('website_event.consultant', function (require) {

    var ajax = require('web.ajax');
    var Widget = require('web.Widget');
    var web_editor_base = require('web_editor.base');
    
    // Catch registration form event, because of JS for attendee details
    var ConsultantEditForm = Widget.extend({
        start: function () {
            var self = this;
            var res = this._super.apply(this.arguments).then(function () {
                $('[name="next_available"]').datetimepicker({});
            });
            return res
        },
    });

    web_editor_base.ready().then(function () {
        var consultant_edit_form = new ConsultantEditForm().appendTo($('#consultant_edit_form'));
    });

    return {
        ConsultantEditForm: ConsultantEditForm
    };

});