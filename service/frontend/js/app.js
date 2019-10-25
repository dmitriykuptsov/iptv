var app = angular.module("streamtv", []);

app.directive('videoPlayer', function() {
	function link(scope, element, attrs) {
		element.html("<div id=\"player\"></div>");
		scope.player = new Clappr.Player({
			plugins: [Clappr.FlasHLS],
			parentId: "#player",
			autoPlay: true,
			width: "100%",
			height: "80%"
		});
	}
	return {
		scope: {
			"player": "="
		},
		link: link
	};
});

/* Creates new channel class. */
var Channel = function(id, streamId, name, iconPath) {
	this.id = id;
	this.streamId = streamId;
	this.name = name;
	this.iconPath = iconPath;
}

/* Returns the name of the channel */
Channel.prototype.getName = function() {
	return this.name;
}

/* Returns ID of channel */
Channel.prototype.getId = function() {
	return this.id;
}

/* Returns the ID of a raw stream */
Channel.prototype.getStreamId = function() {
	return this.streamId;
}

Channel.prototype.getIconPath = function() {
	return this.iconPath;
}

/* Constructs the program using raw data */
var Program = function(id, programName, startTime, endTime) {
	this.channelId = id;
	this.program = programName;
	this.startTime = new Date(startTime);
	this.endTime = new Date(endTime);
}

/* Returns the ID of channel */
Program.prototype.getChannelId = function() {
	return this.channelId;
}

/* Retruns the name of the program */
Program.prototype.getProgramName = function() {
	return this.program;
}

/* Gets program start time */
Program.prototype.getProgramStartTime = function() {
	return this.startTime;
}

/* Returns formatted program start time */
Program.prototype.getProgramStartTimeFormatted = function() {
	var formatted = "";
	var hours = this.startTime.getHours();
	var minutes = this.startTime.getMinutes();
	if (hours < 10) {
		formatted = "0" + hours;
	} else {
		formatted = hours;
	}
	if (minutes < 10) {
		formatted += ":0" + minutes;
	} else {
		formatted += ":" + minutes;
	}
	return formatted;
}

/* Returns formatted program end time */
Program.prototype.getProgramEndTimeFormatted = function() {
	var formatted = "";
	var hours = this.endTime.getHours();
	var minutes = this.endTime.getMinutes();
	if (hours < 10) {
		formatted = "0" + hours;
	} else {
		formatted = hours;
	}
	if (minutes < 10) {
		formatted += ":0" + minutes;
	} else {
		formatted += ":" + minutes;
	}
	return formatted;
}

/* Gets the style for the program based on the start and end time */
/* Programs which are in past will have past-program style */
/* Currently showing program will have the style current-program */
/* Future programs will have future-program style */
Program.prototype.getStyleBasedOnProgramTime = function() {
	var now = new Date();
	if (now > this.endTime) {
		return "past-program";
	}
	if (now > this.startTime && now < this.endTime) {
		return "current-program";
	}
	if (now < this.endTime) {
		return "future-program";
	}
}

/* Gets program end time */
Program.prototype.getProgramEndTime = function() {
	return this.endTime;
}

/* Basic exception class */
var Exception = function(msg) {
	this.message = msg;
}

/* Gets message of exception */
Exception.prototype.getMessage = function() {
	return this.message;
}

/* Starts the registration procedure */
function register(username, password, first_name, last_name, $http, cb) {
	$http({
		method: "POST",
		url: "/api/register/",
		data: {
			username: username,
			password: password,
			first_name: first_name,
			last_name: last_name
		},
		headers: {
			"Content-type": "application/json;charset=utf-8"
		}
	})
	.then(function(response) {
		cb(true);
	}, function(rejection) {
		cb(false, new Exception(rejection.data.reason));
	});	
}

/* Authenticates the user */
function authenticate(username, password, $http, cb) {
	$http({
		method: "POST",
		url: "/api/authenticate/",
		data: {
			username: username,
			password: password
		},
		headers: {
			"Content-type": "application/json;charset=utf-8"
		}
	})
	.then(function(response) {
		cb(true, null);
	}, function(rejection) {
		cb(false, new Exception(rejection.data.reason));
	});
}

/* Logs out from the system */
function logout($http, cb) {
	$http({
		method: "GET",
		url: "/api/logout/",
		headers: {
			"Content-type": "application/json;charset=utf-8"
		}
	})
	.then(function(response) {
		cb(true);
	}, function(rejection) {
		cb(false);
	});
}

/* Checks the access */
function check_access($http, cb) {
	$http({
		method: "GET",
		url: "/api/check_token/",
		headers: {
			"Content-type": "application/json;charset=utf-8"
		}
	})
	.then(function(response) {
		cb(true);
	}, function(rejection) {
		cb(false);
	});
}

/* Changes the password */
function change_password($http, username, old_password, new_password, cb) {
	$http({
		method: "POST",
		url: "/api/change_password/",
		data: {
			username: username,
			old_password: old_password,
			new_password: new_password
		},
		headers: {
			"Content-type": "application/json;charset=utf-8"
		}
	})
	.then(function(response) {
		cb(true, null);
	}, function(rejection) {
		cb(false, new Exception(rejection.data.reason));
	});	
}

/* Gets list of channels */
function get_channels($http, cb) {
	$http({
		method: "GET",
		url: "/api/channels/",
		headers: {
			"Content-type": "application/json;charset=utf-8"
		}
	})
	.then(function(response) {
		var data = response.data;
		if (data.result instanceof Array) {
			var channels = [];
			for (var i = 0; i < data.result.length; i++) {
				channels.push(
					new Channel(
						data.result[i]["id"], 
						data.result[i]["stream_id"],
						data.result[i]["channel_name"],
						data.result[i]["icon_path"]
					)
				);
			}
			cb(true, channels);
		} else {
			cb(true, []);
		}
		
	}, function(rejection) {
		cb(false, new Exception(rejection.data.reason));
	});
}

/* Gets program for the selected channel */
function get_program(id, $http, cb) {
	$http({
		method: "GET",
		url: "/api/program/" + encodeURIComponent(id) + "/",
		headers: {
			"Content-type": "application/json;charset=utf-8"
		}
	})
	.then(function(response) {
		var data = response.data;
		if (data.result instanceof Array) {
			var programs = [];
			for (var i = 0; i < data.result.length; i++) {
				var startTime = data.result[i]["start_time"];
				var endTime = data.result[i]["end_time"];
				if (!(startTime instanceof Date)) {
					startTime = new Date(startTime);
				}
				if (!(endTime instanceof Date)) {
					endTime = new Date(endTime);
				}
				programs.push(
					new Program(
						data.result[i]["id"], 
						data.result[i]["program_name"], 
						startTime,
						endTime
					)
				);
			}
			cb(true, programs);
		} else {
			cb(true, []);
		}
	}, function(rejection) {
		cb(false, new Exception(rejection.data.reason));
	});
}

/* Main application controller */
app.controller("mainCtrl", function($scope, $http, $location, $interval) {

	$scope.auth = {};
	$scope.player = { value: null };
	$scope.playlist = null;

	check_access($http, function(status) {
		$scope.authenticated = status;
	});

	/* Periodically checks the authentication token */
	var promise = $interval(function() {
		check_access($http, function(status) {
			$scope.authenticated = status;
		});
	}, 1000);

	/* Gets list of channles and later on the program for the first channel in the list */
	get_channels($http, function(status, channels) {
		if (status) {
			$scope.channels = channels;
			if ($scope.channels.length > 0) {
				var baseUrl = $location.protocol() + "://" + $location.host() + ":" + $location.port();
				$scope.playlist = baseUrl + "/streaming/playlist/" + $scope.channels[0].getStreamId() + "/stream.m3u8";
				// Get the pro                                                     ram for the first selected channel
				$scope.selected_channel = $scope.channels[0];
				get_program($scope.selected_channel.getId(), $http, function(status, programs) {
					if (status) {
						$scope.programs = programs;
					} else {
						//Show error
					}
				});
			}
		}
	});

	/* Logs into the system */
	$scope.login = function() {
		authenticate($scope.auth.username, $scope.auth.password, $http, function(authenticated, exception) {
			if (authenticated) {
				$scope.authenticated = true;
				get_channels($http, function(status, response) {
					if (status) {
						$scope.channels = response;
						$scope.selected_channel = $scope.channels[0];
						get_program($scope.selected_channel.getId(), $http, function(status, programs) {
							if (status) {
								$scope.programs = programs;
							} else {
								//Show error
							}
						});
					}
				});
			} else {
				$scope.authenticated = false;
			}
		});
		return false;
	}

	/* Logs out of the system */
	$scope.logout = function() {
		logout($http, function(status, response) {
			if (status) {
				$scope.authenticated = false;
			} else {
				check_access($http, function(status) {
					$scope.authenticated = status;	
				});
			}
		});
		return false;
	}

	/* Registers the user in the system */
	$scope.register = function() {
		register($http, 
			$scope.auth.username, 
			$scope.auth.password, 
			$scope.auth.first_name, 
			$scope.auth.last_name, 
			function(status, exception) {
				if (status) {
					// 
				} else {

				}
			}
		);
	}

	/* Updates the playlist variable and program based on selected channel */
	$scope.channel_selected = function(id, stream_id) {
		var baseUrl = $location.protocol() + "://" + $location.host() + ":" + $location.port();
		$scope.playlist = baseUrl + "/streaming/playlist/" + stream_id + "/stream.m3u8";
		//$scope.selected_channel = $scope.channels[0];
		$scope.channels.forEach(function(channel) {
			if (channel.getId() == id) {
				$scope.selected_channel = channel;
			}
		})
		get_program(id, $http, function(status, programs) {
			if (status) {
				$scope.programs = programs;
			} else {
				//Show error
			}
		});
	}

	$scope.go_to_register = function() {
		$scope.registration = true;
	}

	$scope.cancel_registration = function() {
		$scope.registration = false;
	}

	/* Watches the changes of the playlist variable */
	/* Once the playlist is updated the player is reconfigured */ 
	$scope.$watch('playlist', function() {
		if ($scope.player.value != null && $scope.playlist != null) {
			$scope.player.value.configure({
				source: $scope.playlist
			});
		}
	});

	/* Watches the changes of the player variable */
	$scope.$watch('player.value', function() {
		if ($scope.player.value != null && $scope.playlist != null) {
			$scope.player.value.configure({
				source: $scope.playlist
			});
		}
	});
});
