package com.oppian.oframe.utils
{
	import flash.events.Event;
	import flash.events.EventDispatcher;
	import flash.events.IEventDispatcher;
	import flash.events.MouseEvent;
	import flash.events.TimerEvent;
	import flash.utils.Timer;
	
	import mx.core.UIComponent;

	/**
	 * The SFDoubleClickManager allows to observe click and double click events on an UIComponent.
	 * When a double click occurs, only the double click event is sent.
	 */
	public class SFDoubleClickManager implements IEventDispatcher
	{
		// This constant must be low to have a responsive interface
		// but higher than the time between two clicks which convert them in a double click. 
		private const TIME_OUT:int = 300;
		
		// Component to observe
		private var component:UIComponent = null;
		// Our own event dispatcher (used to implement IEventDispatcher)
		private var eventDispatcher:IEventDispatcher = null;
		
		public function SFDoubleClickManager(component:UIComponent)
		{
			super();
			this.component = component;
			
			// We use this constructor for EventDispatcher to keep current target unchanged when we forward events
			this.eventDispatcher = new EventDispatcher(this.component);
			this.component.addEventListener(MouseEvent.CLICK, singleClick);
			this.component.addEventListener(MouseEvent.DOUBLE_CLICK, doubleClick);
		}
		
		// This timer will be used to measure time between click and double click events.
		private var timer:Timer = null;
		// This var is used to store click event.
		private var storedEvent:Event = null;
		// This method resets timer and nullify var
		private function stopTimer():Event {
			var lc_storedEvent:Event = storedEvent;
			storedEvent = null;
			if (timer != null) {
				timer.removeEventListener(TimerEvent.TIMER_COMPLETE, deferredSingleClick);
				timer.reset();
				timer = null;
			}
			return lc_storedEvent;
		}
		// This method stops current timer, creates a new one and starts it.
		private function startTimer(event:Event):void {
			stopTimer();
			storedEvent = event;
			timer = new Timer(TIME_OUT, 1);
	        timer.addEventListener(TimerEvent.TIMER_COMPLETE, deferredSingleClick);
	        timer.start();
		}
		
		// This method is called when a click event is sent
		// One timer is started, event will be forwarded only if timer times out.
		private function singleClick(event:MouseEvent):void {
			startTimer(event);
		}
		// This method is called when timer times out (no double click)
		// Stored event is forwarded
	    private function deferredSingleClick(event:TimerEvent = null):void {
	    	var lc_event:Event = stopTimer();
			dispatchEvent(lc_event);
	    }
		// This method is called when a double click event is sent
		// Timer is stopped, so that click event is not sent
		private function doubleClick(event:MouseEvent):void {
			stopTimer();
			dispatchEvent(event);
		}
		
// The following methods implement IEventDispatcher.
public function addEventListener(type:String, listener:Function, useCapture:Boolean = false, priority:int = 0, useWeakReference:Boolean = false):void {
	this.eventDispatcher.addEventListener(type, listener, useCapture, priority, useWeakReference);
}
 	 	
public function dispatchEvent(event:Event):Boolean {
	return this.eventDispatcher.dispatchEvent(event);
}
 	 	
public function hasEventListener(type:String):Boolean {
	return this.eventDispatcher.hasEventListener(type);
}

public function removeEventListener(type:String, listener:Function, useCapture:Boolean = false):void {
	this.eventDispatcher.removeEventListener(type, listener, useCapture);
}
 	 	
public function willTrigger(type:String):Boolean {
	return this.eventDispatcher.willTrigger(type);
}
		
	}
	
	
	
}