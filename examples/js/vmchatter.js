function VMChatter(host, port, route, params, master)
{
	this.host = host;
	this.port = port;
	this.route = route;
	this.isOpened = false;
	this.onError = false;
	this.onOpen = false;
	this.onClose = false;
	this.onStatus = false;
	this.callbacks = [];
	this.eventCallbacks = {};
	this.master = master;

	this.ws = new WebSocket('ws://' + this.host + ':' + this.port + '/' + this.route);

	var th = this;

	for(var k in params)
	{
		this[k] = params[k];
	}

	this.ws.onopen = function()
	{
		th.isOpened = true;
		th.setStatus('success', 'Соединение установлено');
		if(typeof th.onOpen == 'function')
		{
			th.onOpen.call(th.master);
		}
	};

	this.ws.onclose = function()
	{
		th.isOpened = false;
		th.setStatus('error', 'Соединение разорвано');
		if(typeof th.onClose == 'function')
		{
			th.onClose.call(th.master);
		}
	};

	this.ws.onerror = function(e)
	{
		th.setStatus('error', 'Произошла ошибка');
		if(typeof th.onError == 'function')
		{
			th.onError.call(th.master, e);
		}
	};

	this.ws.onmessage = function(e)
	{
		var x = eval('(' + e.data + ')')

		if(!x.success)
		{
			if(typeof th.onError == 'function')
			{
				th.onError.call(th.master, x.response);
			}
		}

		if(typeof th.callbacks[x.id - 1] == 'function')
		{
			th.callbacks[x.id - 1].call(th.master, x.response, x.success);
		}
	};

	this.setStatus = function(type, message)
	{
		if(typeof th.onStatus == 'function')
		{
			th.onStatus.call(th.master, type, message);
		}
	};
}

VMChatter.prototype.isOpened = false;
VMChatter.prototype.onError = false;
VMChatter.prototype.onOpen = false;
VMChatter.prototype.onClose = false;
VMChatter.prototype.callbacks = [];
VMChatter.prototype.eventSubscribe = function(group, eventName, params, callback)
{
	var idx = this.callbacks.push(callback);
	this.eventCallbacks[idx] = callback;

	this.callMethod('event', 'subscribe', {
		'group': group,
		'event': eventName,
		'params': params,
		'callback': idx
	}, function(){});
};
VMChatter.prototype.applyMethod = function(group, method, args)
{
	var s = new String(args.callee);
	var sParams = s.match(/function \((.*)\)/g)[0].match(/\w+/g);

	var params = {};

	var callback = function(){};

	var i = 0;
	for(var k in sParams)
	{
		i += 1;

		var paramName = sParams[k];

		if(paramName == 'function')
		{
			continue;
		}
		var val = args[i - 2];

		if(paramName == 'callback')
		{
			callback = val;
			continue;
		}

		params[paramName] = val;
	}

	this.callMethod(group, method, params, callback);
};
VMChatter.prototype.callMethod = function(group, method, params, callback)
{
	var id = this.callbacks.push(callback);
	this.ws.send( JSON.stringify({group: group, method: method, params: params, id: id}) );
};