(function() {
	function MarkerView( $container ) {
		$container = $( $container );
		
		var markerView = this,
			$markers = $container.find('div.annotation');
		
		
		this._makeDraggable( $markers );
		
		markerView.$container = $container;
		markerView._$markers = $markers;
	}
	
	var MarkerViewProto = MarkerView.prototype = new scampCat.EventEmitter;
	
	MarkerViewProto.populateAnnotations = function( annotations ) {
		this._$markers.each(function(i) {
			annotations[i].$marker = $(this).data( 'annotation', annotations[i] );
		});
	};
	
	MarkerViewProto.add = function( annotation, x, y ) {
		var $newMarker = $('<div class="annotation"><div class="label-180"><span class="index"></span><div class="arrow"></div></div></div>');
		
		// copy index number - this could be quicker (eg, no dom)
		$newMarker.find('span.index').html( annotation.$listItem.find('span.index').html() );
		
		$newMarker.css({
			top: y + '%',
			left: x + '%',
			position: 'absolute'
		});
		
		annotation.$marker = $newMarker;
		$newMarker.data('annotation', annotation);
		this._makeDraggable( $newMarker );
		this.$container.append( $newMarker );
	};
	
	MarkerViewProto.remove = function(annotation) {
		annotation.$marker.remove();
	}
	
	MarkerViewProto.reorder = function( annotations ) {
		for (var i = 0, len = annotations.length; i < len; i++) {
			annotations[i].$marker.appendTo( this.$container )
				.find('span.index').text( i+1 );
		}
	};
	
	MarkerViewProto._fixedToPercent = function( $marker ) {
		var $container = this.$container,
			markerPos = $marker.position();
		
		$marker.css({
			left: Math.round( ( markerPos.left / $container.width()  ) * 100000 ) / 1000 + '%',
			top:  Math.round( ( markerPos.top  / $container.height() ) * 100000 ) / 1000 + '%'
		});
	};
	
	MarkerViewProto._makeDraggable = function( $elms ) {
		var markerView = this;
		
		$elms.draggable({
			containment: this.$container,
			stop: function() {
				var $marker = $(this);
				markerView._fixedToPercent( $marker );
				markerView.trigger('markerMoved', $marker);
			}
		});
	};
	
	// export
	scampCat.MarkerView = MarkerView;
})();