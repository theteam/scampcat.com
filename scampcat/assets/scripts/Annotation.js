(function() {
	function Annotation() {
		this.$listItem = null;
		this.$marker = null;
		this.order = -1;
		this.markdown = '';
		this.editUrl = '';
		this.id = 0;
	}
	
	var AnnotationProto = Annotation.prototype;
	
	AnnotationProto.save = function() {
		return $.ajax( this.editUrl, {
			data: {
				text: this.markdown,
				order: this.order,
				pos_x: parseFloat( this.$marker[0].style.left ),
				pos_y: parseFloat( this.$marker[0].style.top ),
				facing: 180
			},
			type: 'POST'
		});
	}
	
	// export
	scampCat.Annotation = Annotation;
})();