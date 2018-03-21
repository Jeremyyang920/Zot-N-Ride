API_URL = 'https://zot-n-ride-dev.herokuapp.com';

angular.module('zotnride.controllers', [])

.controller('AppCtrl', function($scope, $ionicModal, $rootScope, $window, $timeout, $ionicHistory, $ionicPlatform, $ionicPopup, $http, $cordovaGeolocation, $cordovaDatePicker, $cordovaLaunchNavigator) {

  // With the new view caching in Ionic, Controllers are only called
  // when they are recreated or on app start, instead of every page change.
  // To listen for when this page is active (for example, to refresh data),
  // listen for the $ionicView.enter event:
  //$scope.$on('$ionicView.enter', function(e) {
  //});

  $scope.loginData = {};
  $scope.user = JSON.parse($window.localStorage.getItem('user'));

  // Login modal
  $ionicModal.fromTemplateUrl('templates/login.html', {
    scope: $scope,
    animation: 'slide-in-up'
  }).then(function(modal) {
    $scope.loginModal = modal;

    if (!$scope.user || typeof $scope.user === undefined) {
      $scope.loginModal.show();
    }
  });

  $scope.closeLogin = function() {
    $scope.loginModal.hide();
    if ($ionicHistory.currentView().title === 'Registration')
      $ionicHistory.backView().go();
  };

  $scope.showLogin = function() {
    $scope.loginModal.show();
  };

  $scope.doLogin = function() {
    $http({
      method: 'POST',
      url: API_URL + '/api/login',
      data: {
        netID: $scope.loginData.email,
        password: $scope.loginData.password
      },
      headers: {'Content-Type': 'application/json'}
    }).then(function successCallback(response) {
      $scope.user = response.data;
      $window.localStorage.setItem('user', JSON.stringify(response.data));
      $scope.loginModal.hide();
      getRideStatus();
    }, function errorCallback(response) {
      $scope.showLoginFailedAlert = function() {
        var alertPopup = $ionicPopup.alert({
          title: 'Login Failed',
          template: 'Email/password is incorrect.'
        });
      };

      $scope.showLoginFailedAlert();
    });
  };

  $scope.logout = function() {
    $scope.user = null;
    $window.localStorage.removeItem('user');
    $scope.loginModal.show();
  }

  // Requests modal
  $scope.showRequests = function(direction) {
    $ionicModal.fromTemplateUrl('templates/requests.html', {
      scope: $scope,
      animation: 'slide-in-up'
    }).then(function(modal) {
      $scope.requestModal = modal;
      $scope.requestDirection = direction;
      $scope.requestModal.show();
    })
  };
  
  $scope.closeRequests = function() {
    $scope.requestModal.hide();
  }

  // Profile Modal
  $scope.showProfile = function(user) {
    $ionicModal.fromTemplateUrl('templates/profile.html', {
      scope: $scope,
      animation: 'slide-in-up'
    }).then(function(modal) {
      $http({
        method: 'GET',
        url: API_URL + '/api/user/' + user
      }).then(function successCallback(response) {
        $scope.otherUser = response.data;
      })
      $scope.profileModal = modal;
      $scope.profileModal.show();
    });
  }

  $scope.closeProfile = function() {
    $scope.profileModal.hide();
  };

  // Time formatters
  $scope.getReadableTime = function(someNumber) {
    return Math.ceil(someNumber);
  }

  $scope.formatTime = function(timestamp) {
    return moment.unix(timestamp).calendar();
  }

  // Get ride status, recursively calls itself every 5 seconds
  var getRideStatus = function() {
    if ($scope.user) {
      $http({
        method: 'GET',
        url: API_URL + '/api/getRideStatus/' + $scope.user.netID
      }).then(function successCallback(response) {
        $scope.rideStatus = response.data;

        if (response.data.toSchool) {
          $scope.activatedArrival = true;
          $scope.arrivalTime = moment.unix(response.data.toSchool.requestedTime);

          if (response.data.toSchool.riderID) {
            $http({
              method: 'GET',
              url: API_URL + '/api/user/' + response.data.toSchool.riderID
            }).then(function successCallback(response) {
              $scope.toSchoolRider = response.data;
            })
          }

          if (response.data.toSchool.driverID) {
            $http({
              method: 'GET',
              url: API_URL + '/api/user/' + response.data.toSchool.driverID
            }).then(function successCallback(response) {
              $scope.toSchoolDriver = response.data;
            })
          }
        } else if ($scope.activatedArrival) {
          $scope.activatedArrival = false;
          autofillArrivalTime();
        }

        if (response.data.fromSchool) {
          $scope.activatedDeparture = true;
          $scope.departureTime = moment.unix(response.data.fromSchool.requestedTime);

          if (response.data.fromSchool.riderID) {
            $http({
              method: 'GET',
              url: API_URL + '/api/user/' + response.data.fromSchool.riderID
            }).then(function successCallback(response) {
              $scope.fromSchoolRider = response.data;
            })
          }

          if (response.data.fromSchool.driverID) {
            $http({
              method: 'GET',
              url: API_URL + '/api/user/' + response.data.fromSchool.driverID
            }).then(function successCallback(response) {
              $scope.fromSchoolDriver = response.data;
            })
          }
        } else if ($scope.activatedDeparture) {
          $scope.activatedDeparture = false;
          autofillDepartureTime();
        }

        if ($scope.user.isDriver && $scope.activatedArrival && response.data.toSchool && !response.data.toSchool.riderID) {
          getToRequests();
        }

        if ($scope.user.isDriver && $scope.activatedDeparture && response.data.fromSchool && !response.data.fromSchool.riderID) {
          getFromRequests();
        }

        $timeout(getRideStatus, 5000);
      })
    }
  }

  // Get all rider requests to school (drivers only)
  var getToRequests = function() {
    $http({
      method: 'GET',
      url: API_URL + '/api/getRequests/' + $scope.user.netID + '/0'
    }).then(function successCallback(response) {
      $scope.toSchool = response.data;
    })
  }

  // Get all rider requests from school (drivers only)
  var getFromRequests = function() {
    $http({
      method: 'GET',
      url: API_URL + '/api/getRequests/' + $scope.user.netID + '/1'
    }).then(function successCallback(response) {
      $scope.fromSchool = response.data;
    })
  }

  // Begin recursive call if user is logged in
  if ($scope.user) {
    getRideStatus();
  }

  // Convert Date.getDay() number [0-6] to its string representations
  var getDayString = function(day) {
    switch(day) {
      case 0:
      case 1:
      case 6:
      case 7:
        return 'Mon';
      case 2:
        return 'Tue';
      case 3:
        return 'Wed';
      case 4:
        return 'Thu';
      case 5:
        return 'Fri';
    }
  }

  // Autofill arrival schedule (to school)
  var autofillArrivalTime = function() {
    if ($scope.user && $scope.user.arrivals) {
      var day = new Date().getDay();
      var dayString = getDayString(day);
  
      var dateObj = moment($scope.user.arrivals[dayString], 'Hmm');
  
      if (dateObj < moment()) {
        dayString = getDayString(day + 1);
        $scope.arrivalTime = moment($scope.user.arrivals[dayString], 'Hmm').add(1, 'day');
        
        if (day === 5) {
          $scope.arrivalTime = $scope.arrivalTime.add(2, 'day');
        } else if (day === 6) {
          $scope.arrivalTime = $scope.arrivalTime.add(1, 'day');
        }
      } else {
        $scope.arrivalTime = dateObj;
      }
    } else {
      $scope.arrivalTime = moment().add(1, 'hours').minute(0).second(0);
    }
  }

  // Autofill departure schedule (from school)
  var autofillDepartureTime = function() {
    if ($scope.user && $scope.user.departures) {
      var day = new Date().getDay();
      var dayString = getDayString(day);
  
      var dateObj = moment($scope.user.departures[dayString], 'Hmm');
  
      if (dateObj < moment()) {
        dayString = getDayString(day + 1);
        $scope.departureTime = moment($scope.user.departures[dayString], 'Hmm').add(1, 'day');
  
        if (day === 5) {
          $scope.departureTime = $scope.departureTime.add(2, 'day');
        } else if (day === 6) {
          $scope.departureTime = $scope.departureTime.add(1, 'day');
        }
      } else {
        $scope.departureTime = dateObj;
      }
    } else {
      $scope.departureTime = moment().add(3, 'hours').minute(0).second(0);
    }
  }

  autofillArrivalTime();
  autofillDepartureTime();

  // Watch the values and update them when changed
  $scope.$watch('arrivalTime', function() {
    $scope.getArrivalTime = moment($scope.arrivalTime).calendar();
  })

  $scope.$watch('departureTime', function() {
    $scope.getDepartureTime = moment($scope.departureTime).calendar();
  })

  $ionicPlatform.ready(function() {
    // Timepickers
    $scope.setArrivalTime = function() {
      $cordovaDatePicker.show({
        date: $scope.arrivalTime,
        mode: 'datetime',
        minDate: Date,
        maxDate: moment().add(1, 'day').endOf('day'),
        allowOldDates: false,
        minuteInterval: 30
      }).then(function(datetime) {
        $scope.arrivalTime = moment(datetime);
      });
    }

    $scope.setDepartureTime = function() {
      $cordovaDatePicker.show({
        date: $scope.departureTime,
        mode: 'datetime',
        minDate: Date,
        maxDate: moment().add(1, 'day').endOf('day'),
        allowOldDates: false,
        minuteInterval: 30
      }).then(function(datetime) {
        $scope.departureTime = moment(datetime);
      });
    }

    // Launch navigation app
    $scope.navigate = function(address) {
      $cordovaLaunchNavigator.navigate(address);
    }
  });

  // Initialize the toggles to `false` so toggleRequest works
  $scope.activatedArrival = false;
  $scope.activatedDeparture = false;

  // Accept rider requests (drivers only)
  $scope.acceptRequest = function(direction, riderID) {
    $http({
      method: 'POST',
      url: API_URL + '/api/confirmRequest',
      data: {
        driverID: $scope.user.netID,
        riderID: riderID,
        direction: direction
      },
      headers: {'Content-Type': 'application/json'}
    }).then(function successCallback(response) {
      $scope.requestModal.hide();
    }, function errorCallback(response) {
      $scope.showAcceptanceFailedAlert = function() {
        var alertPopup = $ionicPopup.alert({
          title: 'Acceptance Failed',
          template: 'Something went wrong!'
        });
      };

      $scope.showAcceptanceFailedAlert();
    });
  }

  // Toggle requests
  $scope.toggleRequest = function(direction) {
    var endpoint, data = {};
    data.netID = $scope.user.netID;
    data.direction = direction;

    // 0 = to school, 1 = from school
    if (direction === 0) {
      if (!$scope.activatedArrival) {
        endpoint = '/api/addRequest';
        data.time = $scope.arrivalTime.unix();
      } else if ($scope.rideStatus.toSchool.riderID || $scope.rideStatus.toSchool.driverID) {
        endpoint = '/api/endRide';
        autofillArrivalTime();
      } else {
        endpoint = '/api/removeRequest';
      }

      $scope.activatedArrival = !$scope.activatedArrival;
    } else {
      if (!$scope.activatedDeparture) {
        endpoint = '/api/addRequest';
        data.time = $scope.departureTime.unix();
      } else if ($scope.rideStatus.fromSchool.riderID || $scope.rideStatus.fromSchool.driverID) {
        endpoint = '/api/endRide';
        autofillDepartureTime();
      } else {
        endpoint = '/api/removeRequest';
      }

      $scope.activatedDeparture = !$scope.activatedDeparture;
    }

    $http({
      method: 'POST',
      url: API_URL + endpoint,
      data: data,
      headers: {'Content-Type': 'application/json'}
    }).then(function successCallback(response) {
      console.log(response);
    }, function errorCallback(response) {
      console.log(response);

      if (direction === 0) {
        $scope.activatedArrival = !$scope.activatedArrival;
      } else {
        $scope.activatedDeparture = !$scope.activatedDeparture;
      }

      $scope.showRequestFailedAlert = function() {
        var alertPopup = $ionicPopup.alert({
          title: 'Request failed!',
          template: 'Something went wrong.'
        });
      };

      $scope.showRequestFailedAlert();
    });
  }
})

.controller('RegistrationCtrl', function($scope, $stateParams, $http) {
  $scope.registrationData = {};

  $scope.registerAccount = function() {
    
  }
})

.controller('UploadCtrl', function($scope, $stateParams, $rootScope, $ionicHistory) {
  if (document.getElementById('DropzoneElementId')) {
    var myDropzone = new Dropzone("div#ical-dropzone", { url: "/file/post"});
  }

  $scope.goHome = function(){
    $ionicHistory.goBack(-2);
  }
  
  $scope.uploadSchedule = function() {
    $scope.goHome();
  }
})

.controller('ListingCtrl', function($scope, $stateParams, $rootScope, $http, $ionicModal) {

});