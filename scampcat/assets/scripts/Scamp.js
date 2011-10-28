(function() {
	function Scamp( $container, submitUrl, reorderUrl, description_markdown, annotation_markdowns ) {
		$container = $( $container );
		this.$container = $container;
		var scamp = this,
            $description = this.$container.find('div.description'),
			annotations = new scampCat.AnnotationList( $container.find('ol.annotation-list'), annotation_markdowns ),
			markerView  = new scampCat.MarkerView( $container.find('div.marker-container') );
		
		markerView.populateAnnotations( annotations.getAnnotations() );
		
		markerView.bind('markerMoved', function( $marker ) {
			$marker.data('annotation').save().done(function(response) {
				
			});
		});
		
		annotations.bind('reordered', function() {
			var annotationsArr = annotations.getAnnotations(),
				ids = $.map(annotationsArr, function(annotation) { return annotation.id });
				
			markerView.reorder( annotationsArr );
			
			$.ajax( reorderUrl, {
				data: 'order=' + ids.join('&order='),
				type: 'POST'
			});
		});
		
		annotations.bind('deleted', function(annotation) {
			markerView.remove( annotation );
			$.ajax( annotation.$listItem.data('editUrl'), {
				type: 'DELETE',
				success: function(data) {
									
				}
			});
		});

        // Attach markdown data to description element
        $description.data('description', description_markdown);
		
		this._annotations = annotations;
		this._markerView = markerView;
		this._description_markdown = description_markdown;
		this._annotation_markdowns = annotation_markdowns;
		this._submitUrl = submitUrl;
        this._reorderUrl = reorderUrl;
		this._initInlineEdit();
		this._addAnnotationEvents();
	}
	
	var ScampProto = Scamp.prototype;
	
	ScampProto._initInlineEdit = function() {
		var scamp = this,
			inlineEdit = new scampCat.InlineEdit( this.$container );
		
		inlineEdit.populateInput = function( $elm ) {
			var deferred = new $.Deferred;
			if ( $elm.hasClass('annotation-text') ) {
				$elm.show();
				$elm.next().width( $elm.width() - 5 );
				$elm.hide();
				deferred.resolve( $elm.closest('li').data('annotation').markdown );
			}
			else if ( $elm.hasClass('description') ) {
                // Gets the markdown.
                deferred.resolve( $elm.data('description') );
            
            } else {
				deferred.resolve( $.trim( $elm.text() ) );
			}
			return deferred.promise();
		};
		
		inlineEdit.saveValue = function( $elm, val ) {
			var deferred = new $.Deferred;
			if ( $elm.hasClass('annotation-text') ) {
				var annotation = $elm.closest('li').data('annotation');
				annotation.markdown = val;
				
				annotation.save().done(function(data) {
					deferred.resolve( data.text_rendered );
				});
			}
			else {
				var data = {},
					isTitle = $elm.hasClass('title'),
                    isDescription = $elm.hasClass('description');
				data.title = isTitle ? val : $.trim( $('span.inline-edit.title').text() );
				data.description = isDescription ? val : $.trim( $('div.inline-edit.description').data('description') );
				
				$.ajax( '.', {
					data: data,
					type: 'POST',
					success: function(data) {
                        if (isDescription) {
                            $elm.data('description', data.description_raw);
                        } 
						deferred.resolve( isTitle ? data.title : data.description );
					}
				});
			}
			return deferred.promise();
		};
	};
	
	ScampProto._addAnnotationEvents = function() {
		var scamp = this;
		
		this.$container.find('div.add-annotation').click(function(event) {
			event.preventDefault();
			if (scamp.busy) { return; }
			scamp.busy = true;
			$.ajax(scamp._submitUrl, {
				type: 'PUT',
				data: {
					text: 'Click to edit',
					order: scamp._annotations.getAnnotations().length + 1,
					pos_x: 0,
					pos_y: 0,
					facing: 180
				},
				success: function(data) {
					var annotation = scamp._annotations.add( data.edit_url, data.text_rendered, data.text_raw, data.id );
					scamp._markerView.add( annotation, 0, 0 );
					scamp.busy = false;					
				}
			});
		});
	};
	
	// export
	scampCat.Scamp = Scamp;
})();
