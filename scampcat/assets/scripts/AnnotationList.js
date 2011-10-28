(function() {
	function AnnotationList( $container, annotation_markdowns ) {
		$container = $( $container );
		
		var annotationList = this;
		
		$container.sortable({
			axis: 'y',
			handle: '.index',
			stop: function() {
				annotationList._reorderAnnotations();
				annotationList._reindexLis();
				annotationList.trigger('reordered', annotationList);
			}
		});
		
		this._annotations = [];
		this.$container = $container;
		this._collectAnnotations( annotation_markdowns );
		this._addDeleteEvent();
	}
	
	var AnnotationListProto = AnnotationList.prototype = new scampCat.EventEmitter;
	
	AnnotationListProto._collectAnnotations = function(annotation_markdowns) {
		var annotationList = this;
		annotationList._annotations = [];
		
		annotationList.$container.children().each(function(i) {
			var annotation = new scampCat.Annotation,
				$listItem = $(this).data('annotation', annotation);
				
			annotation.$listItem = $listItem;
			annotation.order = i+1;
			annotation.id = $listItem.data('id');
			annotation.markdown = annotation_markdowns[i];
			annotation.editUrl = $listItem.data('editUrl');
			annotationList._annotations[i] = annotation;
		});
	};
	
	AnnotationListProto.getAnnotations = function() {
		return this._annotations.slice(0);
	};
	
	AnnotationListProto._reorderAnnotations = function() {
		// recreate the _annotations array by their list item dom order
		
		var annotationList = this,
			annotation,
			newAnnotationsOrder = [],
			$items = annotationList.$container.children();
			
		$items.each(function(i) {
			annotation = $(this).data('annotation');
			annotation.order = i+1;
			newAnnotationsOrder[i] = annotation;
		});
		
		annotationList._annotations = newAnnotationsOrder;
	};
	
	AnnotationListProto._reindexLis = function() {
		this.$container.find('span.index').each(function(i) {
			this.innerHTML = i+1;
		});
	};
	
	AnnotationListProto.add = function(editUrl, text, markdown, id) {
		var annotation = new scampCat.Annotation,
			$listItems =  this.$container.children(),
			$newListItem = $('<li class="annotation"><span class="index"></span><div class="inline-edit annotation-text" tabindex="0" data-edit-type="textarea"><p>Click to edit</p></div><div class="delete custom" title="Delete">X</div></li>');
		
		$newListItem.data('annotation', annotation);
		$newListItem.find('span.index').text( $listItems.length + 1 );
		$newListItem.find('div.text').html( text );
		this.$container.append( $newListItem );
		
		annotation.$listItem = $newListItem;
		annotation.order = $listItems.length + 1;
		annotation.markdown = markdown;
		annotation.editUrl = editUrl;
		annotation.id = id;
		this._annotations.push( annotation );
		return annotation;
	};
	
	AnnotationListProto._addDeleteEvent = function() {
		var annotationList = this;
		
		annotationList.$container.delegate('.delete', 'click', function() {
			var $listItem = $(this).closest('li'),
				annotation = $listItem.data('annotation');
			
			annotation.$listItem.remove();
			annotationList._reorderAnnotations();
			annotationList._reindexLis();
			annotationList.trigger('deleted', annotation);
			annotationList.trigger('reordered', annotationList);
		});
	};
	
	// export
	scampCat.AnnotationList = AnnotationList;
})();
