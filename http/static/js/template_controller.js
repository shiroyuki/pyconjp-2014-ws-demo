function TemplateController() {
    this.templates = {};
}

TemplateController.prototype.get = function (name) {
    var template = this.templates[name],
        $template
    ;

    if (template === undefined) {
        template = $('script[data-name=' + name + ']').text();
        this.templates[name] = template;
    }
    
    return template
};